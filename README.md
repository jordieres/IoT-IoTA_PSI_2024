# **IoT-IoTA_PSI_2024**

## **Overview**
This project is an **IoT system** designed for **environmental monitoring and GPS tracking** using **LoRaWAN**. It integrates multiple technologies, including Bluetooth Low Energy (BLE), OLED displays and LoRaWAN to collect, process and transmit sensor data.

Although Wi-Fi and MQTT modules are included for future applications, they are not used in the current implementation.

The system runs on a **WiFi LoRa 32 (V3.2) ESP32-S3** board and communicates using LoRaWAN, which allows long-range communication with low power consumption.

---

## **Features**
- **Environmental data collection:** gathers temperature, humidity and pressure from RuuviTag sensor.
- **GPS tracking:** collects and transmits position data from NEO6MV2 receiver.
- **LoRaWAN communication:** manages packet encryption and transmission.
- **OLED display:** provides real-time visual feedback.
- **BLE scanning**: detects and processes data from nearby BLE devices (RuuviTag).

---

## **Project Structure**
The code is structured into different modules, each handling specific functionalities:

- **`bluetoothv1/`** → Handles BLE scanning and communication.
- **`examples/`** → Various test scripts for MQTT communication, OLED display, and WiFi connection testing.
- **`loraWan/`** → Implements LoRaWAN encryption, packet management, and radio control.
- **`mqtt/`** → MQTT-based communication modules (not currently in use).
- **`oled/`** → OLED screen management and display utilities.
- **`ruuvitag/`** → RuuviTag sensor data acquisition, decoding, and formatting.
- **`tangle/`** → Interface to interact with an IOTA Hornet node.
- **`wifi/`** → WiFi connectivity module.
- **`heltec.py`** → Configuration file for the Heltec WiFi LoRa 32 V3.2 (ESP32-S3) module.
- **`main.py`** → Main execution script, orchestrating sensor reading, GPS tracking, and LoRaWAN transmission.
- **`utils.py`** → Utility functions for data processing, encoding, and filtering.

---

## **Setup and configuration**

### **1. Hardware requirements**
- **WiFi LoRa 32 (V3.2) board**
- **RuuviTag sensor**
- **GPS Module** (e.g., Neo-6M)
- **LoRaWAN gateway** 

### **2. Installation**
1. Clone the repository:
    ```bash
   git clone https://github.com/jordieres/IoT-IoTA_PSI_2024
   cd IoT-IoTA_PSI_2024

2. Install required dependencies specific to MicroPython
    ```bash
   esptool.py --port /dev/ttyUSB0 erase_flash
   esptool.py --port /dev/ttyUSB0 --baud 460800 write_flash 0 ESP32_BOARD_NAME-DATE-VERSION.bin
    ````
    Replace /dev/ttyUSB0 with the correct port for your system.

3. Flash the scripts onto the ESP32-S3 board

---

## **Usage**
Once the necessary files have been flashed onto the ESP32, the execution behavior depends on how the module is powered:

**1. Running via REPL (for debugging)**

If you are connected via a serial interface, you can manually start the script in the REPL:
```bash
import main
main.main(scan_interval=30, send_interval_gps=300, send_interval_env=3600)
````
This method allows you to test different parameters dynamically.

**2. Running automatically (Normal operation)**

If the ESP32 is powered externally, the script will execute automatically upon startup, running main.py with default settings:
- GPS data sent every 5 minutes
- Environmental data sent every hour

This ensures that the system collects and transmits data without user intervention.

## **LoRaWAN payloads**
The system transmits two types of payload to comply with LoRaWAN payload size limits:

- **Type 1 (every 5 minutes):**
  - 1 byte: payload type indicator (0x01)
  - 4 bytes: timestamp of the message
  - Up to 5 sets of:
    - 4 bytes: latitude
    - 4 bytes: longitude

- **Type 2 (every hour):**
  - 1 byte: payload type indicator (0x02)
  - 1 byte: number of recorded samples
  - 4 bytes each:
    - Temperature {max, mean, min, std} 
    - Humidity {max, mean, min, std}
    - Pressure {max, mean, min, std}

Both payloads are structured to ensure efficient transmission under LoRaWAN duty cycle restrictions.

## **Acknowledgments**
This project is developed as part of the Master's Thesis in Industrial Engineering at the Polytechnic University of Madrid, implementing LoRaWAN-based sensor networks for real-world environmental monitoring and position tracking, with potential applications in healthcare and food industry.

For any questions, contributions or improvements, feel free to open an issue or submit a pull request.

