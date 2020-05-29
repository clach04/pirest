#!/usr/bin/env python3

import datetime
import json
import logging
import os
import sys
from time import sleep

import paho.mqtt.client as paho

from flask import Flask, abort, request

try:
    if os.environ.get('SENTRY_DSN') is None:
        raise ImportError
    import sentry_sdk
    from sentry_sdk.integrations.flask import FlaskIntegration
    # dsn param to sentry_sdk.init() can be ommited if SENTRY_DSN environment variable is set
    def sentry_init():
        log.error('clach04 entry')
        sentry_sdk.init(
            integrations=[FlaskIntegration()]
        )
        sentry_sdk.capture_message('Starting')
except ImportError:
    def sentry_init():
        log.error('sentry_init() called without SENTRY_DSN or sentry_sdk')
        pass


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


@app.route('/debug-sentry')
def trigger_error():
    division_by_zero = 1 / 0

@app.route("/")
def hello():
    return 'nello'

def mqtt_send(mqtt_payload):
    (res, mid) =  mqttc.publish(mqtt_payload.get('topic'), mqtt_payload.get('message'))
    # TODO process/return res, mid - check for MQTT_ERR_SUCCESS
    log.info('res, mid %r / %r', res, mid)

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
        mqtt_payload = config['status'][action]
        result = mqtt_send(mqtt_payload)
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
        mqtt_payload = d['mqtt']  # TODO handle bad config? What if this key is missing? Config validator would avoid this
        return mqtt_send(mqtt_payload)
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
        #'ssl_context': 'adhoc'
        #'ssl_context': (cert_path, key_path)
    }
    default_config.update(config['config'])
    config['config'] = default_config
    config['mqtt'] = config.get('mqtt', {})
    config['mqtt']['mqtt_broker'] = config['mqtt'].get('mqtt_broker', 'localhost')
    config['mqtt']['mqtt_port'] = config['mqtt'].get('mqtt_port', 1883)

    settings = config['config']
    # dumb "comment" support, remove any keys that start with a "#"
    for key in list(settings.keys()):
        if key.startswith('#'):
            del(config['config'][key])
    protocol = 'http'
    if settings.get('ssl_context'):
        protocol = 'https'
        ssl_context = settings['ssl_context']
        if ssl_context != 'adhoc':
            settings['ssl_context'] = (ssl_context[0], ssl_context[1])

    sentry_init()

    mqttc = paho.Client()  # TODO pass in clientid
    mqttc.connect(config['mqtt']['mqtt_broker'], config['mqtt']['mqtt_port'])

    log.info('Serving on %s://%s:%d', protocol, settings['host'], settings['port'])
    app.run(**settings)
