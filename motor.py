try:
    import RPi.GPIO as GPIO
except:
    import Mock.GPIO as GPIO
import time
import math
from constants import GPIO_ENABLED

class Stepper:
    def __init__(self, in1, in2, in3, in4, switchPin):
        self.MINSLEEP = 0.0007
        self.STEPSPERREV = 4096
        self.steps = 0
        self.in1 = in1
        self.in2 = in2
        self.in3 = in3
        self.in4 = in4
        self.switchPin = switchPin
        GPIO.setup(in1, GPIO.OUT)
        GPIO.setup(in2, GPIO.OUT)
        GPIO.setup(in3, GPIO.OUT)
        GPIO.setup(in4, GPIO.OUT)
        GPIO.setup(switchPin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def rotateUntilSwitchActivation(self, forward = True, speed = 10, rotateUntilSwitchIs = True):
        if not GPIO_ENABLED:
            time.sleep(2)
            return

        speed = min(max(speed, 1), 10)

        # If the pin is already on, rotate until the button is no longer pressed.
        while (GPIO.input(self.switchPin) == rotateUntilSwitchIs):
            self.step(1, forward)
            time.sleep(self.MINSLEEP / speed * 10)
        
        # After the button is unpressed, rotate until it is pressed again.
        while (GPIO.input(self.switchPin) != rotateUntilSwitchIs):
            self.step(1, forward)
            time.sleep(self.MINSLEEP / speed * 10)

    def rotateDegrees(self, angle, forward = True, speed = 10):
        if not GPIO_ENABLED:
            time.sleep(2)
            return

        speed = min(max(speed, 1), 10)
        numSteps = math.ceil(angle * self.STEPSPERREV / 360)
        for i in range(numSteps):
            self.step(1, forward)
            time.sleep(self.MINSLEEP / speed * 10)

    def step(self, numSteps, direction):
        for x in range(numSteps):
            mode = self.steps % 8
            if mode == 0:
                GPIO.output(self.in1, GPIO.LOW)
                GPIO.output(self.in2, GPIO.LOW)
                GPIO.output(self.in3, GPIO.LOW)
                GPIO.output(self.in4, GPIO.HIGH)
            elif mode == 1:
                GPIO.output(self.in1, GPIO.LOW)
                GPIO.output(self.in2, GPIO.LOW)
                GPIO.output(self.in3, GPIO.HIGH)
                GPIO.output(self.in4, GPIO.HIGH)
            elif mode == 2:
                GPIO.output(self.in1, GPIO.LOW)
                GPIO.output(self.in2, GPIO.LOW)
                GPIO.output(self.in3, GPIO.HIGH)
                GPIO.output(self.in4, GPIO.LOW)
            elif mode == 3:
                GPIO.output(self.in1, GPIO.LOW)
                GPIO.output(self.in2, GPIO.HIGH)
                GPIO.output(self.in3, GPIO.HIGH)
                GPIO.output(self.in4, GPIO.LOW)
            elif mode == 4:
                GPIO.output(self.in1, GPIO.LOW)
                GPIO.output(self.in2, GPIO.HIGH)
                GPIO.output(self.in3, GPIO.LOW)
                GPIO.output(self.in4, GPIO.LOW)
            elif mode == 5:
                GPIO.output(self.in1, GPIO.HIGH)
                GPIO.output(self.in2, GPIO.HIGH)
                GPIO.output(self.in3, GPIO.LOW)
                GPIO.output(self.in4, GPIO.LOW)
            elif mode == 6:
                GPIO.output(self.in1, GPIO.HIGH)
                GPIO.output(self.in2, GPIO.LOW)
                GPIO.output(self.in3, GPIO.LOW)
                GPIO.output(self.in4, GPIO.LOW)
            elif mode == 7:
                GPIO.output(self.in1, GPIO.HIGH)
                GPIO.output(self.in2, GPIO.LOW)
                GPIO.output(self.in3, GPIO.LOW)
                GPIO.output(self.in4, GPIO.HIGH)
            else:
                GPIO.output(self.in1, GPIO.LOW)
                GPIO.output(self.in2, GPIO.LOW)
                GPIO.output(self.in3, GPIO.LOW)
                GPIO.output(self.in4, GPIO.LOW)

            if direction == True:
                self.steps += 1
            elif direction == False:
                self.steps -= 1
            if self.steps > self.STEPSPERREV:
                self.steps = 0
            elif self.steps < 0:
                self.steps = self.STEPSPERREV
