from LspAlgorithms.GeneticAlgorithms.CrossOverNode import CrossOverNode
from LspInputDataReading.LspInputDataInstance import InputDataInstance
from LspAlgorithms.GeneticAlgorithms.Chromosome import Chromosome


class CrossOverOperator:
    """
    """

    def __init__(self, parentChromosomes) -> None:
        """
        """

        self.parentChromosomes = parentChromosomes

    
    def rootNode(self):
        """
        """
        node = CrossOverNode(self.parentChromosomes)
        return node

    
    def process(self):
        """
        """

        chromosome = max(self.parentChromosomes)

        node = self.rootNode()
        queue = node.children()

        while len(queue) > 0:
            node = queue[-1]
            queue = queue[:-1]

            children = node.children()
            if len(children) == 0 and node.period < 0:
                if node.chromosome.cost < chromosome.cost:
                    print("fuckkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk", node.chromosome)
                    chromosome = node.chromosome
                # return node.chromosome

            queue += children

        return chromosome
