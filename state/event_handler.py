import state.leds as leds


STATE_IDLE = 0
STATE_READY = 1
STATE_STARTED = 2
STATE_ERROR = 1000
READY_LIMIT = 4 * 30 # 30 Seconds
STARTED_LIMIT = 1 # .25 Seconds
ERROR_LIMIT = 4 * 30 # 30 Seconds

class EventHandler:
    def __init__(self):
        self.current = STATE_IDLE
        self.idle_count = 0
        self.set_led_for_state()

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

    def set_led_for_state(self):
        state = self.current
        if state == STATE_IDLE:
            leds.turn_all_off()
        elif state == STATE_READY:
            leds.turn_on(leds.BLUE)
        elif state == STATE_STARTED:
            leds.turn_on(leds.GREEN)
        else:
            leds.turn_on(leds.RED)
