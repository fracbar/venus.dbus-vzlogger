# venus.dbus-vzlogger

Venus OS dbus service for volkszaehler.org (vzlogger)

## Purpose

This is a service implementation for Venus OS querying an energy meter (based on vzlogger) and providing those values in DBUS for
"com.victronenergy.grid" (grid meter).

It's based on latest examples from: https://github.com/victronenergy/velib_python

## Installation

Currently only manual installaion is supported:

* enable SSH access to your Venus OS
* create folder `/data/dbus-vzlogger`
* copy `dbus-vzlogger.py` and `service` folder there
* configure (see next section)
* test it manually: `python dbus-vzlogger.py`
* if "volkszaehler.org" service appears, create `/data/rc.local` file (chmod 755) with the following content:

      ln -s /data/dbus-vzlogger/service /service/dbus-vzlogger

## Configuration

Assuming your Volkzszaehler.org is already installed, please modify constants in `dbus-vzlogger.py`:

* VZLOGGER_URL: the URL to your Volkszaehler.org response (example: "http://192.168.10.35:8090")
* VZLOGGER_CONSUMPTION_UUID: UUID from current power consumption: (example: "dbc081e0-f188-11e2-8e30-3dd74b6c6043")
* VZLOGGER_REVERSE_UUID: UUID from overall sold energy (example: "8a834b00-fa42-11e7-a4b9-df1027ed2346")
* VZLOGGER_FORWARD_UUID: UUID from overall buying energy (example: "5078fef0-fa42-11e7-a3aa-8fcd37e01f0e")

This is an example of my response:

    {
     "version": "0.8.2",
     "generator": "vzlogger",
     "data": [
       {
         "uuid": "5078fef0-fa42-11e7-a3aa-8fcd37e01f0e",
         "last": 1689520983761,
         "interval": -1,
         "protocol": "sml",
         "tuples": [
          [
            1689520983761,
            1212.1
          ]
         ]
        },
        ...
     ] 
    }

## Tested on

* Raspberry Pi 3B+ - For running Venus OS
* Raspberry Pi 3B+ - For running Volkszaehler.org (version vzlogger 0.8.2)
* Victron MultiPlus-II 3000 - Battery Inverter (single phase)
* Pylontech US3000 - LiFePO Battery

## Credits

Thanks to:

* People from volkszaehler.org
* RalfZim (https://github.com/RalfZim) for sharing his dbus service for Fronius energy meter
* Victron for supporting OS community