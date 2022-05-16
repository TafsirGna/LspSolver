from collections import defaultdict
import threading
from LspAlgorithms.GeneticAlgorithms.GAOperators.CrossOverNode import CrossOverNode
from LspAlgorithms.GeneticAlgorithms.Chromosome import Chromosome


class CrossOverOperator:
    """
    """

    def __init__(self, parentChromosomes) -> None:
        """
        """

        self.parentChromosomes = parentChromosomes
        self._stopSearchEvent = threading.Event()
        self._visitedNodes = defaultdict(lambda: None)

    
    def rootNode(self):
        """
        """

        node = CrossOverNode(self.parentChromosomes)
        node.prepSearch()
        return node

    
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

        node = self.rootNode()
        result = []
        self.nextNode(node, result)

        # TODO
        if len(result) == 0:
            return min(self.parentChromosomes)
        return result[0]

    
    def nextNode(self, node, result):
        """
        """

        if node is None:
            return None

        node.chromosome.stringIdentifier = tuple(node.chromosome.stringIdentifier)

        if self._visitedNodes[node.chromosome.stringIdentifier] is not None:
            return None
        self._visitedNodes[node.chromosome.stringIdentifier] = 1

        if len(node.blankPeriods) == 0:

            chromosome = Chromosome.pool[node.chromosome.stringIdentifier]
            if chromosome is None:
                chromosome = Chromosome.evaluateDnaArray(node.chromosome.dnaArray)

            if not Chromosome.feasible(chromosome):
                print("processing : ", node.chromosome, node.blankPeriods, " | ", node.itemsToOrder, ' | ', node.chromosome.dnaArray)
                print("//////////////////////////////////////////////////////////////////////////", self.parentChromosomes)
            else:
                # print("after processing : ", node.chromosome, node.blankPeriods, " | ", node.itemsToOrder, ' | ', node.chromosome.dnaArray)
                self._stopSearchEvent.set()
                result.append(chromosome)
                return None

        for child in node.generateChild(self._stopSearchEvent):
            self.nextNode(child, result)
            
            if self._stopSearchEvent.is_set():
                return None

        return None
