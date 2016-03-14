from __future__ import division

from mario import Mario
from nn import NeuralNetwork
import cPickle as pickle

emulator = Mario()
with open('./bestNN', 'rb') as file:
    nn = pickle.load(file)

print(nn.weights)

emulator.setNeuralNetwork(nn)
emulator.run()
