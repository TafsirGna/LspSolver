import pandas as pd
import csv

mlDataFilePathInput = "data/ML/sets/raw/1.csv"
mlDataFilePathOutput = "data/ML/sets/preproc/1.csv"


def readDNA(preProcRow, data):
	"""
	"""

	data = data.replace("(", "")
	data = data.replace(")", "")
	data = data.split(", ")

	for datum in data:
		preProcRow.append(int(datum))

	return preProcRow

def readStockingCosts(preProcRow, data):
	"""
	"""

	data = data.replace("[", "")
	data = data.replace("]", "")
	data = data.split(" ")

	# index = 0
	for datum in data:
		if len(datum) > 0:
			preProcRow.append(int(datum))
			# index += 1
	# print(index)

	return preProcRow

def readChangeOverCosts(preProcRow, data):
	"""
	"""

	data = data.replace("[", "")
	data = data.replace("]", "")
	data = data.split("\n")

	# index = 0
	for line in data:
		numbers = line.split(" ")
		for number in numbers:
			if len(number) > 0:
				preProcRow.append(int(number))
				# index += 1
	# print(index)

	return preProcRow

def readDeadlines(preProcRow, data):
	"""
	"""

	return readChangeOverCosts(preProcRow, data)


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
			preProcRow = []
			# preProcRow.append(row[8])
			preProcRow = readDNA(preProcRow, row[0])
			preProcRow.append(row[1])
			preProcRow.append(row[2])
			# preProcRow = readChangeOverCosts(preProcRow, row[3])
			# preProcRow = readStockingCosts(preProcRow, row[4])
			# preProcRow = readDeadlines(preProcRow, row[5])
			preProcRow.append(row[7] > row[6])

			preProcData.append(preProcRow)
		index += 1


with open(mlDataFilePathOutput, mode='w') as csv_file:
    writer = csv.writer(csv_file, delimiter=',')
    for row in preProcData:
    	writer.writerow(row)


mlDF = pd.read_csv(mlDataFilePathOutput)

# mlDF.head()
mlDF = mlDF.drop_duplicates()
print(mlDF.info())


