
from LspAlgorithms.GeneticAlgorithms.LocalSearchNode import LocalSearchNode


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

    def process(self, chromosome, strategy = "simple_mutation", data = []): # strategy :  simple_mutation/advanced_mutation/population
        """
        """

        node = self.localSearchNode(chromosome)
        queue = node.children()
        depth = 1 if strategy == "easy" else None
        depthIndex = 0

        while len(queue) > 0:
            node = queue[-1]
            queue = queue[:-1]

            children = node.children()

            if strategy == "population":
                for child in children:
                    # with data[0]:
                    data[1].add(child.chromosome)
            elif strategy == "simple_mutation":
                depth = 1
                if depthIndex == depth:
                    return node.chromosome
            elif strategy ==  "advanced_mutation":
                if len(children) == 0:
                    return node.chromosome

            queue += children
            depthIndex += 1

        return None