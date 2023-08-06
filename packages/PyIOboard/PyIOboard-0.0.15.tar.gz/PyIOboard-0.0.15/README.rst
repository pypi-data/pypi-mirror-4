USAGE
=======

NOTE: The user running the script calling the relayboard code, must have permissions to use the serial port you are trying to communicate via.

You can use the module directly via other scripts, or via the webservice.



Sample Web Service
--------------------

.. code-block:: python
    from paste import httpserver
    from pyioboard import RelayBoard, ws

    settings = {"serialport":'/dev/ttyACM0',
                "gpios": [0, 1, 2, 3, 4, 5],
                "relays": [0, 1, 2, 3],
                }

    with RelayBoard(settings['serialport']) as relayboard:
        app = ws.create_ws(relayboard, settings)
        httpserver.serve(app, host='0.0.0.0', port=8080)
