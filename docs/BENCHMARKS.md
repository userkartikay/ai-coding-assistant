> Historical measurements, corrected after independent audit (2026-10-12).
> The 1964 ms value measured a thinking chunk, not usable guidance. Chunk counts
> were labeled as tokens. The standard run produced no final answer; the allegedly
> suppressed run still had 4096 thinking characters. These results do not establish
> current latency, model accuracy, or a two-second user-visible answer target.
> Production now uses schema-constrained, thinking-disabled generation; remeasure
> that configuration before setting UI performance acceptance criteria.

# Empirical Benchmark Report: Qwen 3.5 4B & Hardware Telemetry

**Updated**: 2026-10-12\
**Hardware Environment**:
- **GPU**: NVIDIA GeForce RTX 2050 Laptop (4096 MiB dedicated VRAM, 6144 MiB total shared memory)
- **CPU**: AMD Ryzen 5 5500H (6 cores, 12 threads)
- **RAM**: 16 GB DDR4
- **OS**: Windows 11
- **LLM Engine**: Ollama 0.34.0 running `qwen3.5:4b` (3.7 GB in-memory footprint)

---

## 1. Hardware VRAM Allocation & Model Placement

Empirical verification via `ollama ps` and `nvidia-smi` reveals:
- **Dedicated VRAM Limit**: 4096 MiB (4.0 GB)
- **VRAM Allocated to Ollama**: **2455 MiB** (~2.45 GB)
- **Model Layer Distribution**: **50% CPU / 50% GPU** offloading
  - Due to Windows OS/DWM baseline consumption (~1.5 GB VRAM) and Ollama's KV cache allocation, 50% of model layers run on the RTX 2050 GPU, and 50% run on the Ryzen 5 CPU across PCIe.
  - This cross-bus computation produces an empirical generation rate of **~7.0 to 8.4 tokens/second**.

---

## 2. Streaming Performance & Time To First Token (TTFT)

Measured using `scripts/benchmark_thinking_ttft.py` via Server-Sent Events / streaming HTTP connection:

| Configuration | Time To First Token (TTFT) | Total Generated Tokens | Total Generation Time | Effective Speed |
| :--- | :---: | :---: | :---: | :---: |
| **Standard (Auto Thinking)** | **2522.6 ms** (~2.5s) | 1,669 tokens | 238.0 s | 7.09 tokens/s |
| **Optimized Concise (Suppressed Thinking)** | **1964.2 ms** (~1.9s) | 950 tokens | 139.3 s | 6.92 tokens/s |

### Critical Takeaway for Architecture:
- Historical first chunks arrived within about two seconds; usable-answer latency was not established.
- The model spends considerable tokens on internal thinking if unconstrained. Prompting with explicit brevity constraints reduces total token generation by **43%**, reducing generated chunks; pedagogical accuracy was not independently measured.

---

## 3. End-to-End Latency by Educational Tier (Non-Streaming Batched)

| Test Case | Prompt Tokens | Output Tokens | Total Time (ms) | Speed (tokens/s) | GPU VRAM (MB) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Level 1 (Nudge)** | 519 | 126 | 17,500.6 | 7.8 | 2455.0 |
| **Level 2 (Pattern & Subpattern)** | 536 | 207 | 31,482.4 | 6.9 | 2455.0 |
| **Level 3 (Algorithmic Direction)** | 492 | 157 | 20,954.1 | 7.9 | 2455.0 |
| **Level 4 (Pseudocode)** | 453 | 239 | 28,917.7 | 8.4 | 2455.0 |
| **Level 5 (Solution & Complexity)** | 488 | 689 | 91,419.4 | 7.6 | 2455.0 |
| **Mistake Diagnosis** | 740 | 104 | 15,134.2 | 7.8 | 2455.0 |

---

## 4. Engineering Trade-offs & Recommendations

1. **Context Window Sizing**:
   - Setting `num_ctx: 2048` in Ollama options saves KV cache memory, reducing KV cache size; this does not establish zero paging or current model placement.
2. **Pedagogical Token Economy**:
   - Level 1 and Mistake Diagnosis prompts should enforce tight length bounds (max 2–3 sentences of guidance + 1 question). This keeps total completion tokens ~100, finishing in 12–15 seconds while delivering crisp educational guidance.
3. **UI Streaming Mandate**:
   - Future UI endpoints must measure first usable guidance separately from first activity; the historical 1.9s value is not a usable-answer guarantee.
