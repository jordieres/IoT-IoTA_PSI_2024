"""
File Name: gps.py
Original Autor: Rui Santos & Sara Santos - Random Nerd Tutorials
Acquisition Date: 15/12/2024
Original Source: https://randomnerdtutorials.com/micropython-esp32-neo-6m-gps/
Description: Script to read and process GPS data from a Neo-6M module using MicropyGPS on an ESP32.
             Parses NMEA sentences and displays relevant information like location, time, and altitude.
"""

import machine
import time
from machine import Pin
import heltec
from gps.micropyGPS import MicropyGPS


class GPSHandler:
    def __init__(self, tx_pin, rx_pin, uart_num=2, baudrate=9600, local_offset=1):
        """Initializes GPS object and UART communication"""
        self.uart = machine.UART(uart_num, baudrate=baudrate, tx=Pin(tx_pin), rx=Pin(rx_pin))
        self.gps = MicropyGPS(local_offset=local_offset)

    def read_gps_data(self):
        """Read GPS data from UART and update GPS object"""
        while self.uart.any():
            data = self.uart.read()
            for byte in data:
                self.gps.update(chr(byte))

    def get_gps_info(self):
        """Returns a dictionary with the processed GPS information"""
        if self.gps.valid:
            return {
                'timestamp': self.gps.timestamp,
                'date': self.gps.date_string('long'),
                'latitude': self.gps.latitude_string(),
                'longitude': self.gps.longitude_string(),
                'altitude': self.gps.altitude,
                'satellites_in_use': self.gps.satellites_in_use,
                'hdop': self.gps.hdop,
            }
        else:
            print("GPS data invalid. No fix available.")
            return None

    def print_gps_info(self):
        """Prints the processed GPS information"""
        gps_info = self.get_gps_info()
        if gps_info:
            print('UTC Timestamp:', gps_info['timestamp'])
            print('Date:', gps_info['date'])
            print('Latitude:', gps_info['latitude'])
            print('Longitude:', gps_info['longitude'])
            print('Altitude:', gps_info['altitude'])
            print('Satellites in use:', gps_info['satellites_in_use'])
            print('Horizontal Dilution of Precision:', gps_info['hdop'])
            print()
        else:
            print("Waiting for valid GPS data...")


def run_gps_handler():
    """Main function to manage GPS"""
    # Set the offset manually (1 for UTC+1, 2 for UTC+2, etc.)
    print("Initializing GPS Handler...")
    local_offset = 1
    gps_handler = GPSHandler(tx_pin=heltec.TX, rx_pin=heltec.RX, local_offset=local_offset)

    while True:
        try:
            gps_handler.read_gps_data()
            gps_handler.print_gps_info()
            time.sleep(3)
        except Exception as e:
            print(f"An error occurred: {e}")


def initialize_gps():
    return GPSHandler(tx_pin=heltec.TX, rx_pin=heltec.RX, local_offset=1)
