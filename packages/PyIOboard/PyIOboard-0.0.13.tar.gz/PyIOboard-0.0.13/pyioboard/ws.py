#!/usr/bin/env python

from pyioboard import RelayBoard
from bottle import route, run, get, post, Bottle
from paste import httpserver
from datetime import datetime


def create_ws(relayboard, settings):
    app = Bottle()


    @app.get('/')
    def index():
        return "USB IO RelayBoard Interface"

    @app.get('/status')
    def all_status():
        status = {'serialport': settings['serialport'],
                  'gpio': {},
                  'relay': {}
                  }

        for pin in settings['gpios']:
            status['gpio'][pin] = relayboard.gpio_read(pin)

        for relay in settings['relays']:
            status['relay'][relay] = relayboard.relay_read(relay)

        return status

    @app.get('/relay/:relay/:command')
    def relay_command(relay, command):
        if command == 'status':
            return relayboard.relay_read(relay)
        else:
            return relayboard.relay_set(relay, command)




    return app




if __name__ == "__main__":
    pass
