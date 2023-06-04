import json
import socket
import uasyncio as asyncio

class SERVERD():
    PORT = 80
    TIMEOUT = 20

    def __init__(self):
        self.run : bool = True
        self._ssl_connection :  socket.socket | None = None
        self.handle_message : "Callable[[str]]" | None = None
        
    async def start(self) -> bool:
        self.server = await asyncio.start_server(self.manage_request, '0.0.0.0', SERVERD.PORT, 100)
        return True
    
    async def manage_request(self, sreader, swriter) -> None:
        request : dict = []
        while True:
            try:
                res = await asyncio.wait_for(sreader.readline(), SERVERD.TIMEOUT)
                res = res.decode()
            except:
                return
            if not res or not len(res) or res == '\r\n':
                break
            request.append(res)
        payload = ""
        for line in request:
            if "GET " in line[0:4]:
                if "/?" in line:
                    # /?{"command": "get_value"; "endpoint_id": 0; "attributes": "[\"Temp\"]"}
                    #javascript changes " to %22
                    payload = line.split(" ")[1].split("?")[1].replace('%22', '"').replace('""', '\\"')
                    #payload already string
                elif len(line.split(" ")[1].split("/")[1]):
                    # /style.css
                    payload = json.dumps({"command": "html", \
                                          "endpoint_id": None, \
                                          "attributes": line.split(" ")[1].split("/")[1]})
                else:
                    # /
                    payload = json.dumps({"command"    : "html", \
                                          "endpoint_id": None, \
                                          "attributes" : "index.html"})
        if self.handle_message is not None and len(payload):
            response = self.handle_message(payload)
            try:
                swriter.write('HTTP/1.0 200 OK\r\nContent-type:' + response["type"] + '\r\n\r\n')
                swriter.write(response["content"])
                await swriter.drain()
            except:
                await sreader.close()
                return
        await sreader.wait_closed()

    async def stop(self) -> None:
        self.run = False
        try:
            self.server.close()
            await self.server.wait_closed()
        except:
            pass
        return None
    
    def network_status(self, status) -> None:
        self._network_status = status

    async def infinite_loop(self) -> None:
        asyncio.create_task(self.start())