from collections import defaultdict
import random
import threading
from LspAlgorithms.GeneticAlgorithms.GAOperators.CrossOverNode import CrossOverNode
from LspAlgorithms.GeneticAlgorithms.Chromosome import Chromosome
from LspInputDataReading.LspInputDataInstance import InputDataInstance
import concurrent.futures


class CrossOverOperator:
    """
    """

    def __init__(self, parentChromosomes) -> None:
        """
        """

        self.parentChromosomes = parentChromosomes
        self._stopSearchEvents = {0: threading.Event(), 1: threading.Event()}
        self._visitedNodes = {0: defaultdict(lambda: None), 1: defaultdict(lambda: None)}
        self.offsprings = {0: None, 1: None}


    def process(self, offspring_result = 2):
        """
        """

        if offspring_result not in [1,2]:
            # TODO: throw an error
            return None, None


        if self.parentChromosomes[0] == self.parentChromosomes[1]:
            return self.parentChromosomes[0], self.parentChromosomes[1]

        # print("Crossover : ", self.parentChromosomes)

        # before launching the recursive search
        gapLength = int(InputDataInstance.instance.nPeriods / 3)
        random.seed()
        crossOverPeriod = random.randint(gapLength, InputDataInstance.instance.nPeriods - (gapLength + 1))

        with concurrent.futures.ThreadPoolExecutor() as executor:
            nodes = []
            # 1rst node
            nodes.append(CrossOverNode(self.parentChromosomes, crossOverPeriod - 1, 0))

            # 2nd node if commanded
            if offspring_result == 2:
                nodes.append(CrossOverNode(self.parentChromosomes, crossOverPeriod - 1, 1))

            print(list(executor.map(self.nextNode, nodes)))

        # if chromosome.cost != Chromosome.createFromIdentifier(chromosome.stringIdentifier).cost:
        #     print(" Watch out")
        print("Cross Over result : ", [self.parentChromosomes, self.offsprings])
        return tuple(self.offsprings.values())


    def nextNode(self, node):
        """
        """

        if node is None:
            print("next node : returning none")
            return None

        node.chromosome.stringIdentifier = tuple(node.chromosome.stringIdentifier)

        if self._visitedNodes[node.index][node.chromosome.stringIdentifier] is not None:
            print("visited node")
            return None
        self._visitedNodes[node.index][node.chromosome.stringIdentifier] = 1

        # print("next node : ", node.chromosome, node.chromosome.dnaArray, node.period)

        if node.period <= -1:

            # if not Chromosome.feasible(node.chromosome):
            if node.chromosome.dnaArray != Chromosome.createFromIdentifier(node.chromosome.stringIdentifier).dnaArray:
                print("//////////////////////////////////////////////////////////////////////////", self.parentChromosomes, node.chromosome, node.chromosome.dnaArray)

            # if Chromosome.pool[node.chromosome.stringIdentifier] is not None:
            #     return None

            self.offsprings[node.index] = node.chromosome
            self._stopSearchEvents[node.index].set()
            return None

        for child in node.generateChild():
            # print("child loop : ", child)
            self.nextNode(child)

            if (self._stopSearchEvents[node.index]).is_set():
                return None

        return None
