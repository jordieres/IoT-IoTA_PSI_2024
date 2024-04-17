"""
File Name: BLEbasic.py
Author: Irene Pereda Serrano
Created On: 05/04/2024
Description: Bluetooth connection with a device and reading messages sent via UART.
             Example of turning the LED on/off via Bluetooth.
"""

from machine import Pin
import bluetooth
from bluetooth.BLE import BLEUART

# Definición del nombre del dispositivo Bluetooth
name = "ESP32-s3"

# Inicialización del Bluetooth
ble = bluetooth.BLE()
uart = BLEUART(ble, name)
print(name, " Bluetooth del dispositivo activado")

led = Pin(35, Pin.OUT)


# Método de manejo de interrupciones de recepción
# Cuando se recibe un mensaje vía UART, esta función
# se activa. Lee el mensaje recibido, lo decodifica,
# lo imprime y luego verifica si el mensaje es "ON"
# o "OFF" para encender o apagar el LED, respectivamente
def on_rx():
    rx_recibe = uart.read().decode().strip()
    uart.write("ESP32-s3 dice: " + str(rx_recibe) + "\n")
    print(rx_recibe)

    # Cadena/comando que enciende el LED
    if rx_recibe == "ON":
        led.value(1)
    # Cadena/comando que apaga el LED
    if rx_recibe == "OFF":
        led.value(0)


# Método que envía mensajes vía UART
def send_message(message):
    uart.write(message + "\n")


# Asignación del manejador de interrupciones a la instancia UART
uart.irq(handler=on_rx)
