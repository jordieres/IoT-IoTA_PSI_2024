"""
File Name: iota_sender.py
Author: Irene Pereda Serrano
Created On: 04/07/2024
Description: This file connects to the IOTa Node.
"""

import urequests
import json
import time
from wifi.connectWifi import connect_wifi

wifiSSID = "PeredaSerrano"
wifiPass = "torrejonWificasa"


# Función para enviar datos al nodo Hornet
def send_data_to_hornet(sensor_data):
    url = "https://iota.etsii.upm.es/api/v1/messages"
    headers = {
        'Content-Type': 'application/json',
    }
    payload = {
        "payload": {
            "type": 2,
            "index": "datos_sensor",
            "data": json.dumps(sensor_data)
        }
    }
    response = urequests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 202:
        print("Datos enviados con éxito:", response.json())
    else:
        print("Error al enviar datos:", response.status_code, response.text)


def main():
    if connect_wifi(wifiSSID, wifiPass):
        while True:
            sensor_data = "Hola, esto es una prueba"
            send_data_to_hornet(sensor_data)
            time.sleep(60)
    else:
        print("No se pudo conectar a la red WiFi")
