"""
File Name: blinking.py
Author: Irene Pereda Serrano
Created On: 20/03/2024
Description: Implementation of functions to control the LED integrated on the board
"""

import time
import machine


def blink(duration, qty, npin):
    """This function flashes an LED.
     nPin: Indicates which pin the LED is connected to
     duration: Controls the time in which the LED turns on and off
     qty: Indicates the maximum number of times the LED will flash"""

    led = machine.Pin(npin, machine.Pin.OUT)

    # Cycle to control flashing

    for x in range(qty):
        led.on()
        time.sleep_ms(duration)
        led.off()
        time.sleep_ms(duration)

    return 'Done!'
