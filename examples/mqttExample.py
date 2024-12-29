"""
File Name: mqttExample.py
Author: Irene Pereda Serrano
Created On: 12/06/2024
Description: This file is an example on how to send messages using the MQTT protocol
"""

import gc
import time
from mqtt.umqttsimple import MQTTClient
from wifi.connectWifi import connect_wifi

wifiSSID = "PeredaSerrano"
wifiPass = "torrejonWificasa"
mqttServer = '138.100.82.170'  # b"apiict00.etsii.upm.es"
mqttPort = 1883
mqttClientID = b"ESP32-S3"
mqttUser = b"ipereda"
mqttPass = b"Madrid#141"
mqttTopic = b"UPM/PrdMon/S001"

if connect_wifi(wifiSSID, wifiPass):
    client = MQTTClient(client_id=mqttClientID, server=mqttServer, port=mqttPort, user=mqttUser, password=mqttPass,
                        keepalive=7200, ssl=False)
    client.connect()

    temperatura = 1

    while True:
        time.sleep(20)

        client.publish(topic=mqttTopic, msg=str(temperatura))
        temperatura += 1
        time.sleep(2)

        print(f"Data sent to MQTT Broker: {temperatura - 1}")

        gc.collect()

else:
    print("Imposible conectar")
