#!/usr/bin/python3.5
# -*-coding: utf-8 -*

from collections import defaultdict
import threading
import uuid
import concurrent.futures

from numpy import math
from LspAlgorithms.GeneticAlgorithms.LocalSearch.LocalSearchEngine import LocalSearchEngine
from LspAlgorithms.GeneticAlgorithms.PopInitialization.InitNodeGenerator import InitNodeGenerator
from LspAlgorithms.GeneticAlgorithms.PopInitialization.InitNodeGeneratorManager import InitNodeGeneratorManager
from LspAlgorithms.GeneticAlgorithms.PopInitialization.Population import Population
from LspRuntimeMonitor import LspRuntimeMonitor
from ParameterSearch.ParameterData import ParameterData
from .InitSearchNode import SearchNode
from threading import Thread

class PopInitializer:
    """
    """

    def __init__(self, strategy = "DFS", criteria = None) -> None:
        """
        """

        self.strategy = strategy
        self.threads = []
        self.populations = defaultdict(lambda: Population([]))
        self.lock = threading.Lock()
        self.popsLock = defaultdict(lambda: threading.Lock())
        self.nodeGeneratorManager = self.createNodeGeneratorManager()


    def process(self):
        """
        """

        with concurrent.futures.ThreadPoolExecutor() as executor:
            for _ in range(ParameterData.instance.nPrimaryThreads):
                executor.submit(self.mainThreadTask)
            # executor.map(self.mainThreadTask)

        LspRuntimeMonitor.output(str(self.populations))
        return self.populations.values()


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


    def mainThreadTask(self):
        """Search chromosomes
        """

        threadUUID = uuid.uuid4()

        with concurrent.futures.ThreadPoolExecutor() as executor:
            for _ in range(ParameterData.instance.nReplicaThreads):
                executor.submit(self.replicaThreadTask, threadUUID)

        (self.populations[threadUUID]).popSize = len((self.populations[threadUUID]).chromosomes)


    def replicaThreadTask(self, mainThreadId):
        """
        """

        with self.lock:
            node = self.nodeGeneratorManager.newInstance(mainThreadId)

        while node is not None: 

            result = None
            with self.popsLock[mainThreadId]:
                result = (self.populations[mainThreadId]).add(node.chromosome)
                # (LocalSearchEngine()).populate(node.chromosome, [self.popsLock[mainThreadId], population])
            if result is None:
                break  

            with self.lock:
                node = self.nodeGeneratorManager.newInstance(mainThreadId)
