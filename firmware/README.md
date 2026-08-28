# EMG Firmware

## Status
Skeleton only. Not yet complete.

## Build Tools
- STM32CubeMX + Keil/IAR/SW4STM32
  or
- PlatformIO (with stm32duino or HAL)

## Configuration
- MCU: STM32F103C8T6 (Blue Pill)
- Clock: 72 MHz (from 8 MHz HSE via PLL)
- ADC: ADC1, 12-bit, 8 channels, DMA circular
- Timer: TIM2, update event @ 2 kHz (period = 72MHz/(2kHz) = 36000, PSC = 0)
- UART: USART1, 921600 baud

## Protocol
- Version: 2
- Frame: 0xAA 0x56 | seq(2) | data(8*2) | crc(2)
- CRC: CRC-16/CCITT-FALSE (poly 0x1021, init 0xFFFF) over seq+data

## TODO
- [ ] Complete HAL initialization code
- [ ] Verify DMA circular buffer size and interrupt priorities
- [ ] Test with PC-side round-trip test
- [ ] Implement hardware flow control if needed