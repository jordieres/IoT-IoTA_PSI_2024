import time
from ruuvitag import core
from loraWan import lorawan
from ustruct import pack
from oled import oledSetup

# Inicializa el OLED
oled = oledSetup.oled

# Funciones para empaquetar los datos
def pack_temp(temp):
    """Temperatura en 0.005 grados como short con signo (16 bits)"""
    temp_conv = round(temp / 0.005)
    return pack("!h", temp_conv)


def pack_humid(hum):
    """Humedad en 0.0025% como unsigned short (16 bits)"""
    hum_conv = round(hum / 0.0025)
    return pack("!H", hum_conv)


def pack_pressure(pressure):
    """Empaqueta la presión en Pa como unsigned short (16 bits)"""
    pres_conv = round(pressure / 10.0)
    return pack("!H", pres_conv)



def main(scan_interval, send_interval):
    # Inicializa el sensor RuuviTag
    ruuvi = core.RuuviTag()

    def display_message(lines, delay=2):
        """Muestra líneas de texto en el OLED durante un tiempo definido."""
        oled.fill(0)  # Limpia la pantalla
        for i, line in enumerate(lines):
            oled.text(line, 0, i * 10)  # Imprime cada línea con un espaciado de 10px
        oled.show()
        time.sleep(delay)  # Pausa para mostrar el mensaje

    def countdown(wait_time):
        """Muestra una cuenta atrás en el OLED."""
        for remaining in range(wait_time, 0, -1):
            oled.fill(0)
            oled.text("Esperando:", 0, 0)
            oled.text(f"{remaining // 60:02}:{remaining % 60:02}", 0, 10)
            oled.show()
            time.sleep(1)

    def callback_handler(data):
        # Verifica y procesa los datos del sensor
        if data:
            display_message([
                "Datos recibidos:",
                f"MAC: {data.mac}",
                f"Temp: {data.temperature} C",
                f"Humedad: {data.humidity}%",
                f"Presion: {data.pressure} hPa",
            ], delay=3)  # Muestra el mensaje durante 3 segundos
            print("Datos recibidos del sensor Ruuvi:")
            print("MAC:", data.mac)
            print("Temperatura:", data.temperature, "°C")
            print("Humedad:", data.humidity, "%")
            print("Presión:", data.pressure, "hPa")
            print("Voltaje de la batería:", data.battery_voltage, "mV")

            # Empaqueta los datos relevantes en un payload optimizado
            payload = (
                    pack_temp(data.temperature) +
                    pack_humid(data.humidity) +
                    pack_pressure(data.pressure) +
                    pack("!H", data.battery_voltage)
            )

            # Envía los datos a TTN
            display_message(["Enviando datos...", "A TTN"])
            print("Enviando datos a TTN...")
            lorawan.send_data(payload)
            display_message(["Datos enviados!", "Con exito!"])
            print("Datos enviados con éxito.\n")

    # Asigna la función de callback al objeto RuuviTag
    ruuvi._callback_handler = callback_handler

    # Bucle principal de escaneo y envío de datos
    try:
        while True:
            display_message(["Escaneando...", "Sensores Ruuvi"])
            print("Iniciando escaneo de sensores Ruuvi...")
            ruuvi.scan()  # Inicia el escaneo de dispositivos RuuviTag
            time.sleep(scan_interval)  # Pausa antes de la siguiente iteración de escaneo
            countdown(send_interval)  # Muestra la cuenta atrás en pantalla
    except KeyboardInterrupt:
        ruuvi.stop()
        display_message(["Escaneo detenido", "manualmente"])
        print("Escaneo detenido manualmente.")


# Variables de intervalo de espera en segundos
scan_interval = 5  # Intervalo de escaneo del sensor (en segundos)
send_interval = 900  # Intervalo entre envíos (en segundos) 15 minutos

if __name__ == "__main__":
    # Mensaje de inicio
    oled.fill(0)
    oled.text("Inicializando...", 0, 0)
    oled.show()
    main(scan_interval=10, send_interval=900)
