from collections import defaultdict
import threading
from LspAlgorithms.GeneticAlgorithms.LocalSearch.LocalSearchNode import LocalSearchNode
from ParameterSearch.ParameterData import ParameterData

class LocalSearchEngine:
    """
    """

    def __init__(self) -> None:
        """
        """

        self.chromosome = None
        self.stopSearchEvent = threading.Event()


    def process(self, chromosome, strategy = "simple_mutation"):
        """Process the given chromosome in order to return a mutated version
        strategy: simple_mutation|absolute_mutation|positive_mutation
        """

        self.visitedNodes = defaultdict(lambda: None)
        self.chromosome = chromosome
        node = LocalSearchNode(chromosome)
        result = {"depthIndex": 0, "chromosomes": []}

        self.nextNode(node, strategy, result)
        return result["chromosomes"]


    def nextNode(self, node, strategy, result):
        """
        """
        if self.visitedNodes[node.chromosome.stringIdentifier] is not None:
            return None
        self.visitedNodes[node.chromosome.stringIdentifier] = 1

        if strategy == "simple_mutation":
            if result["depthIndex"] == ParameterData.instance.simpleMutationDepthIndex:
                result["chromosomes"].append(node.chromosome)
                self.stopSearchEvent.set()
                return None
        elif strategy == "positive_mutation":
            print(result["depthIndex"], node.chromosome, node.chromosome < self.chromosome)
            if node.chromosome < self.chromosome:
                result["chromosomes"].append(node.chromosome)
                self.stopSearchEvent.set()
                return 
        elif strategy == "population":
            result["chromosomes"].append(node.chromosome)

        result["depthIndex"] += 1
        children = []
        for child in node.generateChild():
            if self.stopSearchEvent.is_set():
                return None
            children.append(child)
            self.nextNode(child, strategy, result)

        # TODO 
        if strategy == "absolute_mutation":
            print("Absolute mutation", len(children))
            if len(children) == 0:
                result["chromosomes"].append(node.chromosome)
                return None

        return None

        