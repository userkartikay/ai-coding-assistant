# Execution readiness assessment — 2026-10-13

This is the O1 investigation, not implementation of browser execution. No untrusted
code was run, no Windows settings changed, and no VM/container/image was installed.

## Verified current state

- `backend/runner/process.py` uses host subprocesses, bounded pipes, timeouts,
  sampled RSS, and observed-child cleanup. There is no filesystem/network boundary
  or kernel Job Object containment. The explicit trusted flag remains essential.
- `backend/api/app.py` has no Run/Submit/judge endpoint; source accepted by review is
  model input only. Backend bootstrap/health still reports execution disabled.
- The catalogue remains 133 official identities and 10 verified executable fixtures.
  No question, test harness, reference report, draft key, or learner record changed.
- This laptop exposes `wsl.exe` and lists Ubuntu plus docker-desktop distributions;
  default WSL version is 2 and default distribution is docker-desktop. Docker CLI
  is installed, but its Linux daemon pipe is unavailable. Merely finding the CLI
  is not proof that a container execution worker is usable.

## Options compared

| Option | Meaningful isolation | Hardware cost / latency | Implementation / maintenance |
| --- | --- | --- | --- |
| Restricted token / Job Object alone | Insufficient for arbitrary code; needs a separate resource-access boundary | Low native overhead; no VM boot | Useful kernel quotas/cleanup, but does not solve host file/network access |
| Native Windows AppContainer, potentially LPAC, plus Job Objects | Documented OS resource boundary when correct capabilities and ACLs are used; not implemented or validated here | Lowest prospective RAM/startup overhead; no second OS | Highest Windows-specific engineering/testing: compilation and execution, compiler/runtime DLL access, per-job ACLs, handles, children, cleanup |
| Plain WSL2 distribution | Not an untrusted-code sandbox | VM memory/CPU shared with other WSL activity; cold-start cost | Easy compiler access, unsafe to treat default drive mounts/interop settings as containment |
| Restricted Linux container through Docker Desktop | Potential container boundary depends on runtime hardening; WSL itself is not the host security boundary | VM/daemon and image overhead; warm container startup likely lower than cold VM startup | Requires working daemon, pinned compiler image, denied networking, no host/socket mounts, non-root user, dropped capabilities, read-only root, kernel quotas and adversarial checks |
| Separately managed restricted Linux VM outside WSL | Stronger explicit host/guest separation with no integration/shared folders | Greatest RAM/boot overhead among these options; must benchmark with Qwen running | More operational work and image maintenance; practical fallback if native isolation cannot pass verification |

Cost/latency comparisons are engineering estimates, **not measurements on this
laptop**. No reliable numeric RAM/latency budget is established yet. Compile and run
must both be contained; a sandboxed executable after host compilation is incomplete.

[Microsoft documents AppContainer resource isolation](https://learn.microsoft.com/en-us/windows/win32/secauthz/appcontainer-isolation).
[Microsoft explicitly states that WSL is not a sandbox for untrusted code](https://github.com/microsoft/WSL/blob/master/doc/docs/technical-documentation/security.md).
[Docker documents runtime/security requirements](https://docs.docker.com/engine/security/)
and [resource limits](https://docs.docker.com/engine/containers/resource_constraints/).
Docker Enhanced Container Isolation is a Business feature and is not part of this
cost-free plan; see [Windows permissions documentation](https://docs.docker.com/desktop/setup/install/windows-permission-requirements/).

## Recommended next milestone and blocker

Prototype native AppContainer/LPAC plus kernel Job limits first: it fits the existing
Windows compiler/judge and avoids another always-running VM alongside Qwen. This is
a **candidate to validate**, not a claim of adequate isolation or an authorization
to connect Run. Reject it if compiler access requires broad user-profile/project
permissions or if malicious tests escape the intended boundary. If it fails, prefer
a separately managed restricted VM rather than assuming ordinary WSL is safe.

Gate browser execution on actual evidence of:

1. Denied host secrets/project/database access and denied network/loopback access.
2. Contained compiler and runtime, including child processes, inherited handles,
   abnormal exits, output floods, excessive threads/processes, and filesystem writes.
3. OS-enforced memory/CPU/process limits with one submission at a time; cleanup
   succeeds after timeout, crash, and cancellation.
4. The existing deterministic judge and visible/hidden test evidence remain accurate.
   Run uses visible cases; Submit uses the available verified suite with limited AC wording.
5. Benchmarked cold/warm latency and total RAM while local Qwen is loaded, followed
   by an independent boundary review before enabling an endpoint.

Until then, Run/Submit stay disabled. The practical interim workflow is editor plus
curated lessons and official LeetCode practice; the local CLI can execute only code
you authored or independently reviewed and trust. Do not send untrusted imported
solutions to the host runner. Later fixture expansion must use repository-authored
references/oracles with explicit trust, or the verified isolated worker.

Stop after O1. O2 isolation work and later lessons/cards/drills/persistence were not
implemented in this increment.
