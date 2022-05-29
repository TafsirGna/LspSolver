from collections import defaultdict
import threading
import copy
from LspAlgorithms.GeneticAlgorithms.Chromosome import Chromosome
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

        print("mutatiooooooon", strategy, chromosome, chromosome.dnaArray)

        self._visitedNodes = defaultdict(lambda: None)
        self.chromosome = chromosome
        node = LocalSearchNode(chromosome)

        result = {"depthIndex": 0, "chromosomes": []}
        self.dfsNextNode(node, strategy, result)

        # if len(result["chromosomes"]) and (result["chromosomes"][0]).dnaArray != Chromosome.createFromIdentifier(result["chromosomes"][0].stringIdentifier).dnaArray:
        #     print(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::", result["chromosomes"][0])

        print("mutation results : ", result["chromosomes"])
        # print("Path : ", LocalSearchNode.absoluteSearchedInstances[self.chromosome.stringIdentifier]["path"])
        return result["chromosomes"]


    def dfsNextNode(self, node, strategy, result):
        """
        """

        # print("*************** Prosus", result["depthIndex"])

        if self._visitedNodes[node.chromosome.stringIdentifier] is not None:
            return None
        self._visitedNodes[node.chromosome.stringIdentifier] = 1

        if strategy == "simple_mutation":
            if result["depthIndex"] >= ParameterData.instance.simpleMutationDepthIndex: #and Chromosome.pool[node.chromosome.stringIdentifier] is None:
                result["chromosomes"].append(node.chromosome)
                self._stopSearchEvent.set()
                return None
        elif strategy == "positive_mutation":
            if node < self: #and Chromosome.pool[node.chromosome.stringIdentifier] is None:
                print("positive_mutation ", result["depthIndex"], node.chromosome, node < self)
                result["chromosomes"].append(node.chromosome)
                self._stopSearchEvent.set()
                return
        elif strategy == "population":
            result["chromosomes"].append(node.chromosome)
            if len(result["chromosomes"]) > ParameterData.instance.popSize * ParameterData.instance.nPrimaryThreads:
                self._stopSearchEvent.set()
                return
        elif strategy == "absolute_mutation":
            if result["depthIndex"] == 0:
                if LocalSearchNode.absoluteSearchedInstances[self.chromosome.stringIdentifier] is not None:
                    return self.resumeLocalSearchOn(node, result)
                LocalSearchNode.absoluteSearchedInstances[self.chromosome.stringIdentifier] = {"path": [], "visitedInstances": defaultdict(lambda: None)}
            (LocalSearchNode.absoluteSearchedInstances[self.chromosome.stringIdentifier]["path"]).append({"node": node, "moves": []})
            LocalSearchNode.absoluteSearchedInstances[self.chromosome.stringIdentifier]["visitedInstances"][node.chromosome.stringIdentifier] = 1

        result["depthIndex"] += 1
        children = []
        depthIndex = result["depthIndex"] - 1
        for child in node.generateChild(depthIndex):

            if child is None:
                break

            print("child ", node.chromosome, child.chromosome)

            next = False
            if strategy == "positive_mutation":
                if child < node:
                    next = True
            elif strategy  == "absolute_mutation":
                    if child < node:
                        children.append(child)
                        next = True
            else:
                next = True

            if next:
                self.dfsNextNode(child, strategy, result)

            if self._stopSearchEvent.is_set():
                return None


        # TODO
        if strategy == "absolute_mutation":
            # print("Absolute mutation", len(children))
            if len(children) == 0:
                result["chromosomes"].append(node.chromosome)
                print("Absolute mutation result ", self.chromosome, node.chromosome)
                self._stopSearchEvent.set()
                return

        return None

    def resumeLocalSearchOn(self, node, result):
        """
        """

        LocalSearchNode.absoluteSearchedInstances[node.chromosome.stringIdentifier]["path"] = LocalSearchNode.absoluteSearchedInstances[node.chromosome.stringIdentifier]["path"][:-1]

        self._visitedNodes = copy.deepcopy(LocalSearchNode.absoluteSearchedInstances[node.chromosome.stringIdentifier]["visitedInstances"])
        del self._visitedNodes[(LocalSearchNode.absoluteSearchedInstances[node.chromosome.stringIdentifier]["path"][-1]["node"]).chromosome.stringIdentifier]

        result["depthIndex"] = len(LocalSearchNode.absoluteSearchedInstances[node.chromosome.stringIdentifier]["path"]) - 2
        for index, element in enumerate(reversed(LocalSearchNode.absoluteSearchedInstances[node.chromosome.stringIdentifier]["path"])):
            node = element["node"]
            print("resume local search", node)
            self.dfsNextNode(node, "absolute_mutation", result)

            if len(result["chromosomes"]) > 0:
                return None


        return None
