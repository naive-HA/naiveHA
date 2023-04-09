import time
import machine

class AHT20:
    I2CADDR = 0x38
    CMD_SOFTRESET = [0xBA]
    CMD_INITIALIZE = [0xBE, 0x08, 0x00]
    CMD_MEASURE = [0xAC, 0x33, 0x00]
    STATUSBIT_BUSY = 7                    # The 7th bit is the Busy indication bit. 1 = Busy, 0 = not.
    STATUSBIT_CALIBRATED = 3              # The 3rd bit is the CAL (calibration) Enable bit. 1 = Calibrated, 0 = not

    def __init__(self):
        # Initialize AHT20
        self.i2c = machine.I2C(0, sda=machine.Pin(8), scl=machine.Pin(9), freq=400000)
        self.i2c.writeto(AHT20.I2CADDR, bytes(AHT20.CMD_SOFTRESET))
        time.sleep(0.04)    # Wait 40 ms after poweron
        # Check for calibration, if not done then do and wait 10 ms
        if not self.get_status_calibrated() == 1:
            self.cmd_initialize()
            while not self.get_status_calibrated() == 1:
                time.sleep(0.01)
                
    def get_normalized_bit(self, value, bit_index):
        # Return only one bit from value indicated in bit_index
        return (value >> bit_index) & 1

    def cmd_initialize(self):
        # Send the command to initialize (calibrate)
        self.i2c.writeto(AHT20.I2CADDR, bytes(AHT20.CMD_INITIALIZE))
        return True

    def cmd_measure(self):
        # Send the command to measure
        self.i2c.writeto(AHT20.I2CADDR, bytes(AHT20.CMD_MEASURE))
        time.sleep(0.08)    # Wait 80 ms after measure
        return True

    def get_status(self):
        # Get the full status byte
        return self.i2c.readfrom(AHT20.I2CADDR, 1)[0]

    def get_status_calibrated(self):
        # Get the calibrated bit
        return self.get_normalized_bit(self.get_status(), AHT20.STATUSBIT_CALIBRATED)

    def get_status_busy(self):
        # Get the busy bit
        return self.get_normalized_bit(self.get_status(), AHT20.STATUSBIT_BUSY)

    def get_measure(self):
        # Get the full measure
        # Command a measure
        self.cmd_measure()
        # Check if busy bit = 0, otherwise wait 80 ms and retry
        while self.get_status_busy() == 1:
            time.sleep(0.08) # Wait 80 ns
        # Read data and return it
        return self.i2c.readfrom(AHT20.I2CADDR, 7)

    def get_temperature(self):
        # Get a measure, select proper bytes, return converted data
        measure = self.get_measure()
        measure = ((measure[3] & 0xF) << 16) | (measure[4] << 8) | measure[5]
        measure = measure / (pow(2,20))*200-50
        return round(measure, 2)

    def get_humidity(self):
        # Get a measure, select proper bytes, return converted data
        measure = self.get_measure()
        measure = (measure[1] << 12) | (measure[2] << 4) | (measure[3] >> 4)
        measure = measure * 100 / pow(2,20)
        return round(measure, 2)
    
    def get(self, attribute):
        if attribute == "Temp":
            return self.get_temperature()
        else:
            return self.get_humidity()