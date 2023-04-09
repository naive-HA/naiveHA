import json
import math
import time
from ir import IR
from custom_extensible_class import CUSTOM_EXTENSIBLE_CLASS

class SPECTOR(IR):
    def __init__(self, endpoint_id):
        CUSTOM_EXTENSIBLE_CLASS.__init__(self, endpoint_id)                
        IR.__init__(self)
        self.description = "Infrared remote control for heat panel Spector"
        with open("IR_signals", 'r') as raw_signals:
            self.signals = json.loads(raw_signals.read())
        self.attributes = {"Power"    : ["Off", "On"], \
                           "HeatLevel": [1, 2, 3, 4], \
                           "Fan"      : ["Off", "Temporary_Off", "On"], \
                           "Temp"     : [x for x in range(5, 38)]}
        self.state = {"Power"    : "Off", \
                      "HeatLevel": 4, \
                      "Fan"      : "Off", \
                      "Temp"     : 5}
        
    def _validate(self, attributes: dict[str, str] | list[str]) -> bool:
        if len(list(attributes)) in [0]:
            return True
        elif len(list(attributes)) in [4]:
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
            with open('spector.html', 'r') as html_file:
                html = html_file.read()
            start = html.find("<<SPECTOR_POWER_OPTIONS>>")
            end = html.find("<</SPECTOR_POWER_OPTIONS>>")
            html_options = html[start+len("<<SPECTOR_POWER_OPTIONS>>"):end]
            _html_options = ""
            for option in self.attributes["Power"]:
                _html_options += html_options\
                                        .replace("<<SPECTOR_POWER_OPTION>>", option)
            html = html[0:start] + _html_options + html[end+len("<</SPECTOR_POWER_OPTIONS>>"):]

            start = html.find("<<SPECTOR_HEAT_LEVEL_OPTIONS>>")
            end = html.find("<</SPECTOR_HEAT_LEVEL_OPTIONS>>")
            html_options = html[start+len("<<SPECTOR_HEAT_LEVEL_OPTIONS>>"):end]
            _html_options = ""
            for option in self.attributes["HeatLevel"]:
                _html_options += html_options\
                                 .replace("<<SPECTOR_HEAT_LEVEL_OPTION>>", str(option))\
                                 .replace("<<_SPECTOR_HEAT_LEVEL_OPTION>>", str(option) if option != 4 else "Off")
            html = html[0:start] + _html_options + html[end+len("<</SPECTOR_HEAT_LEVEL_OPTIONS>>"):]
            
            start = html.find("<<SPECTOR_FAN_OPTIONS>>")
            end = html.find("<</SPECTOR_FAN_OPTIONS>>")
            html_options = html[start+len("<<SPECTOR_FAN_OPTIONS>>"):end]
            _html_options = ""
            for option in self.attributes["Fan"]:
                if option == "Temporary_Off":
                    continue
                _html_options += html_options\
                                 .replace("<<SPECTOR_FAN_OPTION>>", str(option))
            html = html[0:start] + _html_options + html[end+len("<</SPECTOR_FAN_OPTIONS>>"):]
            
            start = html.find("<<SPECTOR_TEMP_OPTIONS>>")
            end = html.find("<</SPECTOR_TEMP_OPTIONS>>")
            html_options = html[start+len("<<SPECTOR_TEMP_OPTIONS>>"):end]
            _html_options = ""
            for option in self.attributes["Temp"]:
                if option == "Temporary_Off":
                    continue
                _html_options += html_options\
                                 .replace("<<SPECTOR_TEMP_OPTION>>", str(option))
            html = html[0:start] + _html_options + html[end+len("<</SPECTOR_TEMP_OPTIONS>>"):]
            return html
        elif ".css" in file_type:
            with open('spector.css', 'r') as css_file:
                css = css_file.read()
            return css
        elif ".js" in file_type:
            with open('spector.js', 'r') as js_file:
                js = js_file.read()
            return js\
                   .replace("<<POWER>>", str(self.state["Power"]))\
                   .replace("<<HEAT_LEVEL>>", str(self.state["HeatLevel"]))\
                   .replace("<<FAN>>", str(self.state["Fan"]))\
                   .replace("<<TEMP>>", str(self.state["Temp"]))\
                   .replace("<<ENDPOINT_ID>>", str(self.endpoint_id))
        else:
            return ""

    def get_attributes(self) -> dict[str, list[str | float]]:
        return self.attributes
    
    def set_value(self, attributes: dict[str, str | float]) -> bool | None:
        attributes["Temp"] = int(attributes["Temp"])
        attributes["HeatLevel"] = int(attributes["HeatLevel"])
        self._validate(attributes)

        if self.state["Power"] == "Off" and attributes["Power"] == "Off":
            return self.get_value(list(self.state))
        if self.state["Power"] == "On" and attributes["Power"] == "Off":
            self.broadcast(self.signals["Power"]["Off"])
            self.state = {"Power"    : "Off", \
                          "HeatLevel": 4, \
                          "Fan"      : "Off", \
                          "Temp"     : 5}
            return self.get_value(list(self.state))
        if self.state["Power"] != attributes["Power"]:
            self.state["Power"] = attributes["Power"]
            self.broadcast(self.signals["Power"][attributes["Power"]])

        heatLevel = attributes["HeatLevel"] + 4 - self.state["HeatLevel"]
        heatLevel += -4 * math.floor(heatLevel/4)
        for i in range(0, heatLevel):
            self.broadcast(self.signals["HeatLevel"]["Up"])
        if self.state["Fan"] == "On" and self.state["HeatLevel"] > attributes["HeatLevel"]:
                self.broadcast(self.signals["Fan"]["On"])
        self.state["HeatLevel"] = attributes["HeatLevel"]

        if self.state["Fan"] != attributes["Fan"]:
            self.broadcast(self.signals["Fan"][attributes["Fan"]])
            self.state["Fan"] = attributes["Fan"]

        TempUpOrDown = "Up" if self.state["Temp"] < attributes["Temp"] else "Down"
        for i in range(0, abs(self.state["Temp"] - attributes["Temp"])):
            self.broadcast(self.signals["Temp"][TempUpOrDown])
        self.state["Temp"] = attributes["Temp"]
        
        return self.get_value([])
    
    def get_value(self, attributes: list[str]) -> dict[str, str | float] | None:
        self._validate(attributes)
        return self.state
    
if __name__ == "__main__":
    signals = {"Power":
                {"Off"  : [9003, 3933, 547, 1638, 547, 547, 547, 547, 547, 547, 547, 547, 547, \
                           547, 547, 547, 547, 547, 547, 547, 547, 1638, 547, 547, 547, 1638, 547, \
                           547, 547, 1638, 547, 1638, 547, 1638, 547, 547, 547, 1638, 547, 547, \
                           547, 547, 547, 1638, 547, 547, 547, 547, 547, 547, 547, 1638, 547, 547, \
                           547, 1638, 547, 1638, 547, 547, 547, 1638, 547, 1638, 547, 1638, 547], \
                 "On"   : [9003, 3933, 547, 1638, 547, 547, 547, 547, 547, 547, 547, 547, 547, \
                           547, 547, 547, 547, 547, 547, 547, 547, 1638, 547, 547, 547, 1638, 547, \
                           547, 547, 1638, 547, 1638, 547, 1638, 547, 547, 547, 1638, 547, 547, \
                           547, 547, 547, 1638, 547, 547, 547, 547, 547, 547, 547, 1638, 547, 547, \
                           547, 1638, 547, 1638, 547, 547, 547, 1638, 547, 1638, 547, 1638, 547]}, \
                "Temp":
                {"Up"   : [9003, 3947, 547, 1629, 547, 547, 547, 547, 547, 547, 547, 547, 547, \
                           547, 547, 547, 547, 547, 547, 547, 547, 1629, 547, 547, 547, 1629, 547, \
                           547, 547, 1629, 547, 1629, 547, 1629, 547, 547, 547, 547, 547, 1629, \
                           547, 1629, 547, 1629, 547, 547, 547, 547, 547, 547, 547, 1629, 547, 1629, \
                           547, 547, 547, 547, 547, 547, 547, 1629, 547, 1629,  547, 1629, 547], \
                 "Down" : [9003, 3951, 548, 1629, 548, 548, 548, 548, 548, 548, 548, 548, 548, \
                           548, 548, 548, 548, 548, 548, 548, 548, 1629, 548, 548, 548, 1629, 548, \
                           548, 548, 1629, 548, 1629, 548, 1629, 548, 548, 548, 548, 548, 548, \
                           548, 1629, 548, 1629, 548, 548, 548, 548, 548, 548, 548, 1629, 548, 1629, \
                           548, 1629, 548, 548, 548, 548, 548, 1629, 548, 1629, 548, 1629, 548]}, \
                "Fan":
                {"Off"  : [9003, 3947, 545, 1626, 545, 545, 545, 545, 545, 545, 545, 545, 545, 545, 545, \
                           545, 545, 545, 545, 545, 545, 1626, 545, 545, 545, 1626, 545, 545, 545, \
                           1626, 545, 1626, 545, 1626, 545, 545, 545, 1626, 545, 1626, 545, 545, 545, \
                           1626, 545, 545, 545, 545, 545, 545, 545, 1626, 545, 545, 545, 545, 545, 1626, \
                           545, 545, 545, 1626, 545, 1626, 545, 1626, 545, 43349, 9003, 3947, 545], \
                 "On"   : [9003, 3947, 545, 1626, 545, 545, 545, 545, 545, 545, 545, 545, 545, 545, 545, \
                           545, 545, 545, 545, 545, 545, 1626, 545, 545, 545, 1626, 545, 545, 545, \
                           1626, 545, 1626, 545, 1626, 545, 545, 545, 1626, 545, 1626, 545, 545, 545, \
                           1626, 545, 545, 545, 545, 545, 545, 545, 1626, 545, 545, 545, 545, 545, 1626, \
                           545, 545, 545, 1626, 545, 1626, 545, 1626, 545, 43349, 9003, 3947, 545]}, \
                "HeatLevel":
                {"Up"    : [9003, 3947, 543, 1660, 543, 543, 543, 543, 543, 543, 543, 543, 543, 543, \
                            543, 543, 543, 543, 543, 543, 543, 1660, 543, 543, 543, 1660, 543, 543, 543, \
                            1660, 543, 1660, 543, 1660, 543, 543, 543, 543, 543, 1660, 543, 543, 543, \
                            1660, 543, 543, 543, 543, 543, 543, 543, 1660, 543, 1660, 543, 543, 543, \
                            1660, 543, 543, 543, 1660, 543, 1660, 543, 1660, 543]}}

    with open("IR_signals", 'w') as raw_signals:
        raw_signals.write(json.dumps(signals))