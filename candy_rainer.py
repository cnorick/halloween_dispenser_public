import pygame
import random

class CandyRainer:
    def __init__(self, screen: pygame.Surface):
        self._screen = screen
        self._candyImages = [
            pygame.image.load("assets/snickers.png").convert_alpha(),
            pygame.image.load("assets/spk.png").convert_alpha(),
            pygame.image.load("assets/milkyway.png").convert_alpha(),
            pygame.image.load("assets/3musk.png").convert_alpha(),
            pygame.image.load("assets/hersheys.png").convert_alpha(),
            pygame.image.load("assets/mnms.png").convert_alpha(),
            pygame.image.load("assets/nerds.png").convert_alpha(),
            pygame.image.load("assets/reeses.png").convert_alpha(),
        ]
        self._fallingCandy = []
        self._maxFalling = 20
        self._speedRange = (3, 15)
        self._sizeRange = (50, 300)
    
    def renderRain(self):
        self._fallingCandy = [c for c in self._fallingCandy if c[1][1] < self._screen.get_height()]
        while len(self._fallingCandy) < self._maxFalling:
            self._addFallingCandy()
        
        for i in range(len(self._fallingCandy)):
            (candy, (x, y), speed) = self._fallingCandy[i]
            self._screen.blit(candy, (x, y))
            y += speed
            self._fallingCandy[i] = (candy, (x, y), speed)
    
    def _addFallingCandy(self):
        candy = self._getRandomCandy()
        startingLocation = self._getRandomStartingLocation()
        speed = self._getRandomSpeed()
        size = self._getRandomCandySize()
        scaledCandy = pygame.transform.scale(candy, (size, size))
        self._fallingCandy.append((scaledCandy, startingLocation, speed))
    
    def _getRandomCandy(self):
        return self._candyImages[random.randint(0, len(self._candyImages) - 1)]
    
    def _getRandomStartingLocation(self):
        return (random.randint(0, self._screen.get_width()), 0)
    
    def _getRandomSpeed(self):
        return random.randint(*self._speedRange)
    
    def _getRandomCandySize(self):
        return random.randint(*self._sizeRange)