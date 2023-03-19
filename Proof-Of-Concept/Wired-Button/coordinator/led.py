import time
import RPi.GPIO as GPIO
from const import _LED_MODES

LED_MODES = _LED_MODES()

class LED():
    BLUE_PIN = 21 #GPIO number, not pin number
    RED_PIN = 20 #GPIO number, not pin number
    GREEN_PIN = 16 #GPIO number, not pin number
    def __init__(self):
        if GPIO.getmode() != GPIO.BCM:
            GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.BLUE_PIN, GPIO.OUT)
        GPIO.setup(self.RED_PIN, GPIO.OUT)
        GPIO.setup(self.GREEN_PIN, GPIO.OUT)
        GPIO.output(self.RED_PIN, GPIO.LOW)
        GPIO.output(self.BLUE_PIN, GPIO.LOW)
        GPIO.output(self.GREEN_PIN, GPIO.LOW)

    def start(self) -> None:
        GPIO.output(self.RED_PIN, GPIO.LOW)
        GPIO.output(self.BLUE_PIN, GPIO.LOW)
        GPIO.output(self.GREEN_PIN, GPIO.LOW)

    def stop(self) -> None:
        GPIO.output(self.RED_PIN, GPIO.LOW)
        GPIO.output(self.BLUE_PIN, GPIO.LOW)
        GPIO.output(self.GREEN_PIN, GPIO.LOW)
        GPIO.cleanup(self.RED_PIN)
        GPIO.cleanup(self.BLUE_PIN)
        GPIO.cleanup(self.GREEN_PIN)

    def display(self, mode: int) -> None:
        GPIO.output(self.RED_PIN, GPIO.LOW)
        GPIO.output(self.BLUE_PIN, GPIO.LOW)
        GPIO.output(self.GREEN_PIN, GPIO.LOW)
        if mode == LED_MODES.NETWORK_DISCONNECTED:
            GPIO.output(self.RED_PIN, GPIO.HIGH)
            return None
        elif mode == LED_MODES.NETWORK_CONNECTED:
            return None
        elif mode == LED_MODES.ACCEPTING_CONNECTIONS:
            GPIO.output(self.BLUE_PIN, GPIO.HIGH)
            return None
        elif mode == LED_MODES.STOPPED_ACCEPTING:
            return None
        elif mode == LED_MODES.TRIGGER_ACTION:
            GPIO.output(self.GREEN_PIN, GPIO.HIGH)
            time.sleep(0.5)
            GPIO.output(self.GREEN_PIN, GPIO.LOW)
            return None
        else:
            return None

