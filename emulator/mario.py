#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from __future__ import (print_function, unicode_literals,
                        absolute_import, division)

from emulator import MarioEmulator


class Mario(MarioEmulator):
    def gameStarted(self):
        #print("game started!")
        self.fitness = 0
        self.previousAbsPos = self.marioAbsPos
        self.timeSinceLastJump = 0
        self.goingRight = False
        self.timeSinceLastFitnessUp = 0

    def frame(self, frame):
        #print(self.nearestGapDist)
        self.timeSinceLastJump += 1
        #if self.goingRight and not(self.marioAbsPos > #self.previousAbsPos):
        #    blocked = 1
        #else:
        #    blocked = 0
        if self.timeSinceLastJump > 100:
            self.timeSinceLastJump = 100

        posPlayer = int(self.otherData[0].encode("hex"), 16)
        posEnemyList = [int(pos.encode("hex"), 16) for pos in self.otherData[1:6]]
        minPos = 255
        for pos in posEnemyList:
            if pos > posPlayer and pos < minPos:
                minPos = pos
        distToEnemy = (minPos - posPlayer)/100

        #print(distToEnemy)
        out = self.nn.feedForward([distToEnemy, self.timeSinceLastJump/100, self.isOnGround(), self.nearestObsDist/250, self.nearestGapDist/250])

        newFitness = self.currentScreen * 255 + self.marioAbsPos
        if newFitness > self.fitness:
            self.timeSinceLastFitnessUp = 0
            self.fitness = newFitness
        else:
            self.timeSinceLastFitnessUp += 1

        self.previousAbsPos = self.marioAbsPos
        current = 0
        if out[0] > 0.5:
            current = current | self.BUTTON_RIGHT
            self.goingRight = True
        else:
            self.goingRight = False
        if out[1] > 0.5:
            current = current | self.BUTTON_LEFT
        if out[2] > 0.5:
            current = current | self.BUTTON_A
            self.timeSinceLastJump = 0
        if out[3] > 0.5:
            current = current | self.BUTTON_B
        #if out[4] > 0.5:
        #    current = current | self.BUTTON_DOWN
        return current

    def run(self):
        self.stop = False
        self.fitness = 0
        super(Mario, self).run()
        if self.isFinishing:
            print(self.timeAtFinish*10)
            return self.timeAtFinish*10
        return self.fitness

    def marioDied(self, n):
        #print("died in frame", n, ":(")
        #self.stop = True
        self.fitness += self.timeRemaining/1000

    def levelFinished(self, n):
        self.fitness = self.timeRemaining/1000
        #self.stop = True

    def setNeuralNetwork(self, nn):
        self.nn = nn
