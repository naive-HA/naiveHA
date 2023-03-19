import RPi.GPIO as GPIO
from typing import Callable

##cheap chinese 3 pin module: pin down
##	    Power   Data    GND
##Pin	1       7	    9
##	            GPIO4

class BUTTON():
    INPUT_PIN = 4 #GPIO number, not pin number
    def __init__(self):
        self.event_detected : "Callable[[]]" | None = None
        def callback(channel):
            if channel == self.INPUT_PIN:
                self.event_detected()
        if GPIO.getmode() != GPIO.BCM:
            GPIO.setmode(GPIO.BCM)
        GPIO.setup(BUTTON.INPUT_PIN,GPIO.IN)
        GPIO.add_event_detect(BUTTON.INPUT_PIN, GPIO.RISING, callback=callback, bouncetime=2500)

    def start(self) -> bool:
        assert self.event_detected is not None

    def stop(self) -> None:
        GPIO.remove_event_detect(BUTTON.INPUT_PIN)
        GPIO.cleanup(BUTTON.INPUT_PIN)
        return None
