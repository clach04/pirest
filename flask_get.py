#!/usr/bin/env python3
# https://www.raspberrypi.org/documentation/usage/gpio/python/README.md

import datetime
import json
import logging
import os
import sys
from time import sleep

is_win = (sys.platform == 'win32')

if is_win:
    # hack for bug https://github.com/RPi-Distro/python-gpiozero/issues/600
    os.environ['GPIOZERO_PIN_FACTORY'] = os.environ.get('GPIOZERO_PIN_FACTORY', 'mock')
    # Alternatively SET GPIOZERO_PIN_FACTORY=mock

from gpiozero import LED

from flask import Flask, abort, request


version_tuple = (0, 0, 1)
version = version_string = __version__ = '%d.%d.%d' % version_tuple
__author__ = 'clach04'

log = logging.getLogger(__name__)
logging.basicConfig()  # TODO include function name/line numbers in log
log.setLevel(level=logging.DEBUG)  # Debug hack!

log.info('Python %s on %s', sys.version, sys.platform)


dump_json = json.dumps
load_json = json.loads

app = Flask(__name__)

## DEBUG dev hack for browser testing!
"""
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response
"""


@app.route("/")
def hello():
    return 'nello'

def control_gpio(gpio_pin):
    # assumes OUT
    # assumes momentary toggle to (hard coded) high/on - hard coded time
    # assumes returns current timestamp
    relay_time = 0.5   # 0.5 seconds
    log.debug('about to momentary toggle gpio/BCM %d', gpio_pin)
    led = LED(gpio_pin)

    led.on()  # FIXME use blink() with n=1
    sleep(relay_time)
    led.off()

    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")


def trigger_emulation(config):
    status = 'LOCKED'  # may not be a good default status
    action = request.args.get('action')
    log.info('GET action %r', action)
    if action in ('state', 'status'):
        return 'LOCKED'
    else:
        # open or close
        gpio_pin = config['status'][action]
        result = control_gpio(gpio_pin)
        if action == 'open':
            status = 'UNLOCKED'
        elif action == 'open':
            status = 'LOCKED'
    return status

@app.route("/<path:url_path>")
def any_path(url_path):
    log.info('path %s', url_path)
    d = url_mapping.get(url_path)
    if d:
        if d.get('status'):
            return trigger_emulation(d)
        gpio_pin = d['gpio']  # TODO handle bad config? What if this key is missing? Config validator would avoid this
        return control_gpio(gpio_pin)
    else:
        abort(404)


if __name__ == "__main__":
    argv = sys.argv

    try:
        config_filename = argv[1]
    except IndexError:
        config_filename = 'config.json'
    log.info('Using config file %r', config_filename)

    f = open(config_filename, 'rb')
    data = f.read()
    data = data.decode('utf-8')
    f.close()

    config = load_json(data)
    url_mapping = config['urls']

    cert_path, key_path = '', ''
    default_config = {
        'debug': False,
        'port': 8080,
        'host': '127.0.0.1',
        #'ssl_context': (cert_path, key_path)
    }
    default_config.update(config['config'])
    config['config'] = default_config

    settings = config['config']
    # dumb "comment" support, remove any keys that start with a "#"
    for key in list(settings.keys()):
        if key.startswith('#'):
            del(config['config'][key])
    log.info('Serving on http://%s:%d', settings['host'], settings['port'])
    app.run(**settings)
