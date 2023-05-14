from aht20 import AHT20
import uasyncio as asyncio
from custom_extensible_class import CUSTOM_EXTENSIBLE_CLASS

class TEMP_SENSOR(CUSTOM_EXTENSIBLE_CLASS, AHT20):
    def __init__(self, endpoint_id):
        CUSTOM_EXTENSIBLE_CLASS.__init__(self, endpoint_id)
        AHT20.__init__(self)
        self.run = True
        self.description = "AHT20 temperature sensor"
        self.attributes = {"Temp": [x/2 for x in range(10, 101)]}
        self.state = {"Temp": round(self.get("Temp"))}

    def get_description(self) -> str:
        return self.description
    
    def get_html(self, file_type: str) -> str:
        if ".html" in file_type:
            with open('temp_sensor.html', 'r') as html_file:
                html = html_file.read()
            temp = self.get_value([])
            return html.replace("<<TEMP>>", str(temp["Temp"]))
        elif ".js" in file_type:
            with open('temp_sensor.js', 'r') as js_file:
                js = js_file.read()
            return js.replace("<<ENDPOINT_ID>>", str(self.endpoint_id))
        elif ".css" in file_type:
            with open('temp_sensor.css', 'r') as css_file:
                css = css_file.read()
            return css
        else:
            return ""

    def get_attributes(self) -> dict[str, list[str | float]]:
        return self.attributes
    
    def set_value(self, values: dict[str, str]) -> bool | None:
        raise Exception("Attribute cannot be set")
    
    def get_value(self, values: list[str]) -> dict[str, str | float] | None:
        for attribute in list(self.state):
            xx = self.get(attribute)
            self.state[attribute] = min(self.attributes[attribute], key = lambda x:abs(x-xx))
        return self.state
    
    def stop(self):
        self.run = False

    async def infinite_loop(self):
        return