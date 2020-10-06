import logging, sys, json
from parser_baseclass import Parser


class OdroidParser(Parser):
    def __init__(self, protocol):
        super().__init__(protocol)
        self.parser_proto = protocol["TO_ODROID"]

    def parse(self, data):
        logging.debug("Parsing")
        data=data.decode("ansi")
        data = json.loads(data)
        logging.debug(f"frame:{data}")
        if (data[0] == self.parser_proto["CONTROL"]):
            logging.debug("CONTROL")
            logging.debug(f"frame: {data}")
            if (data[1] == self.control_spec["START_TELEMETRY"]):
                logging.debug("START_TELEMETRY")
                self.start_sending(data[2])
            elif (data[1] == self.control_spec["STOP_TELEMETRY"]):
                logging.debug("STOP_TELEMETRY")
                self.stop_sending()
            elif (data[1] == self.control_spec["START_PID"]):
                logging.debug("START_PID")
                self.start_sending(data[2])
            elif (data[1] == self.control_spec["STOP_PID"]):
                logging.debug("STOP_PID")
                self.stop_sending()
            elif (data[1] == self.control_spec["ARMED"]):
                logging.debug("ARMED")
            elif (data[1] == self.control_spec["DISARMED"]):
                logging.debug("DISARMED")
            elif (data[1] == self.control_spec["START_AUTONOMY"]):
                logging.debug("START_AUTONOMY")
            elif (data[1] == self.control_spec["STOP_AUTONOMY"]):
                logging.debug("STOP_AUTONOMY")
            elif (data[1] == self.control_spec["MODE"]):
                logging.debug("MODE")

        elif data[0] == self.parser_proto["PID"]:
            logging.debug("PID")
            if data[1] != self.pid_spec["all"]:
                msg = list(data)
                msg.pop(0)
                if msg[0] == self.pid_spec["roll"]:
                    msg[0] = 'roll'
                elif msg[0] == self.pid_spec["pitch"]:
                    msg[0] = 'pitch'
                elif msg[0] == self.pid_spec["yaw"]:
                    msg[0] = 'yaw'
                logging.debug(msg[0])
                self.setPIDs(msg)
            else:
                msg = list(data)
                msg.pop(0)
                msg[0] = 'all'
                logging.debug(msg[0])
                self.setPIDs(msg)

        elif data[0] == self.parser_proto["PID_REQUEST"]:
            logging.debug("PID_REQUEST")
            msg = list(data)
            if msg[1] == self.pid_spec["roll"]:
                msg[1] = 'roll'
            elif msg[1] == self.pid_spec["pitch"]:
                msg[1] = 'pitch'
            elif msg[1] == self.pid_spec["yaw"]:
                msg[1] = 'yaw'
            elif msg[1] == self.pid_spec["all"]:
                msg[1] = 'all'
            logging.debug(msg[1])
            self.sendPid(self.getPIDs(msg[1]))

        elif data[0] == self.parser_proto["BOAT_DATA_REQUEST"]:
            logging.debug("BOAT_DATA_REQUEST")
            msg = list(data)
            self.sendBoatData(['boat data'])

        elif data[0] == self.parser_proto["PAD"]:
            logging.debug("PAD")
            msg = list(data)


