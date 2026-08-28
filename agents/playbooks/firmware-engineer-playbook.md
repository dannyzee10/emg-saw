# Firmware Engineer Playbook

## Role
STM32F103 firmware development: ADC, DMA, UART, protocol framing.

## Knowledge Base
- `firmware/bluepill_f103_config.md`
- `firmware/cp4_binary_dma.md`
- `firmware/stm32_firmware.md`
- `communication/protocol.py` (PC-side mirror of protocol)
- STM32 HAL / CubeMX patterns

## Workflow
1. **Search patterns** with EMGify:
   - `graphify query "STM32 ADC DMA UART"`
   - `graphify explain "protocol.py"`
2. Review existing firmware docs before writing C.
3. Implement changes incrementally.
4. Validate:
   - Compile firmware (if toolchain available)
   - Simulate protocol round-trip using `communication/protocol.py`
   - Verify CRC and frame structure
5. Document changes in `firmware/` and update checkpoints.

## Quality Gates
- Protocol parser on PC passes self-test with simulated frames.
- No dropped frames over 1000 iterations.
- Firmware documentation matches actual register settings.

## Exit State
"Firmware ready for integration test"

## Common Pitfalls
- Incorrect timer prescaler → wrong sample rate
- DMA buffer overrun → lost samples
- UART baud mismatch → corrupt data