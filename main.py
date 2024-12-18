import time
from ruuvitag import core
from loraWan import lorawan
from ustruct import pack
from oled import oledSetup

oled = oledSetup.oled


# Functions to pack data
def pack_temp(temp):
    temp_conv = round(temp / 0.005)
    return pack("!h", temp_conv)


def pack_humid(hum):
    hum_conv = round(hum / 0.0025)
    return pack("!H", hum_conv)


def pack_pressure(pressure):
    pres_conv = round(pressure / 10.0)
    return pack("!H", pres_conv)


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


def main(scan_interval, send_interval):

    ruuvi = core.RuuviTag()

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

            display_message([
                "Data received:",
                f"Temp: {data.temperature:.2f} C",
                f"Hum: {data.humidity:.2f}%",
                f"Press: {data.pressure:.2f} hPa",
            ], delay=2)

            print(f"Sensor data: Temp={data.temperature} C, Hum={data.humidity}%, Press={data.pressure} hPa")

    ruuvi._callback_handler = callback_handler

    last_send_time = time.time()  # Last time data was sent via LoRa
    last_scan_time = time.time()  # Last time BLE scanning was performed

    try:
        while True:
            current_time = time.time()

            # Remaining time for the next send
            time_to_next_send = int(send_interval - (current_time - last_send_time))
            if time_to_next_send > 0:
                display_countdown(time_to_next_send)

            # Perform BLE scanning every `scan_interval`
            if current_time - last_scan_time >= scan_interval:
                print("Scanning Ruuvi sensors...")
                display_message(["Scanning...", "Ruuvi sensors"])
                ruuvi.scan()
                last_scan_time = current_time

            # Send data to TTN every `send_interval`
            if current_time - last_send_time >= send_interval:
                print("Preparing data to send to TTN...")

                temp_stats = calculate_statistics(temperature_data)
                hum_stats = calculate_statistics(humidity_data)
                pres_stats = calculate_statistics(pressure_data)

                if all(stat is not None for stat in temp_stats) and all(stat is not None for stat in hum_stats) and all(
                        stat is not None for stat in pres_stats):
                    payload = (
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
                            pack_pressure(pres_stats[3])
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
        display_message(["Scanning stopped", "manually"])
        print("Scanning manually stopped.")


scan_interval = 30   # BLE scan interval
send_interval = 900  # LoRa send interval

if __name__ == "__main__":
    oled.fill(0)
    oled.text("Initializing...", 0, 0)
    oled.show()
    main(scan_interval=30, send_interval=900)
