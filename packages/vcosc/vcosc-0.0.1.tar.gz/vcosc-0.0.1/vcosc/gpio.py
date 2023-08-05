import time
import select

class GPIO:
    def __init__(self):
        self.path = '/sys/class/gpio/gpio'
        self.address_pins   = [23, 22] 
        self.strobe_pins    = [24, 25]
        self.trigger_pins   = [4, 14, 15, 7, 8, 9, 10, 11] 

        self.data_pins      = [27, 17, 3, 2, 31, 30, 29, 28] 


    def __make_path(self, pin, endpoint):
        return self.path + str(pin) + '/' + endpoint

    def __bin(self, number, width=2):
        """ Takes an integer and an optional 
            width (default is 2) and returns 
            a string representation of the binary 
            literal with leading zeros where appropriate.
        """
        # validate range & force 0 for numbers out of range
        number = number if number >= 0 and number <= 2**width else 0

        # Convert to python's binary literal format
        binary_number = bin(number)

        # Trim 0b prefix
        binary_number = binary_number[2:]

        # Pad with zeros if needed
        if len(binary_number) != width:
            zeros = ''.join(['0' for zero in range(width - len(binary_number))])
            binary_number = '%s%s' % (zeros, binary_number)

        return binary_number

    def set(self, pin, endpoint, value):
        """ Opens the given file representation for
            a valid GPIO pin and writes a value to it

            To output, first set /direction to 'out', 
            then set /value to desired value
        """
        with open(self.__make_path(pin, endpoint), 'w') as file:
            file.write('%s%s' % (str(value), '\n'))

    def get(self, pin):
        """ Opens the /value file for a valid GPIO pin for reading,
            then sets /description to 'in' and /edge to 'both'
            before returning the current value from /value
        """
        with open(self.__make_path(pin, 'value'), 'r') as file:
            self.set(pin, 'direction', 'in')
            self.set(pin, 'edge', 'both')

            poll = select.poll()
            poll.register(file, select.POLLPRI)

            return file.read(1)

    def dac(self, value, dac_id=0):
        """ Writes an 8 bit value to one of four special DACs, 
            addressed with ids between 0 and 3
        """
        # Convert dac_id to a 2 bit word 
        # represented as a list of strings
        address_values = list(self.__bin(dac_id % 4, 2))
        
        # Update address pins
        for index, address_value in enumerate(address_values):
            self.set(self.address_pins[index], 'direction', 'out')
            self.set(self.address_pins[index], 'value', address_value)

        # Convert 8 bit data to an 8 bit word 
        # represented as a list of strings
        data_values = list(self.__bin(value, 8))

        # Update data pins
        for index, data_value in enumerate(data_values):
            self.set(self.data_pins[index], 'direction', 'out')
            self.set(self.data_pins[index], 'value', data_value)

        # Set strobe pin low to update state,
        # then high to sample & hold
        strobe_id = 0 if dac_id <= 3 else 1
        self.set(self.strobe_pins[strobe_id], 'direction', 'out')
        self.set(self.strobe_pins[strobe_id], 'value', 0)
        self.set(self.strobe_pins[strobe_id], 'value', 1)

    def tick(self, length=0.1):
        pass


if __name__ == '__main__':
    # Test GPIO 

    gpio = GPIO()

    # Sweep each DAC
        #gpio.dac(0, dac_id)
    dac_id =7
    for i in range(10):
        for value in range(0, 2**8, 25):
            print 'Sending', value, 'to DAC', dac_id
            time.sleep(0.5)
            gpio.dac(value, dac_id)

    print 'Testing input'
    for i in range(10):
        print 'Pin 23 set:', gpio.get(23)
        time.sleep(0.2)

