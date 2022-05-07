from LspAlgorithms.GeneticAlgorithms.GAOperators.CrossOverNode import CrossOverNode
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
        node.chromosome.stringIdentifier = "0" * InputDataInstance.instance.nPeriods
        return node

    
    def process(self):
        """
        """

        node = self.rootNode()
        queue = node.children()

        while len(queue) > 0:
            node = queue[-1]
            queue = queue[:-1]

            children = node.children()
            # if len(children) == 0 and node.period < 0:
            if len(children) == 0 and node.pointer == (None, None):

                chromosome = Chromosome.pool[node.chromosome.stringIdentifier]
                if chromosome is None:
                    # return Chromosome.createFromIdentifier(node.chromosome.stringIdentifier)
                    return Chromosome.evaluateDnaArray(node.chromosome.dnaArray)
                return chromosome

            queue += children

        return None