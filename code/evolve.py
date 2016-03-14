from __future__ import division

from mario import Mario
from nn import NeuralNetwork
from operator import itemgetter

import multiprocessing

import numpy as np
import cPickle as pickle

NBWORKERS = 3

emulatorList = [Mario() for i in range(NBWORKERS)]


def emulate(nn):
    workerID = multiprocessing.current_process()._identity[0]%NBWORKERS
    emulator = emulatorList[workerID]
    emulator.setNeuralNetwork(nn[0])
    fitness = emulator.run()
    return [nn[0], fitness]


def getFitness(nnList):
    #print(nnList)
    pool = multiprocessing.Pool(processes=NBWORKERS)
    result = pool.map(emulate, nnList)
    pool.close()
    pool.join()
    return result

def evolve():
    # TODO : fucking speed that up
    def select_parent(sortedPop):
        tmp1 = np.random.random()
        tmp2 = 0
        for item in sortedPop:
            tmp2 += item[1]
            if tmp2 >= tmp1:
                #print("selected", item[0])
                return item[0]

    shape = [5, 10, 4]

    popSize = 100
    genNb = 1000
    mutRate = 0.05
    crossRate = 1.0
    elitism = 2

    popList = []

    nnTemplate = NeuralNetwork(shape, 0, 0)
    genesNb = sum([x.size for x in nnTemplate.weights])
    print("\n"
          "############################################\n"
          "# Nb of genes           : {}".format(genesNb) + "\n"
          "# Population size       : {}".format(popSize) + "\n"
          "# Number of generations : {}".format(genNb) + "\n"
          "# Crossover rate        : {0:.0f}%".format(crossRate*100) + "\n"
          "# Mutation rate         : {0:.0f}%".format(mutRate*100) + "\n"
          "# Elitism               : {}".format(elitism) + "\n"
          "############################################\n"
          )

    print("Creating initial population of size {}".format(popSize))

    for i in range(popSize):
        # initial fitness of None
        popList.append([NeuralNetwork(shape, minStartWeight=-3.0, maxStartWeight=3.0), None])
    print("Population created.\n")

    for g in range(genNb):
        # print("Evaluating fitness.")
        popList = getFitness(popList)

        sortedPop = sorted(popList, key=itemgetter(1))

        if (g+1) == genNb:
            return sortedPop[0][0]

        print("Generation", g)
        print("Fitness min : ", sortedPop[0][1])
        print("Fitness max : ", sortedPop[-1][1])

        with open('./bestNN', 'w') as file:
            pickle.dump(sortedPop[-1][0], file)

        with open('./csv', 'a') as file:
            for item in sortedPop:
                file.write(str(item[1]))
                file.write(',')
            file.write('\n')


        # Normalizing fitness
        sumFit = 0
        for item in sortedPop:
            sumFit += item[1]

        for item in sortedPop:
            try:
                item[1] = item[1] / sumFit
            except ZeroDivisionError:
                item[1] = 1/popSize

        sortedPop = list(reversed(sortedPop))
        #print(sortedPop)
        # print("Fitness evaluated.\n")

        # print("Generating next generation.")
        newPop = []

        # Elitism step : copying bests
        for i in range(elitism):
            newPop.append(sortedPop[i])

        # For the rest
        for i in range(popSize-elitism):
            if np.random.random() < crossRate:  # CROSSOVER TIME
                parent1 = select_parent(sortedPop).weights
                parent2 = select_parent(sortedPop).weights

                child = NeuralNetwork(shape)
                for l in range(len(child.weights)):
                    for n in range(len(child.weights[l])):
                        for w in range(len(child.weights[l][n])):
                            if np.random.random() >= 0.5:
                                parent = parent1
                            else:
                                parent = parent2
                            child.weights[l][n][w] = parent[l][n][w]

                            if np.random.random() <= mutRate:  # MUTATION !
                                child.weights[l][n][w] += ((1.0 - (-1.0)) * np.random.random() + (-1.0))
            else:
                # CLONING TIME
                parent = select_parent(sortedPop).weights
                child = NeuralNetwork(shape)
                child.weights = parent

            newPop.append([child, None])
        popList = newPop

if __name__ == '__main__':
    evolve()
