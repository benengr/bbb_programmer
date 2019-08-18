import RPi.GPIO as GPIO

OFF = 1
ON = 0


def init_gpio():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)


def init_led(led):
    GPIO.setup(led, GPIO.OUT)


def turn_off(led):
    GPIO.output(led, OFF)


def turn_on(led):
    GPIO.output(led, ON)
