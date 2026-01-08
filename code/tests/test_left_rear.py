import RPi.GPIO as GPIO
import time

# --- GPIO ayarları ---
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# --- MOTOR SÜRÜCÜ 1: Sol Motorlar (ENA1 controls speed for both) ---
ENA1 = 13  # Speed control for left side motors
# IN1 = 17 # Presumed Front-Left motor direction
# IN2 = 18 # Presumed Front-Left motor direction
IN5 = 19   # Presumed Rear-Left motor direction
IN6 = 26   # Presumed Rear-Left motor direction

# --- GPIO çıkış ayarları ---
# Only setup pins we are using for this specific test
left_rear_motor_pins = [IN5, IN6, ENA1]
GPIO.setup(left_rear_motor_pins, GPIO.OUT)

# --- PWM ayarları ---
pwm_left_rear = GPIO.PWM(ENA1, 1000) # Using ENA1 for left side
pwm_left_rear.start(0) # Start with 0% duty cycle (motor off)

def left_rear_forward(hiz=60):
    print(f"Left Rear Forward at {hiz}% speed")
    GPIO.output(IN5, True)
    GPIO.output(IN6, False)
    pwm_left_rear.ChangeDutyCycle(hiz)

def left_rear_backward(hiz=60):
    print(f"Left Rear Backward at {hiz}% speed")
    GPIO.output(IN5, False)
    GPIO.output(IN6, True)
    pwm_left_rear.ChangeDutyCycle(hiz)

def left_rear_stop():
    print("Left Rear Stop")
    pwm_left_rear.ChangeDutyCycle(0)
    GPIO.output(IN5, False) # Good practice to set direction pins to False
    GPIO.output(IN6, False)

# --- Test Program ---
if __name__ == "__main__":
    try:
        print("Testing Left Rear Motor...")

        # Test forward
        left_rear_forward(50)  # Run at 50% speed
        time.sleep(3)          # Run for 3 seconds

        left_rear_stop()
        time.sleep(1)          # Pause for 1 second

        # Test backward
        left_rear_backward(70) # Run at 70% speed
        time.sleep(3)          # Run for 3 seconds

        left_rear_stop()
        time.sleep(1)

        print("Test complete.")

    except KeyboardInterrupt:
        print("Test interrupted by user.")
    finally:
        print("Cleaning up GPIO...")
        left_rear_stop()       # Ensure motor is stopped
        GPIO.cleanup()         # Release all GPIO pins
