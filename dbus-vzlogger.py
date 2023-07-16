#!/usr/bin/env python

"""
Used https://github.com/victronenergy/velib_python/blob/master/dbusdummyservice.py (as spec) and
https://github.com/RalfZim/venus.dbus-fronius-smartmeter (as impl) as basis for this service.

Reading information from the (in Germany very popular) https://wiki.volkszaehler.org/http (using REST API)
and puts the info on dbus.
"""
from gi.repository import GLib
import platform
# import argparse
import logging
import sys
import os
import requests  # for http GET

# our own packages
sys.path.insert(1, os.path.join(os.path.dirname(__file__), '../ext/velib_python'))
from vedbus import VeDbusService

VZLOGGER_URL="http://192.168.10.35:8090"
VZLOGGER_CONSUMPTION_UUID="dbc081e0-f188-11e2-8e30-3dd74b6c6043"
VZLOGGER_REVERSE_UUID="8a834b00-fa42-11e7-a4b9-df1027ed2346"
VZLOGGER_FORWARD_UUID="5078fef0-fa42-11e7-a3aa-8fcd37e01f0e"


class DbusDummyService:
    def __init__(self, servicename, deviceinstance, paths, productname='volkszaehler.org',
                 connection='volkszaehler.org service'):
        self._dbusservice = VeDbusService(servicename)
        self._paths = paths

        logging.debug("%s /DeviceInstance = %d" % (servicename, deviceinstance))

        # Create the management objects, as specified in the ccgx dbus-api document
        self._dbusservice.add_path('/Mgmt/ProcessName', __file__)
        self._dbusservice.add_path('/Mgmt/ProcessVersion',
                                   'Unkown version, and running on Python ' + platform.python_version())
        self._dbusservice.add_path('/Mgmt/Connection', connection)

        # Create the mandatory objects
        self._dbusservice.add_path('/DeviceInstance', deviceinstance)
        self._dbusservice.add_path('/ProductId', 16)  # value used in ac_sensor_bridge.cpp of dbus-cgwacs
        self._dbusservice.add_path('/ProductName', productname)
        self._dbusservice.add_path('/FirmwareVersion', 0.1)
        self._dbusservice.add_path('/HardwareVersion', 0)
        self._dbusservice.add_path('/Connected', 1)

        for path, settings in self._paths.items():
            self._dbusservice.add_path(
                path, settings['initial'], writeable=True, onchangecallback=self._handlechangedvalue)

        GLib.timeout_add(1000, self._update)  # pause 1000ms before the next request

    def _update(self):
        meter_r = requests.get(url=VZLOGGER_URL)
        meter_data = meter_r.json()
        logging.info("Getting response %s" % (meter_data))
        
        consumption_item = next(filter(lambda item: item['uuid'] == VZLOGGER_CONSUMPTION_UUID, meter_data['data']), {'tuples' : [[0, 0]]})
        reverse_item = next(filter(lambda item: item['uuid'] == VZLOGGER_REVERSE_UUID, meter_data['data']), {'tuples' : [[0, 0]]})
        forward_item = next(filter(lambda item: item['uuid'] == VZLOGGER_FORWARD_UUID, meter_data['data']), {'tuples' : [[0, 0]]})

        consumption = '{:4.2f}'.format(consumption_item['tuples'][0][1])
        consumption_1p = '{:4.2f}'.format(consumption_item['tuples'][0][1] / 3) # my meter is only providing sum of all phases

        self._dbusservice['/Ac/Power'] = consumption  # positive: consumption, negative: feed into grid
        #self._dbusservice['/Ac/L1/Voltage'] = 0 # not provided
        #self._dbusservice['/Ac/L2/Voltage'] = 0 # not provided
        #self._dbusservice['/Ac/L3/Voltage'] = 0 # not provided
        #self._dbusservice['/Ac/L1/Current'] = 0 # not provided
        #self._dbusservice['/Ac/L2/Current'] = 0 # not provided
        #self._dbusservice['/Ac/L3/Current'] = 0 # not provided
        self._dbusservice['/Ac/L1/Power'] = consumption_1p
        self._dbusservice['/Ac/L2/Power'] = consumption_1p
        self._dbusservice['/Ac/L3/Power'] = consumption_1p
        self._dbusservice['/Ac/Energy/Forward'] = '{:07.2f}'.format(forward_item['tuples'][0][1] / 1000)
        self._dbusservice['/Ac/Energy/Reverse'] = '{:07.2f}'.format(reverse_item['tuples'][0][1] / 1000)
        logging.info("House consumption: %s" % (consumption))
        return True

    def _handlechangedvalue(self, path, value):
        logging.debug("someone else updated %s to %s" % (path, value))
        return True  # accept the change


def main():
    logging.basicConfig(level=logging.INFO)

    from dbus.mainloop.glib import DBusGMainLoop
    # Have a mainloop, so we can send/receive asynchronous calls to and from dbus
    DBusGMainLoop(set_as_default=True)

    pvac_output = DbusDummyService(
        servicename='com.victronenergy.grid',
        deviceinstance=0,
        paths={
            '/Ac/Power': {'initial': 0},
            '/Ac/L1/Voltage': {'initial': 0},
            '/Ac/L2/Voltage': {'initial': 0},
            '/Ac/L3/Voltage': {'initial': 0},
            '/Ac/L1/Current': {'initial': 0},
            '/Ac/L2/Current': {'initial': 0},
            '/Ac/L3/Current': {'initial': 0},
            '/Ac/L1/Power': {'initial': 0},
            '/Ac/L2/Power': {'initial': 0},
            '/Ac/L3/Power': {'initial': 0},
            '/Ac/Energy/Forward': {'initial': 0},  # energy bought from the grid
            '/Ac/Energy/Reverse': {'initial': 0},  # energy sold to the grid
        })

    logging.info('Connected to dbus, and switching over to gobject.MainLoop() (= event based)')
    mainloop = GLib.MainLoop()
    mainloop.run()


if __name__ == "__main__":
    main()