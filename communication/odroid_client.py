import socket, struct, threading, logging, sys

from concurrent.futures import ThreadPoolExecutor
from odroid_sender import OdroidSender
from odroid_parser import OdroidParser





class OdroidClient(threading.Thread, OdroidParser, OdroidSender):
    def __init__(self, addr, protocol):
        threading.Thread.__init__(self)
        self.socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(addr)
        OdroidSender.__init__(self, socket, protocol)
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
        logging.debug(("Connecting to: "+ str(self.host)+":"+str(self.port)))
        try:
            logging.debug("Connecting...")
            # reader, self.writer = await asyncio.open_connection(host = self.host, port = self.port, family = socket.AF_INET, flags = socket.SOCK_STREAM)
        except (socket.gaierror,socket.error):
            logging.debug("Connection refused")
            return
        logging.debug("Socket now Connect with port:{}".format(self.port))
        executor = ThreadPoolExecutor(max_workers=5)
        HEADER = 0
        DATA = 1
        rx_state = HEADER
        rx_len =0
        self.start_telemetry(30)

        self.sendBoatDataRequest()
        self.sendPIDRequest("all")
        try:
            while self.active:
                try:
                    if(rx_state ==HEADER):
                        async def receive4():
                            data = await reader.readexactly(4)
                            return data
                        self.reader_task = asyncio.create_task(receive4())
                        data = await self.reader_task
                        rx_len = struct.unpack("<L",data)[0]
                        rx_len -= 4
                        rx_state = DATA

                    elif(rx_state == DATA):
                        data = await reader.readexactly(rx_len)
                        executor.submit(self.parse ,data)
                        rx_state = HEADER
                except asyncio.IncompleteReadError:
                    rx_state = HEADER
                except asyncio.CancelledError:
                    pass
        except (socket.gaierror, socket.error):
            executor.shutdown()
            self.reader_task.cancel()
            logging.debug("Connection terminated")
            return
        executor.shutdown()
        self.writer.close()
        logging.debug("Connection terminated")
        self.signals.connectionButton.emit("Connect")
        self.signals.connectionTerminated.emit()

    def run(self):
        self.client()

    def stop(self):
        async def coro():
            self.reader_task.cancel()
        self.active = False
        try:
            if self.client_loop.is_running():
                asyncio.run_coroutine_threadsafe(coro(), self.client_loop)
        except AttributeError:
            pass
