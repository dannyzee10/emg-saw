# Data Pipeline — 5-Channel Simultaneous EMG Streaming (feasibility + optimal design)

**Question:** can STM32U575 + ST67W611M1 stream all 5 EMG channels at once to the laptop emg-plotter,
and is there a better option? **Verdict: yes, it works well with large margin. Wi-Fi (TCP) is the
optimal transport for laptop streaming; the hardware combo is the right choice — keep it.**

## 1. The data rate is tiny
| Setting | Per-channel | 5 channels | vs ST67 capacity (~17 Mbps TCP) |
|---|---|---|---|
| 1 kS/s × 2 B (14-bit) | 2 kB/s | **10 kB/s = 80 kbit/s** | 0.5 % |
| 2 kS/s × 2 B | 4 kB/s | **20 kB/s = 160 kbit/s** | ~1 % |
EMG lives in 20–500 Hz, so **1–2 kS/s per channel is plenty** (Nyquist). The radio sits ~99 % idle.

## 2. "All 5 at the same time" is easy on the U575
One ADC in **scan mode** samples the 5 inputs back-to-back (~1 µs each) and **DMA** moves them to memory
with **zero CPU load**. The 5 channels are captured within a few µs of each other — negligible skew
against a 2 ms (500 Hz) EMG period. (True simultaneous via 2 ADCs is possible but not needed for EMG.)

## 3. What actually makes it "work well" (the 4 keys)
1. **Hardware-timer-triggered ADC** (e.g., TIM6 @ 2 kHz → ADC → DMA): sample spacing is *exact*, set by
   the timer — **no jitter at the source**, no missed samples, no CPU involvement.
2. **Batch samples into packets** (~10 ms = 20 samples/ch → 200 B payload, ~100 packets/s). Never one
   sample per packet. Efficient over Wi-Fi, low overhead.
3. **TCP transport** (reliable): no lost samples → clean recordings; the ST67's 17 Mbps easily absorbs
   retransmissions at our 0.16 Mbps load.
4. **Sample-counter timeline:** every packet carries a running sample index. The emg-plotter rebuilds the
   time axis from the counter, so **Wi-Fi latency/jitter never distorts the signal** — it only delays the
   display slightly. A small (~50–100 ms) receive buffer smooths the display.

Typical end-to-end latency ≈ 20–50 ms — fine for a live scope and for %MVC biofeedback (human reaction
~200 ms).

## 4. Better option? Wi-Fi vs BLE vs USB
| Transport | Fits 5-ch? | Latency | Power | Laptop side | Verdict |
|---|---|---|---|---|---|
| **Wi-Fi TCP (ST67)** | Yes, ×100 headroom | ~20–50 ms | higher (bursts) | simple TCP socket | **best for laptop streaming** |
| BLE (ST67 also) | 1 kS/s OK; 2 kS/s marginal | higher | lowest | needs BLE stack + dongle | power-saving option only |
| USB wired | Yes | lowest | n/a (wired) | serial/USB | keep as debug/fallback |
The ST67 does **both** Wi-Fi and BLE — so you can ship Wi-Fi now and add a low-power BLE mode later. No
reason to change the hardware; U575 + ST67 is ST's own reference combo and is over-spec for this job.

## 5. The one honest risk + the fix
ST67W611M1 is **2.4 GHz** Wi-Fi 6. In a congested lab (many APs/phones) 2.4 GHz can have latency spikes /
occasional packet loss. Fully mitigated by: **TCP** (no data lost) + the **receive buffer** (absorbs
jitter for display) + the **sample counter** (recording stays time-accurate regardless). For hard
low-latency needs, a UDP mode with sequence numbers is a drop-in alternative.

## 6. Recommended optimal config
- **2 kS/s/ch, 14-bit, one ADC scan + TIM-triggered + DMA double-buffer.**
- **Packet:** header {sample_index, n_ch=5, seq} + 20 samples/ch, every ~10 ms.
- **Transport:** TCP; board = client, laptop emg-plotter = server (or mDNS discovery).
- **emg-plotter:** add a TCP-source thread → same plotting pipeline it uses for serial today; rebuild time
  axis from sample_index; 50–100 ms jitter buffer.

## 7. This is exactly what the dev-board step (Step 3) proves
On NUCLEO-U575 + X-NUCLEO-67W61M1, *before* ordering the custom board: run 5-ch ADC@2 kHz+DMA → ST67 Wi-Fi
TCP → laptop, wire your working 1-ch analog into an ADC pin, and **measure** sustained rate, latency,
jitter, dropped packets. If the numbers are good (they will be), you order the custom board with proof.
