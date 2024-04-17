# Proof-of-concept of a REPL over BLE UART.
#
# Tested with the Adafruit Bluefruit app on Android.
# Set the EoL characters to \r\n.

import bluetooth
import io
import os
import micropython
import machine
from micropython import const
import struct
import time
from machine import Pin

# Configuración del pin 2 como salida y su posterior apagado
pbt = Pin(2, Pin.OUT) # LNA_IN
pbt.off() 

# Constantes que representan diferentes eventos de interrupción que pueden ocurrir durante la comunicación Bluetooth
_IRQ_CENTRAL_CONNECT = const(1)         # If a central has connected to this peripheral
_IRQ_CENTRAL_DISCONNECT = const(2)      # If a central has disconnected from this peripheral
_IRQ_GATTS_WRITE = const(3)             # If a client has written to this characteristic or descriptor

# Define constantes que representan diferentes eventos de interrupción que pueden ocurrir durante la comunicación Bluetooth
_FLAG_WRITE = const(0x0008)
_FLAG_NOTIFY = const(0x0010)

# Define UUIDs (Identificadores Únicos Universales) para los servicios y características UART BLE que serán
# utilizados para la comunicación Bluetooth
_UART_UUID = bluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
_UART_TX = (
    bluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E"),
    _FLAG_NOTIFY,
)
_UART_RX = (
    bluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E"),
    _FLAG_WRITE,
)
_UART_SERVICE = (
    _UART_UUID,
    (_UART_TX, _UART_RX),
)

# Define la apariencia del dispositivo para el anuncio Bluetooth como un equipo informático genérico
_ADV_APPEARANCE_GENERIC_COMPUTER = const(128)


# clase `BLEUART` que representa un dispositivo UART BLE. El método `__init__` inicializa el dispositivo y
# configura la conexión Bluetooth. También prepara el dispositivo para recibir y enviar datos
class BLEUART:
    def __init__(self, ble, name, rxbuf=1000):
        self._ble = ble
        self._ble.active(True)
        self._ble.irq(self._irq)
        ((self._tx_handle, self._rx_handle),
         ) = self._ble.gatts_register_services((_UART_SERVICE,))
        # Increase the size of the rx buffer and enable append mode.
        self._ble.gatts_set_buffer(self._rx_handle, rxbuf, True)
        self._connections = set()
        self._rx_buffer = bytearray()
        self._handler = None
        # Optionally add services=[_UART_UUID], but this is likely to make the payload too large.
        self._payload = advertising_payload(
            name=name, appearance=_ADV_APPEARANCE_GENERIC_COMPUTER)
        self._advertise()

    #  Método para configurar un manejador de interrupciones para el dispositivo BLE
    def irq(self, handler):
        self._handler = handler

    # Define un manejador de interrupciones para manejar eventos Bluetooth como la conexión y desconexión
    # de dispositivos, y la escritura de datos en el dispositivo
    def _irq(self, event, data):
        # Track connections so we can send notifications.
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, _, _ = data
            print("_IRQ_CENTRAL_CONNECT")
            pbt.on() 
            self._connections.add(conn_handle)
        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, _, _ = data
            pbt.off()
            print('_IRQ_CENTRAL_DISCONNECT')
            if conn_handle in self._connections:
                self._connections.remove(conn_handle)
            # Start advertising again to allow a new connection.
            self._advertise()
        elif event == _IRQ_GATTS_WRITE:
            conn_handle, value_handle = data
            if conn_handle in self._connections and value_handle == self._rx_handle:
                self._rx_buffer += self._ble.gatts_read(self._rx_handle)
                if self._handler:
                    self._handler()

    # Método que devuelve la cantidad de datos recibidos y aún no leídos en el buffer
    def any(self):
        return len(self._rx_buffer)

    # Método para leer datos del buffer de recepción
    def read(self, sz=None):
        if not sz:
            sz = len(self._rx_buffer)
        result = self._rx_buffer[0:sz]
        self._rx_buffer = self._rx_buffer[sz:]
        return result

    # Método para escribir datos en el dispositivo conectado
    def write(self, data):
        for conn_handle in self._connections:
            self._ble.gatts_notify(conn_handle, self._tx_handle, data)

    # Método para cerrar la conexión Bluetooth
    def close(self):
        for conn_handle in self._connections:
            self._ble.gap_disconnect(conn_handle)
        self._connections.clear()

    # Método para enviar publicidad Bluetooth para anunciar la disponibilidad del dispositivo
    def _advertise(self, interval_us=500000):
        self._ble.gap_advertise(interval_us, adv_data=self._payload)


# Advertising payloads are repeated packets of the following form:
#   1 byte data length (N + 1)
#   1 byte type (see constants below)
#   N bytes type-specific data
# Constantes que representan diferentes tipos de datos en los paquetes de publicidad Bluetooth
_ADV_TYPE_FLAGS = const(0x01)
_ADV_TYPE_NAME = const(0x09)
_ADV_TYPE_UUID16_COMPLETE = const(0x3)
_ADV_TYPE_UUID32_COMPLETE = const(0x5)
_ADV_TYPE_UUID128_COMPLETE = const(0x7)
_ADV_TYPE_UUID16_MORE = const(0x2)
_ADV_TYPE_UUID32_MORE = const(0x4)
_ADV_TYPE_UUID128_MORE = const(0x6)
_ADV_TYPE_APPEARANCE = const(0x19)


# Generate a payload to be passed to gap_advertise(adv_data=...).
def advertising_payload(limited_disc=False, br_edr=False, name=None, services=None, appearance=0):
    payload = bytearray()

    def _append(adv_type, value):
        nonlocal payload
        payload += struct.pack("BB", len(value) + 1, adv_type) + value

    _append(
        _ADV_TYPE_FLAGS,
        struct.pack("B", (0x01 if limited_disc else 0x02) +
                    (0x18 if br_edr else 0x04)),
    )

    if name:
        _append(_ADV_TYPE_NAME, name)

    if services:
        for uuid in services:
            b = bytes(uuid)
            if len(b) == 2:
                _append(_ADV_TYPE_UUID16_COMPLETE, b)
            elif len(b) == 4:
                _append(_ADV_TYPE_UUID32_COMPLETE, b)
            elif len(b) == 16:
                _append(_ADV_TYPE_UUID128_COMPLETE, b)

    # See org.bluetooth.characteristic.gap.appearance.xml
    if appearance:
        _append(_ADV_TYPE_APPEARANCE, struct.pack("<h", appearance))

    return payload


def demo():
    print("demo")   


if __name__ == "__main__":
    demo()
