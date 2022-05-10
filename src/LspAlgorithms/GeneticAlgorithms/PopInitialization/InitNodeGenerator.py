import uuid
from LspAlgorithms.GeneticAlgorithms.Chromosome import Chromosome


class InitNodeGenerator:
    
    def __init__(self, queue) -> None:
        """
        """
        self.queue = queue
        self.uuid = uuid.uuid4()


    def generate(self, pipeline):
        """
        """

        while len(self.queue) > 0 and not pipeline.full():
            node = self.queue[-1]
            self.queue = self.queue[:-1]

            self.nextNode(node, pipeline)

        return None


    def nextNode(self, node, pipeline):
        """
        """

        # print("------ : ", node.chromosome, node.itemsToOrder, len(node.chromosome.stringIdentifier))
        if node.period < 0:
            if pipeline.full():
                return None

            if not Chromosome.feasible(node.chromosome):
                print("/////////////////////////////////////////////////", node.chromosome)

            node.chromosome.stringIdentifier = tuple(node.chromosome.stringIdentifier)
            pipeline.put(node)
            return None

        for child in node.generateChild():
            if pipeline.full():
                return None
            self.nextNode(child, pipeline)

        return None


