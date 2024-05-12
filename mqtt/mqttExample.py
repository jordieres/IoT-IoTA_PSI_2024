# Envia temperatura y humedad a Hive MQ usando MQTT
# Usa el broker publico

from mqtt.umqttsimple import MQTTClient

import network, time, gc


def conectaWifi(red, password):
    global miRed
    miRed = network.WLAN(network.STA_IF)
    if not miRed.isconnected():  # Si no está conectado…
        miRed.active(True)  # activa la interface
        miRed.connect(red, password)  # Intenta conectar con la red
        print('Conectando a la red', red + "…")
        timeout = time.time()
        while not miRed.isconnected():  # Mientras no se conecte..
            if (time.ticks_diff(time.time(), timeout) > 10):
                return False
    return True


# Parametros
wifiSSID = "PeredaSerrano"
wifiPass = "torrejonWificasa"
mqttServer = b"broker.hivemq.com"
mqttPort = 1883
mqttClientID = b"ESP32-S3"
mqttUser = b""
mqttPass = b""
mqttTopicTemp = b"test/Temperatura"
mqttTopicHum = b"test/Humedad"

if conectaWifi(wifiSSID, wifiPass):

    print("Conexión exitosa!")
    print('Datos de la red (IP/netmask/gw/DNS):', miRed.ifconfig())

    cliente = MQTTClient(client_id=mqttClientID, server=mqttServer, port=mqttPort, user=mqttUser, password=mqttPass,
                         keepalive=7200, ssl=False)

    cliente.connect()

    while (True):
        time.sleep(20)

        # Datos constantes de prueba
        Temperatura = 27
        Humedad = 60

        # Publicar los datos
        cliente.publish(topic=mqttTopicTemp, msg=str(Temperatura))
        time.sleep(2)
        cliente.publish(topic=mqttTopicHum, msg=str(Humedad))

        print("Datos enviados!")

        gc.collect()

else:
    print("Imposible conectar")
    miRed.active(False)