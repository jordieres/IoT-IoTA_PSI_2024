
import time
import machine


led = machine.Pin(35, machine.Pin.OUT)
led.on()
time.sleep_ms(5000)
led.off()
