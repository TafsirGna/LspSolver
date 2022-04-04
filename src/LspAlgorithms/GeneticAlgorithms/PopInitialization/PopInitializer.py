#!/usr/bin/python3.5
# -*-coding: utf-8 -*

from LspAlgorithms.GeneticAlgorithms.Chromosome import Chromosome
from LspAlgorithms.GeneticAlgorithms.PopInitialization.Population import Population
from LspInputDataReading.LspInputDataInstance import InputDataInstance
from LspStatistics.LspRuntimeStatisticsMonitor import LspRuntimeStatisticsMonitor
import time
import random

from ParameterSearch.ParameterData import ParameterData

from .InitSearchNode import SearchNode

class PopInitializer:
    """
    """

    def __init__(self, strategy = "DFS", criteria = None) -> None:
        """
        """

        self.strategy = strategy

    def process(self, inputDataInstance):
        """
        """

        self.inputDataInstance = inputDataInstance
        self.queue = []

        ###
        if LspRuntimeStatisticsMonitor.instance:
            LspRuntimeStatisticsMonitor.instance.popInitClockStart = time.clock()
        ###

        rootNode = self.rootNode()

        population = self.search(rootNode)

        ###
        if LspRuntimeStatisticsMonitor.instance:
            LspRuntimeStatisticsMonitor.instance.popInitClockEnd = time.clock()
        ###

        return population

    def rootNode(self):
        """
        """

        return SearchNode.root(self.inputDataInstance)

    def search(self, node):
        """
        """
        
        chromosomes = []

        children = node.children()

        self.queue += children

        while len(self.queue) > 0:

            node = self.queue[-1]
            self.queue = self.queue[0:len(self.queue) - 1]

            children = node.children()

            if len(children) == 0: # leaf node
                chromosomes.append(node.chromosome)

                ###
                if ParameterData.instance:
                    if len(chromosomes) >= ParameterData.instance.popSize:
                        population = Population(chromosomes)
                        print(population)
                        return population
                ###

            random.shuffle(children)
            self.queue += children

        population = Population(chromosomes)
        print(population)

        return population