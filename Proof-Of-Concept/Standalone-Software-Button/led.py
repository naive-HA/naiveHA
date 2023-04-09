from const import _LED_MODES
from machine import Pin, Timer

LED_MODES = _LED_MODES()

class LED():
    def __init__(self):
        self.timer = Timer()
        self.led = Pin("LED", Pin.OUT)
        
    def stop(self) -> None:
        self.timer.deinit()
        self.led.off()
        return None
    
    def display(self, mode: int) -> None:
        self.stop()
        if mode == LED_MODES.NETWORK_DISCONNECTED:
            self.led.off()
            self.timer.init(freq=25, mode=Timer.PERIODIC, callback = lambda timer: self.led.toggle())
            return None
        elif mode == LED_MODES.NETWORK_CONNECTED:
            self.stop()
            return None
        elif mode == LED_MODES.CONNECTING:
            self.led.on()
            return None
        elif mode == LED_MODES.STOPPED_CONNECTING:
            self.stop()
            return None
        elif mode == LED_MODES.EXECUTING_COMMAND:
            self.led.on()
            return None
        elif mode == LED_MODES.STOPPED_EXECUTING_COMMAND:
            self.stop()
            return None
        else:
            self.stop()
            return None






