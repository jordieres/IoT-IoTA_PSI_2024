"""
Nombre del archivo: connectWifi.py
Autor: Irene Pereda Serrano
Fecha de creación: 04/04/2024
Descripción: Conexión a la red wifi del hogar
"""

import network
import time

wlan = network.WLAN(network.STA_IF)  # create station interface
wlan.active(True)  # activate the interface
wlan.isconnected()  # check if the station is connected to an AP
time.sleep_ms(500)
if not wlan.isconnected():
    print('connecting to network...')
    wlan.connect('PeredaSerrano', 'torrejonWificasa')  # connect to an AP
    time.sleep_ms(500)
    while not wlan.isconnected():
        pass
print('network config:', wlan.ifconfig())
