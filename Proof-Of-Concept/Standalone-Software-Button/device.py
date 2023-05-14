import time
import json
from arlec import ARLEC
import uasyncio as asyncio
from spector import SPECTOR
from const import _LED_MODES
from temp_sensor import TEMP_SENSOR
from temp_control import TEMP_CONTROL
from custom_extensible_class import CUSTOM_EXTENSIBLE_CLASS

LED_MODES = _LED_MODES()

class DEVICE():
    SLEEP_TIME = 60
    def __init__(self, list_of_custom_classes: list[str]):
        self.run = True
        self.unique_id = '00:00:00:00:00:00'
        self.endpoints : list = list()
        self.endpoint_attributes : dict = dict()
        for custom_class in list_of_custom_classes:
            endpoint_id = len(self.endpoints)
            if custom_class == "temp_sensor":
                self.endpoints.append(TEMP_SENSOR(endpoint_id))
            elif custom_class == "temp_control":
                self.endpoints.append(TEMP_CONTROL(endpoint_id))
            elif custom_class == "spector":
                self.endpoints.append(SPECTOR(endpoint_id))
            elif custom_class == "arlec":
                self.endpoints.append(ARLEC(endpoint_id))
            else:
                raise Exception("Unknown custom class")
            self.endpoint_attributes[endpoint_id] = self._deep_copy(self.endpoints[endpoint_id].get_attributes())
            for attribute in self.endpoint_attributes[endpoint_id]:
                str_values = []
                for value in self.endpoint_attributes[endpoint_id][attribute]:
                    str_values.append(str(value))
                self.endpoint_attributes[endpoint_id][attribute] = str_values
        self.send_packet = None
        self.set_led_mode : "Callable[[LED_MODES]]" | None = None
        
    def _deep_copy(self, old_array):
        new_array = dict()
        for key in list(old_array):
            new_array[key] = old_array[key]
        return new_array

    def handle_message(self, packet: dict):
        self.set_led_mode(LED_MODES.EXECUTING_COMMAND)
        if packet["command"] == "get_profile":
            profile : dict = {"unique_id": self.unique_id}
            for endpoint_id in range(len(self.endpoints)):
                profile[endpoint_id] = {"description"  : self.endpoints[endpoint_id].get_description(),
                                        "attributes"   : self.endpoints[endpoint_id].get_attributes()}
            send_back = {"type"   : "text/html", \
                         "content": json.dumps({"command": "profile", \
                                                "endpoint_id": None, \
                                                "attributes": profile})}
        elif packet["command"] == "html":
            if ".css" in packet["attributes"]:
                with open('index.css') as css_file:
                    css = css_file.read()
                for endpoint_id in range(len(self.endpoints)):
                    css += self.endpoints[endpoint_id].get_html(packet["attributes"])
                send_back = {"type"   : "text/css", \
                             "content": css}
            elif ".js" in packet["attributes"]:
                javascript = ""
                for endpoint_id in range(len(self.endpoints)):
                    javascript += self.endpoints[endpoint_id].get_html(packet["attributes"])
                send_back = {"type"   : "text/javascript", \
                             "content": javascript}
            else:
                device_html = ""
                for endpoint_id in range(len(self.endpoints)):
                    device_html += self.endpoints[endpoint_id].get_html("index.html")
                with open('index.html') as html_file:
                    html = html_file.read().replace("<<DEVICE_SPECIFIC_HTML>>", device_html)
                send_back = {"type"   : "text/html", \
                             "content": html}
        elif packet["command"] == "set_value":
            try:
                endpoint_id = int(packet["endpoint_id"])
                attributes = json.loads(packet["attributes"])
                if self._validate(attributes, self.endpoint_attributes[endpoint_id]):
                    state = self.endpoints[endpoint_id].set_value(attributes)
                else:
                    state = {"Error": "Invalid attributes"}
            except Exception as e:
                state = {"Error": e}
            send_back = {"type": "text/html", \
                         "content": json.dumps({"command"    : "state", \
                                                "endpoint_id": endpoint_id, \
                                                "attributes" : state})}
        elif packet["command"] == "get_value":
            try:
                endpoint_id = int(packet["endpoint_id"])
                attributes = json.loads(packet["attributes"])
                if self._validate(attributes, self.endpoint_attributes[endpoint_id]):
                    state = self.endpoints[endpoint_id].get_value(attributes)
                else:
                    state = {"Error": "Invalid attributes"}
            except Exception as e:
                state = {"Error": e}
            send_back = {"type": "text/html", \
                         "content": json.dumps({"command"    : "state", \
                                                "endpoint_id": endpoint_id, \
                                                "attributes" : state})}
        else:
            send_back = {"type"  : "text/html", \
                         "content": json.dumps({"command"    : "error", \
                                                "endpoint_id": int(packet["endpoint_id"]), \
                                                "error"      : "unknown command"})}
        self.set_led_mode(LED_MODES.STOPPED_EXECUTING_COMMAND)
        return send_back
    
    def _validate(self, attributes: dict[str, str] | list[str], endpoint_attributes: dict[str, str] | list[str]) -> bool:
        if len(list(attributes)) in [0]:
            pass
        elif len(list(attributes)) == len(list(endpoint_attributes)):
            pass
        else:
            return False #Incorrect number of attributes

        for attribute in list(attributes):
            found_it = False
            for _attribute in list(endpoint_attributes):
                if _attribute == attribute:
                    found_it = True
                    break
            if not found_it:
                return False #Attribute does not exist
        
        if isinstance(attributes, dict):
            for attribute in list(attributes):
                if attributes[attribute] not in endpoint_attributes[attribute]:
                    return False #Incorrect attribute value
        return True
    
    async def infinite_loop(self):
        assert self.set_led_mode is not None
        for endpoint_id in range(len(self.endpoints)):
            asyncio.create_task(self.endpoints[endpoint_id].infinite_loop())