"""
File Name: displayWifi.py
Author: Irene Pereda Serrano
Created On: 17/04/2024
Description: This file is an example about how to print WiFi information on the OLED screen
"""

from oled import oledSetup
from wifi import connectWifi

oled = oledSetup.oled

if connectWifi.connect_wifi("PeredaSerrano", "TorrejonWifiCasa"):
    oled.fill(0)
    oled.text('CONECTADO A IP:', 0, 0)
    oled.text('HELLO WiFi ESP32', 0, 55)
    oled.show()
