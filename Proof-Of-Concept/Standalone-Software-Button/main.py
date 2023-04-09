import json
import machine
from led import LED
from device import DEVICE
from serverd import SERVERD
from const import _LED_MODES

LED_MODES = _LED_MODES()

class APPLICATION():
    def __init__(self, list_of_custom_classes: list[str]):
        rtc = machine.RTC()
        rtc.datetime((2023, 3, 18, 0, 0, 0, 0, 0))
        
        self.light = LED()
        self.device = DEVICE(list_of_custom_classes)
        self.server_daemon = SERVERD()
        
    def start(self) -> None:
        self.device.set_led_mode = self.light.display
        self.server_daemon.set_led_mode = self.light.display
        self.server_daemon.handle_message = self.handle_request
        self.server_daemon.start()

    def infinite_loop(self):
        self.server_daemon.infinite_loop()

    def stop(self) -> None:
        self.light.stop()
        self.server_daemon.stop()

    def handle_request(self, request: str) -> str:
        return self.device.get_html(request)

if __name__ == "__main__":
    application = APPLICATION(["temp_sensor", "spector", "arlec"])
    application.start()
    application.infinite_loop()
    application.stop()