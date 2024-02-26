from pygame import mixer
from time import sleep

mixer.init()

sound1 = mixer.Sound('250Hz.wav')
sound2 = mixer.Sound('1kHz.wav')

sound1.play()
sleep(2)
sound2.play()
sleep(1)
sound1.fadeout(100)
sleep(1)
sound2.fadeout(100)


