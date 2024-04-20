import time

from ruuvitag import core


def cb(ruuvitag):
    print(ruuvitag)
    print("\n")


def run(ruuvi):
    try:
        while True:
            ruuvi.scan()
            time.sleep_ms(50000)
    except KeyboardInterrupt:
        ruuvi.stop()


ruuvi = core.RuuviTag()
ruuvi._callback_handler = cb
run(ruuvi)

# whitelist = (b'aabbccddee21', b'aabbccddee42',)
# ruuvi = RuuviTag(whitelist=whitelist)
