#!/usr/bin/python3.5
# -*-coding: utf-8 -*

import queue
from LspAlgorithms.GeneticAlgorithms.Chromosome import Chromosome
from LspAlgorithms.GeneticAlgorithms.PopInitialization.NodeGenerator import NodeGenerator
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
        self.nodeGenerator = None

    def process(self, inputDataInstance):
        """
        """

        self.inputDataInstance = inputDataInstance

        ###
        if LspRuntimeStatisticsMonitor.instance:
            LspRuntimeStatisticsMonitor.instance.popInitClockStart = time.clock()
        ###

        rootNode = self.rootNode()
        self.nodeGenerator = NodeGenerator(rootNode)
        NodeGenerator.instance = self.nodeGenerator

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
        for node in self.nodeGenerator.generate(): 
            chromosomes.append(node.chromosome)
            if ParameterData.instance and len(chromosomes) >= ParameterData.instance.popSize:
                break  

        population = Population(chromosomes)
        print(population)

        return population