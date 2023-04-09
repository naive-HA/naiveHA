import json
import time
import socket
import network
from const import _LED_MODES

LED_MODES = _LED_MODES()

class SERVERD():
    PORT = 80
    WAIT_TIME = 1
    LONG_WAIT_TIME = 5
    VERY_LONG_WAIT_TIME = 10

    def __init__(self):
        self.run : bool = False
        self._ssl_connection :  socket.socket | None = None
        self.handle_message : "Callable[[str]]" | None = None
        self.set_led_mode : "Callable[[LED_MODES]]" | None = None
        
    def start(self) -> bool:
        self.run = True
        assert self.set_led_mode is not None
        assert self.handle_message is not None
        
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
        self.wlan.config(pm = 0x111022)
        #0x111022 - performance mode
        #0xa11140 - remove power saving mode
        #0xa11142 - default
        self.set_led_mode(LED_MODES.NETWORK_DISCONNECTED)
        self._connect_wifi()
        self.set_led_mode(LED_MODES.NETWORK_CONNECTED)
        return True
    
    def stop(self) -> None:
        self.run = False
        return None
    
    def _connect_wifi(self):
        with open('wifi_configs', 'r') as config_file:
            config_file_content = config_file.read()
        configs = json.loads(config_file_content)
        while self.run:
            self.wlan.scan()
            self.wlan.connect(configs["SSID"], configs["password"])
            if self.wlan.status() < 0 or self.wlan.status() >= 3:
                if self.wlan.status() != 3:
                    #network connection failed
                    #try again
                    time.sleep(NETWORKD.LONG_WAIT_TIME)
                else:
                    #connected
                    break

    def _network_is_connected(self) -> bool:
        if self.wlan.status() < 0 or self.wlan.status() >= 3:
            if self.wlan.status() != 3:
                #network connection failed
                #try again
                return False
            else:
                #connected
                try:
                    localIP = self.wlan.ifconfig()[0]
                    int(localIP.split(".")[-1])
                    return True
                except:
                    return False
        return False

    def _serve_forever(self) -> bool:
        #how does this work when network briefly disconnects?
        _socket = socket.socket()
        _socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        _socket.bind(socket.getaddrinfo(self.wlan.ifconfig()[0], 80)[0][-1])
        _socket.listen(1)
        while self.run:
            connection, _ = _socket.accept()
            request_file = connection.makefile('rwb', 0)
            request = []
            while self.run:
                line = request_file.readline().decode()
                request.append(line)
                if not line or not len(line) or line == '\r\n':
                    break
            response = self.handle_message(request)
            connection.send('HTTP/1.0 200 OK\r\nContent-type: ' + response["type"] + '\r\n\r\n')
            connection.send(response["content"])
            connection.close()

    def infinite_loop(self):
        self._serve_forever()