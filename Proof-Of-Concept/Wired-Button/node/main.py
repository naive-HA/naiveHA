import time
import machine
from led import LED
from rf433 import RF433
from const import _LED_MODES
from networkd import NETWORKD

LED_MODES = _LED_MODES()

if __name__ == "__main__":
    rtc = machine.RTC()
    rtc.datetime((2023, 3, 18, 0, 0, 0, 0, 0))
    light = LED()
    trx = RF433()
    def set_led_mode(flag: int) -> None:
        print(flag)
        light.display(flag)
        return None

    def packet_received(data: str) -> None:
        print("received data: " + data)
        trx.toggle()
        return None

    network_daemon = NETWORKD()
    network_daemon.set_led_mode = set_led_mode
    network_daemon.packet_received = packet_received
    network_daemon.start()
    print("connecting to coordinator")
    network_daemon.connect()
    print("listening to commands")
    network_daemon._receive()
    time.sleep(60000)
    light.stop()
    network_daemon.stop()

