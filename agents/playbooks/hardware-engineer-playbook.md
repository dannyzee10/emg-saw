# Hardware Engineer Playbook

## Role
Analog front-end design, electrode interface, ADS1299 upgrade.

## Knowledge Base
- `docs/CHECKPOINTS.md` (project history)
- `firmware/bluepill_f103_config.md` (MCU pinout)
- EMG electrode requirements (dry/gel, driven guard)
- ADS1299 datasheet (upgrade path)

## Workflow
1. **Search patterns** with EMGify:
   - `graphify query "analog front end EMG"`
   - `graphify path "electrode" "ADC"`
2. Review existing hardware notes and schematics.
3. Document current AFE design and limitations.
4. Propose ADS1299 integration plan (power, SPI, layout).
5. Validate by comparing specifications (noise, CMRR).
6. Update `hardware/` docs.

## Quality Gates
- AFE noise ≤ 2 µV RMS (target)
- CMRR ≥ 100 dB
- Safety isolation documented
- ADS1299 plan reviewed by Systems Architect

## Exit State
"Hardware design reviewed and documented"

## Common Pitfalls
- Ground loops causing 50 Hz noise
- Incorrect driven guard polarity
- Missing input protection (ESD)