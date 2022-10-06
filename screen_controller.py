import platform
import pygame
from enum import Enum
from candy_rainer import CandyRainer
from constants import COLOR_BAD, COLOR_BLACK, COLOR_GOOD, COLOR_PRIMARY, COLOR_SECONDARY, REFRESH_RATE
from spinner import Spinner
from prize_selector import Prize

SPINNER_ENTRIES = 8

class ScreenState(Enum):
    idle = 0,
    spinning = 1,
    showingWinSequence = 2,

class ScreenController:
    def __init__(self):
        self._state = ScreenState.idle
        self.size = width, height = 1360, 768
        self.fullSpinnerSize = 500
        self.spinnerSize = self.fullSpinnerSize

        self._timeBetweenRefreshes = 1000 / REFRESH_RATE
        self._lastRefresh = pygame.time.get_ticks()
        self._lastBlink = pygame.time.get_ticks()
        self._blinkShow = True

        flags = pygame.FULLSCREEN | pygame.NOFRAME | pygame.HWSURFACE | pygame.DOUBLEBUF
        if (platform.system() == "Windows"):
            self.screen = pygame.display.set_mode(self.size)
        else:
            self.screen = pygame.display.set_mode(self.size, flags)
        pygame.mouse.set_visible(False)
        self.centerScreen = (self.screen.get_width()/2, self.screen.get_height()/2)
        self.background = pygame.image.load('assets/background.jpg').convert()
        self.spinner = Spinner(self.screen, SPINNER_ENTRIES)
        self.spinner.setLocation(self.centerScreen)
        self._candyRainer = CandyRainer(self.screen)
    
    def render(self):
        self.screen.fill(COLOR_BLACK)
        self.screen.blit(self.background, (50,0))

        if self._state == ScreenState.idle:
            self._renderIdleSpinner()
        if self._state == ScreenState.spinning:
            self._renderSpinningSpinner()
            if self.spinner.done:
                self._state = ScreenState.showingWinSequence
        if self._state == ScreenState.showingWinSequence:
            self._renderWinSequence()

        pygame.display.flip()
        endTicks = pygame.time.get_ticks()
        timeTaken = endTicks - self._lastRefresh
        timeToSleep = max(self._timeBetweenRefreshes - timeTaken, 0)
        pygame.time.delay(int(timeToSleep))
        self._lastRefresh = pygame.time.get_ticks()
    
    def start(self, prize: Prize):
        if self._state != ScreenState.idle:
            return
        self._state = ScreenState.spinning
        self._prize = prize
        landOnLocation = self._convertPrizeToWheelLocation(prize)
        self.spinner.startSpin(landOnLocation)
    
    def reset(self):
        self._state = ScreenState.idle
    
    def getState(self):
        return self._state

    def _renderSpinningSpinner(self):
        if self.spinnerSize < self.fullSpinnerSize:
            self.spinnerSize += 10
            self.spinner.setScale(self.spinnerSize)
        self.spinner.render()
    
    def _renderIdleSpinner(self):
        if self.spinnerSize >= self.fullSpinnerSize:
            self.idleSpinnerGrow = False
        elif self.spinnerSize <= self.fullSpinnerSize * .9:
            self.idleSpinnerGrow = True

        growAmount = 2
        self.spinnerSize += growAmount if self.idleSpinnerGrow else -growAmount
        self.spinner.setScale(self.spinnerSize)
        self.spinner.render()
        self._renderTextTop("Happy Halloween", COLOR_PRIMARY, fontSize=120)
        self._renderTextBottom("Press Button for Candy", COLOR_SECONDARY, showArrows=False, blink=True, fontSize=80)

    def _renderWinSequence(self):
        if self.spinnerSize > self.fullSpinnerSize / 3:
            self.spinnerSize -= 5
            self.spinner.setScale(self.spinnerSize)

        self.spinner.render()
        self._candyRainer.renderRain()
        
        (winnerText, color) = self._getWinnerTextAndColor(self._prize)
        self._renderTextTop(winnerText, COLOR_PRIMARY, blink=False)
        self._renderTextBottom("Candy", COLOR_SECONDARY, blink=True)
    
    def _renderTextBottom(self, text, color, showArrows=True, blink=False, fontSize=100):
        marginBottom = 50
        center = (self.centerScreen[0], self.screen.get_height() - fontSize / 2 - marginBottom)
        self._renderText(text, color, center, blink, fontSize, showArrows)
    
    def _renderTextTop(self, text, color, blink=False, fontSize=100):
        marginTop = 50
        center = (self.centerScreen[0], fontSize / 2 + marginTop)
        self._renderText(text, color, center, blink, fontSize)
   
    def _renderText(self, text, color, center, blink=False, fontSize=100, showArrows=False):
        if blink:
            blinkTime = 700 # milliseconds
            if self._lastBlink + blinkTime <= pygame.time.get_ticks():
                self._blinkShow = not self._blinkShow
                self._lastBlink = pygame.time.get_ticks()
            if not self._blinkShow:
                return

        font = pygame.font.Font("assets/fonts/monster-pumpkin-font/MonsterPumpkin-MVBzP.ttf", fontSize)
        text = font.render(text, True, color)
        textRect = text.get_rect(center=center)
        self.screen.blit(text, textRect)

        if showArrows:
            padding = 40
            arrowSize = (fontSize * 2/3, fontSize)
            arrow = self._getArrow(color, arrowSize)
            self.screen.blit(arrow, (textRect.left - arrowSize[0] - padding, textRect.y))
            self.screen.blit(arrow, (textRect.right + padding, textRect.y))
    
    def _getArrow(self, color, size):
        width, height = size
        surf = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.polygon(surf, color, (
            (width/3, 0),
            (width/3, height/2),
            (width/2, height/2),
            (0, height/2),
            (width/2, height),
            (width, height/2),
            (width*2/3, height/2),
            (width*2/3, 0),
        ))
        return surf


    def _convertPrizeToWheelLocation(self, prize: Prize):
        if prize == Prize.singleSm:
            return 0
        if prize == Prize.singleMd:
            return 3
        if prize == Prize.doubleMd:
            return 6
        if prize == Prize.doubleSm:
            return 2
        if prize == Prize.singleSmAndSingleMd:
            return 1
        if prize == Prize.doubleSmAndSingleMd:
            return 5
        if prize == Prize.quadrupleSm:
            return 4
        if prize == Prize.singleFullsized:
            return 7

    def _getWinnerTextAndColor(self, prize: Prize):
        if prize == Prize.singleSm:
            return ("Good Try", COLOR_BAD)
        if prize == Prize.singleMd:
            return ("Good Try", COLOR_BAD)
        if prize == Prize.doubleMd:
            return ("Not Bad", COLOR_BAD)
        if prize == Prize.doubleSm:
            return ("Not Bad", COLOR_BAD)
        if prize == Prize.singleSmAndSingleMd:
            return ("Not Bad", COLOR_BAD)
        if prize == Prize.doubleSmAndSingleMd:
            return ("Nice", COLOR_GOOD)
        if prize == Prize.quadrupleSm:
            return ("Big Winner", COLOR_GOOD)
        if prize == Prize.singleFullsized:
            return ("Jackpot", COLOR_GOOD)
