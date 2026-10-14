"""Bounded subprocess I/O and sampled resource safeguards for TRUSTED code only.

No filesystem/network isolation. RSS polling is a soft limit (20 ms sampling),
not a Windows Job Object or OS-enforced allocation limit.
"""
from dataclasses import dataclass
import os
import subprocess
import threading
import time
import psutil


def kill_process_tree(pid, known_children=()):
    processes = list(known_children)
    try:
        parent = psutil.Process(pid)
        processes.extend(parent.children(recursive=True))
        processes.append(parent)
    except psutil.NoSuchProcess:
        pass
    for process in processes:
        try:
            process.kill()
        except psutil.NoSuchProcess:
            pass
    if processes:
        _, alive = psutil.wait_procs(processes, timeout=1)
        for process in alive:
            try:
                process.kill()
            except psutil.NoSuchProcess:
                pass


@dataclass
class ProcessResult:
    returncode: int
    stdout: str
    stderr: str
    reason: str | None
    elapsed_ms: float
    stdout_bytes: int
    stderr_bytes: int


def run_bounded(command, *, cwd, input_data='', timeout=2, output_limit=10240,
                memory_limit_mb=256):
    """Retain at most output_limit bytes PER pipe and terminate on overflow."""
    if timeout <= 0 or output_limit <= 0 or memory_limit_mb <= 0:
        raise ValueError('Resource limits must be positive')
    start = time.perf_counter()
    if os.name == 'nt':
        # Suppress host crash/error dialog boxes, which can turn faults into TLE.
        import ctypes
        ctypes.windll.kernel32.SetErrorMode(0x0001 | 0x0002)
    proc = subprocess.Popen(command, cwd=cwd, stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
    buffers = [bytearray(), bytearray()]
    overflow = threading.Event()
    io_errors = []
    children = {}

    def read_pipe(pipe, buffer):
        try:
            while True:
                chunk = os.read(pipe.fileno(), min(4096, output_limit + 1))
                if not chunk:
                    break
                remaining = output_limit - len(buffer)
                buffer.extend(chunk[:remaining])
                if len(chunk) > remaining:
                    overflow.set()
                    break
        except (OSError, ValueError) as exc:
            io_errors.append(exc)

    def write_input():
        try:
            data = input_data.encode('utf-8')
            for index in range(0, len(data), 4096):
                proc.stdin.write(data[index:index + 4096])
            proc.stdin.flush()
        except (BrokenPipeError, OSError):
            pass  # Exiting without consuming input is legal; judge stdout/exit code.
        finally:
            try:
                proc.stdin.close()
            except (BrokenPipeError, OSError):
                pass

    threads = [threading.Thread(target=read_pipe, args=(pipe, buf), daemon=True)
               for pipe, buf in zip((proc.stdout, proc.stderr), buffers)]
    threads.append(threading.Thread(target=write_input, daemon=True))
    reason = None
    try:
        for thread in threads:
            thread.start()
        while True:
            try:
                parent = psutil.Process(proc.pid)
                for child in parent.children(recursive=True):
                    children[(child.pid, child.create_time())] = child
                processes = [parent, *children.values()]
                rss = 0
                for process in processes:
                    try:
                        rss += process.memory_info().rss
                    except psutil.NoSuchProcess:
                        pass
                if rss > memory_limit_mb * 1024 * 1024:
                    reason = 'memory'
            except psutil.NoSuchProcess:
                pass
            if overflow.is_set():
                reason = 'output'
            if io_errors:
                reason = 'io'
            if reason or time.perf_counter() - start > timeout:
                reason = reason or 'timeout'
                break
            if proc.poll() is not None and all(not t.is_alive() for t in threads):
                break
            time.sleep(.02)
    finally:
        # Also terminate observed children after the parent exits successfully.
        kill_process_tree(proc.pid, children.values())
        proc.wait(timeout=2)
        for thread in threads:
            thread.join(timeout=2)
        if any(t.is_alive() for t in threads):
            raise RuntimeError('Process pipe cleanup incomplete; execution stopped')
        proc.stdout.close()
        proc.stderr.close()
    decoded = [bytes(buf).decode('utf-8', errors='replace') for buf in buffers]
    if reason == 'output':
        # Fixed-size metadata; original retained buffers remain bounded.
        decoded[0] += '\n[Output truncated at buffer limit]'
    return ProcessResult(proc.returncode, *decoded, reason,
                         (time.perf_counter() - start) * 1000,
                         len(buffers[0]), len(buffers[1]))
