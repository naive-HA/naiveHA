import time
import socket
import ustruct
import uselect
import uctypes
import uasyncio as asyncio

class ICMP_ECHO_REQUEST():
    TIMEOUT = 1000
    MAX_TRIES = 300
    SLEEP_TIME = 10
    PACKET_SIZE = 32
    def __init__(self, host):
        self.host = host
        # prepare packet
        self.packet = b'Q'*ICMP_ECHO_REQUEST.PACKET_SIZE
        self.packet_description = {
            "type": uctypes.UINT8 | 0,
            "code": uctypes.UINT8 | 1,
            "checksum": uctypes.UINT16 | 2,
            "id": uctypes.UINT16 | 4,
            "sequence": uctypes.INT16 | 6,
            "timestamp": uctypes.UINT64 | 8,
        } # packet header descriptor
        self.header = uctypes.struct(uctypes.addressof(self.packet), self.packet_description, uctypes.BIG_ENDIAN)
        self.header.type = 8 # ICMP_ECHO_REQUEST
        self.header.code = 0
        self.header.checksum = 0
        self.header.id = 1
        self.header.sequence = 1
        self.header.timestamp = time.ticks_us()
        self.header.checksum = self.checksum(self.packet)        

    async def send_ping(self):
        _socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, 1)
        _socket.settimeout(ICMP_ECHO_REQUEST.TIMEOUT)
        _socket.connect((socket.getaddrinfo(self.host, 1)[0][-1][0], 1))
        
        counter = 0
        while counter <= ICMP_ECHO_REQUEST.MAX_TRIES:
            await asyncio.sleep_ms(1)
            counter += 1
            self.header.checksum = 0
            self.header.id = int(time.time())
            self.header.sequence = counter
            self.header.timestamp = time.ticks_us()
            self.header.checksum = self.checksum(self.packet)
            try:
                _socket.send(self.packet)
            except:
                _socket.close()
                return False
            while True:
                sockets, _, _ = uselect.select([_socket], [], [], 0)
                if sockets:
                    try:
                        response = sockets[0].recv(4096)
                    except:
                        continue
                    response_mv = memoryview(response)
                    header = uctypes.struct(uctypes.addressof(response_mv[20:]), self.packet_description, uctypes.BIG_ENDIAN)
                    if header.type == 0 and header.id == self.header.id:
                        _socket.close()
                        #print(header.id)
                        return True
                else:
                    break
        return False
    
    def checksum(self, data):
        if len(data) & 0x1: # Odd number of bytes
            data += b'\0'
        cs = 0
        for pos in range(0, len(data), 2):
            b1 = data[pos]
            b2 = data[pos + 1]
            cs += (b1 << 8) + b2
        while cs >= 0x10000:
            cs = (cs & 0xffff) + (cs >> 16)
        cs = ~cs & 0xffff
        return cs
    
    async def ping(self) -> None:
        asyncio.create_task(self.send_ping())

if __name__ == "__main__":
    import time
    import json
    import network
    from machine import Pin, Timer

    timer = Timer()
    led = Pin("LED", Pin.OUT)
    led.off()
    timer.init(freq=25, mode=Timer.PERIODIC, callback = lambda timer: led.toggle())

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.config(pm = 0x111022)
    with open('wifi_configs', 'r') as config_file:
        config_file_content = config_file.read()
    configs = json.loads(config_file_content)
    while True:
        wlan.scan()
        wlan.connect(configs["SSID"], configs["password"])
        if wlan.status() < 0 or wlan.status() >= 3:
            if wlan.status() != 3:
                #network connection failed
                #try again
                time.sleep(1)
            else:
                #connected
                break
    timer.deinit()
    led.off()
    ip, mask, gateway, dns = wlan.ifconfig()
    ping = ICMP_ECHO_REQUEST(gateway)
    
    async def send_pings():
        await ping.ping()
    
    async def main_loop():
        asyncio.create_task(send_pings())
        await asyncio.sleep(2)
    
    for _ in range(5):
        asyncio.run(main_loop())
