"""
File Name: format.py
Original Autor: Rafael Römhild
Acquisition Date: 15/04/2024
Original Source: https://github.com/rroemhild/micropython-ruuvitag/tree/main
Description: This file defines named tuples for storing data from RuuviTag
             sensors in two different formats, RAWv1 and RAWv2. These named
             tuples provide a structured way to store and access sensor data in Python applications.
"""


from ucollections import namedtuple

RuuviTagRAWv1 = namedtuple(
    "RuuviTagRAWv1",
    (
        "mac",
        "rssi",
        "format",
        "humidity",
        "temperature",
        "pressure",
        "acceleration_x",
        "acceleration_y",
        "acceleration_z",
        "battery_voltage",
    ),
)

RuuviTagRAWv2 = namedtuple(
    "RuuviTagRAWv2",
    (
        "mac",
        "rssi",
        "format",
        "humidity",
        "temperature",
        "pressure",
        "acceleration_x",
        "acceleration_y",
        "acceleration_z",
        "battery_voltage",
        "power_info",
        "movement_counter",
        "measurement_sequence",
    ),
)
