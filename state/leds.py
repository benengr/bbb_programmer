import RPi.GPIO as GPIO

OFF = 0
RED = 1
BLUE = 2
GREEN = 3

LEDS = [RED, BLUE, GREEN]

GPIO.setmode(GPIO.BOARD)
for led in LEDS:
    GPIO.setup(led, GPIO.OUT)


def turn_all_off():
    for led in LEDS:
        GPIO.output(led, 0)


def turn_on(led):
    turn_all_off()
    GPIO.output(led, 1)
