import state.leds as leds
from threading import Thread
from time import sleep


STATE_IDLE = 0
STATE_READY = 1
STATE_STARTED = 2
STATE_ERROR = 1000
READY_LIMIT = 4 * 30 # 30 Seconds
STARTED_LIMIT = 1 # .25 Seconds
ERROR_LIMIT = 4 * 30 # 30 Seconds


class EventHandler:
    def __init__(self, red=leds.RED, green=leds.GREEN, blue=leds.BLUE):
        self.current = STATE_IDLE
        self.idle_count = 0
        self.set_led_for_state()
        self.red = red
        self.green = green
        self.blue = blue

    def startup(self):
        t = Thread(target=self.startup_indicator)
        t.start()

    @staticmethod
    def next_startup_color(current):
        if current == leds.RED:
            return leds.GREEN
        elif current == leds.GREEN:
            return leds.BLUE
        else:
            return leds.RED

    def startup_indicator(self):
        leds.turn_all_off()
        led_color = leds.RED
        count = 0
        while self.current == STATE_IDLE and count < 10:
            leds.turn_on(led_color)
            leds.turn_on(leds.RED)
            led_color = EventHandler.next_startup_color(led_color)
            sleep(0.25)
        if self.current == STATE_IDLE:
            leds.turn_all_off()

    def set_leds(self, red=leds.RED, green=leds.GREEN, blue=leds.BLUE):
        self.red = red
        self.green = green
        self.blue = blue

    def booted_system_connected(self):
        self.current = STATE_STARTED
        self.set_led_for_state()
        self.idle_count = 0

    def unknown_system_connected(self):
        if self.current == STATE_ERROR or self.current == STATE_IDLE:
            self.current = STATE_READY
            self.set_led_for_state()
            self.idle_count = 0

    def error(self):
        self.current = STATE_ERROR
        self.set_led_for_state()

    def no_connection(self):
        if self.current == STATE_READY:
            self.idle_count += 1
            if self.idle_count > READY_LIMIT:
                self.current = STATE_IDLE
                self.set_led_for_state()
        if self.current == STATE_STARTED:
            self.idle_count += 1
            if self.idle_count > STARTED_LIMIT:
                self.current = STATE_IDLE
                self.set_led_for_state()
        if self.current == STATE_ERROR:
            self.idle_count += 1
            if self.idle_count > ERROR_LIMIT:
                self.current = STATE_IDLE
                self.set_led_for_state()

    def handle_connection(self, vendor):
        if vendor == "udhcp 1.23.1":
            self.booted_system_connected()

    def set_led_for_state(self):
        state = self.current
        if state == STATE_IDLE:
            leds.turn_all_off()
        elif state == STATE_READY:
            leds.turn_on(self.blue)
        elif state == STATE_STARTED:
            leds.turn_on(self.green)
        else:
            leds.turn_on(self.red)
