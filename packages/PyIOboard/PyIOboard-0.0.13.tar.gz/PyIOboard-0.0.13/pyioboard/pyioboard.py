from time import sleep
import serial
import io

class RelayBoard(object):
    def __init__(self, serial_port, serial_obj=None):
        '''Accepts a serial port and will create a pyserial connection, otherwise you can pass in serial_port = "dummy"
        and pass in a mock serial object'''
        self.__serial_port = serial_port
        if serial_obj == None:
            self.__openport()
        else:
            self._serial = serial_obj

    def __enter__(self):
        if self._serial == None:
            self.__openport()
        return self

    def __exit__(self, type, value, traceback):
        if self._serial != None:
            self._serial.close()

    def __openport(self):
        try:
            self._serial = serial.Serial(self.__serial_port, 19200, timeout=0.5)
        except Exception, e:
            print "Could not open port"
            raise


    def gpio_read(self, pin):
	status = "ERROR"
        self._serial.write("gpio read "+ str(pin) + "\n\r")
        response = self._serial.read(25)
        if response[-4] == "1":
            status = "on"
        elif response[-4] == "0":
            status = "off"
        return status


    def gpio_set(self, pin):
        self._serial.write("gpio set "+ str(pin) + "\n\r")
        return 'set'


    def gpio_clear(self, pin):
        self._serial.write("gpio clear "+ str(pin) + "\n\r")


    def relay_read(self, relay):
        self._serial.write("relay read "+ str(relay) + "\n\r")
        response = self._serial.read(25)
        if(response.find("on") > 0):
            return "on"
        elif(response.find("off") > 0):
            return "off"
        else:
            return "ERROR"


    def relay_set(self, relay, command):
        if command == 'on' or command == 'off':
            relay = int(relay)
            self._serial.write("relay "+ str(command) +" "+ str(relay) + "\n\r")
        else:
            return "ERROR"
        status = self.relay_read(relay)
        if status == "ERROR":
            return status
        elif status == command:
            return "success"
        else:
	    sleep(1)
	    if status == command:
		return "success"
            return "failure"



if __name__ == "__main__":
    pass
