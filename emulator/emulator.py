# -*- coding: utf-8 -*-
from __future__ import (print_function, unicode_literals,
                        absolute_import, division)

import os
import time
import subprocess as sub
import cv2
import numpy as np
import sys
import abc
import threading
from image_matching import compare

if sys.platform.startswith('win'):
    import win32file
    import win32pipe

# 256x240, 11 byte header, then 4 byte per pixel (first byte is always 0)
# gd file size: 245771
# 256x240x4  =  245760


class PipeController(object):

    '''
    Abstract Base class for the Linux and windows pipe interfaces
    '''
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def openRead(self):
        '''
        Function: openRead
        Summary: Opens the reading pipe
        Examples:
        Attributes:
            @param (self):
        Returns:
        '''
        raise NotImplementedError(
            "Please use the specific subclasses for Linux or Win32")

    @abc.abstractmethod
    def openWrite(self):
        '''
        Function: openWrite
        Summary: Opens the writing pipe
        Examples:
        Attributes:
            @param (self):
        Returns:
        '''
        raise NotImplementedError(
            "Please use the specific subclasses for Linux or Win32")

    @abc.abstractmethod
    def write(self, data):
        raise NotImplementedError(
            "Please use the specific subclasses for Linux or Win32")

    @abc.abstractmethod
    def read(self, buf):
        raise NotImplementedError(
            "Please use the specific subclasses for Linux or Win32")

    @abc.abstractmethod
    def startFceux(self):
        '''
        Function: startFceux
        Summary: Starts Fceux, since the windows and linux api have different parameters , they need to be specified here
        Examples:
        Attributes:
            @param (self):
        Returns: Nothing
        '''
        raise NotImplementedError(
            "Please use the specific subclasses for Linux or Win32")

    @abc.abstractmethod
    def readScreenshot(self, argb=False):
        raise NotImplementedError(
            "Please use the specific subclasses for Linux or Win32")


class Pipe(object):

    '''
    Abtract base class for the pipes connected to the .lua script
    '''
    __metaclass__ = abc.ABCMeta

    def __init__(self, pipepath, mode):
        if os.path.exists(pipepath):
            os.remove(pipepath)
        self._path = pipepath
        self._mode = mode

    @abc.abstractmethod
    def open(self):
        raise NotImplementedError(
            "Please use the specific subclasses for Linux or Win32")

    @abc.abstractmethod
    def read(self, buffer):
        raise NotImplementedError(
            "Please use the specific subclasses for Linux or Win32")

    @abc.abstractmethod
    def write(self, data):
        raise NotImplementedError(
            "Please use the specific subclasses for Linux or Win32")

    @abc.abstractmethod
    def close(self):
        raise NotImplementedError(
            "Please use the specific subclasses for Linux or Win32")


class LinuxEmulator(PipeController):        # <-- This SHOULD work with Mac OSX

    filenameData = '/tmp/mariofifo-data'
    filenameData2 = '/tmp/mariofifo-data2'
    filenameCommand = '/tmp/mariofifo-command'

    class IOPipe(Pipe):

        def __init__(self, path, mode):
            Pipe.__init__(self, path, mode)
            os.mkfifo(path)

        def open(self):
            self._openpipe = open(self._path, self._mode)

        def write(self, data):
            self._openpipe.write(data)
            self._openpipe.flush()

        def read(self, buf):
            return self._openpipe.read(buf)

        def close(self):
            self._openpipe.close()

        def __del__(self):
            self._openpipe.close()

    def __init__(self,rom):
        # Might want to use Pipe.__init__(self, pipepath, mode) for Python 2.7
        self._dataPipe = self.IOPipe(self.filenameData, 'rb')
        self._dataPipe2 = self.IOPipe(self.filenameData2, 'rb')
        self._commandPipe = self.IOPipe(self.filenameCommand, 'wb')
        self._FCEUX = which('fceux')
        if not self._FCEUX:
            raise OSError(
                "Fceux not found in the /usr/bin directory, are you sure you installed it?")
        self._rom = rom

    def openRead(self):
        self._dataPipe.open()
        self._dataPipe2.open()

    def openWrite(self):
        self._commandPipe.open()

    def write(self, data):
        self._commandPipe.write(data)

    def read(self, buf=245771):
        return self._dataPipe.read(buf)

    def read2(self, buf=15):
        return self._dataPipe2.read(buf)

    def startFceux(self):
        cmd = [self._FCEUX]
        cmd += ['--loadlua']
        cmd += ['emulator-interface.lua']
        cmd += [self._rom]
        with open('/dev/null', 'w') as output:
            self.emulatorinstance = sub.Popen(cmd, stdout=output)
        self.openRead()
        self.openWrite()

    def readScreenshot(self, argb=False):
        # data = self._fifoData.read(245771)  # 256x240x4 + 11 bytes header
        data = self.read(245771)
        # remove the header
        data = data[11:]
        # Read into np array
        rawdata = np.frombuffer(data, dtype=np.uint8)
        # Reshape it from 1 dimensional into ARGB format.
        #::-1 will reverse the order of the ARGB to RGBA, so that
        # cv2 can procude a proper output
        out = rawdata.reshape((240, 256, 4))

        if argb:
            return out
        else:
            return out[:, :, ::-1]

    def readOtherData(self):
        data = self.read2()
        return data

    def close(self):
        self._dataPipe.close()
        self._dataPipe2.close()
        self._commandPipe.close()

    def __del__(self):
        self._dataPipe.close()
        self._dataPipe2.close()
        self._commandPipe.close()


class WinEmulator(PipeController):

    filenameData = "\\\\.\\pipe\\mariofifo-data"
    filenameCommand = "\\\\.\\pipe\\mariofifo-command"


    ###### CHANGE HERE ################
    FCEUX_BASEDIR = os.path.abspath('emulator')

    class IOPipe(Pipe):

        def __init__(self, path, mode):

            Pipe.__init__(self, path, mode)
            self._pipe = win32pipe.CreateNamedPipe(self._path,
                                                   win32pipe.PIPE_ACCESS_DUPLEX,
                                                   win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_WAIT,
                                                   1, 65536, 65536, 30, None)
            self._pipeconnection = threading.Thread(target=self._connectPipe)
            self._pipeconnection.daemon = True

        def _connectPipe(self):
            win32pipe.ConnectNamedPipe(self._pipe, None)

        def open(self):
            self._pipeconnection.start()
            # Returns no value to store?

        def write(self, data):
            # Make sure pipe is connected
            self._pipeconnection.join()
            if self._mode == 'wb':
                win32file.WriteFile(self._pipe, data)
            # Maybe flush?

        def read(self, buf):
            self._pipeconnection.join()
            if self._mode == 'rb':
                # Reads from the winpipe and closes it
                data = win32file.ReadFile(self._pipe, buf)
                # data will be a 2-element tuple with [result, read data]
                data = data[1]
                # try to read more if the received data is smaller than the
                # requested size
                while len(data) < buf:
                    moreData = win32file.ReadFile(self._pipe, buf - len(data))
                    if len(moreData[1]) == 0:
                        break
                    data += moreData[1]
                return data

        def close(self):
            win32file.CloseHandle(self._pipe)
            # self._pipeconnection.join()

        def __del__(self):
            win32file.CloseHandle(self._pipe)
            # self._pipeconnection.join()

    def __init__(self,rom):
        # Might want to use Pipe.__init__(self, pipepath, mode) for Python 2.7
        self._dataPipe = self.IOPipe(self.filenameData, 'rb')
        self._commandPipe = self.IOPipe(self.filenameCommand, 'wb')
        self._FCEUX = which(os.path.join(self.FCEUX_BASEDIR,'fceux.exe'))
        self._rom = rom
        if not self._FCEUX:
            raise OSError(
                "Fceux not found in the directory fceux-2.2.2-win32. Please specify another one")


    def write(self, data):
        self._commandPipe.write(data)
        # win32pipe.ConnectNamedPipe(p, None)
        # win32file.WriteFile(p, data)

    def read(self, buf):
        return self._dataPipe.read(buf)

    def openRead(self):
        self._dataPipe.open()

    def openWrite(self):
        self._commandPipe.open()

    def startFceux(self):
        cmd = [self._FCEUX]
        cmd += ['-lua']
        cmd += ['emulator-interface.lua']
        cmd += [self._rom]
        self.openRead()
        self.openWrite()
        self.emulatorinstance = sub.Popen(cmd)

    def readScreenshot(self, argb=False):
        # data = self._fifoData.read(245771)  # 256x240x4 NO HEADER
        data = self.read(245771)
        # remove the header
        data = data[11:]
        # Read into np array
        rawdata = np.frombuffer(data, dtype=np.uint8)
        # if rawdata.shape < (245760,):
        #     return np.zeros(shape=(240, 256, 4))
        # Reshape it from 1 dimensional into ARGB format.
        #::-1 will reverse the order of the ARGB to RGBA, so that
        # cv2 can procude a proper output
        out = rawdata.reshape((240, 256, 4))
        if argb:
            return out
        else:
            return out[:, :, ::-1]



    def close(self):
        win32file.CloseHandle(self._dataPipe)
        win32file.CloseHandle(self._commandPipe)

    def __del__(self):
        win32file.CloseHandle(self._dataPipe)
        win32file.CloseHandle(self._commandPipe)


def which(program):

    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None


class Emulator(object):
    BUTTON_UP = 1
    BUTTON_DOWN = 2
    BUTTON_LEFT = 4
    BUTTON_RIGHT = 8
    BUTTON_A = 16
    BUTTON_B = 32
    BUTTON_START = 64
    BUTTON_SELECT = 128
    SOFTRESET = 255

    def __init__(self, rom='mario.nes'):

        if sys.platform.startswith('win'):
            self._pipe = WinEmulator(rom)
        else:
            self._pipe = LinuxEmulator(rom)
        self._rom = rom

        # remove the old Data and command pipes and create a new onse
        # self._pipedata = Pipe(self.filenameData, 'rb')
        # self._commandpipe = Pipe(self.filenameCommand, 'wb')

    def startFceux(self):
        '''
        Function: startFceux
        Summary: Starts the Emulator FCeux. Fceux needs to be installed on the machine with e.g. sudo apt-get install fceux

        Examples: Emulator().startFceux()
        Attributes:
            @param (self):
        Returns: None
        '''
        # Starts the instance and does not wait to finish
        self._pipe.startFceux()

    def readScreenshot(self):
        '''
        Function: readScreenshot
        Summary: Reads the screenshot from the pipe and converts it to a numpy array
        Examples: Emulator().readScreenshot()
        Attributes:
            @param (self):
            @param (argb) default=False: If true, returns argb format, else bgra
        Returns: numpy array with dimensions 240,256,4
        '''
        return self._pipe.readScreenshot()
        # data = self._fifoData.read(245771)  # 256x240x4 + 11 bytes header
        # data = self._pipe.read(245771)
        # remove the header
        # data = data[11:]
        # Read into np array
        # rawdata = np.frombuffer(data, dtype=np.uint8)
        # Reshape it from 1 dimensional into ARGB format.
        # ::-1 will reverse the order of the ARGB to RGBA, so that
        # cv2 can procude a proper output
        # print (rawdata.shape)
        # out = rawdata.reshape((240, 256, 4))

        # if argb:
        #     return out
        # else:
        #     return out[:, :, ::-1]
    def readOtherData(self):
        return self._pipe.readOtherData()

    def simulateFrame(self, buttons=0):
        '''
        Function: simulateFrame
        Summary: Sends the desired button presses to the emulator, which will advance the frame of the Emulator
        Examples: Emulator().simulateFrame(Emulator.BUTTON_RIGHT)
        Attributes:
            @param (self):
            @param (buttons) default=0: Buttons to be pressed
        Returns: None
        '''
        self._pipe.write(chr(buttons))
        # self._fifoCommand.flush()

    def __del__(self):
        self._pipe.emulatorinstance.kill()
        self._pipe.close()
        # self._fifoCommand.close()
        # self._fifoData.close()


class MarioEmulator(Emulator):

    def __init__(self, displayFrames=5):
        # by default only show every 5th frame in the opencv window
        Emulator.__init__(self)
        self._stop = False
        self._displayFrames = displayFrames
        self.otherData = None
        self.startFceux()
        self.isFinishing = False
        self.timeRemaining = 0

    def run(self):
        #cv2.namedWindow('Mario', cv2.WINDOW_NORMAL)

        # note that it is extremely important that readScreenshot() and simulateFrame()
        # are called in turns. calling readScreenshot() twice in a row will freeze the
        # emulator!
        t = time.time()
        state = 0
        n = 0
        pressStartFrame = 0
        self.isFinishing = False
        self.timeAtFinish = 0
        self.fitness = 0
        while not self.stop:
            screenshot = self.readScreenshot()
            self.otherData = self.readOtherData()
            self.updateTimeRemaining()
            #print(self.otherData.encode("hex"))
            if not self.isBlackScreen(screenshot):
                obstacles = compare(screenshot)
                #
                #print(obstacles.getHover())
                #print(obstacles.getCanyon())
                nearestObsDist = 250
                for obstacle in obstacles.getFixed():
                    if obstacle[0][0] < nearestObsDist:
                        nearestObsDist = obstacle[0][0]
                self.nearestObsDist = nearestObsDist

                nearestGapDist = 250
                for gap in obstacles.getCanyon():
                    if gap[0][0] < nearestGapDist:
                        nearestGapDist = gap[0][0]
                self.nearestGapDist = nearestGapDist




            if (self.isOnPole()):
                self.isFinishing = True

            buttons = 0
            if state == 0:
                if self.marioScreenPos == int('db', 16):
                    pressStartFrame = n + 3
                    state = 1
            elif state == 1:  # the start screen appears
                if n == pressStartFrame:
                    buttons = self.BUTTON_START
                    state = 2
            elif state == 2:
                if int(self.otherData[7].encode("hex"),16) == 5:
                    state = 3
            elif state == 3:
                if int(self.otherData[7].encode("hex"),16) == 6:
                    self.gameStarted()
                    state = 4
            elif state == 4:  # playing
                if self.isOnPole():
                    self.isFinishing = True
                    self.timeAtFinish = self.timeRemaining
                if self.marioState == 11 or self.marioState == 6 or self.timeSinceLastFitnessUp > 150:
                    self.marioDied(n)
                    buttons = self.SOFTRESET
                    state = 0
                    #print(n, 'frames,', n / (time.time() - t), 'fps')
                    n = -1
                    t = time.time()
                    self.stop = True
                else:
                    buttons = self.frame(n)

            self.simulateFrame(buttons)
            #if self.displayFrames and n % self.displayFrames == 0:
            #    cv2.imshow('Mario', screenshot)
            #    cv2.waitKey(1)
            n += 1

    @property
    def enemyScreenPos(self):
        return [int(i.encode("hex"),16) for i in self.otherData[1:-1]]

    @property
    def marioAbsPos(self):
        return int(self.otherData[6].encode("hex"),16)

    @property
    def marioState(self):
        return int(self.otherData[13].encode("hex"),16)

    @property
    def currentScreen(self):
        return int(self.otherData[14].encode("hex"),16)

    def isOnGround(self):
        if int(self.otherData[9].encode("hex"),16) == 0:
            return 1
        else:
            return 0

    def isOnPole(self):
        if int(self.otherData[9].encode("hex"),16) == 3:
            return True
        else:
            return False

    @property
    def marioScreenPos(self):
        return int(self.otherData[0].encode("hex"),16)

    def updateTimeRemaining(self):
        if not self.isFinishing:
            c = int(self.otherData[10].encode("hex"), 16)
            d = int(self.otherData[11].encode("hex"), 16)
            u = int(self.otherData[12].encode("hex"), 16)
            self.timeRemaining = u + d*10 + c*100
        return self.timeRemaining

    @property
    def stop(self):
        return self._stop

    @stop.setter
    def stop(self, stop):
        self._stop = stop

    @property
    def displayFrames(self):
        return self._displayFrames

    @property
    def xSpeed(self):
        nb = int(self.otherData[8].encode("hex"), 16)
        if nb >= 128:
            nb = nb - 255
        return nb

    @displayFrames.setter
    def displayFrames(self, displayFrames):
        self._displayFrames = displayFrames

    def gameStarted(self):
        raise NotImplementedError()

    def frame(self, n):
        raise NotImplementedError()

    def marioDied(self, n):
        raise NotImplementedError()

    def levelFinished(self, n):
        raise NotImplementedError()

    def isBlackScreen(self, screenshot):
        return np.all(screenshot[190:200, :, :] == 0)

    def isLevel2StartingScreen(self, screenshot):
        # Should return 1 if (x,y) = (154,77) is white.
        return np.all(screenshot[77, 154, :] > 250)
        # TODO: find out if WORLD 1-1 or WORLD 1-2 is displayed in the image
        # proably the easiest way is to just check one pixel that is different in 1 and 2
                # Check if pixel (x,y)=(154,77) is white. If white -> level 1-2 started -> victory
                # This is if the image is (x,y) = (256,224) large.return False
