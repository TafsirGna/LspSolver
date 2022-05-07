from LspAlgorithms.GeneticAlgorithms.LocalSearch.LocalSearchNode import LocalSearchNode
from ParameterSearch.ParameterData import ParameterData

class LocalSearchEngine:
    """
    """

    def __init__(self) -> None:
        pass


    def localSearchNode(self, chromosome):
        """
        """

        node = LocalSearchNode(chromosome)
        return node


    # def process(self, chromosome, strategy = "simple_mutation"):
    #     """Process the given chromosome in order to return a mutated version
    #     strategy: simple_mutation|absolute_mutation|positive_mutation
    #     """

    #     depthIndex = [0]
    #     node = self.localSearchNode(chromosome)
    #     return self.nextNode(node, depthIndex, strategy)


    # def nextNode(self, node, depthIndex, strategy):
    #     """
    #     """
    #     depthIndex[0] += 1
    #     for child in node.ge

    #     return self.nextNode(node, depthIndex, strategy)


    def process(self, chromosome, strategy = "simple_mutation"): 
        """Process the given chromosome in order to return a mutated version
        strategy: simple_mutation|absolute_mutation|positive_mutation
        """

        print("mutatioooooooooooooooooooooooooooooooon 1 ", strategy, ParameterData.instance.mutationRate, chromosome)
        node = self.localSearchNode(chromosome)
        queue = node.children()
        depthIndex = 0

        while len(queue) > 0:
            node = queue[-1]
            queue = queue[:-1]

            children = None
            if strategy == "simple_mutation": 
                # simple means random here
                if depthIndex == 1:
                    print("mutatioooooooooooooooooooooooooooooooon 2 ", strategy, ParameterData.instance.mutationRate, chromosome)
                    return node.chromosome
                children = node.children()
                depthIndex += 1
            elif strategy == "positive_mutation":
                if node.chromosome.cost < chromosome.cost:
                    return node.chromosome
                children = node.children()
            elif strategy ==  "absolute_mutation":
                children = node.children()
                if len(children) == 0:
                    return node.chromosome

            queue += children

        return None


    def populate(self, chromosome, popSet):
        """
        """

        node = self.localSearchNode(chromosome)
        population = popSet[1]
        queue = []

        while len(population.chromosomes) < ParameterData.instance.popSize:
            for child in node.generateChild():
                queue.append(child)
                result = population.add(child.chromosome)
                if result is None:
                    return

            if len(queue) == 0:
                return
            node = queue[-1]
            queue = queue[:-1]
        