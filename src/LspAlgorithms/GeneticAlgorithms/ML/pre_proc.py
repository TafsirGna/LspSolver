import pandas as pd
import csv
from ....LspLibrary import *

mlDataFilePathInput = "data/ML/sets/raw/1.csv"
mlDataFilePathOutput = "data/ML/sets/preproc/1.csv"

# 1st step of the preprocessing

# removing duplicated rows
mlDF = pd.read_csv(mlDataFilePathInput)

# mlDF.head()
mlDF = mlDF.drop_duplicates()
mlDF.to_csv(mlDataFilePathInput, index=False)

# changing data format

with open(mlDataFilePathInput) as csv_file:
	csv_reader = csv.reader(csv_file, delimiter=",")
	preProcData = []
	index = 0
	# InstanceIndexChangeOverCost
	for row in csv_reader:
		if index > 0:
			
			preProcData.append(extractMLFeatures(row))

			# break
		index += 1


with open(mlDataFilePathOutput, mode='w') as csv_file:
    writer = csv.writer(csv_file, delimiter=',')
    for row in preProcData:
    	writer.writerow(row)


mlDF = pd.read_csv(mlDataFilePathOutput)

# mlDF.head()
mlDF = mlDF.drop_duplicates()
print(mlDF.info())
mlDF.to_csv(mlDataFilePathOutput, index=False)


