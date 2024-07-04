"""
File Name: connectWifi.py
Author: Irene Pereda Serrano
Created On: 04/04/2024
Description: Connecting to the home Wi-Fi network
"""

import network
import time


def connect_wifi(net, password):
    wlan = network.WLAN(network.STA_IF)  # create station interface
    if not wlan.isconnected():
        wlan.active(True)
        wlan.connect(net, password)  # connect to an AP
        print('Connecting to the network', net + "...")
        timeout = time.time()
        while not wlan.isconnected():
            if time.ticks_diff(time.time(), timeout) > 10:
                wlan.active(False)
                return False
    print("Succesful connection!")
    print('Network data (IP/netmask/gw/DNS):', wlan.ifconfig())
    return True
