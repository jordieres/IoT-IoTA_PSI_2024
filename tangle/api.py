import urequests as requests
import urandom
import ujson as json
from wifi.connectWifi import connect_wifi


def get_node_info(base_url):
    """
    Obtiene la información del nodo IOTA.

    Args:
        base_url (str): URL base del nodo

    Returns:
        dict: Información del nodo en formato JSON, o None si hubo un error.
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
    Verifica el estado de salud del nodo IOTA.

    Args:
        base_url (str): URL base del nodo.

    Returns:
        bool: True si el nodo está saludable, False en caso contrario.
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
    Obtiene las rutas disponibles en la API del nodo.

    Args:
        base_url (str): URL base del nodo.

    Returns:
        list: Lista de rutas disponibles en la API.
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
    Obtiene tips válidos del nodo.

    :param api_url: La URL de la API del nodo Hornet.
    :return: Una lista de tips (IDs de bloques) o None si falla.
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
    Genera datos aleatorios de temperatura y humedad en formato JSON.

    :return: Una cadena JSON con los datos generados.
    """
    temperature = round((urandom.getrandbits(8) % 15) + 15, 2)  # Rango 15.0 a 30.0
    humidity = round((urandom.getrandbits(8) % 60) + 30, 2)  # Rango 30.0 a 90.0
    data = {"temperature": temperature, "humidity": humidity}
    return json.dumps(data)


def submit_block_with_tagged_data(api_url, tag, data):
    """
    Envía un bloque al Tangle con un TaggedDataPayload.

    :param api_url: La URL de la API del nodo Hornet.
    :param tag: Etiqueta para los datos en formato hexadecimal.
    :param data: Datos en formato de cadena que se codificarán en hexadecimal.
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


# URL de la API del nodo
API_URL = "https://iota.etsii.upm.es/api/core/v2"

# Etiqueta para los datos
TAG = "TemperatureHumidity"

# Generar datos aleatorios de temperatura y humedad
DATA = generate_random_data()

# Configuración de red Wi-Fi
WIFI_SSID = "PeredaSerrano"
WIFI_PASSWORD = "torrejonWificasa"

if connect_wifi(WIFI_SSID, WIFI_PASSWORD):
    DATA = generate_random_data()
    print(f"Datos generados: {DATA}")
    submit_block_with_tagged_data(API_URL, TAG, DATA)
else:
    print("Imposible conectar al Wi-Fi.")
