import RPi.GPIO as GPIO
import time


class MotorController:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        #Motor driver pins
        self.ENA1 = 13
        self.IN1 = 17
        self.IN2 = 18
        self.ENB2 = 12
        self.IN3 = 22
        self.IN4 = 23
        self.IN5 = 19
        self.IN6 = 26
        self.IN7 = 20
        self.IN8 = 21
        
        #Setup motor pins
        motor_pins = [self.IN1, self.IN2, self.IN3, self.IN4, 
                     self.IN5, self.IN6, self.IN7, self.IN8, 
                     self.ENA1, self.ENB2]
        GPIO.setup(motor_pins, GPIO.OUT)
        
        #PWM setup
        self.pwm_left = GPIO.PWM(self.ENA1, 1000)
        self.pwm_right = GPIO.PWM(self.ENB2, 1000)
        self.pwm_left.start(0)
        self.pwm_right.start(0)
    
    def move_forward(self, speed=40):
        """İleri hareket"""
        GPIO.output([self.IN1, self.IN5], False)
        GPIO.output([self.IN2, self.IN6], True)
        GPIO.output([self.IN3, self.IN7], False)
        GPIO.output([self.IN4, self.IN8], True)
        self.pwm_left.ChangeDutyCycle(speed)
        self.pwm_right.ChangeDutyCycle(speed)
    
    def move_backward(self, speed=60):
        """Geri hareket"""
        GPIO.output([self.IN1, self.IN5], True)
        GPIO.output([self.IN2, self.IN6], False)
        GPIO.output([self.IN3, self.IN7], True)
        GPIO.output([self.IN4, self.IN8], False)
        self.pwm_left.ChangeDutyCycle(speed)
        self.pwm_right.ChangeDutyCycle(speed)
    
    def tank_turn_right(self, speed=60):
        """Tank modu sağa dönüş"""
        GPIO.output([self.IN1, self.IN5], False)
        GPIO.output([self.IN2, self.IN6], True)
        GPIO.output([self.IN3, self.IN7], True)
        GPIO.output([self.IN4, self.IN8], False)
        self.pwm_left.ChangeDutyCycle(speed)
        self.pwm_right.ChangeDutyCycle(speed)
    
    def tank_turn_left(self, speed=60):
        """Tank modu sola dönüş"""
        GPIO.output([self.IN1, self.IN5], True)
        GPIO.output([self.IN2, self.IN6], False)
        GPIO.output([self.IN3, self.IN7], False)
        GPIO.output([self.IN4, self.IN8], True)
        self.pwm_left.ChangeDutyCycle(speed)
        self.pwm_right.ChangeDutyCycle(speed)

    def move_forward_differential(self, left_speed, right_speed):
        """Forward movement with differential steering"""
        GPIO.output([self.IN1, self.IN5], False)
        GPIO.output([self.IN2, self.IN6], True)
        GPIO.output([self.IN3, self.IN7], False)
        GPIO.output([self.IN4, self.IN8], True)

        #Use different PWM speeds for "steering".
        left_speed = max(0, min(left_speed, 100))
        right_speed = max(0, min(right_speed, 100))
        self.pwm_left.ChangeDutyCycle(left_speed)
        self.pwm_right.ChangeDutyCycle(right_speed)

    def move_backward_differential(self, left_speed, right_speed):
        """Backward movement with differential steering"""
        GPIO.output([self.IN1, self.IN5], True)
        GPIO.output([self.IN2, self.IN6], False)
        GPIO.output([self.IN3, self.IN7], True)
        GPIO.output([self.IN4, self.IN8], False)

        #Use different PWM speeds for "steering".
        left_speed = max(0, min(left_speed, 100))
        right_speed = max(0, min(right_speed, 100))
        self.pwm_left.ChangeDutyCycle(left_speed)
        self.pwm_right.ChangeDutyCycle(right_speed)

    def stop(self):
        """Dur"""
        self.pwm_left.ChangeDutyCycle(0)
        self.pwm_right.ChangeDutyCycle(0)
        GPIO.output([self.IN1, self.IN2, self.IN3, self.IN4, 
                    self.IN5, self.IN6, self.IN7, self.IN8], False)
    
    def cleanup(self):
        """Cleanup GPIO"""
        self.stop()
        GPIO.cleanup()