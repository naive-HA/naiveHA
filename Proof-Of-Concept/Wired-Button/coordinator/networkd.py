import ssl
import time
import json
import struct
import socket
import subprocess
from typing import Callable
from const import _LED_MODES
from threading import Thread

LED_MODES = _LED_MODES()

class NETWORKD():
    WAIT_TIME = 60
    SHORT_WAIT_TIME = 5
    PORT = 65432

    SERVER_PUBLIC_CERTIFICATE = "server_public_certificate.crt"
    SERVER_PRIVATE_KEY = 'server_private_key.key'
    NODE_PUBLIC_CERTIFICATE = 'node_public_certificate.crt'

    def __init__(self):
        self.run : bool = False
        self._accepting_connection : bool = False
        self._connections :  dict[int, socket.socket] = {}
        self.set_led_mode : "Callable[[LED_MODES]]" | None = None
        self.packet_received : "Callable[[int], [str]]" | None = None
        self._listening_for_messages_threads :  dict[int, Thread] = {}

    def start(self) -> bool:
        self.run = True
        assert self.set_led_mode is not None
        assert self.packet_received is not None
        self.set_led_mode(LED_MODES.NETWORK_DISCONNECTED)
        return True

    def stop(self) -> None:
        self.run = False
        for node in list(self._connections):
            self.disconnect_node(node)
        return None

    def _network_is_connected(self) -> bool:
        while self.run:
            try:
                lanIP = subprocess.Popen(['hostname', '-I'], stdout=subprocess.PIPE).communicate()[0]
                localIP = str(lanIP).split("'")[1].split(" ")[0]
                localIP = localIP.split(".")
                hostID = localIP[len(localIP) - 1]
                int(hostID)
                self.set_led_mode(LED_MODES.NETWORK_CONNECTED)
                #coordinator does not need Internet connection
                #check whether existing connections are still valid. otherwise drop them
                return True
            except:
                self.set_led_mode(LED_MODES.NETWORK_DISCONNECTED)
                #as per experience, the network can briefly fail and then recover without the disconnecting clients
                #allow sufficient time to recover brief network failures
                time.sleep(NETWORKD.SHORT_WAIT_TIME)
        return False

    def accept_node_connection(self, timeout: int) -> bool:
        self._accepting_connection = True
        #make sure the network is connected
        assert self._network_is_connected() == True
        
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.verify_mode = ssl.CERT_REQUIRED
        context.load_cert_chain(certfile=NETWORKD.SERVER_PUBLIC_CERTIFICATE, keyfile=NETWORKD.SERVER_PRIVATE_KEY)
        context.load_verify_locations(cafile=NETWORKD.NODE_PUBLIC_CERTIFICATE)
        while self.run and self._accepting_connection:
            try:
                server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                server.bind(("", NETWORKD.PORT))
            except:
                self.run = False
                return False
            try:
                #if the connection times out: start again from the top
                #server.listen(5)
                server.listen()
                self.set_led_mode(LED_MODES.ACCEPTING_CONNECTIONS)

                #accept function is blocking: waits until a connection is established
                connection, address = server.accept()
                ssl_connection = context.wrap_socket(connection, server_side=True)
                ssl_connection.settimeout(timeout)
                self.set_led_mode(LED_MODES.STOPPED_ACCEPTING)
                print("node connected successfully " + str(address))
                #flag used to quickly exit the function, when new connections are not expected anymore
                if not self._accepting_connection:
                    connection.close()
                    return True
                else:
                    self._accepting_connection = False
                ssl_connection.settimeout(None)
                #request unique_id
                #save the connection for later use in Receive and Send
                self._connections[0] = ssl_connection
                #start a thread to listening on incoming messages: _receive is blocking execution
                node = 0
                self._listening_for_messages_threads[node] = Thread(target=self._receive, args=(node,))
                self._listening_for_messages_threads[node].daemon = True
                self._listening_for_messages_threads[node].start()
                return True
            except:
                pass
            #empty the socket buffer
            try:
                ssl_connection.settimeout(timeout).setblocking(0)
                #read and discard until there is nothing left
                while ssl_connection.settimeout(timeout).recv(1024): pass
                ssl_connection.settimeout(timeout).close()
            except:
                pass

    def stop_accepting_node_connection(self) -> bool:
        if self._accepting_connection:
            #accept() in self.accept_node_connection is blocking. to unblock, make a dummy connection to the socket
            self._accepting_connection = False
            try:
                socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("127.0.0.1", NETWORKD.PORT))
            except:
                pass
            return True
        else: 
            return False

    def disconnect_node(self, node) -> bool:
        try:
            self._connections[node].close()
        except:
            pass
        if node in list(self._connections):
            self._connections.pop(node)
            return True
        else: 
            return False

    def _receive(self, node: int) -> None:
        while True:
            try:
                raw_msglen = self._connections[node].read(4)
                if not raw_msglen:
                    raise Exception("Error: message length")
            except:
                #disconnect node
                return None
            msglen = struct.unpack('>I', raw_msglen)[0]
            data = bytearray()
            while len(data) < msglen:
                try:
                    buffer = self._connections[node].read(msglen - len(data))
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

    def send_packet(self, node: int, data: str) -> bool:
        try:
            data = struct.pack('>I', len(data)) + data.encode()
            self._connections[node].write(data)
            return True
        except:
            #disconnect node
            return False




