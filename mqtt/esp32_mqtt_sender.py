"""
File Name: esp32_mqtt_sender.py
Author: Irene Pereda Serrano
Created On: 05/05/2024
Description: This file connects to the MQTT Broker defined in MQTT_BROKER and publishes data to
             the specified topic in TOPIC.
"""

from umqttsimple import MQTTClient
from wifi import connectWifi

# MQTT Broker configuration
MQTT_BROKER = "apiict00.etsii.upm.es"  # MQTT Broker address
TOPIC = "sensores/temperatura"  # Topic to publish the data


def send_data(data):
    # Connect to MQTT Broker and publish data
    client = MQTTClient("ESP32-S3", MQTT_BROKER)
    client.connect()
    client.publish(TOPIC, data)
    client.disconnect()
    print("Data sent to MQTT Broker:", data)


def main():
    # Connect to the WiFi network
    connectWifi.connect_wifi()

    # Simulate temperature data (replace this part with reading from the sensor)
    temperature_data = "25.5"

    # Send data to MQTT Broker
    send_data(temperature_data)


if __name__ == "__main__":
    main()
