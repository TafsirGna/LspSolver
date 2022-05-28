from collections import defaultdict
import random
import threading

from pyparsing import copy
from LspAlgorithms.GeneticAlgorithms.GAOperators.CrossOverNode import CrossOverNode
from LspAlgorithms.GeneticAlgorithms.Chromosome import Chromosome
from LspInputDataReading.LspInputDataInstance import InputDataInstance


class CrossOverOperator:
    """
    """

    def __init__(self, parentChromosomes) -> None:
        """
        """

        self.parentChromosomes = parentChromosomes
        self._stopSearchEvent = threading.Event()
        self._visitedNodes = defaultdict(lambda: None)

    
    def process(self):
        """
        """
        
        same = True
        reference = self.parentChromosomes[0]
        for chromosome in self.parentChromosomes: 
            if chromosome != reference:
                same = False
        
        if same:
            return reference

        print("Crossover : ", self.parentChromosomes)

        # before launching the recursive search
        minInstance, maxInstance = (self.parentChromosomes[0], self.parentChromosomes[1]) if self.parentChromosomes[0] < self.parentChromosomes[0] else (self.parentChromosomes[1], self.parentChromosomes[0])
        random.seed()
        gapLength = int(InputDataInstance.instance.nPeriods / 4) 
        crossOverPeriod = random.randint(gapLength, InputDataInstance.instance.nPeriods - (gapLength + 1))

        node = CrossOverNode(maxInstance, crossOverPeriod - 1)
        node.chromosome.stringIdentifier = minInstance.stringIdentifier
        node.prepSearchSettings(minInstance)

        result = []
        self.nextNode(node, result)

        # TODO
        if len(result) == 0:
            print("weeeeeeeeeeeeeeeeiiiiiiiiiiiiiiiiiiiiird")
            return min(self.parentChromosomes)

        chromosome = result[0]
        # if chromosome.cost != Chromosome.createFromIdentifier(chromosome.stringIdentifier).cost:
        #     print(" hiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii")
        print("Cross Over result : ", chromosome)
        return chromosome

    
    def nextNode(self, node, result):
        """
        """

        if node is None:
            print("next node : returning none")
            return None

        node.chromosome.stringIdentifier = tuple(node.chromosome.stringIdentifier)

        if self._visitedNodes[node.chromosome.stringIdentifier] is not None:
            print("visited node")
            return None
        self._visitedNodes[node.chromosome.stringIdentifier] = 1

        # print("next node : ", node.chromosome, node.chromosome.dnaArray, node.period)

        if node.period <= -1:

            # if not Chromosome.feasible(node.chromosome):
            # if node.chromosome.dnaArray != Chromosome.createFromIdentifier(node.chromosome.stringIdentifier).dnaArray:
            #     print("//////////////////////////////////////////////////////////////////////////", self.parentChromosomes, node.chromosome, node.chromosome.dnaArray)
            
            # if Chromosome.pool[node.chromosome.stringIdentifier] is not None:
            #     return None

            result.append(node.chromosome)
            self._stopSearchEvent.set()
            return None

        for child in node.generateChild():
            # print("child loop : ", child)
            self.nextNode(child, result)
            
            if self._stopSearchEvent.is_set():
                return None

        return None
