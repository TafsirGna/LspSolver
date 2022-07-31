#!/usr/bin/python3.5
# -*-coding: utf-8 -*


class PseudoChromosome(object):
	"""
	"""

	def __init__(self, value) -> None:
		"""
		"""

		self.stringIdentifier = value["newStringIdentifier"]
		self.value = value
		self.cost = value["chromosome"].cost - value["variance"]

	def __lt__(self, chromosome):
		return self.cost < chromosome.cost

	def __repr__(self):
		return "{} : {}".format(self.stringIdentifier, self.cost)


	