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

        node = self.rootNode()
        result = []
        self.nextNode(node, result)

        return result[0]

    
    def nextNode(self, node, result):
        """
        """
        if node is None:
            return None

        print("processing : ", node.chromosome, node.blankPeriods, " | ", node.itemsToOrder, ' | ', node.chromosome.dnaArray)

        if len(node.blankPeriods) == 0:
            
            if node.prevBlankPeriod is not None and node.prevBlankPeriod > 0:
                node.blankPeriods.insert(0, -1)
                node.catchUpLeftOrders() 

            node.chromosome.stringIdentifier = tuple(node.chromosome.stringIdentifier)
            chromosome = Chromosome.pool[node.chromosome.stringIdentifier]
            if chromosome is None:
                # return Chromosome.createFromIdentifier(node.chromosome.stringIdentifier)
                chromosome = node.chromosome
                # print("cooling", self.parentChromosomes, chromosome, chromosome.dnaArray)
                chromosome.cost = Chromosome.classLightCostCalculation(chromosome.dnaArray)
                # print("equal cost : ", chromosome, Chromosome.createFromIdentifier(chromosome.stringIdentifier))
            # print("equal cost : ", chromosome)
            if not Chromosome.feasible(chromosome):
                print("processing : ", node.chromosome, node.blankPeriods, " | ", node.itemsToOrder, ' | ', node.chromosome.dnaArray)
                print("//////////////////////////////////////////////////////////////////////////", self.parentChromosomes)
            else:
                print("after processing : ", node.chromosome, node.blankPeriods, " | ", node.itemsToOrder, ' | ', node.chromosome.dnaArray)
                self.stopSearchEvent.set()
                result.append(chromosome)
                return None

        for child in node.generateChild(self.stopSearchEvent):
            self.nextNode(child, result)
            
            if self.stopSearchEvent.is_set():
                return None

        return None
