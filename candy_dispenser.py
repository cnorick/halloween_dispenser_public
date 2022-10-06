from multiprocessing.context import Process
import time
import pygame
from enum import Enum, IntEnum
from constants import STEPPER1_PINS, STEPPER2_PINS, STEPPER3_PINS
from event_service import EventService
from prize_selector import Prize
from motor import Stepper

class CandyDispenserState(Enum):
    idle = 0,
    dispensing = 1,

class Motor(IntEnum):
    sm = 0,
    md = 1,
    lg = 2,

# (direction, defaultSpeed)
MOTOR_CONFIG_DICT = {
    Motor.sm: (False, 10),
    Motor.md: (False, 10),
    Motor.lg: (True, 5)
}

class CandyDispenser:
    def __init__(self, eventService: EventService):
        self._state = CandyDispenserState.idle
        self.motors = {
            Motor.sm: Stepper(*STEPPER1_PINS),
            Motor.md: Stepper(*STEPPER2_PINS),
            Motor.lg: Stepper(*STEPPER3_PINS),
        }
        self.processDict = {}
        print(self.motors)
        eventService.subscribe(pygame.QUIT, self._onQuit)

    def vendCandy(self, prize: Prize):
        self._state = CandyDispenserState.dispensing

        if prize == Prize.singleSm:
            self._spawnVendProcessesPerMotor({
                Motor.sm: 1,
            })
        elif prize == Prize.singleMd:
            self._spawnVendProcessesPerMotor({
                Motor.md: 1,
            })
        elif prize == Prize.doubleSm:
            self._spawnVendProcessesPerMotor({
                Motor.sm: 2,
            })
        elif prize == Prize.doubleMd:
            self._spawnVendProcessesPerMotor({
                Motor.md: 2,
            })
        elif prize == Prize.singleSmAndSingleMd:
            self._spawnVendProcessesPerMotor({
                Motor.sm: 1,
                Motor.md: 1,
            })
        elif prize == Prize.doubleSmAndSingleMd:
            self._spawnVendProcessesPerMotor({
                Motor.sm: 2,
                Motor.md: 1,
            })
        elif prize == Prize.quadrupleSm:
            self._spawnVendProcessesPerMotor({
                Motor.sm: 4,
            })
        elif prize == Prize.singleFullsized:
            self._spawnVendProcessesPerMotor({
                Motor.lg: 1,
            })
        print("vending " + str(prize))

    def bypassMotor(self, motor, speedOverride = None):
        d = {}
        d[motor] = 1
        self._spawnVendProcessesPerMotor(d, speedOverride)

    def _onQuit(self, event):
        print("killing motor processes")
        for (k, p) in self.processDict.items():
            p.kill()

    def checkState(self):
        if (self._state == CandyDispenserState.dispensing):
            liveProcesses = [(k, p) for (k, p) in self.processDict.items() if p.is_alive()]
            deadProcesses = [(k, p) for (k, p) in self.processDict.items() if (k, p) not in liveProcesses]
            for k, p in deadProcesses:
                p.join()
                del self.processDict[k]

            if not liveProcesses:
                print("done vending")
                self._state = CandyDispenserState.idle

        return self._state
    
    def _spawnVendProcessesPerMotor(self, numPerMotor, speedOverride = None):
        for motor, num in numPerMotor.items():
            if (motor in self.processDict):
                self.processDict[motor].kill()
                del self.processDict[motor]
            p = Process(target=_vendNumFromMotor, args=(self.motors, motor, num, speedOverride))
            p.start()
            self.processDict[motor] = p

# Methods passed to Process have to be at the top level of the module.    
def _vendNumFromMotor(motors, motor: Motor, num, speedOverride = None):
    stepper = motors[motor]
    config = list(MOTOR_CONFIG_DICT[motor])
    
    if (speedOverride != None):
        config[1] = speedOverride

    for i in range(num):
        print ("start rotation for motor " + str(i+1))
        stepper.rotateUntilSwitchActivation(*config)
        time.sleep(1)

