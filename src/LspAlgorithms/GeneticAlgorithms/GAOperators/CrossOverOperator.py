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
        self.stopSearchEvent = threading.Event()

    
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

        # print("processing : ", node.chromosome, node.blankPeriods, " | ", node.itemsToOrder, ' | ', node.chromosome.dnaArray)

        if len(node.blankPeriods) == 0:

            if node.prevBlankPeriod is not None and node.prevBlankPeriod > 0:
                node.completeCrossOver()

            node.chromosome.stringIdentifier = tuple(node.chromosome.stringIdentifier)
            chromosome = Chromosome.pool[node.chromosome.stringIdentifier]
            if chromosome is None:
                chromosome = node.chromosome
                chromosome.cost = Chromosome.classLightCostCalculation(chromosome.dnaArray)
            if not Chromosome.feasible(chromosome):
                print("processing : ", node.chromosome, node.blankPeriods, " | ", node.itemsToOrder, ' | ', node.chromosome.dnaArray)
                print("//////////////////////////////////////////////////////////////////////////", self.parentChromosomes)
            else:
                # print("after processing : ", node.chromosome, node.blankPeriods, " | ", node.itemsToOrder, ' | ', node.chromosome.dnaArray)
                self.stopSearchEvent.set()
                result.append(chromosome)
                return None

        for child in node.generateChild(self.stopSearchEvent):
            self.nextNode(child, result)
            
            if self.stopSearchEvent.is_set():
                return None

        return None
