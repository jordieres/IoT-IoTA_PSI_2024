"""
File Name: utils.py
Author: Irene Pereda Serrano
Created On: 29/12/2024
Description: Utility functions for packing sensor data and performing statistical analysis.
"""

from ustruct import pack

def pack_temp(temp):
    temp_conv = round(temp / 0.005)
    return pack("!h", temp_conv)


def pack_humid(hum):
    hum_conv = round(hum / 0.0025)
    return pack("!H", hum_conv)


def pack_pressure(pressure):
    pres_conv = round(pressure / 10.0)
    return pack("!H", pres_conv)


def pack_std(std):
    std_conv = round(std / 0.005)
    return pack("!H", std_conv)


def pack_latitude(latitude_str):
    coord, hemi = latitude_str.split("°")
    decimal_lat = float(coord.strip())
    if hemi.strip() == 'S':
        decimal_lat = -decimal_lat
    return pack("!i", int(decimal_lat * 10 ** 6))


def pack_longitude(longitude_str):
    coord, hemi = longitude_str.split("°")
    decimal_lon = float(coord.strip())
    if hemi.strip() == 'W':
        decimal_lon = -decimal_lon
    return pack("!i", int(decimal_lon * 10 ** 6))


def pack_altitude(altitude):
    return pack("!H", int(altitude))


def pack_satellites(satellites):
    return pack("!B", satellites)


def pack_hdop(hdop):
    hdop_scaled = int(hdop * 100)
    return pack("!B", hdop_scaled)


def mean(data):
    return sum(data) / len(data) if data else 0


def stdev(data):
    if len(data) <= 1:
        return 0
    avg = mean(data)
    variance = sum((x - avg) ** 2 for x in data) / len(data)
    return variance ** 0.5


def calculate_statistics(data):
    """Calculate max, min, mean, and standard deviation for a list of data."""
    if not data:
        return 0, 0, 0, 0
    return max(data), min(data), mean(data), stdev(data)