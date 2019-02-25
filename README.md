# Pi REST - pirest

Yet another Raspberry Pi GPIO REST (like) interface.

Consider these alternatives!:

   * WebIOPi / Cayenne http://webiopi.trouch.com/
   * https://github.com/ThisIsQasim/WebGPIO
   * https://github.com/projectweekend/Pi-GPIO-Server

Right now this responds to GETs, so not exactly RESTful.
A GET will result in a (GPIO) side effect!

## Getting Started

If installing/working with a source checkout issue:

    pip install -r requirements.txt

Run:

    cp example_config.json config.json
    python flask_get.py

Then open a browser to http://localhost:8080/led_17 or issue:

    curl http://localhost:8080/led_17

NOTE `http://localhost:8080/led_17` will work but `http://localhost:8080/led_17/` will *not*.

## pirest service

Systemd service (e.g. for Raspbian).

Based on https://www.raspberrypi.org/documentation/linux/usage/systemd.md

NOTE hard coded `WorkingDirectory=/home/pi/py/pirest` in `pirest.service`.

Install

    cd scripts
    sudo cp pirest.service /etc/systemd/system/pirest.service
    sudo chmod 644 /etc/systemd/system/pirest.service
    sudo systemctl enable pirest.service

Useage

    sudo systemctl stop pirest.service
    sudo systemctl start pirest.service
    sudo systemctl restart pirest.service
    sudo systemctl status pirest.service


    systemctl list-unit-files --state=enabled | grep pirest

## Trigger Android app

The sample config file has an entry for a garage that works with https://github.com/mwarning/trigger

NOTE at this time, this is experimental as the token is **ignored** and https is not implemented.
