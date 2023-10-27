#!/usr/bin/python3.6
# -*-coding: utf-8 -*

from LspAlgorithms.GeneticAlgorithms.Hcm.Solver import GeneticAlgorithm
from LspInputDataReading.LspInputDataReader import InputDataReader
from LspAlgorithms.GeneticAlgorithms.LspRuntimeMonitor import LspRuntimeMonitor
from ParameterSearch.ParameterData import ParameterData
import LspLibrary as lspLib
import numpy as np
import random

ParameterData.instance = ParameterData()

# Reading the tuning instances
tuning_instances_data = []
with open("data/param_tuning_instances.txt", "r") as tuning_instances_file:
    tuning_instances_data = tuning_instances_file.readlines()

# print(tuning_instances_data)

# loading the ml model
# LspRuntimeMonitor.mlModel = keras.models.load_model("ga_ml_model.h5")
# LspRuntimeMonitor.mlConfusionMatrix = [[0, 0], [0, 0]]
LspRuntimeMonitor.mlTestSetFeatures = []
LspRuntimeMonitor.mlTestSetLabels = []

tuningData = None
# Setting the tuning parameters for it to launch
for pop_size in range(25, 41, 1):

    ParameterData.instance.popSize = pop_size

    for mutation_rate in np.arange(0.05, 0.16, 0.1):

        mutation_rate = round(mutation_rate, 2)
        ParameterData.instance.mutationRate = mutation_rate

        for crossover_rate in np.arange(0.75, 0.91, 0.01):

            crossover_rate = round(crossover_rate, 2)
            ParameterData.instance.crossOverRate = crossover_rate
            print(ParameterData.instance.popSize, ParameterData.instance.mutationRate, ParameterData.instance.crossOverRate)

            random.shuffle(tuning_instances_data)
            instancesEpochData = []

            for index, tuning_instance_data in enumerate(tuning_instances_data):

                tuning_instance_data = tuning_instance_data.split(" ")
                tuning_instance_path = tuning_instance_data[0]
                tuning_instance_opt = int(tuning_instance_data[1])
                print("--- ", tuning_instance_path, tuning_instance_opt)


                # Reading the file to get the problem to solve
                inputFilePath = tuning_instance_path
                inputDataReader = InputDataReader()
                inputDataInstance = inputDataReader.readInput(inputFilePath)
                # print(inputDataInstance)

                # LspRuntimeMonitor properties
                LspRuntimeMonitor.fileName = inputFilePath.replace("data/input/", "")
                LspRuntimeMonitor.fileName = LspRuntimeMonitor.fileName.replace("/", "_")
                LspRuntimeMonitor.fileName = LspRuntimeMonitor.fileName.replace(".", "_")
                LspRuntimeMonitor.outputFolderPath += LspRuntimeMonitor.fileName


                nIterations = 5
                globalData = {"mins": [], "timeLengths": []}
                iterationsData = []

                for _ in range(nIterations):

                    # LspRuntimeMonitor.mlData = []
                    LspRuntimeMonitor.instance = LspRuntimeMonitor()

                    # # I create an instance of the genetic algorithm to be used
                    lspSolver = GeneticAlgorithm()

                    lspSolver.solve()

                    ###
                    LspRuntimeMonitor.instance.stop()
                    ##

                    # Reporting all statistics collected when running the selected algo
                    mins = []
                    for threadId in LspRuntimeMonitor.instance.popsData:
                        # mins.append(LspRuntimeMonitor.instance.popsData[threadId]["min"][-1])
                        mins.append(min(LspRuntimeMonitor.instance.popsData[threadId]["min"]))

                    globalData["mins"].append(min(mins))
                    globalData["timeLengths"].append(LspRuntimeMonitor.instance.timeLength)
                    
                    if (len(globalData["mins"]) == 1) \
                        or (len(globalData["mins"]) > 1 \
                            and (globalData["mins"][-1] < globalData["min"] \
                                or (globalData["mins"][-1] == globalData["min"] and globalData["timeLengths"][-1] < globalData["timeLength"])
                            )
                        ):
                        globalData["min"] = globalData["mins"][-1]
                        globalData["timeLength"] = globalData["timeLengths"][-1]

                    iterationsData.append(globalData["min"] - tuning_instance_opt)

                iterationsData = sum(iterationsData) / len(iterationsData)
                instancesEpochData.append(iterationsData)

            instancesEpochData = sum(instancesEpochData) / len(instancesEpochData)

            if (tuningData is None or (tuningData is not None and instancesEpochData < tuningData[0])):
                tuningData = (instancesEpochData, ParameterData.instance.popSize, ParameterData.instance.mutationRate, ParameterData.instance.crossOverRate)

print("************** : ", tuningData)