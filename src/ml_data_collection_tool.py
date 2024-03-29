import pandas as pd
import os
from LspAlgorithms.GeneticAlgorithms.Hcm.Solver import GeneticAlgorithm
from ParameterSearch.ParameterData import ParameterData
from LspInputDataReading.LspInputDataReader import InputDataReader
from LspAlgorithms.GeneticAlgorithms.LspRuntimeMonitor import LspRuntimeMonitor
from pathlib import Path
import csv
import LspLibrary as lspLib

# instanceIndices = [1, 2, 3, 4, 5, 8, 21, 23, 35, 36, 53, 58, 61, 69, 73, 78, 85, 87, 90, 94]
instanceIndices = [1]
mlDataPath = "data/ML/sets/raw/"
instanceRootPath = "data/input/instancesWith20periods/"
ParameterData.instance = ParameterData()

for index in reversed(instanceIndices):
    inputDataReader = InputDataReader()
    inputFilePath = instanceRootPath + str(index)
    inputDataInstance = inputDataReader.readInput(inputFilePath)

    trialIndex = 0
    nRows = 0
    nIdles = 0
    filePath = mlDataPath + str(index) + ".csv"

    while True:
    # while trialIndex < 10:
        # reading the data from the file if it exists
        if not os.path.isfile(filePath):
            # Path(mlDataFilePath0).touch()
            with open(filePath, "w") as csv_file:
                # print headers
                writer = csv.DictWriter(csv_file, fieldnames=lspLib.fieldnames)
                writer.writeheader()

        df = pd.read_csv(filePath)
        nRows = len(df)

        print("--- Processing instance: ", str(index), "trial -> ", trialIndex, " / ", nRows)
        LspRuntimeMonitor.instanceFileRootName = index
        LspRuntimeMonitor.mlData = pd.DataFrame(columns=lspLib.fieldnames) # []
        LspRuntimeMonitor.mlTestSetFeatures = []
        LspRuntimeMonitor.mlTestSetLabels = []
        LspRuntimeMonitor.instance = LspRuntimeMonitor()
        
        lspSolver = GeneticAlgorithm()
        lspSolver.solve()

        LspRuntimeMonitor.instance.stop()

        trialIndex += 1

        df = pd.concat([df, LspRuntimeMonitor.mlData], axis=0)
        # for index, row in enumerate(LspRuntimeMonitor.mlData):
        #     df.loc[index] = row

        df = df.drop_duplicates(keep='first')
        df.to_csv(filePath, index=False)

        if nRows == len(df):
            nIdles += 1
        else:
            nRows = len(df)

        if nIdles == 5:
            break
