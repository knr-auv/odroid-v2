import um7
#from connectionForTesting import *
import threading
import time
from Integrator import *
import numpy as np
import math

IP_ADDRESS = '192.168.137.45'
FILTER_VALUE = 0.2  # value for low frequency filter used for debugging drift

class IMUClass():
    """Class for setting up, control and also calculate and validate IMU's input
    This class is kind of runnable class ( like in java ) - can be used as target for Thread object"""
    def __init__(self, *statevars):
        self.gyro_integrator = Integrator()
        self.acc_integrator = Integrator()
        self.vel_integrator = Integrator()
        self.i = 0
        self.gyro_filter = 0.2
        self.integrator = Integrator()
        name1 = 's'
        port1 = '/dev/ttySAC0'
        self.statevars = []  # example: ['roll', 'pitch', 'yaw']
        for state in statevars:
            self.statevars.append(state)
        # All states avaible:
        # ['roll', 'pitch', 'yaw']
        # ['health', 'roll', 'pitch', 'yaw'] #'mag_proc_x', 'mag_proc_y', 'mag_proc_z', 'mag_raw_x', 'mag_raw_y',
        # 'mag_raw_z', #'accel_raw_x', 'accel_raw_y', 'accel_raw_z', 'accel_proc_x', 'accel_proc_y', 'accel_proc_z',
        # 'gyro_proc_x', 'gyro_proc_y', #'gyro_proc_z', 'accel_raw_time', 'accel_proc_time', 'euler_time']

        self.s1 = um7.UM7(name1, port1, self.statevars, baud=115200)
        try:
            print('IMU initialition process:')
            # self.s1.reset_to_factory()
            print('GET_FW_REVISION=' + '{}'.format(self.s1.get_fw_revision()))
            print('ZERO_GYROS ' + 'ok.' if self.s1.zero_gyros() else 'failed.')
            time.sleep(1.1)
            print('RESET_EKF ' + 'ok.' if self.s1.reset_ekf() else 'failed.')
            print('SET_MAG_REFERENCE ' + 'ok.' if self.s1.set_mag_reference() else 'failed.')
            time.sleep(1.1)
			# print('SET_HOME_POSITION ' + 'ok.' if self.s1.set_home_position() else 'failed.')
            # print('RESET_EKF ' + 'ok.' if self.s1.reset_ekf() else 'failed.')

			# print('FLASH_COMMIT ' + 'ok.' if self.s1.flash_commit() else 'failed.')
        # time.sleep(3)
        except:
            print('------------!ERROR occured!--------------\n')

        # readings view format:
        self.fs = ''
        self.hs = ''
        for i in self.statevars:
            self.hs += '{:>9.9s} '
            if i == 'health':
                self.fs += ' {0[' + i + ']:08b} '
            else:
                self.fs += '{0[' + i + ']:9.3f} '

        self.sv = ['roll', 'pitch', 'yaw']

        self.prev_sample = 0
        self.drift = 0
        self.gravity_vector = (0, 0, 0)
        # init
        time.sleep(1)
        self.catchSamples()
        angles = self.makeAnglesDict(self.getSample('roll'), self.getSample('pitch'), self.getSample('yaw'))
        vec = self.makeVector(self.getSample('accel_proc_x'), self.getSample('accel_proc_y'),
                              self.getSample('accel_proc_z'))
        self.gravity_vector = self.rotate(angles, vec, True)

    # x = 0
    # y = 0
    # z = 0
    # for i in range(50):
    #	self.catchSamples()
    #	xs ``	'= self.getSample('accel_proc_x')
    #	ys = self.getSample('accel_proc_y')
    #	zs = self.getSample('accel_proc_z')

    #	x+=xs
    #	y+=ys
    #	z+=zs
    #	time.sleep(0.05)

    # self.gravity = np.sqrt(np.power(x/50,2)+np.power(y/50,2)+np.power(z/50,2))
    # print('GRAVITY:  ', self.gravity)
    # self.prev_sample = 0

    def catchSamples(self):
        self.s1.catchallsamples(self.sv, 1.0)
        self.printSamples(False)

    def getSamples(self):
        samples = {}
        for state in self.statevars:
            samples[state] = self.getSample(state)

        samples['vel_x'] = self.getSample('vel_x')  # just for now
        return samples

    # method that returns validated and precalculated IMU's state valueas
    def getSample(self, sample):
        if (sample == 'roll' or sample == 'pitch'):
            state = self.s1.state[sample]
            return self.correctAngles(state)
        elif sample == 'yaw':
            #state = self.s1.state[sample]
            state = self.getSample('gyro_raw_z')
            if state > -self.gyro_filter and state < self.gyro_filter:
                state = 0
            return self.correctAngles(self.gyro_integrator.integrate(state)/scipy.pi*18)
            # return self.correctAngles(state)
            #return self.correctAngles(self.debugDrift(state))
            #return state

        elif (sample == 'vel_x'):
            # It was made for estimating volocity of AUV, but doesnt work properly
            # Not used because of issues

            self.i = self.i + 1
            if self.i <= 10:
                return 0

            angles = self.makeAnglesDict(self.getSample('roll'), self.getSample('pitch'), self.getSample('yaw'))
            vec = self.makeVector(self.getSample('accel_proc_x'), self.getSample('accel_proc_y'),
                                  self.getSample('accel_proc_z'))
            acc = self.rotate(angles, vec)
            acc_x = acc[0]
            if abs(acc_x) < 0.02:
                acc_x = 0  
            velocity = self.vel_integrator.integrate(acc_x)
            #if abs(velocity) < 0.02:
            #    velocity = 0
            return velocity
			# vec = tuple(map(lambda x: abs(x), vec))
			# self.gravity_vector = tuple(map(lambda x: abs(x), self.gravity_vector))
            # acc_vec = self.debugAcceleration(angles, vec)
            # acc_x = acc_vec[0]
            
            # vel = self.acc_integrator.integrate(acc_x)
            #return self.integrator.integrate(vel)
            #return self.debugDrift(vel)
            # return acc_x

        return self.s1.state[sample]

    # Method that calculates raw angles provided by IMU to values from -180 to 180 degrees
    def correctAngles(self, state):
        if (state > 180):
            # print(str(360 - state))
            return (-360 + state)
        if (state < -180):
            # print("state < -180")
            return (360 + state)
        return state

    # Method that fixes low frequency drift
    def debugDrift(self, sample):
        result = 0
        d = sample - self.prev_sample

        if abs(d) < FILTER_VALUE :
            self.drift += d
            result = sample - self.drift
            self.prev_sample = sample
        else:
            result = sample - self.drift
            self.prev_sample = sample

        return result

    def printSamples(self, headerFlag):
        pass
        # printing in terminal for testing
        #if headerFlag:
        #    print(self.hs.format(*self.statevars))
        #print(self.getSample('roll'), ' ', self.getSample('pitch'), ' ', self.getSample('yaw'), ' ',
        #      self.getSample('vel_x'))

    def startSendingSamples(self, connectionObject):  # without printing
        # this method can be a target -> in Thread constructor
        # Just for visualizing reasons, not being used now
        # c = 0
        while True:
            # self.catchSamples()
            # self.printSamples(c % 50 == 0)
            # c += 1
            connectionObject.setDataFrame(self.s1.state)

    def makeAnglesDict(self, roll, pitch, yaw):
        return {'roll': roll, 'pitch': pitch, 'yaw': yaw}

    def makeVector(self, x, y, z):
        return x, y, z

    # Method for rotating AUV state, used for deleting gravity acceleration vector from IMU values
    def rotate(self, angles, vector, transposeFlag=False):

        angles = dict(map(lambda x: (x, math.radians(angles[x])), angles))

        rotMatrixYPR = np.array(
            [[math.cos(angles['yaw']) * math.cos(angles['pitch']),
              math.cos(angles['yaw']) * math.sin(angles['pitch']) * math.sin(angles['roll']) - math.sin(
                  angles['yaw']) * math.cos(angles['roll']),
              math.cos(angles['yaw']) * math.sin(angles['pitch']) * math.cos(angles['roll']) + math.sin(
                  angles['yaw']) * math.sin(angles['roll']),
              ],
             [math.sin(angles['yaw']) * math.cos(angles['pitch']),
              math.sin(angles['yaw']) * math.sin(angles['pitch']) * math.sin(angles['roll']) + math.cos(
                  angles['yaw']) * math.cos(angles['roll']),
              math.sin(angles['yaw']) * math.sin(angles['pitch']) * math.cos(angles['roll']) - math.cos(
                  angles['yaw']) * math.sin(angles['roll']),
              ],
             [-math.sin(angles['pitch']),
              math.cos(angles['pitch']) * math.sin(angles['roll']),
              math.cos(angles['pitch']) * math.cos(angles['roll']),
              ]], np.float_)

        if transposeFlag:
            rotMatrixYPR = np.transpose(rotMatrixYPR)

        vectorMatrix = np.asarray(vector, np.float_)
        # vectorMatrix[1], vectorMatrix[2] = vectorMatrix[2], vectorMatrix[1]

        return rotMatrixYPR.dot(vectorMatrix)

    def debugAcceleration(self, angles, vector):
        gravity_vec_rotated = self.rotate(angles, self.gravity_vector, False)
        # vec = tuple(map(lambda x: abs(vector[vector.index(x)] - gravity_vec_rotated[vector.index(x)]), vector))
        vec = tuple(map(lambda x: vector[vector.index(x)] - gravity_vec_rotated[vector.index(x)], vector))

        return vec


# imu = IMUClass('roll', 'pitch', 'yaw', 'accel_raw_x')
# connThread = Connection(IP_ADDRESS)

# threading.Thread(target=imu.startSendingSamples, args=[connThread]).start()
# connThread.start()
# while True:
#	imu.catchSamples()
