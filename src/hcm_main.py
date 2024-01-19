#!/usr/bin/python3.6
# -*-coding: utf-8 -*

# import sys
import argparse
from LspAlgorithms.GeneticAlgorithms.Hcm.Solver import GeneticAlgorithm
from LspInputDataReading.LspInputDataReader import InputDataReader
from LspAlgorithms.GeneticAlgorithms.LspRuntimeMonitor import LspRuntimeMonitor
from ParameterSearch.ParameterData import ParameterData
#from tensorflow import keras
# from sklearn.preprocessing import StandardScaler
import pandas as pd
# from sklearn.metrics import confusion_matrix, precision_score, recall_score
# import os
import LspLibrary as lspLib

ParameterData.instance = ParameterData()

# Setting solver's options 
parser = argparse.ArgumentParser(description = "LspSolver : Lot sizing problems solver tool implementing different AI methods" )
parser.add_argument("filePath", help = "Instance of lot sizing problem described as a plain text")
parser.add_argument("-v", "--verbose", help = "Display on the screen the details of search process", action = "store_true")
# parser.add_argument("-o", "--output", help = "Redirect the output of the program to a given file")
# parser.add_argument("-t", "--nbThreads", help = "Number of the threads involved in the search", type = int)
parser.add_argument("-s", "--stats", help = "Display on the screen the stats gathered when applying the algo", action = "store_true")

args = parser.parse_args()

# Reading the file to get the problem to solve
inputFilePath = args.filePath  #sys.argv[1]
LspRuntimeMonitor.verbose = args.verbose
inputDataReader = InputDataReader()
inputDataInstance = inputDataReader.readInput(inputFilePath)
# print(inputDataInstance)

# LspRuntimeMonitor properties
LspRuntimeMonitor.fileName = inputFilePath.replace("data/input/", "")
LspRuntimeMonitor.fileName = LspRuntimeMonitor.fileName.replace("/", "_")
LspRuntimeMonitor.fileName = LspRuntimeMonitor.fileName.replace(".", "_")
LspRuntimeMonitor.outputFolderPath += LspRuntimeMonitor.fileName

# loading the ml model
#LspRuntimeMonitor.mlModel = keras.models.load_model("ga_ml_model.h5")
# LspRuntimeMonitor.mlConfusionMatrix = [[0, 0], [0, 0]]
LspRuntimeMonitor.mlTestSetFeatures = []
LspRuntimeMonitor.mlTestSetLabels = []
LspRuntimeMonitor.applyLocalSearch = True # False


nIterations = 10 if args.stats else 1 
globalData = {"mins": [], "timeLengths": []}

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
		mins.append(min(LspRuntimeMonitor.instance.popsData[threadId]["min"]))
		# mins.append(LspRuntimeMonitor.instance.popsData[threadId]["min"][-1])

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

	if not args.stats:
		LspRuntimeMonitor.instance.report()

# # printing confusion matrix

# LspRuntimeMonitor.mlTestSetFeatures = pd.DataFrame(LspRuntimeMonitor.mlTestSetFeatures)
# LspRuntimeMonitor.mlTestSetLabels = pd.DataFrame(LspRuntimeMonitor.mlTestSetLabels)

# scaler = StandardScaler()
# LspRuntimeMonitor.mlTestSetFeatures = pd.DataFrame(scaler.fit_transform(LspRuntimeMonitor.mlTestSetFeatures))

# predictions = LspRuntimeMonitor.mlModel.predict(LspRuntimeMonitor.mlTestSetFeatures)
# predictions = (predictions > .5)

# # print(LspRuntimeMonitor.mlModel.evaluate(LspRuntimeMonitor.mlTestSetFeatures, LspRuntimeMonitor.mlTestSetLabels))

# print(confusion_matrix(LspRuntimeMonitor.mlTestSetLabels, predictions))
# print(precision_score(LspRuntimeMonitor.mlTestSetLabels, predictions))
# print(recall_score(LspRuntimeMonitor.mlTestSetLabels, predictions))

# print(LspRuntimeMonitor.mlConfusionMatrix)

print("Global Data : ", globalData)
file = LspRuntimeMonitor.outputFolderPath+"/"+"stats_data.csv"
lspLib.printGlobalResults(file, globalData)
