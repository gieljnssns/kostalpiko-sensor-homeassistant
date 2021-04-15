## I will archive this custom component since my Kostal inverter is broken and I can not test any changes, you should try https://github.com/rcasula/kostalpiko-homeassistant

# kostalpiko-sensor-homeassistant
A custom component to get the readings of a Kostal Piko inverter NOT the Plenticore inverter

Since the component is based on web scraping from the web server interface, your web server should look like this.
You can try like this
```
http://pvserver:<YOUR_PASSWORD>@<YOUR_INVERTER_IP>/index.fhtml
```
Otherwise it will not work

![Alt text](https://github.com/gieljnssns/kostalpiko-sensor-homeassistant/blob/master/img/Schermafbeelding%202020-03-30%20om%2011.25.18.png?raw=true "Optional Title")

```
sensor:
  - platform: kostal
    host: !secret kostal_host  # "http://192.168.xx.xx"
    username: !secret kostal_username
    password: !secret kostal_password
    monitored_conditions:
      - solar_generator_power  # only available when using a BA sensor
      - consumption_phase_1    # only available when using a BA sensor
      - consumption_phase_2    # only available when using a BA sensor
      - consumption_phase_3    # only available when using a BA sensor
      - current_power
      - total_energy
      - daily_energy
      - string1_voltage
      - string1_current
      - string2_voltage
      - string2_current
      - l1_voltage
      - l1_power
      - l2_voltage
      - l2_power
      - l3_voltage
      - l3_power
      - status
```
