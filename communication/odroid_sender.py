import struct, logging
from sender import Sender

class OdroidSender(Sender):
    def __init__(self, protocol):
        super().__init__(protocol)
        self.proto = protocol["TO_ODROID"]

    def sendControl(self, msg):
        if msg[0] == self.control_spec['START_TELEMETRY']:
            tx_buffer = [self.proto["CONTROL"]]+msg
            tx_buffer = struct.pack('<2BI',*(tx_buffer))
            self.send_msg(tx_buffer)
        elif msg[0] == self.control_spec['STOP_TELEMETRY']:
            tx_buffer = [self.proto["CONTROL"]]+msg
            tx_buffer = struct.pack('<2B',*(tx_buffer))
            self.send_msg(tx_buffer)

        elif msg[0] == self.control_spec['START_PID']:
            tx_buffer = [self.proto["CONTROL"]]+msg
            tx_buffer = struct.pack('<2BI',*(tx_buffer))
            self.send_msg(tx_buffer)

        elif msg[0] == self.control_spec['STOP_PID']:
            tx_buffer = [self.proto["CONTROL"]]+msg
            tx_buffer = struct.pack('<2B',*(tx_buffer))
            self.send_msg(tx_buffer)
        elif msg[0]==self.control_spec['START_AUTONOMY']:
            tx_buffer = [self.proto["CONTROL"]]+msg
            tx_buffer = struct.pack('<2B',*(tx_buffer))
            self.send_msg(tx_buffer)

        elif msg[0]==self.control_spec['STOP_AUTONOMY']:
            tx_buffer = [self.proto["CONTROL"]]+msg
            tx_buffer = struct.pack('<2B',*(tx_buffer))
            self.send_msg(tx_buffer)
        elif msg[0]==self.control_spec['MODE']:
            tx_buffer = [self.proto["CONTROL"]]+msg
            tx_buffer = struct.pack('<3B',*(tx_buffer))
            self.send_msg(tx_buffer)


    def sendPIDRequest(self, axis):
        if axis=='roll':
            spec=self.pid_spec["roll"]
        elif axis =='pitch':
            spec = self.pid_spec["pitch"]
        elif axis == 'yaw':
            spec = self.pid_spec["yaw"]
        elif axis=='depth':
            spec=self.pid_spec["depth"]
        elif axis =='all':
            spec = self.pid_spec["all"]
        else:
            logging.debug(f"{axis} is not a valid argument of pidSend. Valid arguments: 'roll', 'pitch', 'yaw', 'all'")
            return
        tx_buffer = [self.proto["PID_REQUEST"],spec]
        tx_buffer = struct.pack('<2B',*(tx_buffer))
        self.send_msg(tx_buffer)

    def sendBoatDataRequest(self):
        tx_buffer = [self.proto["BOAT_DATA_REQUEST"]]
        tx_buffer = struct.pack('<B',*(tx_buffer))
        self.send_msg(tx_buffer)

    def sendInput(self, data):
        tx_buffer=[self.proto['PAD']]+data
        tx_buffer = struct.pack('<B2f3i',*(tx_buffer))
        self.send_msg(tx_buffer)
        if(self.checked==False):
            self.checked = True
            logging.debug("Msg was sent succesfully, connection with odroid has been established")
