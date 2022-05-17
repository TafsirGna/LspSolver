from collections import defaultdict
import queue
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
        self._stopSearchEvent = threading.Event()


    def process(self, chromosome, strategy = "simple_mutation"):
        """Process the given chromosome in order to return a mutated version
        strategy: simple_mutation|absolute_mutation|positive_mutation
        """

        # print("mutatioooooooooooon", strategy, chromosome)

        self._visitedNodes = defaultdict(lambda: None)
        self.chromosome = chromosome
        node = LocalSearchNode(chromosome)

        result = {"depthIndex": 0, "chromosomes": []}

        if strategy in ["simple_mutation", "population"]:
            self.dfsNextNode(node, strategy, result)
        elif strategy in ["absolute_mutation", "positive_mutation"]:
            self.greedySearch(node, strategy, result)

        return result["chromosomes"]
            

    def greedySearch(self, node, strategy, result):
        """
        Args - strategy: positive_mutation
        """

        queue = [node]

        while len(queue) > 0:

            node = queue[0]
            queue = queue[1:]

            if self._visitedNodes[node.chromosome.stringIdentifier] is not None:
                continue
            self._visitedNodes[node.chromosome.stringIdentifier] = 1

            # print("print")
            for child in node.generateChild():
                
                # print(len(self._visitedNodes), "|", self._visitedNodes[child.chromosome.stringIdentifier])

                if self._visitedNodes[child.chromosome.stringIdentifier] is not None or child in queue:
                    continue

                if strategy == "positive_mutation":
                    # print("oooooooooooooooooooooooooooooooooooooooooo", child.chromosome)
                    if child < self:
                        result["chromosomes"].append(child.chromosome)
                        return

                queue.append(child)     

            queue.sort() 


    def dfsNextNode(self, node, strategy, result):
        """
        """
        if self._visitedNodes[node.chromosome.stringIdentifier] is not None:
            return None
        self._visitedNodes[node.chromosome.stringIdentifier] = 1

        if strategy == "simple_mutation":
            if result["depthIndex"] == ParameterData.instance.simpleMutationDepthIndex:
                result["chromosomes"].append(node.chromosome)
                self._stopSearchEvent.set()
                return None
        elif strategy == "population":
            result["chromosomes"].append(node.chromosome)
            if len(result["chromosomes"]) > ParameterData.instance.popSize:
                self._stopSearchEvent.set()
                return

        result["depthIndex"] += 1
        children = []
        for child in node.generateChild():
            if self._stopSearchEvent.is_set():
                return None
            children.append(child)
            self.dfsNextNode(child, strategy, result)

        # TODO 
        if strategy == "absolute_mutation":
            print("Absolute mutation", len(children))
            if len(children) == 0:
                result["chromosomes"].append(node.chromosome)
                return None

        return None