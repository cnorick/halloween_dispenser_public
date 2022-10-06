import pygame, random

ARROW_SIZE = 30
ARROW_COLOR = [255, 255, 0]

def blitRotateCenter(surf, image, topleft, angle):
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(topleft = topleft).center)

    surf.blit(rotated_image, new_rect)

class Spinner:
    def __init__(self, screen, numEntries):
        self.screen = screen
        self.numEntries = numEntries
        self.landsOnFor0 = 128.48999999999 # observed last rotationAngle. Recalculate if you change rotation physics
        self.preRotate = 0
        self.wiggleRoom = 360 / numEntries
        self.randomSpotInWiggleRoom = random.randrange(5, 90) * .01 * self.wiggleRoom
        self.rotateSpeed = 50
        self.deceleration = 0.7
        self.rotationAngle = 0
        self.done = False
        self.spinning = False
        self.spinner = pygame.image.load("assets/wheel.png").convert_alpha()
    
    def startSpin(self, landOn):
        self.spinning = True
        self.done = False
        self.landOn = landOn
        self.preRotate = (360 / self.numEntries) * self.landOn
        self.randomSpotInWiggleRoom = random.randrange(5, 90) * .01 * self.wiggleRoom
        self.rotateSpeed = 50
        self.deceleration = 0.7
        self.rotationAngle = 0
        
    def showIdle(self):
        pass

    def setLocation(self, location):
        self.location = location

    def setScale(self, scale):
        self.scaledSpinner = pygame.transform.scale(self.spinner, (scale, scale))
        self.spinner_rect = self.scaledSpinner.get_rect()
        self.spinnerTopLeft = (round((self.location[0]) - self.spinner_rect.width / 2), round((self.location[1]) - self.spinner_rect.height / 2))
        self.arrowMiddleLeft = (self.spinnerTopLeft[0] + self.spinner_rect.width, self.spinnerTopLeft[1] + self.spinner_rect.height / 2) 
        self.arrowTopRight = (self.arrowMiddleLeft[0] + ARROW_SIZE, self.arrowMiddleLeft[1] + ARROW_SIZE)
        self.arrowBottomRight = (self.arrowMiddleLeft[0] + ARROW_SIZE, self.arrowMiddleLeft[1] - ARROW_SIZE)

    # location is the location to draw the center of the spinner.
    def render(self):
        self._renderSpinner(self.scaledSpinner, self.spinnerTopLeft)
        self._renderArrow()

    def _renderSpinner(self, spinner, topLeft):
        if self.spinning:
            self._updateRotationCalculations()
        blitRotateCenter(self.screen, spinner, topLeft, self.rotationAngle + self.preRotate - self.landsOnFor0 - 90 + self.randomSpotInWiggleRoom)

    def _renderArrow(self):
        pygame.draw.polygon(self.screen, ARROW_COLOR, (self.arrowMiddleLeft, self.arrowTopRight, self.arrowBottomRight))
    
    def _updateRotationCalculations(self):
        if self.rotateSpeed < 10:
            self.deceleration = 0.6
        if self.rotateSpeed < 8:
            self.deceleration = 0.4
        if self.rotateSpeed < 5:
            self.deceleration = 0.1
        if self.rotateSpeed < 4:
            self.deceleration = 0.09
        if self.rotateSpeed < 3:
            self.deceleration = 0.05
        # if self.rotateSpeed < 2:
        #     self.deceleration = 0.02
        # if self.rotateSpeed < 1:
        #     self.deceleration = 0.01

        self.rotateSpeed = self.rotateSpeed - self.deceleration
        if self.rotateSpeed <= 0:
            print(self.rotationAngle)
            self.spinning = False
            self.done = True

        self.rotationAngle += self.rotateSpeed
        self.rotationAngle = (self.rotationAngle) % 360
