from collections import defaultdict
import threading
import copy
from LspAlgorithms.GeneticAlgorithms.Chromosome import Chromosome
# from LspAlgorithms.GeneticAlgorithms.LocalSearch.LocalSearchNode import LocalSearchNode
from ParameterSearch.ParameterData import ParameterData
import concurrent.futures
from LspInputDataReading.LspInputDataInstance import InputDataInstance
import random
import numpy as np

class LocalSearchEngine:
    """
    """

    genericGeneIndices = None
    mutationsMemory = {"lock": threading.Lock(), "db":defaultdict(lambda: None)}

    def __init__(self) -> None:
        """
        """

        self.searchDepth = 0
        self.result = None
        self._stopSearchEvent = threading.Event()

        # if LocalSearchEngine.genericGeneIndices is None:
        #     LocalSearchEngine.genericGeneIndices = [(item, position) for item, itemGenes in enumerate(InputDataInstance.instance.demandsArrayZipped) for position, _ in enumerate(itemGenes)]


    def process(self, chromosome, strategy = "simple_mutation"):
        """Process the given chromosome in order to return a mutated version
        strategy: random_mutation|absolute_mutation|simple_mutation
        """

        print("mutatiooon", strategy, chromosome, chromosome.dnaArray, chromosome.dnaArray == Chromosome.createFromIdentifier(chromosome.stringIdentifier).dnaArray)

        self._visitedNodes = defaultdict(lambda: None)

        self.searchIndividu(chromosome, strategy)

        # print("cro : ", chromosome.genesByPeriod)
        print("Mutation results : ", strategy, chromosome, self.result)

        c = Chromosome.createFromIdentifier(self.result.stringIdentifier)
        if c.dnaArray != self.result.dnaArray or c.cost != self.result.cost or c.genesByPeriod != self.result.genesByPeriod:
            print("Mutation error : ", self.result.cost != c.cost, self.result.genesByPeriod != c.genesByPeriod, self.result.dnaArray != c.dnaArray, "\n",
                self.result.cost, c.cost, "\n",
                # self.result.genesByPeriod, " --- ", c.genesByPeriod, "\n", 
                self.result.dnaArray, c.dnaArray)

        # if strategy != "population":
        #     if self.result.dnaArray != Chromosome.createFromIdentifier(self.result.stringIdentifier).dnaArray:
        #         print("Oaaaaaaaaaaaaaaaaauuuuuuuuuuuuuuuuuuuuuuuuuhhhhhhhhhhhhhhh")
        #         print(self.result.dnaArray, "\n", Chromosome.createFromIdentifier(self.result.stringIdentifier).dnaArray)

        #     print("cro ***** : ", self.result.genesByPeriod)
        return (self.result if self.result is not None else chromosome)


    def searchIndividu(self, chromosome, strategy):
        """
        """

        results = []

        if strategy == "absolute_mutation":
            if self._visitedNodes[chromosome.stringIdentifier] is not None:
                return None
            print("chrom : ", chromosome, self.searchDepth) 

        # shuffledPeriods = [(period, item) for period, item in enumerate(chromosome.stringIdentifier)]

        # print("shuffledPeriods : ", shuffledPeriods, chromosome.stringIdentifier)
        # random.shuffle(shuffledPeriods)

        orderedGenes = [gene for itemGenes in chromosome.dnaArray for gene in itemGenes if gene.cost > 0]
        # orderedGenes.sort(key=lambda gene: gene.cost, reverse= True)

        # random.shuffle(orderedGenes)

        # print("ordered : ", orderedGenes)
        for periodGene in orderedGenes:

            print("gene : ", periodGene)
            periodGeneLowerLimit, periodGeneUpperLimit = Chromosome.geneLowerUpperLimit(chromosome, periodGene)
            
            i = 1
            backwardPeriod, forwardPeriod = periodGene.period, periodGene.period
            while True:
                if forwardPeriod is not None:
                    forwardPeriod = periodGene.period + i
                if backwardPeriod is not None:
                    backwardPeriod = periodGene.period - i

                if backwardPeriod is not None and backwardPeriod < 0:
                    backwardPeriod = None

                if forwardPeriod is not None and forwardPeriod > InputDataInstance.instance.nPeriods - 1:
                    forwardPeriod = None

                # print(backwardPeriod, forwardPeriod)
                if backwardPeriod is not None :
                    if self.areItemsSwitchable(chromosome, periodGene, backwardPeriod, periodGeneLowerLimit, periodGeneUpperLimit):
                        evaluationData = self.evaluateItemsSwitch(chromosome, periodGene, backwardPeriod)
                        if strategy == "random_mutation":
                            self.result = self.switchItems(chromosome, evaluationData)
                            return None 

                        if strategy == "population":
                            results.append(self.switchItems(chromosome, evaluationData))

                        if strategy == "positive_mutation":
                            if evaluationData["variance"] > 0:
                                self.result = self.switchItems(chromosome, evaluationData)
                                return None 

                        if strategy == "simple_mutation":
                            if evaluationData["variance"] > 0:
                                self.result = self.switchItems(chromosome, evaluationData)
                                return None 
                            results.append(evaluationData)

                        if strategy == "absolute_mutation":
                            if evaluationData["variance"] > 0:
                                results.append(evaluationData)
                    else:
                        backwardPeriod = None

                if forwardPeriod is not None :
                    if self.areItemsSwitchable(chromosome, periodGene, forwardPeriod, periodGeneLowerLimit, periodGeneUpperLimit):
                        evaluationData = self.evaluateItemsSwitch(chromosome, periodGene, forwardPeriod)
                        if strategy == "random_mutation":
                            self.result = self.switchItems(chromosome, evaluationData)
                            return None 

                        if strategy == "population":
                            results.append(self.switchItems(chromosome, evaluationData))

                        if strategy == "positive_mutation":
                            if evaluationData["variance"] > 0:
                                self.result = self.switchItems(chromosome, evaluationData)
                                return None 

                        if strategy == "simple_mutation":
                            if evaluationData["variance"] > 0:
                                self.result = self.switchItems(chromosome, evaluationData)
                                return None 
                            results.append(evaluationData)

                        if strategy == "absolute_mutation":
                            if evaluationData["variance"] > 0:
                                results.append(evaluationData)
                    else:
                        forwardPeriod = None

                if backwardPeriod is None and forwardPeriod is None:
                    break

                i += 1

                if strategy == "absolute_mutation":
                    if len(results) > 0:
                        self.searchDepth += 1
                        self._visitedNodes[chromosome.stringIdentifier] = 1
                        self.searchIndividu(results[-1], strategy)

                        if self._stopSearchEvent.is_set():
                            return None


        if strategy == "absolute_mutation":
            if len(results) == 0:
                self.result = chromosome
                self._stopSearchEvent.set()
                return None
        elif strategy == "simple_mutation":
            # self.result = 
            self.result = self.switchItems(chromosome, np.random.choice(results))
            return None
        elif strategy == "population":
            self.result = results
            return None


    def areItemsSwitchable(self, chromosome, periodGene, altPeriod, periodGeneLowerLimit, periodGeneUpperLimit):
        """
        """

        if chromosome.stringIdentifier[altPeriod] > 0: 
            altPeriodGene = chromosome.dnaArray[(chromosome.genesByPeriod[altPeriod])[0]][(chromosome.genesByPeriod[altPeriod])[1]]
            altPeriodGeneLowerLimit, altPeriodGeneUpperLimit = Chromosome.geneLowerUpperLimit(chromosome, altPeriodGene)

            if (periodGeneLowerLimit <= altPeriod and altPeriod < periodGeneUpperLimit) and (altPeriodGeneLowerLimit <= periodGene.period and periodGene.period < altPeriodGeneUpperLimit):
                return True
        else:
            if (periodGeneLowerLimit <= altPeriod and altPeriod < periodGeneUpperLimit):
                return True

        return False


    def switchItems(self, chromosome, evaluationData):
        """
        """

        print("Switching item : ", evaluationData)

        mutation = Chromosome()
        periodGene = chromosome.dnaArray[(chromosome.genesByPeriod[evaluationData["period"]])[0]][(chromosome.genesByPeriod[evaluationData["period"]])[1]]
        altPeriod = evaluationData["altPeriod"]
        mutation.stringIdentifier = self.mutationStringIdentifier(chromosome.stringIdentifier, periodGene, altPeriod)
        mutation.dnaArray = copy.deepcopy(chromosome.dnaArray)
        mutation.genesByPeriod = copy.deepcopy(chromosome.genesByPeriod)
        mutation.cost = chromosome.cost - evaluationData["variance"]

        period = (mutation.dnaArray[periodGene.item][periodGene.position]).period
        (mutation.dnaArray[periodGene.item][periodGene.position]).period = altPeriod
        (mutation.dnaArray[periodGene.item][periodGene.position]).changeOverCost = evaluationData["periodGene"]["changeOverCost"]
        (mutation.dnaArray[periodGene.item][periodGene.position]).stockingCost = evaluationData["periodGene"]["stockingCost"]
        if "prevGene" in evaluationData["periodGene"]:
            (mutation.dnaArray[periodGene.item][periodGene.position]).prevGene = None if evaluationData["periodGene"]["prevGene"] is None else ((evaluationData["periodGene"]["prevGene"]).item, (evaluationData["periodGene"]["prevGene"]).position)
        if "nextGene" in evaluationData["periodGene"]:
            (mutation.dnaArray[periodGene.item][periodGene.position]).nextGene = None if evaluationData["periodGene"]["nextGene"] is None else ((evaluationData["periodGene"]["nextGene"]).item, (evaluationData["periodGene"]["nextGene"]).position)
        (mutation.dnaArray[periodGene.item][periodGene.position]).cost = evaluationData["periodGene"]["stockingCost"] + evaluationData["periodGene"]["changeOverCost"]

        if chromosome.stringIdentifier[altPeriod] == 0:

            del mutation.genesByPeriod[periodGene.period]
            mutation.genesByPeriod[altPeriod] = (periodGene.item, periodGene.position)

            if evaluationData["case"] == 1:
                if "prevGene" in evaluationData["periodGene"] and evaluationData["periodGene"]["prevGene"] is not None:
                    (mutation.dnaArray[(evaluationData["periodGene"]["prevGene"]).item][(evaluationData["periodGene"]["prevGene"]).position]).nextGene = (periodGene.item, periodGene.position)
                if "nextGene" in evaluationData["periodGene"] and evaluationData["periodGene"]["nextGene"] is not None:
                    (mutation.dnaArray[(evaluationData["periodGene"]["nextGene"]).item][(evaluationData["periodGene"]["nextGene"]).position]).prevGene = (periodGene.item, periodGene.position)
                    (mutation.dnaArray[(evaluationData["periodGene"]["nextGene"]).item][(evaluationData["periodGene"]["nextGene"]).position]).changeOverCost = evaluationData["periodGene"]["nextPeriodGeneChangeOverCost"]
                    (mutation.dnaArray[(evaluationData["periodGene"]["nextGene"]).item][(evaluationData["periodGene"]["nextGene"]).position]).calculateCost()

                if "nextAltPeriodGeneChangeOverCost" in evaluationData["altPeriodGene"]:
                    (mutation.dnaArray[(evaluationData["altPeriodGene"]["nextAltPeriodGene"]).item][(evaluationData["altPeriodGene"]["nextAltPeriodGene"]).position]).changeOverCost = evaluationData["altPeriodGene"]["nextAltPeriodGeneChangeOverCost"]
                    (mutation.dnaArray[(evaluationData["altPeriodGene"]["nextAltPeriodGene"]).item][(evaluationData["altPeriodGene"]["nextAltPeriodGene"]).position]).calculateCost()
                    (mutation.dnaArray[(evaluationData["altPeriodGene"]["nextAltPeriodGene"]).item][(evaluationData["altPeriodGene"]["nextAltPeriodGene"]).position]).prevGene = periodGene.prevGene

                if periodGene.prevGene is not None:
                    (mutation.dnaArray[periodGene.prevGene[0]][periodGene.prevGene[1]]).nextGene = periodGene.nextGene
        else:

            mutation.genesByPeriod[periodGene.period] = ((chromosome.genesByPeriod[altPeriod])[0], (chromosome.genesByPeriod[altPeriod])[1])
            mutation.genesByPeriod[altPeriod] = (periodGene.item, periodGene.position)

            altPeriodGene = chromosome.dnaArray[(chromosome.genesByPeriod[altPeriod])[0]][(chromosome.genesByPeriod[altPeriod])[1]]

            (mutation.dnaArray[altPeriodGene.item][altPeriodGene.position]).period = period
            (mutation.dnaArray[altPeriodGene.item][altPeriodGene.position]).changeOverCost = evaluationData["altPeriodGene"]["changeOverCost"]
            (mutation.dnaArray[altPeriodGene.item][altPeriodGene.position]).stockingCost = evaluationData["altPeriodGene"]["stockingCost"]
            if "prevGene" in evaluationData["altPeriodGene"]:
                (mutation.dnaArray[altPeriodGene.item][altPeriodGene.position]).prevGene = None if evaluationData["altPeriodGene"]["prevGene"] is None else ((evaluationData["altPeriodGene"]["prevGene"]).item, (evaluationData["altPeriodGene"]["prevGene"]).position)
            if "nextGene" in evaluationData["altPeriodGene"]:
                (mutation.dnaArray[altPeriodGene.item][altPeriodGene.position]).nextGene = None if evaluationData["altPeriodGene"]["nextGene"] is None else ((evaluationData["altPeriodGene"]["nextGene"]).item, (evaluationData["altPeriodGene"]["nextGene"]).position)
            (mutation.dnaArray[altPeriodGene.item][altPeriodGene.position]).cost = evaluationData["altPeriodGene"]["stockingCost"] + evaluationData["altPeriodGene"]["changeOverCost"]

            if evaluationData["case"] == 2:
                if altPeriodGene.prevGene is not None:
                    (mutation.dnaArray[altPeriodGene.prevGene[0]][altPeriodGene.prevGene[1]]).nextGene = (periodGene.item, periodGene.position)
                if periodGene.nextGene is not None:
                    (mutation.dnaArray[periodGene.nextGene[0]][periodGene.nextGene[1]]).prevGene = (altPeriodGene.item, altPeriodGene.position)
                    (mutation.dnaArray[periodGene.nextGene[0]][periodGene.nextGene[1]]).changeOverCost = evaluationData["periodGene"]["nextPeriodGeneChangeOverCost"]
                    (mutation.dnaArray[periodGene.nextGene[0]][periodGene.nextGene[1]]).calculateCost()

            elif evaluationData["case"] == 1:
                if periodGene.prevGene is not None:
                    (mutation.dnaArray[periodGene.prevGene[0]][periodGene.prevGene[1]]).nextGene = (altPeriodGene.item, altPeriodGene.position)
                if altPeriodGene.nextGene is not None:
                    (mutation.dnaArray[altPeriodGene.nextGene[0]][altPeriodGene.nextGene[1]]).prevGene = (periodGene.item, periodGene.position)
                    (mutation.dnaArray[altPeriodGene.nextGene[0]][altPeriodGene.nextGene[1]]).changeOverCost = evaluationData["altPeriodGene"]["nextAltPeriodGeneChangeOverCost"]
                    (mutation.dnaArray[altPeriodGene.nextGene[0]][altPeriodGene.nextGene[1]]).calculateCost()

            elif evaluationData["case"] == 3:
                if altPeriodGene.nextGene is not None:
                    (mutation.dnaArray[altPeriodGene.nextGene[0]][altPeriodGene.nextGene[1]]).prevGene = (periodGene.item, periodGene.position)
                    (mutation.dnaArray[altPeriodGene.nextGene[0]][altPeriodGene.nextGene[1]]).changeOverCost = evaluationData["altPeriodGene"]["nextAltPeriodGeneChangeOverCost"]
                    (mutation.dnaArray[altPeriodGene.nextGene[0]][altPeriodGene.nextGene[1]]).calculateCost()

                if altPeriodGene.prevGene is not None:
                    (mutation.dnaArray[altPeriodGene.prevGene[0]][altPeriodGene.prevGene[1]]).nextGene = (periodGene.item, periodGene.position)

                if periodGene.prevGene is not None:
                    (mutation.dnaArray[periodGene.prevGene[0]][periodGene.prevGene[1]]).nextGene = (altPeriodGene.item, altPeriodGene.position)

                if periodGene.nextGene is not None:
                    (mutation.dnaArray[periodGene.nextGene[0]][periodGene.nextGene[1]]).prevGene = (altPeriodGene.item, altPeriodGene.position)
                    (mutation.dnaArray[periodGene.nextGene[0]][periodGene.nextGene[1]]).changeOverCost = evaluationData["periodGene"]["nextPeriodGeneChangeOverCost"]
                    (mutation.dnaArray[periodGene.nextGene[0]][periodGene.nextGene[1]]).calculateCost()

        # genesByPeriod
        # mutation.genesByPeriod = dict({gene.period: (gene.item, gen) for itemGenes in mutation.dnaArray for gene in itemGenes})

        return mutation


    def isSwitchWorth(self):
        """
        """

        pass

    def mutationStringIdentifier(self, stringIdentifier, periodGene, altPeriod):
        """
        """
# 
        stringIdentifier = list(stringIdentifier) #copy.deepcopy(stringIdentifier)
        stringIdentifier[periodGene.period], stringIdentifier[altPeriod] = stringIdentifier[altPeriod], stringIdentifier[periodGene.period]

        return tuple(stringIdentifier)


    def evaluateItemsSwitch(self, chromosome, periodGene, altPeriod):
        """
        """

        print("Evaluating : --- ", chromosome, periodGene.period, altPeriod, chromosome.dnaArray, chromosome.dnaArray == Chromosome.createFromIdentifier(chromosome.stringIdentifier).dnaArray, chromosome.cost == Chromosome.createFromIdentifier(chromosome.stringIdentifier).cost)

        evaluationData = {"variance": periodGene.cost, "periodGene": {}, "altPeriodGene": {}, "altPeriod": altPeriod, "period": periodGene.period}
        if chromosome.stringIdentifier[altPeriod] > 0: 
            altPeriodGene = chromosome.dnaArray[(chromosome.genesByPeriod[altPeriod])[0]][(chromosome.genesByPeriod[altPeriod])[1]]
            evaluationData["variance"] += altPeriodGene.cost

            nextPeriodGene = None if periodGene.nextGene is None else chromosome.dnaArray[periodGene.nextGene[0]][periodGene.nextGene[1]]
            nextAltPeriodGene = None if altPeriodGene.nextGene is None else chromosome.dnaArray[altPeriodGene.nextGene[0]][altPeriodGene.nextGene[1]]

            prevPeriodGene = None if periodGene.prevGene is None else chromosome.dnaArray[periodGene.prevGene[0]][periodGene.prevGene[1]]
            prevAltPeriodGene = None if altPeriodGene.prevGene is None else chromosome.dnaArray[altPeriodGene.prevGene[0]][altPeriodGene.prevGene[1]]
            

            if nextPeriodGene is not None and nextPeriodGene == altPeriodGene:
                evaluationData["case"] = 1
                print("choice 1-1", periodGene, altPeriodGene, evaluationData["variance"], periodGene.cost, altPeriodGene.cost)
                if nextAltPeriodGene is not None:
                    print("compris  : ", nextAltPeriodGene, nextAltPeriodGene.changeOverCost, nextAltPeriodGene.changeOverCost - InputDataInstance.instance.changeOverCostsArray[periodGene.item][nextAltPeriodGene.item], InputDataInstance.instance.changeOverCostsArray[periodGene.item][nextAltPeriodGene.item])
                    evaluationData["altPeriodGene"]["nextAltPeriodGeneChangeOverCost"] = InputDataInstance.instance.changeOverCostsArray[periodGene.item][nextAltPeriodGene.item] 
                    evaluationData["variance"] += nextAltPeriodGene.changeOverCost - evaluationData["altPeriodGene"]["nextAltPeriodGeneChangeOverCost"]
                    print(" $$$$$$$$$$$$$$$$$$$$$ : ", evaluationData)

                evaluationData["altPeriodGene"]["changeOverCost"] = (0 if prevPeriodGene is None else InputDataInstance.instance.changeOverCostsArray[prevPeriodGene.item][altPeriodGene.item])
                evaluationData["periodGene"]["changeOverCost"] = InputDataInstance.instance.changeOverCostsArray[altPeriodGene.item][periodGene.item]

                evaluationData["periodGene"]["prevGene"] = altPeriodGene
                evaluationData["periodGene"]["nextGene"] = nextAltPeriodGene
                evaluationData["altPeriodGene"]["prevGene"] = prevPeriodGene
                evaluationData["altPeriodGene"]["nextGene"] = periodGene

                print("vovo 1 : ", evaluationData)

            elif nextAltPeriodGene is not None and nextAltPeriodGene == periodGene:
                evaluationData["case"] = 2
                print("choice 1-2", periodGene, altPeriodGene)
                if nextPeriodGene is not None:
                    # print("compris --- : ", nextPeriodGene.changeOverCost - InputDataInstance.instance.changeOverCostsArray[altPeriodGene.item][nextPeriodGene.item])
                    evaluationData["periodGene"]["nextPeriodGeneChangeOverCost"] = InputDataInstance.instance.changeOverCostsArray[altPeriodGene.item][nextPeriodGene.item]
                    evaluationData["variance"] += nextPeriodGene.changeOverCost - evaluationData["periodGene"]["nextPeriodGeneChangeOverCost"]

                evaluationData["periodGene"]["changeOverCost"] = (0 if prevAltPeriodGene is None else InputDataInstance.instance.changeOverCostsArray[prevAltPeriodGene.item][periodGene.item])
                evaluationData["altPeriodGene"]["changeOverCost"] = InputDataInstance.instance.changeOverCostsArray[periodGene.item][altPeriodGene.item]

                evaluationData["periodGene"]["prevGene"] = prevAltPeriodGene
                evaluationData["periodGene"]["nextGene"] = altPeriodGene
                evaluationData["altPeriodGene"]["prevGene"] = periodGene
                evaluationData["altPeriodGene"]["nextGene"] = nextPeriodGene

            else:
                print("choice 1-3", periodGene, altPeriodGene)
                evaluationData["case"] = 3
                if nextAltPeriodGene is not None:
                    evaluationData["altPeriodGene"]["nextAltPeriodGeneChangeOverCost"] = InputDataInstance.instance.changeOverCostsArray[periodGene.item][nextAltPeriodGene.item]
                    evaluationData["variance"] += nextAltPeriodGene.changeOverCost - evaluationData["altPeriodGene"]["nextAltPeriodGeneChangeOverCost"]

                if nextPeriodGene is not None:
                    evaluationData["periodGene"]["nextPeriodGeneChangeOverCost"] = InputDataInstance.instance.changeOverCostsArray[altPeriodGene.item][nextPeriodGene.item]
                    evaluationData["variance"] += nextPeriodGene.changeOverCost - evaluationData["periodGene"]["nextPeriodGeneChangeOverCost"]

                evaluationData["periodGene"]["changeOverCost"] = (0 if prevAltPeriodGene is None else InputDataInstance.instance.changeOverCostsArray[prevAltPeriodGene.item][periodGene.item])
                evaluationData["altPeriodGene"]["changeOverCost"] = (0 if prevPeriodGene is None else InputDataInstance.instance.changeOverCostsArray[prevPeriodGene.item][altPeriodGene.item])

                evaluationData["periodGene"]["prevGene"] = prevAltPeriodGene
                evaluationData["periodGene"]["nextGene"] = nextAltPeriodGene
                evaluationData["altPeriodGene"]["prevGene"] = prevPeriodGene
                evaluationData["altPeriodGene"]["nextGene"] = nextPeriodGene

            evaluationData["altPeriodGene"]["stockingCost"] = InputDataInstance.instance.stockingCostsArray[altPeriodGene.item] * (InputDataInstance.instance.demandsArrayZipped[altPeriodGene.item][altPeriodGene.position] - periodGene.period)
            evaluationData["periodGene"]["stockingCost"] = InputDataInstance.instance.stockingCostsArray[periodGene.item] * (InputDataInstance.instance.demandsArrayZipped[periodGene.item][periodGene.position] - altPeriod)

            print("compris nice --- : ", (evaluationData["altPeriodGene"]["stockingCost"] + evaluationData["altPeriodGene"]["changeOverCost"]))
            evaluationData["variance"] -= (evaluationData["altPeriodGene"]["stockingCost"] + evaluationData["altPeriodGene"]["changeOverCost"])

            print("vovo 2 : ", evaluationData)

        else:
            prevGene0 = Chromosome.prevProdGene(altPeriod, chromosome.dnaArray, chromosome.stringIdentifier)  
            nextGene0 = Chromosome.nextProdGene(altPeriod, chromosome.dnaArray, chromosome.stringIdentifier)

            # print("jean ************************************************", prevGene0, nextGene0)
            if not((nextGene0 is not None and nextGene0 == periodGene) or (prevGene0 is not None and prevGene0 == periodGene)):
                evaluationData["case"] = 1
                evaluationData["periodGene"]["prevGene"] = prevGene0
                evaluationData["periodGene"]["nextGene"] = nextGene0

                # prevPeriodGene = None if periodGene.prevGene is None else chromosome.dnaArray[periodGene.prevGene[0]][periodGene.prevGene[1]]
                nextPeriodGene = None if periodGene.nextGene is None else chromosome.dnaArray[periodGene.nextGene[0]][periodGene.nextGene[1]]
                if nextPeriodGene is not None:
                    evaluationData["altPeriodGene"]["nextAltPeriodGene"] = nextPeriodGene
                    evaluationData["altPeriodGene"]["nextAltPeriodGeneChangeOverCost"] = (0 if periodGene.prevGene is None else InputDataInstance.instance.changeOverCostsArray[periodGene.prevGene[0]][nextPeriodGene.item])  
                    evaluationData["variance"] += nextPeriodGene.changeOverCost - evaluationData["altPeriodGene"]["nextAltPeriodGeneChangeOverCost"]

                if nextGene0 is not None:
                    evaluationData["periodGene"]["nextPeriodGeneChangeOverCost"] = InputDataInstance.instance.changeOverCostsArray[periodGene.item][nextGene0.item]
                    evaluationData["variance"] += nextGene0.changeOverCost - evaluationData["periodGene"]["nextPeriodGeneChangeOverCost"]

                evaluationData["periodGene"]["changeOverCost"] = (0 if prevGene0 is None else InputDataInstance.instance.changeOverCostsArray[prevGene0.item][periodGene.item])

            else:
                print("turtle ...")
                evaluationData["case"] = 2
                evaluationData["periodGene"]["changeOverCost"] = periodGene.changeOverCost

            evaluationData["periodGene"]["stockingCost"] = InputDataInstance.instance.stockingCostsArray[periodGene.item] * (InputDataInstance.instance.demandsArrayZipped[periodGene.item][periodGene.position] - altPeriod)

        print("ending compris : ", evaluationData["variance"], periodGene, periodGene.cost,  evaluationData["periodGene"]["stockingCost"] + evaluationData["periodGene"]["changeOverCost"])
        evaluationData["variance"] -= evaluationData["periodGene"]["stockingCost"] + evaluationData["periodGene"]["changeOverCost"]

        print("Evaluation result : ", chromosome, periodGene.period, altPeriod, " ---> ", evaluationData)

        return evaluationData        
