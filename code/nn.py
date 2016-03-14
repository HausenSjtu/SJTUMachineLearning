import math
import numpy as np

from operator import itemgetter
from copy import deepcopy


def sigmoid(x):
    return 1.0 / (1.0 + math.exp(-x))


def sigmoid_prime(x):
    return sigmoid(x) * (1.0 - sigmoid(x))

class NeuralNetwork:
    def __init__(self, shape, learningRate=0, momentum=0,
                 activation=sigmoid, activation_prime=sigmoid_prime,
                 minStartWeight=-1.0, maxStartWeight=1.0):
        self.learningRate = learningRate
        self.activation = activation
        self.activation_prime = activation_prime
        self.momentum = momentum
        self.minStartWeight = minStartWeight
        self.maxStartWeight = maxStartWeight
        ############################################################
        # self.weights is a list of layers
        # Each layer is a list of neurons
        # Each neuron is a list of n float weights
        # With n the number of neurons of the previous layer
        ############################################################

        self.weights = []
        self.oldGrad = []

        previousNbNeurons = shape[0]
        for nbNeurons in shape[1:]:
            # +1 for bias
            weightMat = np.random.uniform(self.minStartWeight,
                                          self.maxStartWeight,
                                          (nbNeurons,
                                           previousNbNeurons + 1))
            self.oldGrad.append(np.zeros((nbNeurons, previousNbNeurons + 1)))
            self.weights.append(weightMat)
            previousNbNeurons = nbNeurons

    def feedForward(self, inputData):
        inputData = deepcopy(inputData)
        inputData.append(1)  # bias
        # For every layer, feed input and get output
        # Use output as input of next layer
        for i, layer in enumerate(self.weights):
            output = []
            nets = []
            for j, neuron in enumerate(layer):
                net = float(np.dot(neuron, inputData))
                nets.append(net)
                output.append(self.activation(net))
            inputData = output
            inputData.append(1)  # bias
        return output
