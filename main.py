
if __name__ == '__main__':
    import sys, random
    import pygame
    from datetime import datetime
    from audio_controller import AudioController
    from button import Button
    from candy_dispenser import CandyDispenser, CandyDispenserState, Motor
    from prize_selector import PrizeSelector
    from screen_controller import ScreenController, ScreenState
    from event_service import EventService
    from constants import ENABLE_BUTTON_EVENT, VEND_CANDY_EVENT, BUTTON_PRESSED_EVENT, IDLE_TIME, IDLE_TIME_HIT_EVENT, READY_FOR_NEXT_PLAYER_EVENT
    try:
        import RPi.GPIO as GPIO
    except:
        import Mock.GPIO as GPIO

class MainController:
    def __init__(self):
        GPIO.setmode(GPIO.BOARD)
        pygame.init()
        random.seed(datetime.now())
        self.eventService = EventService()
        self.screenController = ScreenController()
        self.prizeSelector = PrizeSelector()
        self.candyDispenser = CandyDispenser(self.eventService)
        self.button = Button(self.eventService)
        self.audio = AudioController(self.eventService)
        self.waitingToVend = False
        self.isVending = False
        self.subscribeToEvents()

        # Start the idle timer
        pygame.time.set_timer(IDLE_TIME_HIT_EVENT, IDLE_TIME)

    def run(self):
        while 1:
            self.eventService.processEvents()

            # Vend candy once the spinner stops
            if self.screenController.getState() == ScreenState.showingWinSequence and not self.waitingToVend and not self.isVending:
                # Give time to get ready to catch candy
                self.waitingToVend = True
                pygame.time.set_timer(VEND_CANDY_EVENT, 1000)
                self.audio.playWinSoundBasedOnPrize(self.prize)

                # Reset the idle timer
                pygame.time.set_timer(IDLE_TIME_HIT_EVENT, IDLE_TIME)
            
            # Reset the game once the candy has been dispensed
            if self.isVending and self.candyDispenser.checkState() == CandyDispenserState.idle:
                self.isVending = False
                self.screenController.reset()
                self.audio.stopWinSound()
                pygame.time.set_timer(READY_FOR_NEXT_PLAYER_EVENT, 2000, 1)
                pygame.time.set_timer(ENABLE_BUTTON_EVENT, 3000, 1)
            
            self.screenController.render()
    
    def subscribeToEvents(self):
        self.eventService.subscribe(pygame.QUIT, self.onQuit)
        self.eventService.subscribe(pygame.KEYDOWN, self.onQuit, pygame.K_c)
        self.eventService.subscribe(pygame.KEYDOWN, self.onBypassMotor1, pygame.K_KP1)
        self.eventService.subscribe(pygame.KEYDOWN, self.onBypassMotor2, pygame.K_KP2)
        self.eventService.subscribe(pygame.KEYDOWN, self.onBypassMotor3, pygame.K_KP3)
        self.eventService.subscribe(pygame.KEYDOWN, self.onPlayPause, pygame.K_p)
        self.eventService.subscribe(pygame.KEYDOWN, self.onPlayNext, pygame.K_n)
        self.eventService.subscribe(pygame.KEYDOWN, self.onPlayLast, pygame.K_l)
        self.eventService.subscribe(pygame.KEYDOWN, self.onVolumeUp, pygame.K_UP)
        self.eventService.subscribe(pygame.KEYDOWN, self.onVolumeDown, pygame.K_DOWN)
        self.eventService.subscribe(ENABLE_BUTTON_EVENT, self.onEnableButton)
        self.eventService.subscribe(VEND_CANDY_EVENT, self.onVendCandy)
        self.eventService.subscribe(BUTTON_PRESSED_EVENT, self.onButtonPress)

    def onButtonPress(self, event):
        if (self.screenController.getState() != ScreenState.idle):
            return
        self.button.disable()
        self.prize = self.prizeSelector.getRandomPrize()
        self.screenController.start(self.prize)
        self.audio.playWheelSound()

    def onEnableButton(self, event):
        pygame.time.set_timer(ENABLE_BUTTON_EVENT, 0)
        self.button.enable()
    
    def onVendCandy(self, event):
        self.isVending = True
        self.waitingToVend = False
        pygame.time.set_timer(VEND_CANDY_EVENT, 0)
        self.candyDispenser.vendCandy(self.prize)

    def onQuit(self, event):
        if (event.key == pygame.K_c and (event.mod & pygame.KMOD_CTRL)):
            self.eventService.fireEvent(pygame.QUIT)
            return
        print("Quitting...")
        sys.exit()
    
    def onBypassMotor1(self, event):
        if (event.mod & pygame.KMOD_CTRL):
            self.candyDispenser.bypassMotor(Motor.sm, 1)
        else:
            self.candyDispenser.bypassMotor(Motor.sm)

    def onBypassMotor2(self, event):
        if (event.mod & pygame.KMOD_CTRL):
            self.candyDispenser.bypassMotor(Motor.md, 1)
        else:
            self.candyDispenser.bypassMotor(Motor.md)

    def onBypassMotor3(self, event):
        if (event.mod & pygame.KMOD_CTRL):
            self.candyDispenser.bypassMotor(Motor.lg, 1)
        else:
            self.candyDispenser.bypassMotor(Motor.lg)
    
    def onPlayNext(self, event):
        self.audio.playNextSong()

    def onPlayLast(self, event):
        self.audio.playPrevSong()

    def onPlayPause(self, event):
        self.audio.pauseOrUnpauseSong()
    
    def onVolumeUp(self, event):
        self.audio.volumeUp()

    def onVolumeDown(self, event):
        self.audio.volumeDown()

if __name__ == '__main__':
    MainController().run()