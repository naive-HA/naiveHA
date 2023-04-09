import json
from rf433 import RF433
from custom_extensible_class import CUSTOM_EXTENSIBLE_CLASS

class ARLEC(CUSTOM_EXTENSIBLE_CLASS, RF433):
    def __init__(self, endpoint_id: int):
        CUSTOM_EXTENSIBLE_CLASS.__init__(self, endpoint_id)
        RF433.__init__(self)
        self.description = "RF433 MHz remote control for Arlec power socket"
        self.endpoint_id = endpoint_id
        with open("RF433_signals", 'r') as raw_signals:
            self.signals = json.loads(raw_signals.read())
        self.attributes = {"Power": ["Off", "On"]}
        self.state = {"Power": "Off"}
    
    def _validate(self, attributes: dict[str, str] | list[str]) -> bool:
        if len(attributes) in [0]:
            pass
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
            with open('arlec.html', 'r') as html_file:
                html = html_file.read()
            return html        
        elif ".css" in file_type:
            with open('arlec.css', 'r') as css_file:
                css = css_file.read()            
            return css
        elif ".js" in file_type:
            with open('arlec.js', 'r') as js_file:
                js = js_file.read()            
            return js.replace("<<POWER>>", str(self.state["Power"]))\
                     .replace("<<ENDPOINT_ID>>", str(self.endpoint_id))
        else:
            return ""

    def get_attributes(self) -> dict[str, list[str]]:
        return self.attributes

    def set_value(self, attributes: dict[str, str | float]) -> bool | None:
        self._validate(attributes)
        self.state["Power"] = attributes["Power"]
        self.broadcast(self.signals["Power"][self.state["Power"]])
        return self.state

    def get_value(self, attributes: list[str]) -> dict[str, str | float] | None:
        self._validate(attributes)
        return self.state

if __name__ == "__main__":
    import time
    import machine
    factor = 1 # if need be to scale down due to lag induce by computations
    short_pulse = int(factor*282) #original: 282 length in microseconds of 1 bit  of 1
    long_pulse = int(factor*876)  #original: 876 length in microseconds of 3 bits of 0
    extended_pulse = int(10.27*1000) #10.27 miliseconds

    signals = {"Power": {"On": "8e888e8e8e8888ee88888e8888e8888e88",
                         "Off": "8e888e8e8e8888ee8888e88888e8eee888"}}

    for state in list(signals["Power"]):
        signal = (len(signals["Power"][state])*2 + 1) *[0]
        i = 0
        for bit in signals["Power"][state]:
            if bit == '8':
                signal[i] = short_pulse
                i += 1
                signal[i] = -1 * long_pulse
                i += 1
            elif bit == 'e':
                signal[i] = long_pulse
                i += 1
                signal[i] = -1 * short_pulse
                i += 1
            else:
                continue
        signal[i] = -1* extended_pulse
        signals["Power"][state] = signal
    with open("RF433_signals", 'w') as raw_signals:
        raw_signals.write(json.dumps(signals))
    
    trx = ARLEC()
    trx.set_value({"Power": "On"})
    time.sleep(1)
    trx.set_value({"Power": "Off"})
    print(trx.get_attributes())