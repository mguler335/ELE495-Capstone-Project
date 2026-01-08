import RPi.GPIO as GPIO
import time
from smbus import SMBus


class MPU6050:
    def __init__(self, address=0x68, bus_num=1):
        self.address = address
        self.bus = SMBus(bus_num)
        self.gyro_offset_z = 0
        self.initialize_sensor()
        self.calibrate_gyro()

    def initialize_sensor(self):
        self.bus.write_byte_data(self.address, 0x6B, 0)
        time.sleep(0.1)

    def read_word(self, reg):
        high = self.bus.read_byte_data(self.address, reg)
        low = self.bus.read_byte_data(self.address, reg + 1)
        val = (high << 8) + low
        if val >= 0x8000:
            val = -((65535 - val) + 1)
        return val

    def calibrate_gyro(self):
        print("Gyro kalibrasyonu... Lütfen robotu sabit tut.")
        offset_sum = 0
        for _ in range(100):
            offset_sum += self.read_word(0x47)
            time.sleep(0.01)
        self.gyro_offset_z = offset_sum / 100 / 131.0
        print(f"Z gyro offset: {self.gyro_offset_z:.2f} deg/s")

    def get_gyro_z(self):
        raw = self.read_word(0x47)
        return (raw / 131.0) - self.gyro_offset_z


class UltrasonicSensor:
    def __init__(self, trig_pin, echo_pin):
        self.trig_pin = trig_pin
        self.echo_pin = echo_pin
        GPIO.setup(trig_pin, GPIO.OUT)
        GPIO.setup(echo_pin, GPIO.IN)
    
    def measure_distance(self):
        """Mesafe ölçümü"""
        GPIO.output(self.trig_pin, False)
        time.sleep(0.05)
        GPIO.output(self.trig_pin, True)
        time.sleep(0.00001)
        GPIO.output(self.trig_pin, False)

        while GPIO.input(self.echo_pin) == 0:
            pulse_start = time.time()
        while GPIO.input(self.echo_pin) == 1:
            pulse_end = time.time()

        pulse_duration = pulse_end - pulse_start
        distance = pulse_duration * 17150
        return distance