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
    def __init__(self, red:int, green:int, blue:int):
        self.current = STATE_IDLE
        self.idle_count = 0
        self.set_led_for_state()
        self.red = red
        self.green = green
        self.blue = blue
        self.init_leds()

    def startup(self):
        t = Thread(target=self.startup_indicator)
        t.start()

    def next_startup_color(self, current):
        if current == self.red:
            return self.green
        elif current == self.green:
            return self.blue
        else:
            return self.red

    def init_leds(self):
        leds.init_led(self.red)
        leds.init_led(self.green)
        leds.init_led(self.blue)

    def turn_all_off(self):
        leds.turn_off(self.red)
        leds.turn_off(self.blue)
        leds.turn_off(self.green)

    def turn_on(self, led):
        self.turn_all_off()
        leds.turn_on(led)

    def startup_indicator(self):
        self.turn_all_off()
        led_color = self.red
        count = 0
        while self.current == STATE_IDLE and count < 10:
            print(f'Starup Loop {count}')
            self.turn_on(led_color)
            led_color = self.next_startup_color(led_color)
            sleep(0.25)
            count += 1
        if self.current == STATE_IDLE:
            self.turn_all_off()

    def set_leds(self, red: int, green: int, blue: int):
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
            self.turn_all_off()
        elif state == STATE_READY:
            self.turn_on(self.blue)
        elif state == STATE_STARTED:
            self.turn_on(self.green)
        else:
            self.turn_on(self.red)
