from LspAlgorithms.GeneticAlgorithms.GAOperators.MutationNode import MutationNode


class MutationOperator:
    """
    """

    def __init__(self, ) -> None:
        """
        """
        pass


    def mutationNode(self, chromosome):
        """
        """
        node = MutationNode(chromosome)
        return node

    def process(self, chromosome, strategy = "easy"): # strategy :  medium/advanced
        """
        """

        depth = 1 if strategy == "easy" else None
        node = self.mutationNode(chromosome)
        queue = node.children()
        depthIndex = 0

        while len(queue) > 0:
            node = queue[-1]
            queue = queue[:-1]

            children = node.children()
            if depth is not None :
                if depthIndex == depth:
                    return node.chromosome
            else:
                if len(children) == 0:
                    return node.chromosome

            queue += children
            depthIndex += 1

        return None