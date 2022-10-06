import math
import random
import pygame
from constants import IDLE_TIME, IDLE_TIME_HIT_EVENT, INTERNAL_IDLE_SOUND_END_EVENT, INTERNAL_MUSIC_FADE_DOWN_EVENT, INTERNAL_MUSIC_FADE_UP_EVENT, INTERNAL_READY_FOR_NEXT_PLAYER_SOUND_DONE_EVENT, MUSIC_END_EVENT, READY_FOR_NEXT_PLAYER_EVENT
from event_service import EventService

from prize_selector import Prize

# (file, relative-volume)
MUSIC = [
    ("8_bit_reverse.mp3", 0.7),
    ("spooker.mp3", 0.8),
    ("8_bit.mp3", 0.4),
    ("atmosphere.mp3", 1.0),
    # ("seance.mp3", 1.0),
    ("haunted_house.mp3", 1.0),
    ("spooky.mp3", 1.0),
    ("evil.mp3", 0.3),
    ("alley.mp3", 0.7),
    ("chase.mp3", 0.3),
    ("dash.mp3", 0.5),
    ("monster.mp3", 0.5),
    ("nightmare.mp3", 0.3),
    ("zombie.mp3", 0.8)
]

SOUNDS = {
    "wheelSound": ("assets/audio/wheel-spin2.wav", 1.0),
    "slotsSound": ("assets/audio/slots-win.wav", 0.5),
    "laughSound": ("assets/audio/laugh.wav", 0.5),
    "middlePrizeSound": ("assets/audio/middle-prize-slots.wav", 1.0),
    "singingGhosts1": ("assets/audio/singing-ghosts-1.wav", 1.0),
    "singingGhosts2": ("assets/audio/singing-ghosts-2.wav", 1.0),
    "beast": ("assets/audio/beast.wav", 1.0),
    "ghost4": ("assets/audio/ghost4.wav", 1.0),
    "heartbeat": ("assets/audio/heartbeat.wav", 1.0),
    "jumpscare": ("assets/audio/jumpscare.wav", 1.0),
    "thunder": ("assets/audio/thunder.wav", 1.0),
    "werewolf": ("assets/audio/werewolf.wav", 1.0),
    "wind": ("assets/audio/wind.wav", 1.0),
    "greatestShowInTown": ("assets/audio/non-free/greatestShowInTown.wav", 1.0),
    "playTheGame": ("assets/audio/non-free/playTheGame.wav", 1.0),
    "playTheGame2": ("assets/audio/non-free/playTheGame2.wav", 1.0),
    "stepRightUp": ("assets/audio/non-free/stepRightUp.wav", 1.0),
    "stepRightUp2": ("assets/audio/non-free/stepRightUp2.wav", 1.0),
    "stepRightUp3": ("assets/audio/non-free/stepRightUp3.wav", 1.0),
    "stepRightUp4": ("assets/audio/non-free/stepRightUp4.wav", 1.0),
    "stepRightUp5": ("assets/audio/non-free/stepRightUp5.wav", 1.0),
    "winAPrize": ("assets/audio/non-free/winAPrize.wav", 1.0),
    "winAPrize2": ("assets/audio/non-free/winAPrize2.wav", 1.0),
}

class AudioController:
    def __init__(self, eventService: EventService):
        self.globalVolume = 0.5
        self.musicVolume = 1.0
        self.volumeIncrement = 0.05
        self.paused = True
        eventService.subscribe(MUSIC_END_EVENT, self._onMusicEnd)
        eventService.subscribe(READY_FOR_NEXT_PLAYER_EVENT, self._onReadyForNextPlayer)
        eventService.subscribe(INTERNAL_READY_FOR_NEXT_PLAYER_SOUND_DONE_EVENT, self._onNextPlayerSoundEnd)
        eventService.subscribe(IDLE_TIME_HIT_EVENT, self._onIdleStart)
        eventService.subscribe(INTERNAL_IDLE_SOUND_END_EVENT, self._onIdleSoundEnd)
        eventService.subscribe(INTERNAL_MUSIC_FADE_UP_EVENT, lambda _: self._onFadeEvent(True))
        eventService.subscribe(INTERNAL_MUSIC_FADE_DOWN_EVENT, lambda _: self._onFadeEvent(False))
        pygame.mixer.init()
        self._loadSounds()
        self._startWithRandomSong()
    
    def _loadSounds(self):
        pygame.mixer.music.set_endevent(MUSIC_END_EVENT)
        self.wheelSound = pygame.mixer.Sound(SOUNDS["wheelSound"][0])
        self.wheelSound.set_volume(SOUNDS["wheelSound"][1])
        self.slotsSound = pygame.mixer.Sound(SOUNDS["slotsSound"][0])
        self.slotsSound.set_volume(SOUNDS["slotsSound"][1])
        self.laughSound = pygame.mixer.Sound(SOUNDS["laughSound"][0]) 
        self.laughSound.set_volume(SOUNDS["laughSound"][1])
        self.middlePrizeSound = pygame.mixer.Sound(SOUNDS["middlePrizeSound"][0])
        self.middlePrizeSound.set_volume(SOUNDS["middlePrizeSound"][1])

        self._prizeDict = {
            Prize.singleMd: self.laughSound,
            Prize.singleSm: self.laughSound,
            Prize.doubleSm: self.middlePrizeSound,
            Prize.doubleMd: self.middlePrizeSound,
            Prize.singleSmAndSingleMd: self.middlePrizeSound,
            Prize.doubleSmAndSingleMd: self.middlePrizeSound,
            Prize.quadrupleSm: self.slotsSound,
            Prize.singleFullsized: self.slotsSound,
        }

        self._nextPlayerSounds = [
            ("greatestShowInTown", pygame.mixer.Sound(SOUNDS["greatestShowInTown"][0])),
            ("playTheGame", pygame.mixer.Sound(SOUNDS["playTheGame"][0])),
            ("playTheGame2", pygame.mixer.Sound(SOUNDS["playTheGame2"][0])),
            ("stepRightUp", pygame.mixer.Sound(SOUNDS["stepRightUp"][0])),
            ("stepRightUp2", pygame.mixer.Sound(SOUNDS["stepRightUp2"][0])),
            ("stepRightUp3", pygame.mixer.Sound(SOUNDS["stepRightUp3"][0])),
            ("stepRightUp4", pygame.mixer.Sound(SOUNDS["stepRightUp4"][0])),
            ("stepRightUp5", pygame.mixer.Sound(SOUNDS["stepRightUp5"][0])),
            ("winAPrize", pygame.mixer.Sound(SOUNDS["winAPrize"][0])),
            ("winAPrize2", pygame.mixer.Sound(SOUNDS["winAPrize2"][0])),
        ]

        self._idleSounds = [
            *self._nextPlayerSounds,
            ("singingGhosts1", pygame.mixer.Sound(SOUNDS["singingGhosts1"][0])),
            ("singingGhosts2", pygame.mixer.Sound(SOUNDS["singingGhosts2"][0])),
            ("beast", pygame.mixer.Sound(SOUNDS["beast"][0])),
            ("ghost4", pygame.mixer.Sound(SOUNDS["ghost4"][0])),
            ("heartbeat", pygame.mixer.Sound(SOUNDS["heartbeat"][0])),
            ("jumpscare", pygame.mixer.Sound(SOUNDS["jumpscare"][0])),
            ("thunder", pygame.mixer.Sound(SOUNDS["thunder"][0])),
            ("werewolf", pygame.mixer.Sound(SOUNDS["werewolf"][0])),
            ("wind", pygame.mixer.Sound(SOUNDS["wind"][0]))
        ]

    def _startWithRandomSong(self):
        self.currentSongIndex = random.randint(0, len(MUSIC) - 1)
        self._playSongAtCurrentIndex()
    
    def _playSongAtCurrentIndex(self):
        (file, volume) = MUSIC[self.currentSongIndex]
        # file = "spooky.mp3"
        # volume = 1.0
        pygame.mixer.music.load("assets/audio/music/" + file)
        self._updateVolume()
        pygame.mixer.music.play(1)
        self.paused = False
    
    def playNextSong(self):
        self.currentSongIndex = (self.currentSongIndex + 1) % len(MUSIC)
        self._playSongAtCurrentIndex()
    
    def playPrevSong(self):
        self.currentSongIndex = self.currentSongIndex - 1
        self.currentSongIndex = len(MUSIC) - 1 if self.currentSongIndex < 0 else self.currentSongIndex
        self._playSongAtCurrentIndex()
    
    def pauseOrUnpauseSong(self):
        if (self.paused):
            self.paused = False
            pygame.mixer.music.unpause()
        else:
            pygame.mixer.music.pause()
            self.paused = True

    def playWheelSound(self):
        pygame.mixer.Sound.play(self.wheelSound)
    
    def playWinSoundBasedOnPrize(self, prize: Prize):
        pygame.mixer.Sound.play(self._prizeDict[prize], -1)
        self._currentWinSound = self._prizeDict[prize]
    
    def stopWinSound(self):
        pygame.mixer.Sound.stop(self._currentWinSound)
        self._currentWinSound = None
    
    def volumeUp(self):
        self.globalVolume = self.globalVolume + self.volumeIncrement
        self.globalVolume = 1.0 if self.globalVolume >= 1.0 else self.globalVolume
        self._updateVolume()

    def volumeDown(self):
        self.globalVolume = self.globalVolume - self.volumeIncrement
        self.globalVolume = 0.0 if self.globalVolume <= 0.0 else self.globalVolume
        self._updateVolume()

    def _updateVolume(self):
        print('update volume: g:' + str(self.globalVolume) + ' m:' + str(self.musicVolume))
        self.wheelSound.set_volume(SOUNDS["wheelSound"][1] * self.globalVolume)
        self.slotsSound.set_volume(SOUNDS["slotsSound"][1] * self.globalVolume)
        self.laughSound.set_volume(SOUNDS["laughSound"][1] * self.globalVolume)
        self.middlePrizeSound.set_volume(SOUNDS["middlePrizeSound"][1] * self.globalVolume)

        for soundName, sound in self._idleSounds:
            sound.set_volume(SOUNDS[soundName][1] * self.globalVolume)

        for soundName, sound in self._nextPlayerSounds:
            sound.set_volume(SOUNDS[soundName][1] * self.globalVolume)

        pygame.mixer.music.set_volume(MUSIC[self.currentSongIndex][1] * self.globalVolume * self.musicVolume)
    
    def _onMusicEnd(self, event):
        self.playNextSong()
    
    def _onReadyForNextPlayer(self, event):
        if (random.choice([True, False])):
            return
        self._fadeMusic(.4, 1)
        (soundName, sound) = random.choice(self._nextPlayerSounds)
        self.nextPlayerSoundChannel = pygame.mixer.Sound.play(sound)
        print("playing next player sound: " + soundName)
        self.nextPlayerSoundChannel.set_endevent(INTERNAL_READY_FOR_NEXT_PLAYER_SOUND_DONE_EVENT)
    
    def _onNextPlayerSoundEnd(self, event):
        self._fadeMusic(1.0, 1)
        print('next player sound done')
        self.nextPlayerSoundChannel.set_endevent()
    
    def _onIdleStart(self, event):
        print('idle sound start')
        self._fadeMusic(.1, 2)
        pygame.time.set_timer(IDLE_TIME_HIT_EVENT, 0)
        (soundName, sound) = random.choice(self._idleSounds)
        self.idleSoundChannel = pygame.mixer.Sound.play(sound)
        print("playing idle sound: " + soundName)
        self.idleSoundChannel.set_endevent(INTERNAL_IDLE_SOUND_END_EVENT)
    
    def _onIdleSoundEnd(self, event):
        self._fadeMusic(1.0)
        print('idle sound done')
        pygame.time.set_timer(IDLE_TIME_HIT_EVENT, IDLE_TIME)
        self.idleSoundChannel.set_endevent()
    
    def _fadeMusic(self, level, fadeTime = 5):
        direction = self.musicVolume < level
        self.fadeLoops = max(round(abs(self.musicVolume - level) / self.volumeIncrement), 1)

        if (self.fadeLoops == 0):
            return

        self.fadeTimeout = max(round(fadeTime * 1000 / self.fadeLoops), 1)
        pygame.time.set_timer(
            INTERNAL_MUSIC_FADE_UP_EVENT if direction else INTERNAL_MUSIC_FADE_DOWN_EVENT, self.fadeTimeout, self.fadeLoops)
    
    def _onFadeEvent(self, direction):
        self.musicVolume = self.musicVolume + (self.volumeIncrement if direction else -self.volumeIncrement)
        if (self.musicVolume > 1):
            self.musicVolume = 1.0
        if (self.musicVolume < 0):
            self.musicVolume = 0.0

        self._updateVolume()
        self.fadeLoops = self.fadeLoops - 1
        if (self.fadeLoops == 0):
            pygame.time.set_timer(
                INTERNAL_MUSIC_FADE_UP_EVENT if direction else INTERNAL_MUSIC_FADE_DOWN_EVENT, 0)
        else:
            pygame.time.set_timer(
                INTERNAL_MUSIC_FADE_UP_EVENT if direction else INTERNAL_MUSIC_FADE_DOWN_EVENT, self.fadeTimeout)