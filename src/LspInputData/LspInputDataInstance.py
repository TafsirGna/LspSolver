import numpy as np
from scipy import sparse

class InputDataInstance:
	"""
	"""

	nbItems = 0
	nbTimes = 0
	demandsArray = []
	stockingCostsArray = []
	chanOverArray = []

	def __init__(self, nbItems = 0, nbTimes = 0, demandsArray = [], stockingCostsArray = [], chanOverArray = []):
		"""
		"""

		self.nbItems = int(nbItems)
		self.nbTimes = int(nbTimes)
		self.demandsArray = sparse.csc_matrix(np.array(demandsArray))
		self.stockingCostsArray = np.array(stockingCostsArray)
		self.chanOverArray = np.array(chanOverArray)

	def __repr__(self):
		return "Number of Items is : {} \n".format(self.nbItems) + \
		"Number of Times is : {} \n".format(self.nbTimes) + \
		"Demands for each item are : {} \n".format(self.demandsArray) + \
		"Holding costs for each item are : {} \n".format(self.stockingCostsArray) + \
		"Changeover costs from one item to another one are : {} \n".format(self.chanOverArray)