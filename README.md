# Pi REST - pirest

Yet another Raspberry Pi -GPIO- MQTT REST (like) interface.

Quick and dirty HTTP/HTTPS to MQTT

Take a look at:

  * https://github.com/clach04/mqtt-launcher
  * https://github.com/flyte/pi-mqtt-gpio/
     * https://github.com/flyte/pi-mqtt-gpio/issues/38

Consider these alternatives!:

   * https://github.com/subzerobo/http-mqtt-bridge.
   * https://github.com/energieip/swh200-rest2mqtt-go
   * https://github.com/petkov/http_to_mqtt
   * https://github.com/JOxBERGER/REST-2-Mqtt
   * https://github.com/krambox/rest2mqtt

Right now this responds to GETs, so not exactly RESTful.
A GET will result in a (MQQT) publish side effect!

## Getting Started

If installing/working with a source checkout issue:

    pip install -r requirements.txt

Run:

    cp example_config.json config.json
    python flask_get.py

Then open a browser to http://localhost:8080/led_17 or issue:

    curl http://localhost:8080/led_17

NOTE `http://localhost:8080/led_17` will work but `http://localhost:8080/led_17/` will *not*.

## Sentry support

Optional:

    pip3 install --upgrade 'sentry-sdk[flask]==0.13.0'



## https / TLS / SSL support

NOTE this requires pyopenssl which is not installed via the requirements above.

Either install via `pip` or package manager for system, e.g.:

    sudo apt-get install python-openssl
    sudo apt-get install python3-openssl

or

    pip install pyopenssl

Edit json config file and add to the `config` section to add a Flask run setting for `ssl_context`.
Add either `adhoc` for quick and dirty testing or add certificate and key file names.

E.g. Uncomment one of the ssl_context entries:

    ....
    "config": {
        "debug": true,
        "host": "0.0.0.0",
        "port": 8080,
        "#ssl_context": "adhoc",
        "#ssl_context": ["cert.pem", "key.pem"],
    },
    ....

Example #2 requires files to exist in current directory, generated via something like:

    openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365

Which will generate a certificate valid for 1 year.


## pirest service

Systemd service (e.g. for Raspbian).

Based on https://www.raspberrypi.org/documentation/linux/usage/systemd.md

NOTE hard coded `WorkingDirectory=/home/pi/py/pirest` in `pirest.service`.

Install

    cd scripts
    sudo cp pirest.service /etc/systemd/system/pirest.service
    sudo chmod 644 /etc/systemd/system/pirest.service
    sudo systemctl enable pirest.service

Usage

    sudo systemctl stop pirest.service
    sudo systemctl start pirest.service
    sudo systemctl restart pirest.service
    sudo systemctl status pirest.service  # status and recent logs
    sudo systemctl status pirest.service -n 100  # show last 100 log entries
    journalctl  -u pirest.service  # show all logs

    sudo systemctl status pirest_https.service -n 100


    systemctl list-unit-files --state=enabled | grep pirest

NOTE if changing service files, e.g. adding `Environment`, restart config (not just specific service):

    sudo systemctl daemon-reload
    sudo systemctl restart pirest.service


## Trigger Android app

The sample config file has an entry for a garage that works with https://github.com/mwarning/trigger
and also https://github.com/openlab-aux/sphincter-remote/releases/tag/0.1.2

NOTE at this time, this is considered experimental as the token is **ignored**.

