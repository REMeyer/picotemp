////////////////////////////////////////////////////////////////////////////////
// Simple pi pico-based temperature station.
// 
// author: R Elliot Meyer
// date: 2022
//
////////////////////////////////////////////////////////////////////////////////

#include <stdio.h>
#include <string.h>
#include "pico/stdlib.h"
#include "hardware/i2c.h"

// Defining the i2c parameters for the SHT40 Sensor
static int addr = 0x44;
#define I2C_PORT i2c1

// Base communication functions adapted from pico example scripts.
static void sht40_reset() {
    // Two byte reset. First byte register, second byte data
    uint8_t buf = 0x06;
    i2c_write_blocking(I2C_PORT, 0x00, &buf, 1, false);
}

static void sht40_read_raw(int16_t *t_ticks, int16_t *rh_ticks) {

        uint8_t buffer[6];

        // Start reading registers from register 0xFD for 6 bytes
        // 0xFD address measures T & H with high precision
        uint8_t val = 0xFD;
        i2c_write_blocking(I2C_PORT, addr, &val, 1, true); // true to keep master control of bus
        sleep_ms(10);
        i2c_read_blocking(I2C_PORT, addr, buffer, 6, false);

        //printf("%u %u %u %u %u %u\n",buffer[0],
        //buffer[1],buffer[2],buffer[3],buffer[4],buffer[5]);

        *t_ticks = buffer[0]*256 + buffer[1];
        *rh_ticks = buffer[3]*256 + buffer[4];
}

int main() {
    stdio_init_all();

    printf("Reading raw data from registers...\n");

    i2c_init(I2C_PORT, 400 * 1000);
    gpio_set_function(14, GPIO_FUNC_I2C);
    gpio_set_function(15, GPIO_FUNC_I2C);
    gpio_pull_down(14);
    gpio_pull_down(15);

    // Initalize the multi-color LED
    const uint LED_PIN_B = 18;
    const uint LED_PIN_G = 19;
    const uint LED_PIN_R = 20;

    int LED = 1;
    if (LED) {
        gpio_init(LED_PIN_B);
        gpio_init(LED_PIN_G);
        gpio_init(LED_PIN_R);

        gpio_set_dir(LED_PIN_B, GPIO_OUT);
        gpio_set_dir(LED_PIN_G, GPIO_OUT);
        gpio_set_dir(LED_PIN_R, GPIO_OUT);

        gpio_put(LED_PIN_B, 0);
        gpio_put(LED_PIN_G, 0);
        gpio_put(LED_PIN_R, 0);
    }

    sht40_reset();

    uint16_t t_ticks, rh_ticks;
    double temp, humid;

    while (1) {

        sht40_read_raw(&t_ticks, &rh_ticks);

        //printf("%u %u\n", t_ticks, rh_ticks);

        temp = -45 + (175*t_ticks)/65535.0;
        humid = -6 + (125*rh_ticks)/65535.0;

        if (humid > 100) 
            humid = 100;
        else if (humid < 0)
            humid = 0;

        if (LED) {
            if (temp >= 20.0f && temp < 21.0f) {
                gpio_put(LED_PIN_B, 1);
                gpio_put(LED_PIN_G, 1);
                gpio_put(LED_PIN_R, 0);
            } else if (temp >= 21.0f && temp <= 22.0f) {
                gpio_put(LED_PIN_B, 0);
                gpio_put(LED_PIN_G, 1);
                gpio_put(LED_PIN_R, 0);
            } else if (temp > 22.0f && temp <= 23.0f) {
                gpio_put(LED_PIN_B, 0);
                gpio_put(LED_PIN_G, 1);
                gpio_put(LED_PIN_R, 1);
            } else if (temp > 23.0f) {
                gpio_put(LED_PIN_B, 0);
                gpio_put(LED_PIN_G, 0);
                gpio_put(LED_PIN_R, 1);
            } else {
                gpio_put(LED_PIN_B, 1);
                gpio_put(LED_PIN_G, 0);
                gpio_put(LED_PIN_R, 0);
            }
        }

        printf("%.2f\t%.2f\n", temp, humid);

        sleep_ms(30000);
    }

    return 0;
}
