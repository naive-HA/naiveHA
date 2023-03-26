import time
import machine

class RF433():
    WAIT_TIME = 300
    OUTPUT_PIN = 22 #GPIO number, not pin number
    
    def __init__(self):
        self.sensor = machine.Pin(RF433.OUTPUT_PIN, machine.Pin.OUT)
        self.remote = {"A": {"on"  : "8e888e8e8e8888ee88888e8888e8888e88",
                             "off" : "8e888e8e8e8888ee8888e88888e8eee888",
                             "name": "power socket"}}
        factor = 0.8227 #scale down to account for the computations in between state changes below
        self.short_pulse = int(285*factor) #original: 285 length in microseconds of 1 bit  of 1
        self.long_pulse = int(865*factor)  #original: 865 length in microseconds of 3 bits of 0
        self.extended_pulse = int(10.27*1000) #10.27 miliseconds
        
        self.state = 0 #off
    
    def toggle(self) -> None:
        if self.state:
            signal = self.remote["A"]["off"]
            self.state = 0
        else:
            signal = self.remote["A"]["on"]
            self.state = 1
            
        #there are about 60% chances of the broadcasted message to be correctly sent
        #broadcast several times to increase the chances of success
        for i in range(0, 10):
            for bit in signal:
                if bit == '8':
                    self.sensor.value(1) #1
                    time.sleep_us(self.short_pulse)
                    self.sensor.value(0) #0
                    time.sleep_us(self.long_pulse)
                elif bit == 'e':
                        self.sensor.value(1) #1
                        time.sleep_us(self.long_pulse)
                        self.sensor.value(0) #0
                        time.sleep_us(self.short_pulse)
                else:
                    continue
            self.sensor.value(0)
            time.sleep_us(self.extended_pulse)
        time.sleep_ms(RF433.WAIT_TIME) #milliseconds
        
