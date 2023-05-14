import uasyncio as asyncio
from spector import SPECTOR
from temp_sensor import TEMP_SENSOR
from custom_extensible_class import CUSTOM_EXTENSIBLE_CLASS

class TEMP_CONTROL(CUSTOM_EXTENSIBLE_CLASS):
    WAIT_TIME = 30
    def __init__(self, endpoint_id):
        CUSTOM_EXTENSIBLE_CLASS.__init__(self, endpoint_id)
        self.run = True
        self.description = "Temperature control with AHT20 and Spector"
        self.endpoint_id = endpoint_id
        self.sensor = TEMP_SENSOR(0)
        self.heater = SPECTOR(1)
        self.attributes : dict[str, list[str | float]] = {"Controller"  : ["Off", "On"], \
                                                          "Heater"      : ["Stand-by", "On"], \
                                                          "Fan"         : ["Off", "Stand-by", "On"], \
                                                          "Target_temp" : [x for x in range(15, 31)], \
                                                          "Room_temp"   : [x/2 for x in range(10, 77)], \
                                                          "Control_band": [1, 1.5, 2]}
        self.state : dict[str, str | float] = {"Controller"  : self.attributes["Controller"][0], \
                                               "Heater"      : self.attributes["Heater"][0], \
                                               "Fan"         : self.attributes["Fan"][0], \
                                               "Target_temp" : self.attributes["Target_temp"][0], \
                                               "Room_temp"   : self.sensor.get_value(["Temp"])["Temp"], \
                                               "Control_band": self.attributes["Control_band"][1]}
        self.heater_state = {"Power"    : "On", \
                             "HeatLevel": 1, \
                             "Fan"      : "Off", \
                             "Temp"     : 37}
        self.heater.set_value(self.heater_state)
        self.heater_state["HeatLevel"] = 4
        self.heater.set_value(self.heater_state)

    def get_description(self) -> str:
        return self.description
    
    def get_html(self, file_type: str) -> str:
        if ".html" in file_type:
            self.state["Room_temp"] = self.sensor.get_value(["Temp"])["Temp"]
            with open('temp_control.html', 'r') as html_file:
                html = html_file.read()
            html = html.replace("<<ROOM_TEMPERATURE>>", str(self.state["Room_temp"])) \
                       .replace("<<TARGET_TEMPERATURE>>", str(self.state["Target_temp"])) \
                       .replace("<<FAN_STATUS>>", str(self.state["Fan"])) \
                       .replace("<<HEATER_STATUS>>", str(self.state["Heater"]))
            start = html.find("<<TEMPERATURE_TARGET_OPTIONS>>")
            end = html.find("<</TEMPERATURE_TARGET_OPTIONS>>")
            html_options = html[start+len("<<TEMPERATURE_TARGET_OPTIONS>>"):end]
            _html_options = ""
            for option in self.attributes["Target_temp"]:
                _html_options += html_options\
                                 .replace("<<TEMPERATURE_TARGET_OPTION>>", str(option))
            html = html[0:start] + _html_options + html[end+len("<</TEMPERATURE_TARGET_OPTIONS>>"):]
            
            start = html.find("<<CONTROL_BAND_OPTIONS>>")
            end = html.find("<</CONTROL_BAND_OPTIONS>>")
            html_options = html[start+len("<<CONTROL_BAND_OPTIONS>>"):end]
            _html_options = ""
            for option in self.attributes["Control_band"]:
                _html_options += html_options\
                                 .replace("<<2xCONTROL_BAND_OPTION>>", str(int(2*option)))\
                                 .replace("<<CONTROL_BAND_OPTION>>", str(option))
            html = html[0:start] + _html_options + html[end+len("<</CONTROL_BAND_OPTIONS>>"):]
            return html
        elif ".js" in file_type:
            with open('temp_control.js', 'r') as js_file:
                js = js_file.read()
            return js.replace("<<ENDPOINT_ID>>", str(self.endpoint_id)) \
                     .replace("<<CONTROLLER_STATUS>>", str(self.state["Controller"])) \
                     .replace("<<HEATER_STATUS>>", str(self.state["Heater"])) \
                     .replace("<<FAN_STATUS>>", str(self.state["Fan"])) \
                     .replace("<<TARGET_TEMP>>", str(self.state["Target_temp"])) \
                     .replace("<<ROOM_TEMP>>", str(self.state["Room_temp"])) \
                     .replace("<<CONTROL_BAND>>", str(self.state["Control_band"]))
        elif ".css" in file_type:
            with open('temp_control.css', 'r') as css_file:
                css = css_file.read()
            return css
        else:
            return ""

    def get_attributes(self) -> dict[str, list[str | float]]:
        return self.attributes

    def set_value(self, values: dict[str, str]) -> bool | None:
        #read room temperature
        self.state["Room_temp"] = self.sensor.get_value(["Temp"])["Temp"]
        self.state["Target_temp"] = int(values["Target_temp"])
        #set new control band
        xx = float(values["Control_band"])
        self.state["Control_band"] = min(self.attributes["Control_band"], key = lambda x:abs(x-xx))
        #set Fan state
        self.state["Fan"] = values["Fan"]
        self.heater_state["Fan"] = self.state["Fan"]
        #set Controllet state
        self.state["Controller"] = values["Controller"]
        if self.state["Controller"] == "Off":
            self.state["Heater"] = self.attributes["Heater"][0] #Stand-by
            self.heater_state["HeatLevel"] = 4 #Stand-by
            if self.state["Fan"] == self.attributes["Fan"][2]:
                #if Fan state is ON, set to Stand-by
                self.state["Fan"] = self.attributes["Fan"][1] #Stand-by
                self.heater_state["Fan"] = self.attributes["Fan"][0] #Off, actually
            self.heater.set_value(self.heater_state)
            return self.state
        #if Controller is ON
        #if Heater is in Stand-by, Fan state can only be in Stand-by or OFF, not ON
        if self.heater_state["HeatLevel"] == 4:
            #set Fan state
            if self.state["Fan"] == self.attributes["Fan"][2]:
                self.state["Fan"] = self.attributes["Fan"][1] #Stand-by
            self.heater_state["Fan"] = self.attributes["Fan"][0] #Off, actually
        #if Heater is in ON, Fan state can only be ON or OFF, not Stand-by
        if self.heater_state["HeatLevel"] != 4 and self.state["Fan"] == self.attributes["Fan"][1]:
            #set Fan state
            self.state["Fan"] = self.attributes["Fan"][2] #On
            self.heater_state["Fan"] = self.attributes["Fan"][2] #On
        self._heater_control()
        return self.state

    def get_value(self, attributes: list[str]) -> dict[str, str | float] | None:
        self.state["Room_temp"] = self.sensor.get_value(["Temp"])["Temp"]
        return self.state
        
    def stop(self):
        self.run = False
        
    def _heater_control(self):
        if self.state["Room_temp"] <= self.state["Target_temp"] - self.state["Control_band"]:
            self.state["Heater"] = self.attributes["Heater"][1] #On
            self.heater_state["HeatLevel"] = 3 #On
            if self.state["Fan"] == self.attributes["Fan"][1]:
                #if Fan is in Stand-by switch to ON
                self.state["Fan"] = self.attributes["Fan"][2] #On
                self.heater_state["Fan"] = self.attributes["Fan"][2] #On
            self.heater.set_value(self.heater_state)
        elif self.state["Room_temp"] >= self.state["Target_temp"] + self.state["Control_band"]:
            self.state["Heater"] = self.attributes["Heater"][0] #Stand-by
            self.heater_state["HeatLevel"] = 4 #Stand-by
            if self.state["Fan"] == self.attributes["Fan"][2]:
                #if Fan is in ON switch to Stand-by
                self.state["Fan"] = self.attributes["Fan"][1] #Stand-by
                self.heater_state["Fan"] = self.attributes["Fan"][0] #Off
            self.heater.set_value(self.heater_state)
        else:
            pass

    async def infinite_loop(self):
        while self.run:
            self.state["Room_temp"] = self.sensor.get_value(["Temp"])["Temp"]
            if self.state["Controller"] == "On":
                self._heater_control()
            await asyncio.sleep(TEMP_SENSOR.WAIT_TIME)