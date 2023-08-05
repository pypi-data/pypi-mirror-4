import OSC
import time
import threading
from vcosc import gpio

class Daemon:
    def __init__(self):
        self.address = ('192.168.1.222', 9000)
        self.server = OSC.OSCServer(self.address)
        self.server.addDefaultHandlers()

        output = gpio.GPIO()

        self.server.addMsgHandler('/dac', self.dac)
        st = threading.Thread(target=self.server.serve_forever)
        print 'before start'
        st.start()
        print 'after start'


    def dac(self, path, tags, args, source):
        print path, tags, args, source
        #gpio.dac(args, 0)


class Client:
    def __init__(self, address, port):
        # Set the network address for the pi's osc server
        self.daemon_address = (address, port)

        # Instantiate a client and connect to the server
        self.osc_client = OSC.OSCClient()
        self.osc_client.connect(self.daemon_address)

    def bundle(self, messages):
        """ Takes a list of tuple size three messages of the format:
            ('/address', 'data', 'ms from now')
        """

        container_bundle = OSC.OSCBundle()

        for message in messages:
            print message
            message_bundle = OSC.OSCBundle('', time.time() + float(message[2]))

            message_bundle.append({'addr': message[0], 'args': message[1]})
            container_bundle.append(message_bundle)

        print container_bundle

        self.osc_client.send(container_bundle)

