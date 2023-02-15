import pandas as pd
import os
from LspAlgorithms.GeneticAlgorithms.Hcm.Solver import GeneticAlgorithm
from ParameterSearch.ParameterData import ParameterData
from LspInputDataReading.LspInputDataReader import InputDataReader
from LspAlgorithms.GeneticAlgorithms.LspRuntimeMonitor import LspRuntimeMonitor
from pathlib import Path
import csv
import LspLibrary as lspLib

instanceIndices = [1, 2, 3, 4, 5, 8, 21, 23, 35, 36, 53, 58, 61, 69, 73, 78, 85, 87, 90, 94]
mlDataFilePath0 = "data/ML/dataset0.csv"
instanceRootPath = "data/input/instancesWith20periods/"
ParameterData.instance = ParameterData()

for index in instanceIndices:
    inputDataReader = InputDataReader()
    inputFilePath = instanceRootPath + str(index)
    inputDataInstance = inputDataReader.readInput(inputFilePath)

    trialIndex = 0
    nRows = 0
    nIdles = 0

    while True:

        # reading the data from the file if it exists
        if not os.path.isfile(mlDataFilePath0):
            # Path(mlDataFilePath0).touch()
            with open(mlDataFilePath0, "w") as csv_file:
                # print headers
                writer = csv.DictWriter(csv_file, fieldnames=lspLib.fieldnames)
                writer.writeheader()

        df = pd.read_csv(mlDataFilePath0)
        nRows = len(df)

        print("--- Processing instance: ", str(index), "trial -> ", trialIndex, " / ", nRows)
        LspRuntimeMonitor.mlData = pd.DataFrame(columns=lspLib.fieldnames) # []
        LspRuntimeMonitor.instance = LspRuntimeMonitor()
        
        lspSolver = GeneticAlgorithm()
        lspSolver.solve()

        LspRuntimeMonitor.instance.stop()

        trialIndex += 1

        df = pd.concat([df, LspRuntimeMonitor.mlData], axis=0)
        # for index, row in enumerate(LspRuntimeMonitor.mlData):
        #     df.loc[index] = row

        df = df.drop_duplicates()
        df.to_csv(mlDataFilePath0, index=False)

        if nRows == len(df):
            nIdles += 1
        else:
            nRows = len(df)

        if nIdles == 5:
            break
