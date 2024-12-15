"""
File Name: oledSetup.py
Author: Irene Pereda Serrano
Created On: 04/04/2024
Description: This file initializes and sets up the SSD1306 OLED display module on the Heltec LoRa 32 board
"""

import time
from oled import ssd1306
from machine import Pin, SoftI2C


# Heltec LoRa 32 with OLED Display
oled_width = 128
oled_height = 64

# Vext ON
vextPin = Pin(36, Pin.OUT)
vextPin.value(0)

# OLED reset pin
i2c_rst = Pin(21, Pin.OUT)

# Initialize the OLED display
i2c_rst.value(0)
time.sleep_ms(5)
i2c_rst.value(1)  # must be held high after initialization

# Set up the I2C lines
i2c_scl = Pin(18, Pin.OUT, Pin.PULL_UP)
i2c_sda = Pin(17, Pin.OUT, Pin.PULL_UP)

# Create the bus object
i2c = SoftI2C(scl=i2c_scl, sda=i2c_sda)

# Create the display object
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c, addr=0x3c)
oled.fill(1)
oled.show()
oled.contrast(0xFF)
