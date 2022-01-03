import math

SLEEP_TIME = 5.0

class Heatsoak:
    def __init__(self, config):
        self.printer = config.get_printer()
        self.reactor = self.printer.get_reactor()
        self.gcode = self.printer.lookup_object('gcode')
        
        self.rate_target = config.getfloat('rate_target', default=0.25, above=0.)
        self.sensor_name = config.get('temp_sensor')

        self.gcode.register_command('HEATSOAK_BED', self.cmd_HEATSOAK_BED,
                                    desc=self.cmd_HEATSOAK_BED_help)
        self.gcode.register_command('HEATSOAK_CANCEL', self.cmd_HEATSOAK_BED_CANCEL,
                                    desc=self.cmd_HEATSOAK_BED_CANCEL_help)
        
        self.printer.register_event_handler("klippy:connect", self.handle_connect)

        self.timer = None
        self._reset_state()

    def handle_connect(self):
        try:
            self.v_sd = self.printer.lookup_object('virtual_sdcard')
        except self.printer.config_error:
            raise self.printer.config_error("Must enable virtual_sdcard in configuration")

        if self.sensor_name == 'heater_bed':
            self.heater_bed = self.printer.lookup_object('heater_bed')
        else:
            try:
                self.sensor = self.printer.lookup_object(self.sensor_name)
            except self.printer.config_error:
                raise self.printer.config_error("Unable to locate sensor named '%s'" % self.sensor_name)

    def _get_current_temperature(self, eventtime):
        if self.sensor_name == 'heater_bed':
            return self.heater_bed.get_status(eventtime)['temperature']
        else:
            return self.sensor.get_temp(eventtime)[0]
    
    def handle_timer(self, eventtime):
        temp_current = self._get_current_temperature(eventtime)

        rate_current = abs((temp_current - self.temp_last) / (SLEEP_TIME / 60.0))
        self.temp_last = temp_current
        
        # Save the last 12 rates (1 min worth of data)
        self.rates.append(rate_current)
        self.rates = self.rates[-12:]
        rate_mean = sum(self.rates) / len(self.rates)

        self.gcode.respond_info("Heatsoaking... rate_current=%.2f, rate_mean=%.2f, target=%.2f" % (rate_current, rate_mean, self.rate_target))
        if rate_mean <= self.rate_target:
            self.gcode.respond_info("Heatsoak complete")
            self._reset_state()
            self.v_sd.do_resume()

        return eventtime + SLEEP_TIME

    def _reset_state(self):
        if self.timer is not None:
            self.reactor.unregister_timer(self.timer)

        self.timer = None 
        self.heatsoaking = False
        self.temp_last = 0
        self.rates = []

    cmd_HEATSOAK_BED_help = "Heatsoak the bed"
    def cmd_HEATSOAK_BED(self, gcmd):
        if not self.heatsoaking:
            self.v_sd.do_pause()
            self.gcode.respond_info("Heatsoak starting")
            self.heatsoaking = True
            self.timer = self.reactor.register_timer(self.handle_timer, self.reactor.monotonic() + 0.1)
        else:
            self.gcode.respond_info("Already heatsoaking, skipping")

    cmd_HEATSOAK_BED_CANCEL_help = "Cancel the bed heatsoak"
    def cmd_HEATSOAK_BED_CANCEL(self, gcmd):
        if not self.heatsoaking:
            self.gcode.respond_info("Canceling heatsoak")
            self._reset_state()
            self.v_sd.do_resume()
        else:
            self.gcode.respond_info("Heatsoak is not running")


def load_config(config):
    return Heatsoak(config)