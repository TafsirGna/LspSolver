#--------------------
# Class : Instance
# author : Tafsir GNA
# purpose : Describing the structure of an instance to the algorithm
#--------------------

class InputDataInstance:
	"""
	"""

	nbItems = 0
	nbTimes = 0
	demandsGrid = []
	holdingGrid = []
	chanOverGrid = []

	def __init__(self, nbItems = 0, nbTimes = 0, demandsGrid = [], holdingGrid = [], chanOverGrid = []):
		"""
		"""

		self.nbItems = int(nbItems)
		self.nbTimes = int(nbTimes)
		self.demandsGrid = demandsGrid
		self.holdingGrid = holdingGrid
		self.chanOverGrid = chanOverGrid

		# then, i perform a process over the 'demandsGrid' to obtain a grid with all the deadlines corresponding to all the demands of items
		# self.deadlineDemandPeriods = []
		# i = 0
		# while i < nbItems:
		# 	self.deadlineDemandPeriods.append(self.getDemandPeriods(demandsGrid[i]))
		# 	i+=1

		# # at this point, i want to determine what category the problem submitted, belongs to
		# # to do so, the number of zeros to be present in a solution is a good factor
		# nbZero = self.nbTimes
		# for deadlines in self.deadlineDemandPeriods:
		# 	nbZero -= len(deadlines)

		# if nbZero == 0:
		# 	self.zerosRow = []
		# else:
		# 	self.zerosRow = [0] * nbZero

		# # 

		# self.orderedPrecs = []

		# for i in range(0, self.nbItems):
		# 	row = []
		# 	row.append([0,0])
		# 	for j in range(0, self.nbItems):
		# 		row.append(list([j+1, int(self.chanOverGrid[j][i])]))
		# 	row = sorted(row ,key = getPrecsTabKey)
		# 	self.orderedPrecs.append(row)





		# // The next step is to record in a table fork each item the different periods in which it could be produce

		#print("category : ", self.category)
		# Additionnal variables
		#self.manufactItemsPeriods = getManufactPeriodsGrid(nbItems, self.deadlineDemandPeriods)

	#	implementation of the function called when an object is printed to the screen

	def __repr__(self):
		return "Number of Items is : {} \n".format(self.nbItems) + \
		"Number of Times is : {} \n".format(self.nbTimes) + \
		"Demands for each item are : {} \n".format(self.demandsGrid) + \
		"Holding costs for each item are : {} \n".format(self.holdingGrid) + \
		"Changeover costs from one item to another one are : {} \n".format(self.chanOverGrid)
		# "Changeover : {} \n".format(self.orderedPrecs)

	def getDemandPeriods(self, demand):

		i=0
		result = []
		size_demand = len(demand)
		while i < size_demand:
			if int(demand[i]) == 1:
				result.append(i)
			i+=1 
		return result