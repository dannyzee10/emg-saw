/*
 * EMG Acquisition Firmware Skeleton
 * STM32F103C8T6 (Blue Pill)
 *
 * Features:
 *   - TIM2 @ 2 kHz triggers ADC1 conversion
 *   - ADC1 (12-bit) scans 8 channels, DMA in circular mode
 *   - USART1 @ 921600 baud sends frames in Protocol v2 format
 *   - Frame: 0xAA 0x56 | uint16 seq | 8 x int16 ADC | uint16 CRC
 *
 * This skeleton is intended as a starting point.
 * TODO: Complete HAL initialization and DMA callbacks.
 */

#include "stm32f1xx_hal.h"
#include <string.h>

// Peripheral handles
TIM_HandleTypeDef htim2;
ADC_HandleTypeDef hadc1;
DMA_HandleTypeDef hdma_adc1;
UART_HandleTypeDef huart1;

// Data buffer for 8 channels (uint16_t raw ADC values)
#define NUM_CHANNELS 8
volatile uint16_t adc_buffer[NUM_CHANNELS];

// Sequence number (16-bit)
volatile uint16_t frame_seq = 0;

// CRC-16/CCITT-FALSE (poly 0x1021, init 0xFFFF)
uint16_t crc16_ccitt(uint8_t *data, uint16_t len) {
    uint16_t crc = 0xFFFF;
    for (uint16_t i = 0; i < len; i++) {
        crc ^= (uint16_t)data[i] << 8;
        for (uint8_t j = 0; j < 8; j++) {
            if (crc & 0x8000)
                crc = (crc << 1) ^ 0x1021;
            else
                crc <<= 1;
        }
    }
    return crc & 0xFFFF;
}

// Build and send a Protocol v2 frame over UART
void send_frame(uint16_t *samples, uint8_t count) {
    uint8_t frame[2 + 2 + count*2 + 2]; // sync(2) + seq(2) + data(count*2) + crc(2)
    uint16_t idx = 0;

    // Sync word
    frame[idx++] = 0xAA;
    frame[idx++] = 0x56;  // v2 marker

    // Sequence (little-endian)
    frame[idx++] = frame_seq & 0xFF;
    frame[idx++] = (frame_seq >> 8) & 0xFF;
    frame_seq++;

    // Channel data (little-endian int16)
    for (uint8_t i = 0; i < count; i++) {
        frame[idx++] = samples[i] & 0xFF;
        frame[idx++] = (samples[i] >> 8) & 0xFF;
    }

    // CRC over body (seq + data), not including sync
    uint16_t crc = crc16_ccitt(&frame[2], 2 + count*2);
    frame[idx++] = crc & 0xFF;
    frame[idx++] = (crc >> 8) & 0xFF;

    HAL_UART_Transmit(&huart1, frame, idx, 100);
}

// ADC DMA callback (called when full buffer is transferred)
void HAL_ADC_ConvCpltCallback(ADC_HandleTypeDef* hadc) {
    if (hadc->Instance == ADC1) {
        // Send a frame with current buffer
        send_frame((uint16_t*)adc_buffer, NUM_CHANNELS);
    }
}

int main(void) {
    HAL_Init();

    // TODO: Configure system clock (e.g., HSE 8MHz -> PLL 72MHz)
    // TODO: Initialize TIM2, ADC1, DMA, USART1
    // TODO: Start ADC in DMA mode and start TIM2

    while (1) {
        // Main loop: currently idle; frame transmission occurs in DMA callback
    }
}