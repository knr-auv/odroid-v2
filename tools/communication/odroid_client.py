import json
import logging
import socket
import struct
import time
from concurrent.futures import ThreadPoolExecutor

from dummy_data_provider import DummyDataProvider as ddp
from odroid_sender import OdroidSender
from odroid_parser import OdroidParser
from variable import *


class OdroidClient(OdroidParser, OdroidSender):
    def __init__(self, getPIDs, setPIDs, getMotors, protocol, addr=JETSON_ADDRESS):
        self.executor = ThreadPoolExecutor(max_workers=3)
        OdroidSender.__init__(self, protocol)
        OdroidParser.__init__(self, protocol)
        self.socket = None
        self.active_conn = None
        self.interval = None
        self.methodCollector(getPIDs, setPIDs, getMotors)
        self.connected = False
        self.host = addr[0]
        self.port = addr[1]
        self.active = True
        self.checked = False
        self.sendingActive = False

    def start_sending(self, interval=30):
        self.interval = interval / 1000
        self.executor.submit(self.loop)

    def stop_sending(self):
        self.sendingActive = False

    def loop(self):
        if self.connected:
            self.sendingActive = True
            logging.debug("Sending")

            while self.connected and self.sendingActive:
                time.sleep(self.interval)
                self.sendMotors(self.getMotors())

            self.sendingActive = False

    def methodCollector(self, getPIDs, setPIDs, getMotors):  # getDepth, getHummidity...
        self.getPIDs = getPIDs
        self.getMotors = getMotors
        self.setPIDs = setPIDs

    def client(self):
        try:
            logging.debug(("Connecting to: " + str(self.host) + ":" + str(self.port)))
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.active_conn = self.socket
            self.connected = True
        except (socket.gaierror, socket.error):
            self.connected = False
            logging.debug("Connection refused")
            return
        logging.debug("Socket now Connect with port:{}".format(self.port))
        rx_state = FRAME_SECTION["HEADER"]
        rx_len = 0

        while self.active:
            try:
                if rx_state == FRAME_SECTION["HEADER"]:
                    logging.debug("Header")

                    data = self.active_conn.recv(4)
                    if data == b'':
                        raise ConnectionResetError
                    rx_len = struct.unpack("<L", data)[0]
                    logging.debug(f"frame length: {rx_len}")
                    # rx_len -= 4
                    #logging.debug(rx_len)
                    rx_state = FRAME_SECTION["DATA"]

                elif rx_state == FRAME_SECTION["DATA"]:
                    logging.debug("Data")
                    data = self.active_conn.recv(rx_len)
                    self.executor.submit(self.parse,data)
                    rx_state = FRAME_SECTION["HEADER"]
            except ConnectionResetError:
                print("Disconnected from server.")
                return
            except socket.gaierror:
                logging.debug("Connection terminated")
                return
            except Exception as e:
                logging.debug(e)
                rx_state = FRAME_SECTION["HEADER"]

        self.active_conn.close()
        self.connected = False
        logging.debug("Connection terminated")

    def run(self):
        self.client()

    def stop(self):
        logging.debug(f"Closing client connection on {self.host}:{self.port}")
        self.active = False
        self.socket.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    addr = ("localhost", 1234)
    with open("protocol.json", 'r') as p:
        protocol = json.load(p)
    client = OdroidClient(lambda x: ddp.provide_dummy_data(len=None, spec=x),
                          print,
                          lambda: ddp.provide_dummy_data(len=5),
                          protocol,
                          addr)
    client.client()

    while True:
        time.sleep(1)

