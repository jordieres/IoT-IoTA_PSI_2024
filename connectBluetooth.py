from machine import Pin
import bluetooth
from BLE import BLEUART

led = Pin(35, Pin.OUT)

# Init Bluetooth
name = 'ESP32-S3'
ble = bluetooth.BLE()
uart = BLEUART(ble, name)


# Bluetooth RX event
def on_rx():
    rx_buffer = uart.read().decode().strip()
    uart.write('ESP32 says: ' + str(rx_buffer) + '\n')
    if rx_buffer == 'L':
        led.on()


# Register Bluetooth event
uart.irq(handler=on_rx())
