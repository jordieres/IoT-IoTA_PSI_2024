"""
Nombre del archivo: oledDisplay.py
Autor: Irene Pereda Serrano
Fecha de creación: 04/04/2024
Descripción: Ejemplo de conexión satisfactoria para imprimir información en la pantalla OLED
"""

import time
import ssd1306
from machine import Pin, SoftI2C

# Heltec LoRa 32 with OLED Display
oled_width = 128
oled_height = 64

# Vext ON
vextPin = Pin(36, Pin.OUT)
vextPin.value(1)

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

oled.fill(0)
oled.text('Hola!', 0, 0)
oled.text('Soy Irene', 0, 10)
oled.text('Display en OLED', 0, 20)
oled.text('CONSEGUIDO!!!', 0, 30)
oled.show()
