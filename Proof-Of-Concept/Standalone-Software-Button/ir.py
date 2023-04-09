import rp2
import time
from array import array
from machine import Pin, PWM

@rp2.asm_pio(autopull=True, pull_thresh=32)
def irqtrain():
    wrap_target()
    out(x, 32)
    irq(rel(0))
    label('loop')
    jmp(x_dec,'loop')
    wrap()

class IR():
    OUTPUT_PIN = 22 #GPIO number, not pin number
    
    def __init__(self):
        duty = 33 # Measured duty ratio 33%
        self.duty = (int(0xffff * duty // 100), 0)

        self.pwm = PWM(Pin(IR.OUTPUT_PIN, Pin.OUT, value = 0))  # Set up PWM with carrier off.
        self.pwm.freq(38000)
        self.pwm.duty_u16(0)

        self.sm = rp2.StateMachine(0, irqtrain, freq=1_000_000)
        self.apt = 0  # Array index
        self.arr = None  # Array
        self.ict = None  # Current IRQ count
        rp2.PIO(0).irq(self._cb)     

    def _cb(self, pio):
        self.pwm.duty_u16(self.duty[self.ict & 1])
        self.ict += 1
        if d := self.arr[self.apt]:
            self.sm.put(d)
            self.apt += 1

    # payload is an list of times in μs
    def broadcast(self, payload):
        signal = array('H', 3933 for _ in range(20 + len(payload)))
        j = 0
        for i in range(len(signal) - len(payload) - 2, len(signal) - 2):
            signal[i] = payload[j]
            j += 1
        signal[-2] = 0  # Ensure at least one STOP
        signal[-1] = 0  # Ensure at least one STOP
        self.sm.active(0)
        ###########################################
        for x, d in enumerate(signal):
            if d == 0:
                break
        if (x & 1):
            signal[x] = 1
            x += 1
            signal[x] = 0
        ###########################################
        mv = memoryview(signal)
        n = min(x, 4)  # Fill FIFO if there are enough data points.
        self.sm.put(mv[0 : n])
        self.arr = signal  # Initial conditions for ISR
        self.apt = n  # Point to next data value
        self.ict = 0  # IRQ count
        self.sm.active(1)
        time.sleep_ms(500)