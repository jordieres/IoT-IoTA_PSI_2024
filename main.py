"""
File Name: main.py
Author: Irene Pereda Serrano
Created On: 29/12/2024
Description: Main script for collecting temperature, humidity, and pressure data from RuuviTag sensors,
             retrieving GPS data, and transmitting the processed statistics to TTN (The Things Network)
             via LoRaWAN.
"""

import time
from ruuvitag import core
from loraWan import lorawan
from oled import oledSetup
from gps.gps import initialize_gps
from utils import (
    pack_environmental_data,
    pack_gps_data,
    convert_to_epoch,
    parse_latitude,
    parse_longitude,
    calculate_statistics,
    filter_outliers_by_distance,
    adjust_threshold_percentile,
)

oled = oledSetup.oled


def display_countdown(remaining_time):
    """Display the countdown on the OLED screen."""
    minutes, seconds = divmod(remaining_time, 60)
    oled.fill(0)
    oled.text("Next TTN send:", 0, 0)
    oled.text(f"{minutes:02}:{seconds:02}", 0, 10)
    oled.show()


def get_valid_gps_data(gps_handler, max_attempts=10):
    """Attempts to obtain valid GPS data in a limited number of attempts"""
    print("Checking GPS data validity...")
    for attempt in range(max_attempts):
        gps_handler.read_gps_data()
        gps_data = gps_handler.get_gps_info()

        if gps_data:
            return gps_data
        else:
            print(f"Invalid GPS data on attempt {attempt + 1}. Retrying...")
        time.sleep(1)

    print("No valid GPS data obtained after retries. Setting default values.")
    return {
        'latitude': "0.0000° N",
        'longitude': "0.0000° E",
        'altitude': 0,
        'satellites_in_use': 0,
        'hdop': 99.99,
    }


def main(scan_interval, send_interval):
    ruuvi = core.RuuviTag()
    gps_handler = initialize_gps()

    temperature_data = []
    humidity_data = []
    pressure_data = []

    gps_data_last_minute = []
    gps_representative_positions = []
    gps_data_last_three_minutes = []

    gps_sample_interval = 20
    outlier_filter_interval = 60
    last_gps_sample_time = time.time()
    last_outlier_filter_time = time.time()

    last_send_time = time.time()
    last_scan_time = time.time()

    gps_reference_timestamp = None
    start_time_relative = None

    def display_message(lines, delay=2):
        oled.fill(0)
        for i, line in enumerate(lines):
            oled.text(line, 0, i * 10)
        oled.show()
        time.sleep(delay)

    def callback_handler(data):
        """Process the received RuuviTag data and store it temporarily."""
        if data:
            temperature_data.append(data.temperature)
            humidity_data.append(data.humidity)
            pressure_data.append(data.pressure)
            display_message(["Data received"])

    ruuvi._callback_handler = callback_handler

    try:
        while True:
            current_time = time.time()
            time_to_next_send = int(send_interval - (current_time - last_send_time))
            if time_to_next_send > 0:
                display_countdown(time_to_next_send)

            # Calculate the current epoch time based on GPS reference
            if gps_reference_timestamp is not None:
                current_epoch_time = gps_reference_timestamp + (current_time - start_time_relative)
            else:
                current_epoch_time = None

            # Muestreo de sensores BLE
            if current_time - last_scan_time >= scan_interval:
                display_message(["Scanning...", "Ruuvi sensors"])
                ruuvi.scan()
                last_scan_time = current_time

            # Muestreo de GPS
            if current_time - last_gps_sample_time >= gps_sample_interval:
                gps_raw = get_valid_gps_data(gps_handler)
                print(f"Raw gps data from Neov2m: ", gps_raw)
                if gps_raw:
                    epoch_time = convert_to_epoch(gps_raw['timestamp'], gps_raw['date'], local_offset=1)
                    lat = parse_latitude(gps_raw['latitude'])
                    lon = parse_longitude(gps_raw['longitude'])

                    gps_data_last_minute.append({'t': epoch_time, 'X': lat, 'Y': lon})
                    print(f"GPS data added to last minute: {gps_data_last_minute}")

                    # Configurar el primer timestamp GPS válido como referencia
                    if gps_reference_timestamp is None:
                        gps_reference_timestamp = epoch_time
                        start_time_relative = time.time()

                last_gps_sample_time = current_time

            # Filtrar outliers y determinar posición representativa
            if current_time - last_outlier_filter_time >= outlier_filter_interval:
                # Calcular threshold dinámico
                try:
                    threshold = adjust_threshold_percentile(gps_data_last_three_minutes)
                    print(f"Dynamic threshold: {threshold}")
                except Exception as e:
                    print(f"Error calculating dynamic threshold: {e}")
                    threshold = 95

                # Filtrar outliers del último minuto
                if not gps_data_last_minute:
                    print("gps_data_last_minute is empty!")
                    gps_data_filtered = []
                else:
                    gps_data_filtered = filter_outliers_by_distance(gps_data_last_minute, threshold)
                    print(f"Filtered GPS data: {gps_data_filtered}")

                # Actualizar lista de últimos 3 minutos con datos filtrados
                if gps_data_filtered:
                    gps_data_last_three_minutes.extend(gps_data_filtered)
                else:
                    print("No GPS data filtered to extend into gps_data_last_three_minutes.")

                # Agregar la última posición filtrada como representativa del minuto actual
                if gps_data_filtered:
                    gps_representative_positions.append(gps_data_filtered[-1])
                else:
                    print("No GPS data filtered, skipping representative position update.")

                print(f"Current time: ", current_epoch_time)
                for j in gps_data_last_three_minutes:
                    print(f"Data time: ", j['t'])

                # Filtrar datos GPS más antiguos a 3 minutos
                if current_epoch_time is not None and gps_data_last_three_minutes:
                    gps_data_last_three_minutes = [
                        data for data in gps_data_last_three_minutes
                        if data['t'] >= current_epoch_time - 180
                    ]
                    print(f"GPS data for last 3 minutes: {gps_data_last_three_minutes}")
                else:
                    print("gps_data_last_three_minutes is empty, skipping filtering.")

                gps_data_last_minute.clear()
                last_outlier_filter_time = current_time

            # Enviar datos cada `send_interval`
            if current_time - last_send_time >= send_interval:
                print("Preparing data to send to TTN...")

                temp_stats = calculate_statistics(temperature_data)
                hum_stats = calculate_statistics(humidity_data)
                pres_stats = calculate_statistics(pressure_data)
                print(f"GPS data to TTN: {gps_representative_positions}")

                environmental_payload = pack_environmental_data(temp_stats, hum_stats, pres_stats)
                gps_payload = pack_gps_data(gps_representative_positions)

                payload = environmental_payload + gps_payload
                print(f"Payload: ", payload)
                display_message(["Sending data...", "To TTN"])

                try:
                    lorawan.send_data(payload)
                    display_message(["Data sent!", "Successfully"])
                    print("Data sent to TTN successfully.")
                except Exception as e:
                    display_message(["Error sending", "data to TTN"])
                    print(f"Error sending data to TTN: {e}")

                temperature_data.clear()
                humidity_data.clear()
                pressure_data.clear()
                gps_representative_positions.clear()

                last_send_time = current_time

            time.sleep(1)
    except KeyboardInterrupt:
        ruuvi.stop()
        display_message(["Scanning stopped"])
        print("Scanning stopped.")

    except Exception as e:
        ruuvi.stop()
        display_message(["Unexpected error"])
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    oled.fill(0)
    oled.text("Initializing...", 0, 0)
    oled.show()
    main(scan_interval=30, send_interval=900)
