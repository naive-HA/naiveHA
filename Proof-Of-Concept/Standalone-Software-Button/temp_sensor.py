from aht20 import AHT20
from custom_extensible_class import CUSTOM_EXTENSIBLE_CLASS

class TEMP_SENSOR(CUSTOM_EXTENSIBLE_CLASS, AHT20):
    def __init__(self, endpoint_id):
        CUSTOM_EXTENSIBLE_CLASS.__init__(self, endpoint_id)        
        AHT20.__init__(self)
        self.run = False
        self.description = "AHT20 temperature sensor"
        self.attributes = {"Temp": [x/2 for x in range(10, 101)]}
        self.state = {"Temp": round(self.get("Temp"))}
        
    def _validate(self, attributes: dict[str, str] | list[str]) -> bool:
        if len(attributes) in [0]:
            return type(None)
        elif len(attributes) in [1]:
            pass
        else:
            raise Exception("Incorrect number of attributes")

        for attribute in list(attributes):
            found_it = False
            for _attribute in list(self.attributes):
                if _attribute == attribute:
                    found_it = True
                    break
            if not found_it:
                raise Exception("Attribute does not exist")
        
        if isinstance(attributes, dict):
            for attribute in list(attributes):
                if attributes[attribute] not in self.attributes[attribute]:
                    raise Exception("Incorrect attribute value")                
        return True

    def get_description(self) -> str:
        return self.description
    
    def get_html(self, file_type) -> str:
        if "html" in file_type:
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
    
    def set_value(self, attributes: dict[str, str | float]) -> bool | None:
        raise Exception("Attribute cannot be set")
    
    def get_value(self, attributes: list[str]) -> dict[str, str | float] | None:
        self._validate(attributes)
        for attribute in self.state:
            xx = self.get(attribute)
            self.state[attribute] = min(self.attributes[attribute], key = lambda x:abs(x-xx))
        return self.state