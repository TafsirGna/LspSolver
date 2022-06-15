from collections import defaultdict
import threading
import copy
from LspAlgorithms.GeneticAlgorithms.Chromosome import Chromosome
from LspAlgorithms.GeneticAlgorithms.LocalSearch.LocalSearchNode import LocalSearchNode
from ParameterSearch.ParameterData import ParameterData
import concurrent.futures
from LspInputDataReading.LspInputDataInstance import InputDataInstance

class LocalSearchEngine:
    """
    """

    def __init__(self) -> None:
        """
        """

        self.chromosome = None
        self._stopSearchEvent = threading.Event()

        if LocalSearchNode.genericGeneIndices is None:
            LocalSearchNode.genericGeneIndices = [(item, position) for item, itemGenes in enumerate(InputDataInstance.instance.demandsArrayZipped) for position, _ in enumerate(itemGenes)]


    def process(self, chromosome, strategy = "simple_mutation"):
        """Process the given chromosome in order to return a mutated version
        strategy: simple_mutation|absolute_mutation|positive_mutation
        """

        print("mutatiooooooon", strategy, chromosome, chromosome.dnaArray)

        self._visitedNodes = defaultdict(lambda: None)
        self.chromosome = chromosome
        node = LocalSearchNode(chromosome)

        result = {"depthIndex": 0, "chromosomes": []}

        # if strategy == "absolute_mutation":
        #     with concurrent.futures.ThreadPoolExecutor() as executor:
        #         index = 0
        #         for child in node.generateChild(result["depthIndex"]):
        #             executor.submit(self.dfsNextNode, child, strategy, result)

        #             index += 1
        #             if index == 3:
        #                 break
        # else:
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
            print("returning none")
            return None
        self._visitedNodes[node.chromosome.stringIdentifier] = 1

        if strategy == "simple_mutation":
            if Chromosome.pool[node.chromosome.stringIdentifier] is None: # result["depthIndex"] >= ParameterData.instance.simpleMutationDepthIndex
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
            if len(result["chromosomes"]) > ParameterData.instance.popSize:
                self._stopSearchEvent.set()
                return
        elif strategy == "absolute_mutation":
            # TODO
            # if node.rootChromosome is None:
            #     if LocalSearchNode.absoluteSearchedInstances[self.chromosome.stringIdentifier] is not None:
            #         return self.resumeLocalSearchOn(node, result)
            #     LocalSearchNode.absoluteSearchedInstances[self.chromosome.stringIdentifier] = {"path": [], "visitedInstances": defaultdict(lambda: None)}
            # instance = node.rootChromosome if node.rootChromosome is not None else self.chromosome
            # (LocalSearchNode.absoluteSearchedInstances[instance.stringIdentifier]["path"]).append({"node": node, "moves": []})
            # LocalSearchNode.absoluteSearchedInstances[instance.stringIdentifier]["visitedInstances"][node.chromosome.stringIdentifier] = 1

            if result["depthIndex"] == 0 and LocalSearchNode.absoluteSearchedInstances[node.chromosome.stringIdentifier] is not None:
                result["chromosomes"].append(LocalSearchNode.absoluteSearchedInstances[node.chromosome.stringIdentifier])
                print("Absolute mutation result ", self.chromosome, node.chromosome)
                self._stopSearchEvent.set()
                return None


        result["depthIndex"] += 1
        children = []
        depthIndex = result["depthIndex"] - 1
        for child in node.generateChild(depthIndex):

            if child is None:
                break

            # print("child ", node.chromosome, child.chromosome)

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
            if len(children) == 0 and node.chromosome not in Chromosome.localOptima["values"]:
                result["chromosomes"].append(node.chromosome)
                # (result["chromosomes"]).sort()
                print("Absolute mutation result ", self.chromosome, node.chromosome)
                # TODO
                LocalSearchNode.absoluteSearchedInstances[self.chromosome.stringIdentifier] = node.chromosome

                with Chromosome.localOptima["lock"]:
                    if node.chromosome not in Chromosome.localOptima["values"]:
                        Chromosome.localOptima["values"].add(node.chromosome)

                self._stopSearchEvent.set()
                return

        return None

    def resumeLocalSearchOn(self, node, result):
        """
        """

        print("----------------------- ", LocalSearchNode.absoluteSearchedInstances[node.chromosome.stringIdentifier]["path"])
        LocalSearchNode.absoluteSearchedInstances[node.chromosome.stringIdentifier]["path"] = LocalSearchNode.absoluteSearchedInstances[node.chromosome.stringIdentifier]["path"][:-1]
        path = copy.deepcopy(LocalSearchNode.absoluteSearchedInstances[node.chromosome.stringIdentifier]["path"])
        for index, element in enumerate(reversed(path)):

            subNode = element["node"]

            self._visitedNodes = copy.deepcopy(LocalSearchNode.absoluteSearchedInstances[node.chromosome.stringIdentifier]["visitedInstances"])
            del self._visitedNodes[subNode.chromosome.stringIdentifier]

            result["depthIndex"] = len(path) - (index + 2)

            print("resume local search", subNode)
            self.dfsNextNode(subNode, "absolute_mutation", result)

            if len(result["chromosomes"]) > 0:
                return None


        return None
