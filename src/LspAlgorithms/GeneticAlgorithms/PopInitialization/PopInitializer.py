#!/usr/bin/python3.5
# -*-coding: utf-8 -*

import threading
from LspAlgorithms.GeneticAlgorithms.PopInitialization.InitNodeGenerator import InitNodeGenerator
from LspAlgorithms.GeneticAlgorithms.PopInitialization.InitNodeGeneratorManager import InitNodeGeneratorManager
from LspAlgorithms.GeneticAlgorithms.PopInitialization.Population import Population
from LspRuntimeMonitor import LspRuntimeMonitor
from ParameterSearch.ParameterData import ParameterData
from .InitSearchNode import SearchNode
from queue import Queue

class PopInitializer:
    """
    """

    def __init__(self) -> None:
        """
        """

        self.populations = [Population([]) for _ in range(ParameterData.instance.nPrimaryThreads)]
        self.initPipeline = Queue(maxsize=(ParameterData.instance.popSize * ParameterData.instance.nPrimaryThreads))
        # self.stopInitEvent = threading.Event()
        
        # NodeGeneratorManager
        self.nodeGeneratorManager = self.createNodeGeneratorManager()
        self.nodeGeneratorManager.start(self.initPipeline)


    def process(self):
        """
        """

        index = 0
        while not self.initPipeline.empty():
            chromosome = self.initPipeline.get()
            self.populations[index].add(chromosome)

            index = index + 1 if index < ParameterData.instance.nPrimaryThreads - 1 else 0 

        LspRuntimeMonitor.output(str(self.populations))
        return self.populations


    def createNodeGeneratorManager(self):
        """ Create a node generator manager
        """

        nodeGenerators = self.initNodeGenerators()
        return InitNodeGeneratorManager(nodeGenerators)


    def rootNode(self):
        """
        """
        return SearchNode.root()


    def initNodeGenerators(self):
        """
        """

        queue = self.rootNode().children()
        nodeGenerators = [InitNodeGenerator([node]) for node in queue]
        return nodeGenerators

