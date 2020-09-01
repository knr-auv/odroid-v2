import json
import logging
import socket
import struct
import time
import threading

from concurrent.futures import ThreadPoolExecutor
from odroid_sender import OdroidSender
from odroid_parser import OdroidParser
from variable import *


class OdroidClient(threading.Thread, OdroidParser, OdroidSender):
    def __init__(self, protocol, addr=JETSON_ADDRESS):
        threading.Thread.__init__(self)
        OdroidSender.__init__(self, protocol)
        self.protocol = protocol
        self.host = addr[0]
        self.port = addr[1]
        self.active = True
        self.checked = False

    def start_telemetry(self, interval):
        self.sendControl([self.protocol["CONTROL_SPEC"]["START_TELEMETRY"],interval])
        logging.debug("Starting telemetry")

    def disarm(self):
        logging.debug("DISARMING")
        self.sendControl([self.protocol["CONTROL_SPEC"]["STOP_PID"]])

    def arm(self, interval):
        logging.debug("ARMING")
        self.sendControl([self.protocol["CONTROL_SPEC"]["START_PID"], interval])

        self.checked = False
    def startAutonomy(self):
        self.sendControl([self.protocol["CONTROL_SPEC"]["START_AUTONOMY"]])

    def stopAutonomy(self):
        self.sendControl([self.protocol["CONTROL_SPEC"]["STOP_AUTONOMY"]])

    def setMode(self, mode):
        self.sendControl([self.protocol["CONTROL_SPEC"]["MODE"], mode])

    def client(self):
        try:
            logging.debug(("Connecting to: "+ str(self.host)+":"+str(self.port)))
            self.socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host,self.port))
        except (socket.gaierror,socket.error):
            logging.debug("Connection refused")
            return
        logging.debug("Socket now Connect with port:{}".format(self.port))
        executor = ThreadPoolExecutor(max_workers=5)
        rx_state = FRAME_SECTION["HEADER"]
        rx_len = 0
        self.start_telemetry(30)

        self.sendBoatDataRequest()
        self.sendPIDRequest("all")
        while self.active:
            try:
                if(rx_state==FRAME_SECTION["HEADER"]):
                    data=self.socket.recv(4)
                    if data == b'':
                        raise ConnectionResetError
                    rx_len=struct.unpack("<I",data)[0]
                    rx_len-=4
                    rx_state=FRAME_SECTION["DATA"]

                elif(rx_state==FRAME_SECTION["DATA"]):
                    data=self.socket.recv(rx_len).decode("ascii")
                    logging.debug(data)
                    self.executor.submit(self.parse ,data)
                    rx_state=FRAME_SECTION["HEADER"]
            except ConnectionResetError:
                self.clientConnected = False
                self.socket.close()
                print("Disconnected from server.")
                return
            except socket.gaierror:
                executor.shutdown()
                logging.debug("Connection terminated")
                return
            except Exception as e:
                logging.debug("Exception")
                rx_state=FRAME_SECTION["HEADER"]

        executor.shutdown()
        self.socket.close()
        logging.debug("Connection terminated")

    def run(self):
        self.client()

    def stop(self):
        logging.debug(f"Closing client connection on {self.host}:{self.port}")
        self.active= False
        self.socket.close()

if __name__=="__main__":
    logging.basicConfig(level=logging.DEBUG)
    addr = ("localhost", 1234)
    with open("protocol.json",'r') as p:
        protocol = json.load(p)
    client=OdroidClient(protocol,addr)
    client.start()
    while True:
            time.sleep(1)
