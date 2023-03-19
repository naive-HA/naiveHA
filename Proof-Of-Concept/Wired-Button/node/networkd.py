import ssl
import json
import time
import struct
import socket
import network
from const import _LED_MODES

LED_MODES = _LED_MODES()

class NETWORKD():
    PORT = 65432
    WAIT_TIME = 5
    MAX_CONCURENT_ATTEMPTS = 50

    SERVER_SNI_HOSTNAME = 'naive.coordinator'
    CA_PUBLIC_CERTIFICATE = "CA_public_certificate.der"
    NODE_PRIVATE_KEY = 'node_private_key.der'
    NODE_PUBLIC_CERTIFICATE = 'node_public_certificate.der'
    
    def __init__(self):
        self.run : bool = False
        self._connecting = False
        self._connection :  socket.socket | None = None
        self.set_led_mode : "Callable[[LED_MODES]]" | None = None
        self.packet_received : "Callable[[str]]" | None = None
        self._listening_for_messages_thread :  Thread | None = None
        
    def start(self) -> bool:
        self.run = True
        assert self.set_led_mode is not None
        assert self.packet_received is not None
        self.set_led_mode(LED_MODES.NETWORK_DISCONNECTED)
        
        with open('/configs', 'r') as config_file:
            config_file_content = config_file.read()
        configs = json.loads(config_file_content)
        #network.hostname("test")
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
        self.wlan.config(pm = 0xa11140)
        while True:
            self.wlan.scan()
            self.wlan.connect(configs["SSID"], configs["password"])
            if self.wlan.status() < 0 or self.wlan.status() >= 3:
                if self.wlan.status() != 3:
                    #network connection failed
                    #try again
                    time.sleep(NETWORKD.WAIT_TIME)
                else:
                    #connected
                    self.set_led_mode(LED_MODES.NETWORK_CONNECTED)
                    break
        return True
    
    def stop(self) -> None:
        self.run = False
        self.disconnect()
        return None
    
    def _network_is_connected(self) -> bool:
        while self.run:
            try:
                localIP = self.wlan.ifconfig()[0]
                localIP = localIP.split(".")
                hostID = localIP[len(localIP) - 1]
                int(hostID)
                self.set_led_mode(LED_MODES.NETWORK_CONNECTED)
                #coordinator does not need Internet connection 
                return True
            except:
                self.set_led_mode(LED_MODES.NETWORK_DISCONNECTED)
                #as per experience, the network can briefly fail and then recover without the disconnecting clients
                #allow sufficient time to recover brief network failures
                time.sleep(NETWORKD.WAIT_TIME)
        return False
        
    def connect(self) -> bool:
        #make sure the network is connected
        assert self._network_is_connected() == True
        local_IP = self.wlan.ifconfig()[0]
        local_IP = local_IP.split(".")
        host_ID = local_IP[-1]
        range_of_IPs = []
        for i in range(256):
            if i == int(host_ID):
                continue
            local_IP[-1] = str(i)
            range_of_IPs.append(".". join(local_IP))
        
        self._connecting = True
        while not self._connect_to_coordinator("192.168.8.149"):
            time.sleep(NETWORKD.WAIT_TIME)
            continue
        return True
    
    def _connect_to_coordinator(self, ip) ->bool:
        try:
            with open(NETWORKD.NODE_PUBLIC_CERTIFICATE, 'rb') as node_public_certificate:
                node_public_certificate_data = node_public_certificate.read()
            with open(NETWORKD.NODE_PRIVATE_KEY, 'rb') as node_private_key:
                node_private_key_data = node_private_key.read()
            with open(NETWORKD.CA_PUBLIC_CERTIFICATE, 'rb') as CA_public_certificate:
                CA_public_certificate_data = CA_public_certificate.read()
            self.set_led_mode(LED_MODES.CONNECTING)
            
            connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            connection.connect(socket.getaddrinfo(ip, NETWORKD.PORT, 0, socket.SOCK_STREAM)[0][-1])
            #connection.settimeout(10)
            ssl_connection = ssl.wrap_socket(connection, \
                                             server_side = False, \
                                             key = node_private_key_data, \
                                             cert = node_public_certificate_data, \
                                             cadata = CA_public_certificate_data, \
                                             cert_reqs = ssl.CERT_REQUIRED, \
                                             server_hostname = NETWORKD.SERVER_SNI_HOSTNAME, \
                                             do_handshake = True)
            self.set_led_mode(LED_MODES.STOPPED_CONNECTING)
            if self._connecting:
                self._connecting = False
                connection.settimeout(None)
                self._connection = ssl_connection
#                 #start a thread to listening on incoming messages: _receive is blocking execution
#                 self._listening_for_messages_thread = Thread(target=self._receive)
#                 self._listening_for_messages_thread.daemon = True
#                 self._listening_for_messages_thread.start()
                return True
        except:
            pass
        #empty the socket buffer
        try:
            ssl_connection.setblocking(0)
            #read and discard until there is nothing left
            while ssl_connection.recv(1024): pass
            ssl_connection.close()           
            return False
        except:
            return False

    def disconnect(self) -> bool:
        if self._connection is not None:
            try:
                self._connection.close()
            except:
                pass
            self._connection = None
            return True
        else:
            return False

    def _receive(self) -> None:
        while True:
            try:
                raw_msglen = self._connection.read(4)
                if not raw_msglen:
                    raise Exception("Error: message length")
            except:
                #disconnect node
                return None
            msglen = struct.unpack('>I', raw_msglen)[0]
            data = bytearray()
            while len(data) < msglen:
                try:
                    buffer = self._connection.read(msglen - len(data))
                    if not buffer:
                        raise Exception("Error: message length")
                except:
                    #disconnect node
                    return None
                data.extend(buffer)
            message = data.decode()
            try:
                message = json.loads(message)
            except:
                pass
            #check CRC8 dict_data["crc8"]
            self.packet_received(message)

    def send_packet(self, data: str) -> bool:
        try:
            data = struct.pack('>I', len(data)) + data.encode()
            self._connection.write(data)
            return True
        except:
            #disconnect node
            return False        
        
        
        

