import time

from ruuvitag import core


def cb(ruuvitag):
    print("RuuviTagRAWv2(mac={}".format(ruuvitag.mac))
    print("              rssi={}".format(ruuvitag.rssi))
    print("              format={}".format(ruuvitag.format))
    print("              humidity={}".format(ruuvitag.humidity))
    print("              temperature={}".format(ruuvitag.temperature))
    print("              pressure={}".format(ruuvitag.pressure))
    print("              acceleration_x={}".format(ruuvitag.acceleration_x))
    print("              acceleration_y={}".format(ruuvitag.acceleration_y))
    print("              acceleration_z={}".format(ruuvitag.acceleration_z))
    print("              battery_voltage={}".format(ruuvitag.battery_voltage))
    print("              power_info={}".format(ruuvitag.power_info))
    print("              movement_counter={}".format(ruuvitag.movement_counter))
    print("              measurement_sequence={}".format(ruuvitag.measurement_sequence)+")")
    print("\n")


def run(ruuvi):
    try:
        while True:
            ruuvi.scan()
            time.sleep_ms(10000)
    except KeyboardInterrupt:
        ruuvi.stop()


ruuvi = core.RuuviTag()
ruuvi._callback_handler = cb
run(ruuvi)

# whitelist = (b'aabbccddee21', b'aabbccddee42',)
# ruuvi = RuuviTag(whitelist=whitelist)
