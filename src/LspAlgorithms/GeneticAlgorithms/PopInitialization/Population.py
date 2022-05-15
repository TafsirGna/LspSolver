from collections import defaultdict
from math import ceil
from queue import Queue
import random
import concurrent.futures
import threading
import uuid
from LspAlgorithms.GeneticAlgorithms.Chromosome import Chromosome
from LspAlgorithms.GeneticAlgorithms.GAOperators.CrossOverOperator import CrossOverOperator
from LspAlgorithms.GeneticAlgorithms.GAOperators.MutationOperator import MutationOperator
from LspAlgorithms.GeneticAlgorithms.GAOperators.SelectionOperator import SelectionOperator
from LspRuntimeMonitor import LspRuntimeMonitor
from ParameterSearch.ParameterData import ParameterData

class Population:

    popSizes = defaultdict(lambda: ParameterData.instance.popSize)
    eliteSizes = defaultdict(lambda: 0)

    def __init__(self, lineageIdentifier = None) -> None:
        """
        """
        self.chromosomes = defaultdict(lambda: None)
        self.lineageIdentifier = uuid.uuid4() if lineageIdentifier is None else lineageIdentifier 
        self.popLength = 0

        self.dThreadOutputPipeline = None


    def fill(self, nodeGeneratorManager):
        """
        """
        
        for instance in nodeGeneratorManager.getInstance():
            if instance is None:
                break
            result = self.add(instance)
            if result is None:
                break
        
        Population.popSizes[self.lineageIdentifier] = self.popLength
        
        
    def evolve(self):
        """
        """
        selectionOperator = SelectionOperator(self)

        #
        # checking pipeline status 
        # if not self.dThreadOutputPipeline.empty():
        #     chromosome = self.dThreadOutputPipeline.get()
        #     elites.append(chromosome)

        newPop = Population(self.lineageIdentifier)
        # filling the elites in the new population
        for chromosome in list(LspRuntimeMonitor.popsData[self.lineageIdentifier]["elites"]):
            newPop.add(chromosome)

        popLock = threading.Lock()

        with concurrent.futures.ThreadPoolExecutor() as executor:
            print(list(executor.map(self.threadTask, 
                                        [selectionOperator] * ParameterData.instance.nReplicaThreads, 
                                        [popLock] * ParameterData.instance.nReplicaThreads,
                                        [newPop] * ParameterData.instance.nReplicaThreads)))
            # executor.submit(self.getNewPopulation)

        newPop.dThreadOutputPipeline =  self.dThreadOutputPipeline
        return newPop


    def elites(self):
        """
        """

        # Elites 
        elites = sorted([element["chromosome"] for element in self.chromosomes.values()])
        if Population.eliteSizes[self.lineageIdentifier] == 0:
            size = Population.popSizes[self.lineageIdentifier] * ParameterData.instance.elitePercentage 
            size = (1 if size < 1 else size)
            Population.eliteSizes[self.lineageIdentifier] = size
            
        return set(elites[:Population.eliteSizes[self.lineageIdentifier]])
                

    def maxElement(self):
        """
        """ 
        elements = sorted(self.chromosomes.values(), key=lambda element: element["chromosome"])
        return elements[-1]["chromosome"]


    def minElement(self):
        """
        """    
        elements = sorted(self.chromosomes.values(), key=lambda element: element["chromosome"])
        return elements[0]["chromosome"]    


    def add(self, chromosome):
        """
        """

        if self.popLength >= Population.popSizes[self.lineageIdentifier]:
            return None

        if self.chromosomes[chromosome.stringIdentifier] is None:
            self.chromosomes[chromosome.stringIdentifier] = {"chromosome": chromosome, "size": 1}
        else:
            self.chromosomes[chromosome.stringIdentifier]["size"] += 1
        
        self.popLength += 1

        # Chromosome Pool
        if Chromosome.pool[chromosome.stringIdentifier] is None:
            Chromosome.pool[chromosome.stringIdentifier] = chromosome   

        return self.chromosomes[chromosome.stringIdentifier]


    def threadTask(self, selectionOperator, popLock, newPop):
        """
        """

        threadID = uuid.uuid4()
        queue = []

        while True:

            while len(queue) < 3:
                chromosomeA, chromosomeB = selectionOperator.select()
                chromosome = None
                if (random.random() < ParameterData.instance.crossOverRate):
                    chromosome = (CrossOverOperator([chromosomeA, chromosomeB])).process()
                    # print("Crossover : ", threadID, chromosomeA, chromosomeB, chromosome, len(newPop.chromosomes))
                else:
                    chromosome = chromosomeA if chromosomeA < chromosomeB else chromosomeB

                if chromosome is not None and (random.random() < ParameterData.instance.mutationRate):
                    # Proceding to mutate the chromosome
                    chromosome = (MutationOperator()).process(chromosome)

                if chromosome is not None:
                    # print("Chromo --- ", chromosome)
                    queue.append(chromosome)

            with popLock:
                for chromosome in queue:
                    # print("pop length : ", len(newPop.chromosomes))
                    result = newPop.add(chromosome)
                    if result is None:
                        return

            queue = []
                    

    def __repr__(self):
        """
        """
        return "Population : {} : \nCost Total :{} ".format(self.chromosomes, 0)
