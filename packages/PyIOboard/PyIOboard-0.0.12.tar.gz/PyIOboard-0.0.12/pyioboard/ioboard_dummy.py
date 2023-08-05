


class iodummy(object):
    def __init__(self):
        self.__gpio_state = {01: 0, 2: 0, 3: 0, 4: 0, 5: 0, 0: 0}
        self.__relay_state = {1: 0, 2: 0, 3: 0, 0: 0}
        self.__buffer = ''

    def _get_pin(self, msg):
        return [int(s) for s in msg.split() if s.isdigit()][0]


    def read(self, size=1):
        buf = self.__buffer
        self.__buffer == ''
        return buf


    def write(self, msg):
        pin = self._get_pin(msg)
        if "relay" in msg:
            if "read" in msg:
                if  self.__relay_state[pin] == 1:
                    status = "on"
                else:
                    status = "off"
                self.__buffer = str("relay {0} is {1}".format(pin, status))
            elif "on" in msg:
                self.__relay_state[pin] = 1
            elif "off" in msg:
                self.__relay_state[pin] = 0
        elif "gpio" in msg:
            pass



    def close(self):
        pass

