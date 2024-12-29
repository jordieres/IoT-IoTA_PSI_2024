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
from utils import pack_temp as pack_temp
from utils import pack_humid as pack_humid
from utils import pack_pressure as pack_pressure
from utils import pack_std as pack_std
from utils import calculate_statistics as calculate_statistics
from utils import pack_latitude as pack_latitude
from utils import pack_longitude as pack_longitude
from utils import pack_altitude as pack_altitude
from utils import pack_hdop as pack_hdop
from utils import pack_satellites as pack_satellites

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
        if gps_data and gps_data['satellites_in_use'] >= 3 and gps_data['hdop'] <= 10:
            print(f"Valid GPS data obtained on attempt {attempt + 1}: {gps_data}")
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

            print(f"Sensor data: Temp={data.temperature} C, Hum={data.humidity}%, Press={data.pressure} hPa")

    ruuvi._callback_handler = callback_handler

    last_send_time = time.time()  # Last time data was sent via LoRa
    last_scan_time = time.time()  # Last time BLE scanning was performed

    try:
        while True:
            current_time = time.time()
            time_to_next_send = int(send_interval - (current_time - last_send_time))

            if time_to_next_send > 0:
                display_countdown(time_to_next_send)

            if current_time - last_scan_time >= scan_interval:
                print("Scanning Ruuvi sensors...")
                display_message(["Scanning...", "Ruuvi sensors"])
                ruuvi.scan()
                last_scan_time = current_time

            if current_time - last_send_time >= send_interval:
                print("Preparing data to send to TTN...")

                temp_stats = calculate_statistics(temperature_data)
                hum_stats = calculate_statistics(humidity_data)
                pres_stats = calculate_statistics(pressure_data)

                gps_data = get_valid_gps_data(gps_handler)

                if all(stat is not None for stat in temp_stats) and all(stat is not None for stat in hum_stats) and all(
                        stat is not None for stat in pres_stats):
                    payload = (
                            pack_temp(temperature_data[-1]) +
                            pack_humid(humidity_data[-1]) +
                            pack_pressure(pressure_data[-1]) +
                            pack_temp(temp_stats[0]) +
                            pack_temp(temp_stats[1]) +
                            pack_temp(temp_stats[2]) +
                            pack_temp(temp_stats[3]) +
                            pack_humid(hum_stats[0]) +
                            pack_humid(hum_stats[1]) +
                            pack_humid(hum_stats[2]) +
                            pack_humid(hum_stats[3]) +
                            pack_pressure(pres_stats[0]) +
                            pack_pressure(pres_stats[1]) +
                            pack_pressure(pres_stats[2]) +
                            pack_std(pres_stats[3]) +
                            pack_latitude(gps_data['latitude']) +
                            pack_longitude(gps_data['longitude']) +
                            pack_altitude(gps_data['altitude']) +
                            pack_satellites(gps_data['satellites_in_use']) +
                            pack_hdop(gps_data['hdop'])
                    )

                    display_message(["Sending data...", "To TTN"])
                    try:
                        lorawan.send_data(payload)
                        display_message(["Data sent!", "Successfully"])
                        print("Data sent to TTN successfully.")
                    except Exception as e:
                        display_message(["Error sending", "data to TTN"])
                        print(f"Error sending data to TTN: {e}")
                else:
                    print("Insufficient data for creating payload.")

                temperature_data.clear()
                humidity_data.clear()
                pressure_data.clear()

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
