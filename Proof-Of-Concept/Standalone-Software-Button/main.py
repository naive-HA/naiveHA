import json
import machine
from led import LED
from device import DEVICE
import uasyncio as asyncio
from serverd import SERVERD
from networkd import NETWORKD
from const import _LED_MODES

LED_MODES = _LED_MODES()

class APPLICATION():
    def __init__(self, list_of_custom_classes: list[str]):
        rtc = machine.RTC()
        rtc.datetime((2023, 3, 18, 0, 0, 0, 0, 0))
        
        self.light = LED()
        self.device = DEVICE(list_of_custom_classes)
        self.network_daemon = NETWORKD()
        self.server_daemon = SERVERD()
        
    def start(self) -> None:
        self.device.set_led_mode = self.light.display
        self.network_daemon.set_led_mode = self.light.display
        self.network_daemon.inform_network_status = self.server_daemon.network_status
        self.network_daemon.start()
        self.device.unique_id = self.network_daemon.mac
        self.server_daemon.handle_message = self.handle_message
        
    async def infinite_loop(self):
        await self.device.infinite_loop()
        await self.server_daemon.infinite_loop()
        await self.network_daemon.watchdog() #main loop

    def stop(self) -> None:
        self.light.stop()
        self.server_daemon.stop()
        self.network_daemon.stop()

    def handle_message(self, payload: str) -> str:
        return self.device.handle_message(json.loads(payload))

if __name__ == "__main__":
    application = APPLICATION(["temp_control"])
    application.start()
    asyncio.run(application.infinite_loop())
    application.stop()