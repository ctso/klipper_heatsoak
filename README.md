# Klipper Heatsoak Plugin

**WARNING**: Turns out this isn't working at the moment, as this is one big hack
around pausing the sdcard in order to make a cancelable heatsoak g-code command.  Stay tuned!

A Klipper plugin that heatsoaks your bed until the rate of temperature increase is below a
defined threshold.  The heatsoak can be canceled, which is often complicated to implement in
pure G-Code.

This is intended to be used with a temperature sensor embedded in the perimeter of the bed.

## Installation

This assumes you are installing on a distribution like [FluiddPi](https://github.com/fluidd-core/FluiddPi)
or [MainsailOS](https://github.com/mainsail-crew/MainsailOS).

```bash
cd /home/pi
git clone https://github.com/ctso/klipper_heatsoak
ln -sf /home/pi/klipper_heatsoak/heatsoak.py /home/klipper/klippy/extras/heatsoak.py
```

Configure Moonraker's update manager by adding the following to `moonraker.conf`:
```config
[update_manager client heatsoak]
type: git_repo
path: /home/pi/klipper_heatsoak
primary_branch: main
origin: https://github.com/ctso/klipper_heatsoak.git
install_script: install.sh
```

## Configuration
Make sure you have `virtual_sdcard` enabled!

```py
[heatsoak]
#rate_target:
#    The target heating rate of your temperature sensor in degrees per minute.
#    A value that is too low here is unlikely to converge.  Defaults to 0.25 degrees/min.
temp_sensor:
#    The name of the temperature sensor to use.  Use the full configuration section name
#    without quotes, for example temperature_sensor in_bed.  You may also specify
#    heater_bed here to use the bed's temperature sensor, however it is recommended
#    to use a sensor embedded in the bed.
#min_seconds:
#    The minimum amount of time, in seconds, to heatsoak.  Defaults to 30.
#max_seconds:
#    The maximum amount of time, in seconds, to heatsoak.  Defaults to 1800 (30 minutes).
#    Make sure your idle_timeout is larger than this maximum.
```

## Usage
This plugin aims to be as simple as possible, meaning it is up to you to set your bed temperature
and turn on any fans that you want running while heatsoaking.

Make sure that your idle timeout is set sufficiently high, as longer heatsoaks may cause idle timeout to
trigger, turning off your heater.

### G-Code Commands
This plugin adds the following G-Code commands:

- **HEATSOAK_BED**: Start heatsoaking the bed
- **HEATSOAK_BED_CANCEL**: Cancels the heatsoak