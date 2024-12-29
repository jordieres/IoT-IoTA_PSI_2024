"""
File Name: api.py
Author: Irene Pereda Serrano
Created On: 28/12/2024
Description: This file contains functions to interact with the IOTA Tangle via a Hornet node API.
             It includes functionalities to retrieve node information, check node health, get API
             routes, fetch tips, and submit blocks with tagged data. Additionally, it generates
             random temperature and humidity data for testing purposes and connects to Wi-Fi
             for network access.
"""

import urequests as requests
import urandom
import ujson as json
from wifi.connectWifi import connect_wifi


def get_node_info(base_url):
    """
    Gets the IOTA node information

    Args:
        base_url (str): base URL of the node

    Returns:
        dict: Node information in JSON format, or None if there was an error
    """
    url = f"{base_url}/api/core/v2/info"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print("Información del nodo obtenida con éxito:")
            return response.json()
        else:
            print(f"Error al obtener información del nodo: {response.status_code}, {response.text}")
            return None
    except Exception as e:
        print(f"Error al conectar con el nodo: {e}")
        return None


def get_health(base_url):
    """
    Checks the health status of the IOTA node.

    Args:
        base_url (str): base URL of the node

    Returns:
        bool: True if the node is healthy, False otherwise
    """
    url = f"{base_url}/health"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print("El nodo está saludable.")
            return True
        else:
            print(f"El nodo no está saludable. Estado: {response.status_code}")
            return False
    except Exception as e:
        print(f"Error al conectar con el nodo: {e}")
        return False


def get_api_routes(base_url):
    """
    Gets the routes available in the node API

    Args:
        base_url (str): base URL of the node

    Returns:
        list: List of routes available in the API
    """
    url = f"{base_url}/api/routes"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print("Rutas disponibles obtenidas con éxito:")
            return response.json()
        else:
            print(f"Error al obtener rutas: {response.status_code}, {response.text}")
            return None
    except Exception as e:
        print(f"Error al conectar con el nodo: {e}")
        return None


def get_tips(api_url):
    """
    Get valid tips from the node

    :param api_url: The URL of the Hornet node API
    :return: A list of tips (block IDs) or None if this fails
    """
    try:
        response = requests.get(f"{api_url}/tips")
        if response.status_code == 200:
            tips = response.json().get("tips")
            return tips
        else:
            print(f"Error al obtener tips: {response.status_code}, {response.text}")
            return None
    except Exception as e:
        print(f"Error al conectar con el nodo: {e}")
        return None


def generate_random_data():
    """
    Generates random temperature and humidity data in JSON format

    :return: A JSON string containing the generated data
    """
    temperature = round((urandom.getrandbits(8) % 15) + 15, 2)
    humidity = round((urandom.getrandbits(8) % 60) + 30, 2)
    data = {"temperature": temperature, "humidity": humidity}
    return json.dumps(data)


def submit_block_with_tagged_data(api_url, tag, data):
    """
    Sends a block to the Tangle with a TaggedDataPayload

    :param api_url: The API URL for the Hornet node
    :param tag: Label for data in hexadecimal format
    :param data: Data in string format to be encoded in hexadecimal
    """
    hex_tag = "0x" + tag.encode().hex()
    hex_data = "0x" + data.encode().hex()

    parents = get_tips(api_url)
    if not parents:
        print("No se pudieron obtener tips válidos para el bloque.")
        return

    block_payload = {
        "protocolVersion": 2,
        "parents": parents,
        "payload": {
            "type": 5,
            "tag": hex_tag,
            "data": hex_data
        }
    }

    try:
        response = requests.post(
            f"{api_url}/blocks",
            json=block_payload,
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 201:
            block_id = response.json().get("blockId")
            print(f"Bloque registrado con éxito. ID del bloque: {block_id}")
        else:
            print(f"Error al registrar bloque: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"Error al conectar con el nodo: {e}")


API_URL = "https://iota.etsii.upm.es/api/core/v2"

TAG = "TemperatureHumidity"

DATA = generate_random_data()

WIFI_SSID = "PeredaSerrano"
WIFI_PASSWORD = "torrejonWificasa"

if connect_wifi(WIFI_SSID, WIFI_PASSWORD):
    DATA = generate_random_data()
    print(f"Datos generados: {DATA}")
    submit_block_with_tagged_data(API_URL, TAG, DATA)
else:
    print("Imposible conectar al Wi-Fi.")
