import ssd1306
import heltec
from machine import Pin, SoftI2C

# ESP32 Pin assignment
i2c = SoftI2C(scl=heltec.SCL_OLED, sda=heltec.SDA_OLED)

pin = Pin(heltec.RST_OLED, Pin.OUT)
pin.value(0)
pin.value(1)

oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)


# Función para escribir la frase en la pantalla
def write_text(oled, text, x, y):
    oled.text(text, x, y)


# Función para mostrar la pantalla
def show_screen(oled):
    oled.show()


# Limpia la pantalla
oled.fill(0)

# Divide la frase en partes más pequeñas
phrase_parts = ["Hola", "soy", "Irene"]

# Calcula el número de partes y el espacio entre ellas
num_parts = len(phrase_parts)
spacing = oled_height // num_parts

# Muestra cada parte de la frase en la pantalla
for i, part in enumerate(phrase_parts):
    y = spacing * i
    oled.text(part, 0, y)

# Muestra la pantalla
show_screen(oled)
