import json
import time
import socket
import uselect
import network
import ubinascii
import uasyncio as asyncio
from const import _LED_MODES
from icmp_echo_request import ICMP_ECHO_REQUEST

LED_MODES = _LED_MODES()

class NETWORKD():
    PORT = 80
    TIMEOUT = 10
    WAIT_TIME = 1
    MAX_RETRIES = 3
    LONG_WAIT_TIME = 5
    PINGING_INTERVAL = 180
    WATCHDOG_INTERVAL = 250

    def __init__(self):
        self.mac = '00:00:00:00:00:00'
        self.run : bool = False
        self.set_led_mode : "Callable[[LED_MODES]]" | None = None
        self.inform_network_status : "Callable[[bool]]" | None = None
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
        self.wlan.config(pm = 0x111022)
        #0x111022 - performance mode
        #0xa11140 - remove power saving mode
        #0xa11142 - default
        
    def start(self) -> bool:
        self.run = True
        assert self.set_led_mode is not None
        
        self.inform_network_status is not None and self.inform_network_status(False)
        self.set_led_mode(LED_MODES.NETWORK_DISCONNECTED)
        self._connect_wifi()
        self.set_led_mode(LED_MODES.NETWORK_CONNECTED)
        ip, mask, gateway, dns = self.wlan.ifconfig()
        self.ping = ICMP_ECHO_REQUEST(gateway)
        self.inform_network_status is not None and self.inform_network_status(True)
        return True
    
    def stop(self) -> None:
        self.run = False
        self.inform_network_status is not None and self.inform_network_status(False)
        return None
    
    def _connect_wifi(self) -> bool:
        with open('wifi_configs', 'r') as config_file:
            config_file_content = config_file.read()
        configs = json.loads(config_file_content)
        while self.run:
            self.wlan.scan()
            self.wlan.connect(configs["SSID"], configs["password"])
            if self._is_network_connected():
                print("IP: " + self.wlan.ifconfig()[0])
                self.mac = ubinascii.hexlify(network.WLAN().config('mac'),':').decode()
                break
            else:
                time.sleep(NETWORKD.WAIT_TIME)
        return True

    def _is_network_connected(self) -> bool:
        #network.STAT_WRONG_PASSWORD = -3
        #network.STAT_NO_AP_FOUND = -2
        #network.STAT_CONNECT_FAIL = -1
        #network.STAT_IDLE = 0
        #network.STAT_CONNECTING = 1
        #network.STAT_GOT_IP = 3
        if self.wlan.status() < 0 or self.wlan.status() >= 3:
            if self.wlan.status() == network.STAT_GOT_IP:
                #connected
                return True
            else:
                #network connection failed
                return False
        else:
            return False
    
    async def watchdog(self) -> None:
        asyncio.create_task(self._keep_wifi_alive())
        while self.run:
            if not self._is_network_connected():
                connected = False
                self.inform_network_status is not None and self.inform_network_status(connected)
                while not connected:
                    self.stop()
                    await asyncio.sleep(NETWORKD.LONG_WAIT_TIME)
                    try:
                        self.start()
                    except:
                        continue
                    for _ in range(NETWORKD.MAX_RETRIES):
                        if not self._is_network_connected():
                            await asyncio.sleep(NETWORKD.LONG_WAIT_TIME)
                        else:
                            connected = True
                            break
                self.inform_network_status is not None and self.inform_network_status(connected)
            await asyncio.sleep_ms(NETWORKD.WATCHDOG_INTERVAL)
            
    async def _keep_wifi_alive(self) -> None:
        while self.run:
            await self.ping.ping()
            await asyncio.sleep(NETWORKD.PINGING_INTERVAL)