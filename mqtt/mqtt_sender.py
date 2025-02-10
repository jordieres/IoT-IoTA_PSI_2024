"""
File Name: mqtt_sender.py
Author: Irene Pereda Serrano
Created On: 05/05/2024
Description: This file connects to the MQTT Broker defined in MQTT_BROKER and publishes data to
             the specified topic in TOPIC.
TODO:
- Fill in the WiFi credentials (wifiSSID, wifiPass)
- Provide the MQTT broker details (mqttServer, mqttUser, mqttPass, mqttTopicTemp)
"""

import gc
import time
from mqtt.umqttsimple import MQTTClient
from wifi.connectWifi import connect_wifi
import os
from dotenv import load_dotenv

load_dotenv()

WIFI_SSID = os.getenv("WIFI_SSID")
WIFI_PASSWORD = os.getenv("WIFI_PASSWORD")
mqttServer = os.getenv("MQTTSERVER")
mqttPort = os.getenv("MQTTPORT")
mqttClientID = os.getenv("MQTTCLIENTID").encode()
mqttUser = os.getenv("MQTTUSER").encode()
mqttPass = os.getenv("MQTTPASS").encode()
mqttTopic = os.getenv("MQTTTOPIC").encode()

if connect_wifi(WIFI_SSID, WIFI_PASSWORD):
    client = MQTTClient(client_id=mqttClientID, server=mqttServer, port=mqttPort, user=mqttUser, password=mqttPass,
                        keepalive=7200, ssl=False)
    client.connect()

    while True:
        time.sleep(20)

        Temperatura = 27
        Humedad = 60

        client.publish(topic=mqttTopic, msg=str(Temperatura))
        time.sleep(2)

        print("Data sent to MQTT Broker")

        gc.collect()

else:
    print("Impossible to connect")
