"""
File Name: main.py
Author: Irene Pereda Serrano
Created On: 29/12/2024
Description: Main script for collecting temperature, humidity, and pressure data from RuuviTag sensors,
             retrieving GPS data, and transmitting the processed statistics via LoRaWAN
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


def display_countdown(remaining_time_gps, remaining_time_env):
    """Display the countdown on the OLED screen"""
    minutes_gps, seconds_gps = divmod(remaining_time_gps, 60)
    minutes_env, seconds_env = divmod(remaining_time_env, 60)

    oled.fill(0)
    oled.text("Next GPS send:", 0, 0)
    oled.text(f"{minutes_gps:02}:{seconds_gps:02}", 0, 10)
    oled.text("Next Env send:", 0, 20)
    oled.text(f"{minutes_env:02}:{seconds_env:02}", 0, 30)
    oled.show()


def get_valid_gps_data(gps_handler, max_attempts=10):
    """Attempts to obtain valid GPS data in a limited number of attempts"""
    try:
        print("Checking GPS data validity...")
        for attempt in range(max_attempts):
            gps_handler.read_gps_data()
            gps_data = gps_handler.get_gps_info()

            if gps_data:
                return gps_data

            time.sleep(1)

        print("No valid GPS data obtained after retries. Setting default values.")
        return None
    except Exception as e:
        print(f"An error occurred in get_valid_gps_data(): {e}")
        return None


def main(scan_interval, send_interval_gps, send_interval_env):
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
    last_send_time_gps = time.time()
    last_send_time_env = time.time()
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
        """Process the received RuuviTag data and store it temporarily"""
        if data:
            temperature_data.append(data.temperature)
            humidity_data.append(data.humidity)
            pressure_data.append(data.pressure)
            display_message(["Data received"])

    ruuvi._callback_handler = callback_handler

    while True:
        try:
            current_time = time.time()
            time_to_next_gps = int(send_interval_gps - (current_time - last_send_time_gps))
            time_to_next_env = int(send_interval_env - (current_time - last_send_time_env))

            display_countdown(time_to_next_gps, time_to_next_env)

            # Calculate the current epoch time based on GPS reference
            if gps_reference_timestamp is not None:
                current_epoch_time = gps_reference_timestamp + (current_time - start_time_relative)
            else:
                current_epoch_time = None

            # BLE scanning
            try:
                if current_time - last_scan_time >= scan_interval:
                    display_message(["Scanning...", "Ruuvi sensors"])
                    ruuvi.scan()
                    last_scan_time = current_time
            except Exception as e:
                display_message(["Unexpected error"])
                print(f"Error during BLE scanning: {e}")

            # GPS sampling
            try:
                if current_time - last_gps_sample_time >= gps_sample_interval:

                    gps_raw = get_valid_gps_data(gps_handler)

                    if gps_raw is not None:
                        epoch_time = convert_to_epoch(gps_raw['timestamp'], gps_raw['date'], local_offset=1)
                        lat = parse_latitude(gps_raw['latitude'])
                        lon = parse_longitude(gps_raw['longitude'])
                        gps_data_last_minute.append({'t': epoch_time, 'X': lat, 'Y': lon})

                        # Setting the initial timestamp reference
                        if gps_reference_timestamp is None:
                            if epoch_time is not None:
                                gps_reference_timestamp = epoch_time
                                start_time_relative = time.time()
                                print(f"GPS reference timestamp set to: {gps_reference_timestamp}")

                    last_gps_sample_time = current_time
            except Exception as e:
                display_message(["Unexpected error"])
                print(f"Error during GPS sampling: {e}")

            # Filter outliers and determine representative position
            try:
                if current_time - last_outlier_filter_time >= outlier_filter_interval:
                    threshold = adjust_threshold_percentile(gps_data_last_three_minutes)

                    if gps_data_last_minute:
                        gps_data_filtered = filter_outliers_by_distance(gps_data_last_minute, threshold)
                        gps_data_last_three_minutes.extend(gps_data_filtered)

                        if gps_data_filtered:
                            gps_representative_positions.append(gps_data_filtered[-1])

                    if current_epoch_time is not None and gps_data_last_three_minutes:
                        gps_data_last_three_minutes = [
                            data for data in gps_data_last_three_minutes
                            if data['t'] >= current_epoch_time - 180
                        ]

                    gps_data_last_minute.clear()
                    last_outlier_filter_time = current_time

            except Exception as e:
                display_message(["Unexpected error"])
                print(f"Error sending data to TTN: {e}")

            # Send data to LoRaWAN
            try:
                # Send GPS data every 5 minutes
                if current_time - last_send_time_gps >= send_interval_gps:
                    gps_payload = pack_gps_data(gps_representative_positions)
                    lorawan.send_data(gps_payload)
                    display_message(["GPS data sent!", "Successfully"])
                    print("Sent GPS payload to TTN")

                    gps_representative_positions.clear()
                    last_send_time_gps = current_time

                # Send environmental data every 60 minutes
                if current_time - last_send_time_env >= send_interval_env:
                    num_samples = len(temperature_data)

                    temp_stats = calculate_statistics(temperature_data)
                    hum_stats = calculate_statistics(humidity_data)
                    pres_stats = calculate_statistics(pressure_data)

                    env_payload = pack_environmental_data(temp_stats, hum_stats, pres_stats, num_samples)
                    lorawan.send_data(env_payload)
                    display_message(["Environmental data sent!", "Successfully"])
                    print("Sent Environmental payload to TTN")

                    temperature_data.clear()
                    humidity_data.clear()
                    pressure_data.clear()

                    last_send_time_env = current_time

            except Exception as e:
                display_message(["Error sending", "data via LoRaWAN"])
                print(f"Error during data transmission: {e}")

            time.sleep(1)

        except KeyboardInterrupt:
            ruuvi.stop()
            display_message(["Scanning stopped"])
            print("Scanning stopped")
            break

        except Exception as e:
            ruuvi.stop()
            display_message(["Unexpected error"])
            print(f"Error type: {type(e).__name__}, details: {e}")


if __name__ == "__main__":
    oled.fill(0)
    oled.text("Initializing...", 0, 0)
    oled.show()
    main(scan_interval=30, send_interval_gps=300, send_interval_env=3600)
