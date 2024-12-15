"""
File Name: oledDisplay.py
Author: Irene Pereda Serrano
Created On: 17/04/2024
Description: This file is an example about how to print text on the OLED screen
"""


from oled import oledSetup

oled = oledSetup.oled

oled.fill(0)
oled.show()

oled.text('Hola!', 0, 0)
oled.text('Soy Irene', 0, 10)
oled.text('Display en OLED', 0, 20)
oled.text('CONSEGUIDO!!!', 0, 30)
oled.show()
