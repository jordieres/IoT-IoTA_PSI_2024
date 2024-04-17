**RuuviTag MicroPython Module**

**Overview**
    
The RuuviTag MicroPython module provides functionality to interact with RuuviTag sensors using Bluetooth Low Energy (BLE) on MicroPython platforms. It includes features for scanning RuuviTag devices, decoding raw sensor data, and formatting the decoded data.

**Files**
- **core.py**: Contains the core functionality for scanning RuuviTag sensors and handling scan results.
- **decoder.py**: Provides functions to decode raw sensor data from RuuviTag devices into structured data formats.
- **format.py**: Defines structured data formats for representing decoded sensor data.
- **init.py**: Initializes the module and provides package metadata.

**Usage**

Import the RuuviTag class from ruuvitag.core to start scanning RuuviTag devices.
Define callback functions to handle the decoded sensor data.
Use the decoding functions from ruuvitag.decoder to parse the raw sensor data.
Access the structured data formats defined in ruuvitag.format to access specific sensor data fields.

**License**

This module is licensed under the MIT License. See the LICENSE file for details.
