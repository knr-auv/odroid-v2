import json
from sender import Sender
import logging


class OdroidSender(Sender):
    def __init__(self, protocol):
        super().__init__(protocol)
        self.sender_proto = protocol["TO_JETSON"]

    def sendMotors(self,data):
        logging.debug("sending motors")
        frame = [self.sender_proto["MOTORS"]]+data
        logging.debug(f"frame: {frame}")
        frame=json.dumps(frame).encode("ansi")
        self.send_msg(frame)

    def sendBoatData(self, data =[]):
        logging.debug("sending boat data")
        frame = [self.sender_proto["BOAT_DATA"]]+data
        logging.debug(f"frame: {frame}")
        frame=json.dumps(frame).encode("ansi")
        self.send_msg(frame)
