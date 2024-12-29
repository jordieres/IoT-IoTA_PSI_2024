"""
File Name: mqtt_sender.py
Author: Irene Pereda Serrano
Created On: 05/05/2024
Description: This file connects to the MQTT Broker defined in MQTT_BROKER and publishes data to
             the specified topic in TOPIC.
"""

import gc
import time

from mqtt.umqttsimple import MQTTClient
from wifi.connectWifi import connect_wifi

wifiSSID = "PeredaSerrano"
wifiPass = "torrejonWificasa"
mqttServer = b"apiict00.etsii.upm.es"
mqttPort = 1883
mqttClientID = b"ESP32-S3"
mqttUser = b"ipereda"
mqttPass = b"Madrid#141"
mqttTopicTemp = b"UPM/PrdMon/S001"

if connect_wifi(wifiSSID, wifiPass):
    client = MQTTClient(client_id=mqttClientID, server=mqttServer, port=mqttPort, user=mqttUser, password=mqttPass,
                        keepalive=7200, ssl=False)
    client.connect()

    while True:
        time.sleep(20)

        Temperatura = 27
        Humedad = 60

        client.publish(topic=mqttTopicTemp, msg=str(Temperatura))
        time.sleep(2)

        print("Data sent to MQTT Broker")

        gc.collect()

else:
    print("Impossible to connect")

"""
def send_data(data):
    # Connect to MQTT Broker and publish data
    client = MQTTClient("ESP32-S3", mqttServer)
    client.connect()
    client.publish(mqttTopicHum, data)
    client.disconnect()
    print("Data sent to MQTT Broker:", data)


def main():
    # Connect to the WiFi network
    connectWifi.connect_wifi()

    # Simulate temperature data
    temperature_data = "25.5"

    # Send data to MQTT Broker
    send_data(temperature_data)


"""
