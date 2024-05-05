"""
File Name: connectWifi.py
Author: Irene Pereda Serrano
Created On: 04/04/2024
Description: Connecting to the home Wi-Fi network
"""

import network
import time


def connect_wifi():
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
