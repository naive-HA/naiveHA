import time
import json
import uasyncio
from arlec import ARLEC
from spector import SPECTOR
from const import _LED_MODES
from temp_sensor import TEMP_SENSOR
from custom_extensible_class import CUSTOM_EXTENSIBLE_CLASS

LED_MODES = _LED_MODES()

class DEVICE():
    def __init__(self, list_of_custom_classes: list[str]):
        self.run = True
        self.reporting_interval = 60 #seconds, adjustable
        self.endpoints : list = []
        for custom_class in list_of_custom_classes:
            if custom_class == "temp_sensor":
                self.endpoints.append(TEMP_SENSOR(len(self.endpoints)))
            elif custom_class == "spector":
                self.endpoints.append(SPECTOR(len(self.endpoints)))
            elif custom_class == "arlec":
                self.endpoints.append(ARLEC(len(self.endpoints)))
            else:
                raise Exception("Unknown custom class")
        self.send_packet = None
        self.set_led_mode : "Callable[[LED_MODES]]" | None = None
        
    def get_html(self, request: str):
        payload = [""]
        for line in request:
            if "GET " in line[0:4]:
                payload = line.split(" ")[1].split("/")[1]
                if len(payload):
                    if "?" in payload:
                        try:
                            packet = json.loads(payload.split("?")[1]\
                                                .replace("%22", '"')\
                                                .replace('""', '\\"'))
                            if isinstance(packet["attributes"], str):
                                packet["attributes"] = json.loads(packet["attributes"])
                            packet["endpoint_id"] = int(packet["endpoint_id"])
                            return {"type": "text/html",\
                                    "content": json.dumps(self.handle_command(packet))}
                        except:
                            pass
                break
        if ".css" in payload:
            with open('style.css') as css_file:
                css = css_file.read()
            for _id in range(len(self.endpoints)):
                css += self.endpoints[_id].get_html(payload)
            return {"type": "text/css",\
                    "content": css}
        elif ".js" in payload:
            js = ""
            for _id in range(len(self.endpoints)):
                js += self.endpoints[_id].get_html(payload)
            return {"type": "text/javascript",\
                    "content": js}
        else:
            with open('index-top.html') as html_file:
                html = html_file.read()
            for _id in range(len(self.endpoints)):
                html += self.endpoints[_id].get_html("index.html")
            with open('index-bottom.html') as html_file:
                html += html_file.read()
            return {"type": "text/html",\
                    "content": html}

    def handle_command(self, packet: dict):
        self.set_led_mode(LED_MODES.EXECUTING_COMMAND)
        if packet["command"] == "get_profile":
            profile : dict = {"unique_id": "some random alpha-numeric sequence"}
            for _id in range(len(self.endpoints)):
                profile[_id] = {"description"  : self.endpoints[_id].get_description(),\
                               "endpoint_type": self.endpoints[_id].get_type(),
                               "attributes"   : self.endpoints[_id].get_attributes()}
            send_back = {"command": "profile",\
                         "endpoint_id": None,\
                         "attributes": profile}
        elif packet["command"] == "set_value":
            try:
                state = self.endpoints[packet["endpoint_id"]].set_value(packet["attributes"])
            except Exception as e:
                state = {"Error": e}
            send_back = {"command": "state",\
                         "endpoint_id": packet["endpoint_id"],\
                         "attributes": state}
        elif packet["command"] == "get_value":
            try:
                state = self.endpoints[packet["endpoint_id"]].get_value(packet["attributes"])
            except Exception as e:
                state = {"Error": e}
            send_back = {"command": "state",\
                         "endpoint_id": packet["endpoint_id"],\
                         "attributes": state}
        #adjust reporting interval
        else:
            send_back = {"command": "error",\
                         "endpoint_id": packet["endpoint_id"],\
                         "error": "unknown command"}
        self.set_led_mode(LED_MODES.STOPPED_EXECUTING_COMMAND)
        return send_back
        
    async def report_state(self, endpoint_id):
        while self.run:
            self.send_packet(("state", endpoint_id, self.endpoints[endpoint_id].get_value([])))
            await uasyncio.sleep(self.reporting_interval)
        
    async def infinite_loop(self):
        assert self.set_led_mode is not None
        for endpoint_id in range(len(self.endpoints)):
            uasyncio.create_task(self.report_state(endpoint_id))