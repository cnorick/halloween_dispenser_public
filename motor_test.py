try:
    import RPi.GPIO as GPIO
except:
    import Mock.GPIO as GPIO
import time
from constants import STEPPER1_PINS, STEPPER2_PINS, STEPPER3_PINS
from motor import Stepper

GPIO.setmode(GPIO.BOARD)

direction = True
steps = 0

steppers = [
    Stepper(*STEPPER1_PINS),
    Stepper(*STEPPER2_PINS),
    Stepper(*STEPPER3_PINS),
    # Stepper(*STEPPER4_PINS),
]
while 1:
    steppers[1].rotateUntilSwitchActivation(False, 10)
    time.sleep(3)

   # steppers[1].rotateUntilSwitchActivation(False, 10)
   # time.sleep(3)

   # steppers[2].rotateUntilSwitchActivation(True, 5, True)
   # time.sleep(3)


