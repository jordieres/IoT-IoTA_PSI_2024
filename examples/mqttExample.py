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

    temperatura = 1

    while True:
        time.sleep(20)

        client.publish(topic=mqttTopic, msg=str(temperatura))
        temperatura += 1
        time.sleep(2)

        print(f"Data sent to MQTT Broker: {temperatura - 1}")

        gc.collect()

else:
    print("Unable to connect")
