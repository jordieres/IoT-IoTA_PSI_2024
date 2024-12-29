import time
from ruuvitag import core
from loraWan import lorawan
from ustruct import pack
from oled import oledSetup
from gps.gps import initialize_gps

oled = oledSetup.oled


# Functions to pack sensor data
def pack_temp(temp):
    temp_conv = round(temp / 0.005)
    return pack("!h", temp_conv)


def pack_humid(hum):
    hum_conv = round(hum / 0.0025)
    return pack("!H", hum_conv)


def pack_pressure(pressure):
    pres_conv = round(pressure / 10.0)
    return pack("!H", pres_conv)


def pack_std(std):
    std_conv = round(std / 0.005)
    return pack("!H", std_conv)


def pack_latitude(latitude_str):
    coord, hemi = latitude_str.split("°")
    decimal_lat = float(coord.strip())
    if hemi.strip() == 'S':
        decimal_lat = -decimal_lat
    return pack("!i", int(decimal_lat * 10 ** 6))


def pack_longitude(longitude_str):
    coord, hemi = longitude_str.split("°")
    decimal_lon = float(coord.strip())
    if hemi.strip() == 'W':
        decimal_lon = -decimal_lon
    return pack("!i", int(decimal_lon * 10 ** 6))


def pack_altitude(altitude):
    return pack("!H", int(altitude))


def pack_satellites(satellites):
    return pack("!B", satellites)


def pack_hdop(hdop):
    hdop_scaled = int(hdop * 100)
    return pack("!B", hdop_scaled)


# Utility functions
def mean(data):
    return sum(data) / len(data) if data else 0


def stdev(data):
    if len(data) <= 1:
        return 0
    avg = mean(data)
    variance = sum((x - avg) ** 2 for x in data) / len(data)
    return variance ** 0.5


def calculate_statistics(data):
    """Calculate max, min, mean, and standard deviation for a list of data."""
    if not data:
        return 0, 0, 0, 0
    return max(data), min(data), mean(data), stdev(data)


def display_countdown(remaining_time):
    """Display the countdown on the OLED screen."""
    minutes, seconds = divmod(remaining_time, 60)
    oled.fill(0)
    oled.text("Next TTN send:", 0, 0)
    oled.text(f"{minutes:02}:{seconds:02}", 0, 10)
    oled.show()


def get_valid_gps_data(gps_handler, max_attempts=10):
    """Intenta obtener datos GPS válidos en un número limitado de intentos."""
    print("Checking GPS data validity...")
    for attempt in range(max_attempts):
        gps_handler.read_gps_data()
        gps_data = gps_handler.get_gps_info()
        if gps_data and gps_data['satellites_in_use'] >= 3 and gps_data['hdop'] <= 10:
            print(f"Valid GPS data obtained on attempt {attempt + 1}: {gps_data}")
            return gps_data
        else:
            print(f"Invalid GPS data on attempt {attempt + 1}. Retrying...")
        time.sleep(1)  # Pequeño retraso entre intentos

    # Si no se obtienen datos válidos, devuelve valores predeterminados
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
