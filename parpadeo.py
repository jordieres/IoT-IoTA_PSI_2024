"""
Nombre del archivo: parpadeo.py
Autor: Irene Pereda Serrano
Fecha de creación: 20/03/2024
Descripción: Implementación de funciones para control de un LED
"""

import time
import machine


def parpadear(duracion, cant, npin):
    """Esta función hace parpadear un LED.
    nPin: Indica en que pin se encuentra conectado el LED
    duracion: Controla el tiempo en el cual el LED se enciende y se apaga
    cant: Indica la cantidad máxima de veces que el LED parpadeará"""

    led = machine.Pin(npin, machine.Pin.OUT)

    # Ciclo para controlar los parpadeos

    for x in range(cant):
        led.on()
        time.sleep_ms(duracion)
        led.off()
        time.sleep_ms(duracion)

    return 'Done!'
