from enum import Enum
from typing import Callable, List, Tuple
import pygame
from pygame.event import Event
try:
    import RPi.GPIO as GPIO
except:
    import Mock.GPIO as GPIO

class SubscriptionType(Enum):
    keydown = 0,
    general = 1,

Subscription = Tuple[SubscriptionType, int, int]
GPIOEvent = Tuple[int, int, int] # (pin, value, event)

class EventService:
    def __init__(self):
        self._subscribersByEvent: dict[int, List[Callable[[Event], None]]] = {}
        self._keyDownSubscribersByKey: dict[int, List[Callable[[Event], None]]] = {}
        self._gpioEvents: List[GPIOEvent] = []

    def processEvents(self):
        self._processGPIOEvents()
        self._prossesPygameEvents()

    def subscribe(self, eventType: int, callback: Callable[[Event], None], key: int = None) -> Subscription:
        if (eventType == pygame.KEYDOWN and key is not None):
            return self._subscribeKeyDown(key, callback)
        else:
            return self._subscribeGeneral(eventType, callback)

    # Do not unsubscribe more than once!!!
    def unsubscribe(self, subscription: Subscription):
        (subscriptionType, eventTypeOrKey, index) = subscription
        if (subscriptionType == SubscriptionType.keydown):
            self._unsubscribeKeyDown(eventTypeOrKey, index)
        else:
            self._unsubscribeGeneral(eventTypeOrKey, index)

    # set up pin before registering
    def registerGPIOInputEvent(self, pin: int, eventTypeToFire: Event, fireOnValue: int = 1):
        self._gpioEvents.append((pin, fireOnValue, eventTypeToFire))
    
    def fireEvent(self, eventOrType):
        if (isinstance(eventOrType, int)):
            pygame.event.post(Event(eventOrType))
        else:
            pygame.event.post(eventOrType)

    def _prossesPygameEvents(self):
        events = pygame.event.get()
        for event in events:
            if (event.type == pygame.KEYDOWN):
                if (event.key in self._keyDownSubscribersByKey):
                    for callback in self._keyDownSubscribersByKey[event.key]:
                        callback(event)
            elif event.type in self._subscribersByEvent:
                for callback in self._subscribersByEvent[event.type]:
                    callback(event)

    def _processGPIOEvents(self):
        for pin, fireOnValue, eventTypeToFire in self._gpioEvents:
            if (GPIO.input(pin) == fireOnValue):
                pygame.event.post(Event(eventTypeToFire, pinValue=fireOnValue))

    def _subscribeKeyDown(self, key: int, callback: Callable[[Event], None]) -> Subscription:
        if (key not in self._keyDownSubscribersByKey):
            self._keyDownSubscribersByKey[key] = []
        self._keyDownSubscribersByKey[key].append(callback)
        return (SubscriptionType.keydown, key, len(self._keyDownSubscribersByKey[key]) - 1)
    
    def _subscribeGeneral(self, eventType: int, callback: Callable[[Event], None]) -> Subscription:
        if (eventType not in self._subscribersByEvent):
            self._subscribersByEvent[eventType] = []
        self._subscribersByEvent[eventType].append(callback)
        return (SubscriptionType.general, eventType, len(self._subscribersByEvent[eventType]) - 1)
    
    def _unsubscribeKeyDown(self, key: int, index: int):
        if (key in self._keyDownSubscribersByKey):
            self._keyDownSubscribersByKey[key].pop(index)
            if (len(self._keyDownSubscribersByKey[key]) == 0):
                del self._keyDownSubscribersByKey[key]

    def _unsubscribeGeneral(self, eventType: int, index: int):
        if (eventType in self._subscribersByEvent):
            self._subscribersByEvent[eventType].pop(index)
            if (len(self._subscribersByEvent[eventType]) == 0):
                del self._subscribersByEvent[eventType]
    