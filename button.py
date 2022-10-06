import pygame
from constants import BUTTON_PIN, IDLE_TIME_HIT_EVENT, INTERNAL_BUTTON_PRESSED_EVENT, BUTTON_PRESSED_EVENT, INTERNAL_LIGHT_BLINK_EVENT, LIGHT_BLINK_TIME, LIGHT_PIN
from event_service import EventService
try:
    import RPi.GPIO as GPIO
except:
    import Mock.GPIO as GPIO

class Button:
    def __init__(self, eventService: EventService):
        self._eventService = eventService
        GPIO.setup(LIGHT_PIN, GPIO.OUT)
        GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        eventService.registerGPIOInputEvent(BUTTON_PIN, INTERNAL_BUTTON_PRESSED_EVENT, GPIO.HIGH)
        eventService.subscribe(INTERNAL_BUTTON_PRESSED_EVENT, self._handleButtonPress)
        eventService.subscribe(INTERNAL_LIGHT_BLINK_EVENT, self._handleLightBlink)
        eventService.subscribe(IDLE_TIME_HIT_EVENT, self._handleIdle)
        eventService.subscribe(pygame.MOUSEBUTTONDOWN, self._handleButtonPress)
        eventService.subscribe(pygame.KEYDOWN, self._handleButtonPress, pygame.K_SPACE)
        eventService.subscribe(pygame.KEYDOWN, self._handleButtonPress, pygame.K_KP_ENTER)
        self._lightPWM = GPIO.PWM(LIGHT_PIN, 1000)
        self.enable()
    
    def enable(self):
        print("Button enabled")
        self._enabled = True
        self._turnOnLight()
    
    def disable(self):
        print("Button disabled")
        self._enabled = False
        self._stopBlinkingLight()
        self._turnOffLight()

    def _startBlinkingLight(self):
        pygame.time.set_timer(INTERNAL_LIGHT_BLINK_EVENT, LIGHT_BLINK_TIME)

    def _stopBlinkingLight(self):
        pygame.time.set_timer(INTERNAL_LIGHT_BLINK_EVENT, 0)

    def _handleIdle(self, event):
        self._startBlinkingLight()

    def _handleLightBlink(self, event):
        if (self.lightOn):
            self._turnOffLight()
        else:
            self._turnOnLight()

    def _turnOnLight(self):
        self.lightOn = True
        self._dutyCycle = 100
        self._lightPWM.start(self._dutyCycle)

    def _turnOffLight(self):
        self.lightOn = False
        self._lightPWM.stop()
    
    def _handleButtonPress(self, event):
        if self._enabled:
            self._eventService.fireEvent(BUTTON_PRESSED_EVENT)