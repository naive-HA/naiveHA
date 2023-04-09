import time
import machine
from led import LED
from const import _LED_MODES

LED_MODES = _LED_MODES()

class RF433():
    OUTPUT_PIN = 22 #GPIO number, not pin number
    
    def __init__(self):
        self.sensor = machine.Pin(RF433.OUTPUT_PIN, machine.Pin.OUT)
        self.light = LED()
    
    def broadcast(self, signal: list[int]) -> bool:
        #there are about 60% chances of the broadcasted message to be correctly sent
        #broadcast several times to increase the chances of success
        self.light.display(LED_MODES.EXECUTING_COMMAND)
        for i in range(0, 10):
            for step in signal:
                if step < 0:
                    self.sensor.value(0) # low
                else:
                    self.sensor.value(1) # high
                time.sleep_us(abs(step))
            self.sensor.value(0) # low
        self.light.display(LED_MODES.STOPPED_EXECUTING_COMMAND)
        return True

        
        