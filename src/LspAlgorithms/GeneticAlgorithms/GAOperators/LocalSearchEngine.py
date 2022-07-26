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
    localSearchMemory = {"lock": threading.Lock(), "content":defaultdict(lambda: None)}
    evaluationDataPool = {"lock": threading.Lock(), "content": dict()}
    # visitedChroms = {"lock": threading.Lock(), "content": dict()}

    def __init__(self) -> None:
        """
        """

        self.result = None


    def process(self, chromosome, strategy = "simple_mutation", args = None):
        """Process the given chromosome in order to return a mutated version
        strategy: random_mutation|absolute_mutation|simple_mutation
        """

        print("mutatiooon", strategy, chromosome, chromosome.dnaArray)

        # if strategy == "fitter_than":
        #     result = LocalSearchEngine.localSearchMemory["content"]["fitter_than"][(chromosome.stringIdentifier, args["fittest"].stringIdentifier)]
        #     if result is not None:
        #         return result
        if strategy == "positive_mutation":
            if LocalSearchEngine.localSearchMemory["content"]["positive_mutation"] is not None and chromosome.stringIdentifier in LocalSearchEngine.localSearchMemory["content"]["positive_mutation"]:
                if LocalSearchEngine.localSearchMemory["content"]["positive_mutation"][chromosome.stringIdentifier]["data"]["genes"] == []:
                    return LocalSearchEngine.localSearchMemory["content"]["positive_mutation"][chromosome.stringIdentifier]["result"] if LocalSearchEngine.localSearchMemory["content"]["positive_mutation"][chromosome.stringIdentifier]["result"] is not None else chromosome

        self.searchIndividu(chromosome, strategy, args)

        # print("cro : ", chromosome.genesByPeriod)
        print("Mutation results : ", strategy, chromosome, self.result)

        if strategy != "population":
            c = Chromosome.createFromIdentifier(self.result.stringIdentifier)
            if c.dnaArray != self.result.dnaArray or c.cost != self.result.cost or c.genesByPeriod != self.result.genesByPeriod:
                print("Mutation error : ", self.result.cost != c.cost, self.result.genesByPeriod != c.genesByPeriod, self.result.dnaArray != c.dnaArray, "\n",
                    self.result.cost, c.cost, "\n",
                    # self.result.genesByPeriod, " --- ", c.genesByPeriod, "\n", 
                    self.result.dnaArray, c.dnaArray)

        return self.result


    def searchIndividu(self, chromosome, strategy, args = None):
        """
        """

        results = []
        self.selectedGenes = None

        # if strategy == "absolute_mutation":
        #     self.refineInstance(chromosome)
        #     return None
        if strategy == "positive_mutation":
            if LocalSearchEngine.localSearchMemory["content"]["positive_mutation"] is None:
                LocalSearchEngine.localSearchMemory["content"]["positive_mutation"] = dict()
            if chromosome.stringIdentifier not in LocalSearchEngine.localSearchMemory["content"]["positive_mutation"]:
                LocalSearchEngine.localSearchMemory["content"]["positive_mutation"][chromosome.stringIdentifier] = {"data": {"genes": None}, "result": None}
            self.selectedGenes = LocalSearchEngine.localSearchMemory["content"]["positive_mutation"][chromosome.stringIdentifier]["data"]["genes"]

        # print("Searching individu !!!")

        if self.selectedGenes is None:
            self.selectedGenes = [gene for itemGenes in chromosome.dnaArray for gene in itemGenes if gene.cost > 0]
        # random.shuffle(selectedGenes)

        # print("selected : ", selectedGenes)
        # for periodGene in selectedGenes:
        while len(self.selectedGenes) > 0:
            periodGene = random.choice(self.selectedGenes)

            # print("gene : ", periodGene)
            periodGeneLowerLimit, periodGeneUpperLimit = Chromosome.geneLowerUpperLimit(chromosome, periodGene)
            
            increment = 1
            backwardPeriod, forwardPeriod = periodGene.period, periodGene.period
            while True:
                if forwardPeriod is not None:
                    forwardPeriod = periodGene.period + increment
                if backwardPeriod is not None:
                    backwardPeriod = periodGene.period - increment

                if backwardPeriod is not None and backwardPeriod < 0:
                    backwardPeriod = None

                if forwardPeriod is not None and forwardPeriod > InputDataInstance.instance.nPeriods - 1:
                    forwardPeriod = None

                # print(backwardPeriod, forwardPeriod)
                if backwardPeriod is not None :
                    result = self.handleAltPeriod(chromosome, strategy, periodGene, backwardPeriod, periodGeneLowerLimit, periodGeneUpperLimit, results, args)
                    if result == "RETURN":
                        return None
                    elif result == "SET_ALT_PERIOD_NONE":
                        backwardPeriod = None

                if forwardPeriod is not None :
                    result = self.handleAltPeriod(chromosome, strategy, periodGene, forwardPeriod, periodGeneLowerLimit, periodGeneUpperLimit, results, args)
                    if result == "RETURN":
                        return None
                    elif result == "SET_ALT_PERIOD_NONE":
                        forwardPeriod = None

                if backwardPeriod is None and forwardPeriod is None:
                    break

                increment += 1

            self.selectedGenes.remove(periodGene)

        if strategy == "simple_mutation":
            pick = np.random.choice(results)
            self.result = pick if isinstance(pick, Chromosome) else self.switchItems(pick)
            return None
        elif strategy == "population":
            self.result = list(set(results))
            return self.result
        elif strategy == "all_evaluations":
            self.result = results
            return self.result
        elif strategy == "positive_mutation":
            LocalSearchEngine.localSearchMemory["content"]["positive_mutation"][chromosome.stringIdentifier]["data"]["genes"] = []
            self.result = chromosome if LocalSearchEngine.localSearchMemory["content"]["positive_mutation"][chromosome.stringIdentifier]["result"] is None else LocalSearchEngine.localSearchMemory["content"]["positive_mutation"][chromosome.stringIdentifier]["result"]
            return None
        # elif strategy == "fitter_than":
        #     if self.result is None:
        #         self.result = chromosome
        #         localSearchMemory["content"]["fitter_than"][(chromosome.stringIdentifier, args["fittest"].stringIdentifier)] = self.result
        #     return None

        print("Search ended")


    def handleAltPeriod(self, chromosome, strategy, periodGene, altPeriod, periodGeneLowerLimit, periodGeneUpperLimit, results, args):
        """
        """

        if self.areItemsSwitchable(chromosome, periodGene, altPeriod, periodGeneLowerLimit, periodGeneUpperLimit):

            mStringIdentifier = self.mutationStringIdentifier(chromosome.stringIdentifier, periodGene.period, altPeriod)
            matchingChromosome = None if mStringIdentifier not in Chromosome.pool["content"] else Chromosome.pool["content"][mStringIdentifier]
            if matchingChromosome is None:
                evaluationData = None if mStringIdentifier not in LocalSearchEngine.evaluationDataPool["content"] else LocalSearchEngine.evaluationDataPool["content"][mStringIdentifier]

            if strategy == "random_mutation":
                if matchingChromosome is not None:
                    self.result = matchingChromosome
                else:
                    if evaluationData is None:
                        evaluationData = self.evaluateItemsSwitch(chromosome, periodGene, altPeriod)
                        LocalSearchEngine.evaluationDataPool["content"][mStringIdentifier] = evaluationData
                    self.result = self.switchItems(evaluationData)
                return "RETURN"

            if strategy == "population":
                if matchingChromosome is not None:
                    results.append(matchingChromosome)
                else:
                    if evaluationData is None:
                        evaluationData = self.evaluateItemsSwitch(chromosome, periodGene, altPeriod)
                        LocalSearchEngine.evaluationDataPool["content"][mStringIdentifier] = evaluationData
                    results.append(self.switchItems(evaluationData))

            if strategy == "all_evaluations":
                if matchingChromosome is not None:
                    evaluationData = None if mStringIdentifier not in LocalSearchEngine.evaluationDataPool["content"] else LocalSearchEngine.evaluationDataPool["content"][mStringIdentifier]
                
                if evaluationData is None:
                    evaluationData = self.evaluateItemsSwitch(chromosome, periodGene, altPeriod)
                    LocalSearchEngine.evaluationDataPool["content"][mStringIdentifier] = evaluationData
                results.append(evaluationData)

            if strategy == "positive_mutation":
                ok = False
                if matchingChromosome is not None:
                    if matchingChromosome < chromosome:
                        self.result = matchingChromosome
                        ok = True     
                else:
                    if self.isSwitchInteresting(chromosome, periodGene, altPeriod):
                        if evaluationData is None:
                            evaluationData = self.evaluateItemsSwitch(chromosome, periodGene, altPeriod)
                            LocalSearchEngine.evaluationDataPool["content"][mStringIdentifier] = evaluationData
                        if evaluationData["variance"] > 0:
                            self.result = self.switchItems(evaluationData)
                            ok = True
                if ok:
                    LocalSearchEngine.localSearchMemory["content"]["positive_mutation"][chromosome.stringIdentifier]["data"]["genes"] = self.selectedGenes
                    if LocalSearchEngine.localSearchMemory["content"]["positive_mutation"][chromosome.stringIdentifier]["result"] is None or \
                        (LocalSearchEngine.localSearchMemory["content"]["positive_mutation"][chromosome.stringIdentifier]["result"] is not None and self. result < LocalSearchEngine.localSearchMemory["content"]["positive_mutation"][chromosome.stringIdentifier]["result"]):
                        LocalSearchEngine.localSearchMemory["content"]["positive_mutation"][chromosome.stringIdentifier]["result"] = self.result
                    return "RETURN"

            # if strategy == "fitter_than":
            #     if matchingChromosome is not None:
            #         if matchingChromosome < args["fittest"]:
            #             self.result = matchingChromosome
            #             return "RETURN"
            #     else:
            #         if self.isSwitchInteresting(chromosome, periodGene, altPeriod):
            #             if evaluationData is None:
            #                 evaluationData = self.evaluateItemsSwitch(chromosome, periodGene, altPeriod)
            #                 LocalSearchEngine.evaluationDataPool["content"][mStringIdentifier] = evaluationData
            #             if evaluationData["variance"] > 0 and evaluationData["chromosome"].cost - evaluationData["variance"] < args["fittest"].cost:
            #                 self.result = self.switchItems(evaluationData)
            #                 return "RETURN"

            if strategy == "simple_mutation":
                if matchingChromosome is not None:
                    if matchingChromosome < chromosome:
                        self.result = matchingChromosome
                        return "RETURN"
                    results.append(matchingChromosome)
                else:
                    if evaluationData is None:
                        evaluationData = self.evaluateItemsSwitch(chromosome, periodGene, altPeriod)
                        LocalSearchEngine.evaluationDataPool["content"][mStringIdentifier] = evaluationData
                    if evaluationData["variance"] > 0:
                        self.result = self.switchItems(evaluationData)
                        return "RETURN"
                    results.append(evaluationData)
        else:
            return "SET_ALT_PERIOD_NONE"



    # def refineInstance(self, chromosome):
    #     """
    #     """
        
    #     visited = set()
    #     queue = [{"depth": 0, "value": chromosome}]
    #     queueItemKeys = set()

    #     while len(queue) > 0:

    #         instance = queue[0]
    #         queue = queue[1:]

    #         if not isinstance(instance["value"], Chromosome):
    #             queueItemKeys.remove(instance["value"]["resultingStringIdentifier"])
    #             instance["value"] = self.switchItems(instance["value"])

    #         # if instance["depth"] > 0 and instance["value"] == chromosome:
    #         #     continue

    #         results = (LocalSearchEngine().searchIndividu(instance["value"], "all_evaluations"))
    #         visited.add(instance["value"].stringIdentifier)

    #         positiveResults = []
    #         for element in results:
    #             element["resulting_cost"] = element["chromosome"].cost - element["variance"]
    #             if element["resulting_cost"] < instance["value"].cost:
    #                 positiveResults.append(element)

    #             element["resultingStringIdentifier"] = self.mutationStringIdentifier(element["chromosome"].stringIdentifier, element["period"], element["altPeriod"]) 
    #             if element["resultingStringIdentifier"] not in queueItemKeys and element["resultingStringIdentifier"] not in visited:
    #                 queue.append({"depth": instance["depth"] + 1, "value": element})
    #                 queueItemKeys.add(element["resultingStringIdentifier"])

    #         if len(positiveResults) == 0 and instance["depth"] > 0:
    #             self.result = instance["value"]
    #             return None

    #         queue.sort(key=lambda item: item["value"]["resulting_cost"])


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


    def isSwitchInteresting(self, chromosome, periodGene, altPeriod):
        """
        """

        if chromosome.stringIdentifier[altPeriod] == 0 and altPeriod < periodGene.period:
            nextGene0 = Chromosome.nextProdGene(altPeriod, chromosome.dnaArray, chromosome.stringIdentifier)
            if nextGene0 is not None and nextGene0 == periodGene:
                return False

        return True


    def switchItems(self, evaluationData):
        """
        """

        print("Switching item : ", evaluationData)

        chromosome = evaluationData["chromosome"]
        mutation = Chromosome()
        periodGene = chromosome.dnaArray[(chromosome.genesByPeriod[evaluationData["period"]])[0]][(chromosome.genesByPeriod[evaluationData["period"]])[1]]
        altPeriod = evaluationData["altPeriod"]
        mutation.stringIdentifier = self.mutationStringIdentifier(chromosome.stringIdentifier, periodGene.period, altPeriod)
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

        print("Switch done")
        return mutation


    def mutationStringIdentifier(self, stringIdentifier, period, altPeriod):
        """
        """
# 
        stringIdentifier = list(stringIdentifier)
        stringIdentifier[period], stringIdentifier[altPeriod] = stringIdentifier[altPeriod], stringIdentifier[period]

        return tuple(stringIdentifier)


    def evaluateItemsSwitch(self, chromosome, periodGene, altPeriod):
        """
        """

        print("Evaluating : --- ", chromosome, periodGene.period, altPeriod, chromosome.dnaArray)

        evaluationData = {"chromosome": chromosome, "variance": periodGene.cost, "periodGene": {}, "altPeriodGene": {}, "altPeriod": altPeriod, "period": periodGene.period}
        if chromosome.stringIdentifier[altPeriod] > 0: 
            altPeriodGene = chromosome.dnaArray[(chromosome.genesByPeriod[altPeriod])[0]][(chromosome.genesByPeriod[altPeriod])[1]]
            evaluationData["variance"] += altPeriodGene.cost

            nextPeriodGene = None if periodGene.nextGene is None else chromosome.dnaArray[periodGene.nextGene[0]][periodGene.nextGene[1]]
            nextAltPeriodGene = None if altPeriodGene.nextGene is None else chromosome.dnaArray[altPeriodGene.nextGene[0]][altPeriodGene.nextGene[1]]

            prevPeriodGene = None if periodGene.prevGene is None else chromosome.dnaArray[periodGene.prevGene[0]][periodGene.prevGene[1]]
            prevAltPeriodGene = None if altPeriodGene.prevGene is None else chromosome.dnaArray[altPeriodGene.prevGene[0]][altPeriodGene.prevGene[1]]
            

            if nextPeriodGene is not None and nextPeriodGene == altPeriodGene:
                evaluationData["case"] = 1
                if nextAltPeriodGene is not None:
                    evaluationData["altPeriodGene"]["nextAltPeriodGeneChangeOverCost"] = InputDataInstance.instance.changeOverCostsArray[periodGene.item][nextAltPeriodGene.item] 
                    evaluationData["variance"] += nextAltPeriodGene.changeOverCost - evaluationData["altPeriodGene"]["nextAltPeriodGeneChangeOverCost"]

                evaluationData["altPeriodGene"]["changeOverCost"] = (0 if prevPeriodGene is None else InputDataInstance.instance.changeOverCostsArray[prevPeriodGene.item][altPeriodGene.item])
                evaluationData["periodGene"]["changeOverCost"] = InputDataInstance.instance.changeOverCostsArray[altPeriodGene.item][periodGene.item]

                evaluationData["periodGene"]["prevGene"] = altPeriodGene
                evaluationData["periodGene"]["nextGene"] = nextAltPeriodGene
                evaluationData["altPeriodGene"]["prevGene"] = prevPeriodGene
                evaluationData["altPeriodGene"]["nextGene"] = periodGene

                # print("vovo 1 : ", evaluationData)

            elif nextAltPeriodGene is not None and nextAltPeriodGene == periodGene:
                evaluationData["case"] = 2
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

            evaluationData["variance"] -= (evaluationData["altPeriodGene"]["stockingCost"] + evaluationData["altPeriodGene"]["changeOverCost"])

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
                evaluationData["case"] = 2
                evaluationData["periodGene"]["changeOverCost"] = periodGene.changeOverCost

            evaluationData["periodGene"]["stockingCost"] = InputDataInstance.instance.stockingCostsArray[periodGene.item] * (InputDataInstance.instance.demandsArrayZipped[periodGene.item][periodGene.position] - altPeriod)

        evaluationData["variance"] -= evaluationData["periodGene"]["stockingCost"] + evaluationData["periodGene"]["changeOverCost"]

        print("Evaluation result : ", chromosome, periodGene.period, altPeriod, " ---> ", evaluationData)

        return evaluationData        
