from collections import defaultdict
import numpy as np
from scipy import sparse

class InputDataInstance:
	"""
	"""

	instance = None

	def __init__(self, nItems = 0, nPeriods = 0, demandsArray = [], stockingCostsArray = [], changeOverCostsArray = []):
		"""
		"""

		self.nItems = int(nItems)
		self.nPeriods = int(nPeriods)
		# self.demandsArray = sparse.csc_matrix(np.array(demandsArray))
		self.demandsArray = np.array(demandsArray)
		self.stockingCostsArray = np.array(stockingCostsArray)
		self.changeOverCostsArray = np.array(changeOverCostsArray)

		# self.demandsArrayZipped = [[j for j,val in enumerate(row) if val == 1] for row in self.demandsArray]
		self.demandsArrayZipped = [[]]
		self.itemDemandsPerPeriod = defaultdict(lambda: [])
		refItem = 0
		for item, row in enumerate(self.demandsArray):
			for period, demand in enumerate(row):
				if demand == 1:
					if refItem == item:
						self.demandsArrayZipped[-1].append(period)
					else:
						self.demandsArrayZipped.append([period])
						refItem = item
					self.itemDemandsPerPeriod[period].append(item) 


		# print("Demands ", self.demandsArrayZipped)

	def __repr__(self):
		return "Number of Items is : {} \n".format(self.nItems) + \
		"Number of Periods is : {} \n".format(self.nPeriods) + \
		"Demands for each item are : {} \n".format(self.demandsArray) + \
		"Holding costs for each item are : {} \n".format(self.stockingCostsArray) + \
		"Changeover costs from one item to another one are : {} \n".format(self.changeOverCostsArray)