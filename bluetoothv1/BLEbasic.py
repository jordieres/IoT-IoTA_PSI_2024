"""
File Name: BLEbasic.py
Author: Irene Pereda Serrano
Created On: 05/04/2024
Description: Bluetooth connection with a device and reading messages sent via UART.
             Example of turning the LED on/off via Bluetooth.
"""

from machine import Pin
import bluetooth
from bluetoothv1.BLE import BLEUART

name = "ESP32-s3"

ble = bluetooth.BLE()
uart = BLEUART(ble, name)
print(name, " Bluetooth del dispositivo activado")

led = Pin(35, Pin.OUT)


def on_rx():
    rx_recibe = uart.read().decode().strip()
    uart.write("ESP32-s3 dice: " + str(rx_recibe) + "\n")
    print(rx_recibe)

    if rx_recibe == "ON":
        led.value(1)
    if rx_recibe == "OFF":
        led.value(0)


def send_message(message):
    uart.write(message + "\n")


uart.irq(handler=on_rx)
