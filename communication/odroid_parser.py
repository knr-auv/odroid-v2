import struct


class OdroidParser():
    CONTROL = 0
    PID_RECEIVED = 1
    PID_REQUEST = 2

    def parse(self, data):
        if data[0] == self.PID_RECEIVED:
            ROLL = 1
            PITCH = 2
            YAW = 3
            ALL = 4

            if data[1]!= ALL:
                msg = struct.unpack('<2B3f', data)
                msg = list(msg)
                msg.pop(0)
                if msg[0]==ROLL:
                    msg[0] = 'roll'
                elif msg[0]==PITCH:
                    msg[0] ='pitch'
                elif msg[0]==YAW:
                    msg[0]='yaw'
                self.setPIDs(msg)
            elif data[1]==ALL:
                msg  = struct.unpack('<2B9f', data)
                msg = list(msg)
                msg.pop(0)
                msg[0]='all'
                self.setPIDs(msg)

        if data[0] == self.PID_REQUEST:
            ROLL = 1
            PITCH = 2
            YAW = 3
            ALL = 4
            msg = struct.unpack('<2B',data)
            msg = list(msg)
            if msg[1]==ROLL:
                msg[1] = 'roll'
            elif msg[1]==PITCH:
                msg[1] ='pitch'
            elif msg[1]==YAW:
                 msg[1]='yaw'
            elif msg[1]== ALL:
                msg[1] = 'all'
            self.sendPid(self.getPIDs(msg[1]))

        if (data[0] == self.CONTROL):
            START_SENDING = 1
            STOP_SENDING = 2
            if (data[1]==START_SENDING):
                msg = struct.unpack('<2BI',data)
                msg = list(msg)
                msg.pop(0)
                self.start_sending(msg[1])
            if (data[1]==STOP_SENDING):
                self.stop_sending()
