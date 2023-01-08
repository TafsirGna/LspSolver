from collections import defaultdict
import threading
import copy
from LspAlgorithms.GeneticAlgorithms.PopInitialization.Chromosome import Chromosome
from LspAlgorithms.GeneticAlgorithms.PopInitialization.PseudoChromosome import PseudoChromosome
# from ParameterSearch.ParameterData import ParameterData
# import concurrent.futures
from LspInputDataReading.LspInputDataInstance import InputDataInstance
import random
# import numpy as np
# from LspAlgorithms.GeneticAlgorithms.LspRuntimeMonitor import LspRuntimeMonitor

class LocalSearchEngine:
    """
    """

    localSearchMemory = None

    def __init__(self) -> None:
        """
        """

        self.result = None

        if LocalSearchEngine.localSearchMemory["content"]["left_genes"] is None:
            LocalSearchEngine.localSearchMemory["content"]["left_genes"] = dict()

        if LocalSearchEngine.localSearchMemory["content"]["switch_quality"] is None:
            LocalSearchEngine.localSearchMemory["content"]["switch_quality"] = dict()

        if LocalSearchEngine.localSearchMemory["content"]["chromosome_distances"] is None:
            LocalSearchEngine.localSearchMemory["content"]["chromosome_distances"] = dict()

        if LocalSearchEngine.localSearchMemory["content"]["switchables"] is None:
            LocalSearchEngine.localSearchMemory["content"]["switchables"] = dict()


    def process(self, chromosome, strategy = "random", args = None):
        """Process the given chromosome in order to return a mutated version
        """

        # print("mutatiooon", strategy, chromosome, chromosome.dnaArray if (isinstance(chromosome, Chromosome)) else None)

        self.searchVicinity(chromosome, strategy, args)

        # print("Mutation results : ", strategy, chromosome, self.result)
        return self.result


    def searchVicinity(self, chromosome, strategy, args = None):
        """
        """

        if isinstance(chromosome, PseudoChromosome):
            chromosome = LocalSearchEngine.switchItems(chromosome.value, args["threadId"])

        results = set()

        with LocalSearchEngine.localSearchMemory["lock"]:
            if chromosome.stringIdentifier not in LocalSearchEngine.localSearchMemory["content"]["left_genes"]:
                LocalSearchEngine.localSearchMemory["content"]["left_genes"][chromosome.stringIdentifier] = dict({(gene.item, gene.position): set() for itemGenes in chromosome.dnaArray for gene in itemGenes})

        listItems = list(LocalSearchEngine.localSearchMemory["content"]["left_genes"][chromosome.stringIdentifier])
        random.shuffle(listItems)

        # print("selected : ", selectedGenes)
        for (geneItem, genePosition) in listItems:
            gene = chromosome.dnaArray[geneItem][genePosition]
            self.improveGene(chromosome, gene, strategy, results, args)  

            if len(LocalSearchEngine.localSearchMemory["content"]["left_genes"][chromosome.stringIdentifier][(geneItem, genePosition)]) == 0:
                del LocalSearchEngine.localSearchMemory["content"]["left_genes"][chromosome.stringIdentifier][(geneItem, genePosition)]

            if strategy in ["random", "near_positive"] and self.result is not None:
                return 
        
        if strategy == "population":
            self.result = list(results)

        # print("Search ended")



    def improveGene(self, chromosome, periodGene, strategy, results, args):
        """
        """

        periods = []

        if len(LocalSearchEngine.localSearchMemory["content"]["left_genes"][chromosome.stringIdentifier][(periodGene.item, periodGene.position)]) == 0:

            (periodGeneLowerLimit, periodGeneUpperLimit) = ((chromosome.dnaArray[periodGene.item][periodGene.position]).lowerPeriodLimit, (chromosome.dnaArray[periodGene.item][periodGene.position]).upperPeriodLimit)
            if (periodGeneLowerLimit, periodGeneUpperLimit) == (None, None):
                periodGeneLowerLimit, periodGeneUpperLimit = Chromosome.geneLowerUpperLimit(chromosome, periodGene)
                ((chromosome.dnaArray[periodGene.item][periodGene.position]).lowerPeriodLimit, (chromosome.dnaArray[periodGene.item][periodGene.position]).upperPeriodLimit) = (periodGeneLowerLimit, periodGeneUpperLimit)

            LocalSearchEngine.localSearchMemory["content"]["left_genes"][chromosome.stringIdentifier][(periodGene.item, periodGene.position)] = set(range(periodGeneLowerLimit, periodGeneUpperLimit))
            (LocalSearchEngine.localSearchMemory["content"]["left_genes"][chromosome.stringIdentifier][(periodGene.item, periodGene.position)]).remove(periodGene.period)

        periods = list(LocalSearchEngine.localSearchMemory["content"]["left_genes"][chromosome.stringIdentifier][(periodGene.item, periodGene.position)])
        # random.shuffle(periods)

        for _, period in enumerate(reversed(periods)):

            result = self.handleAltPeriod(chromosome, strategy, periodGene, period, results, args)
            if result == "RETURN":
                (LocalSearchEngine.localSearchMemory["content"]["left_genes"][chromosome.stringIdentifier][(periodGene.item, periodGene.position)]).remove(period)
                return


    def handleAltPeriod(self, chromosome, strategy, periodGene, altPeriod, results, args):
        """
        """

        mStringIdentifier = LocalSearchEngine.mutationStringIdentifier(chromosome.stringIdentifier, periodGene.period, altPeriod)

        # making sure the process doesn't take a path already taken before

        # tmpChromosome = Chromosome()
        # tmpChromosome.stringIdentifier = mStringIdentifier
        # if tmpChromosome in self.population.chromosomes:
        inPool = True
        with Chromosome.pool["lock"]:
            inPool = False if mStringIdentifier not in Chromosome.pool["content"] else True
        if inPool:
            # print("booo")
            return None

        else:   

            # inPool = True
            # with Chromosome.pool["lock"]:
            #     inPool = False if mStringIdentifier not in Chromosome.pool["content"] else True

            # if inPool:
            #     c = Chromosome.popByThread[list(Chromosome.pool["content"][mStringIdentifier])[0]]["content"][mStringIdentifier]
            #     if isinstance(c, PseudoChromosome):
            #         if strategy == "crossover":
            #             if c < chromosome:
            #                 if Chromosome.gettingCloser(c, args["target"], periodGene, altPeriod, LocalSearchEngine.localSearchMemory["content"]["chromosome_distances"]):
            #                     # print("croo")
            #                     self.result = c 
            #                     return "RETURN"
            #             # else:
            #             #     if "closer_anyway" in args:
            #             #         self.result = c 
            #             #         return "RETURN"

            #         elif strategy == "near_positive":
            #             if c < chromosome:
            #                 self.result = c
            #                 return "RETURN"
            #         elif strategy == "random":
            #             self.result = c
            #             return "RETURN"
            #     return None

            if LocalSearchEngine.areItemsSwitchable(chromosome, periodGene, altPeriod):

                interestingResult = None
                if strategy == "crossover":
                    if not Chromosome.gettingCloser(chromosome, args["target"], periodGene, altPeriod, LocalSearchEngine.localSearchMemory["content"]["chromosome_distances"]):
                        # print("not getting closer *** ")
                        return
                    # print("yes getting closer *** ")

                    if "closer_anyway" not in args:
                        interestingResult = LocalSearchEngine.isSwitchInteresting(chromosome, periodGene, altPeriod)
                        if not interestingResult[0]:
                            return
                    # else:
                    #     print("tesssssssssssss")
                elif strategy == "near_positive":
                    interestingResult = LocalSearchEngine.isSwitchInteresting(chromosome, periodGene, altPeriod)
                    if not interestingResult[0]:
                        return

                evaluationData = LocalSearchEngine.evaluateItemsSwitch(chromosome, periodGene, altPeriod) if interestingResult is None else interestingResult[1]

                if strategy == "population":
                    chromosome = LocalSearchEngine.switchItems(evaluationData)
                    results.add(chromosome)
                else:
                    pseudoChromosome = PseudoChromosome(evaluationData)
                    Chromosome.addToPop(args["threadId"], pseudoChromosome)

                    self.result = pseudoChromosome
                    return "RETURN"

            else:
                (LocalSearchEngine.localSearchMemory["content"]["left_genes"][chromosome.stringIdentifier][(periodGene.item, periodGene.position)]).remove(altPeriod)


    @classmethod
    def areItemsSwitchable(cls, chromosome, periodGene, altPeriod):
        """
        """

        if (chromosome.stringIdentifier, periodGene.period, altPeriod) in LocalSearchEngine.localSearchMemory["content"]["switchables"]:
            return LocalSearchEngine.localSearchMemory["content"]["switchables"][(chromosome.stringIdentifier, periodGene.period, altPeriod)]


        (periodGeneLowerLimit, periodGeneUpperLimit) = ((chromosome.dnaArray[periodGene.item][periodGene.position]).lowerPeriodLimit, (chromosome.dnaArray[periodGene.item][periodGene.position]).upperPeriodLimit)


        if chromosome.stringIdentifier[altPeriod] > 0: 
            altPeriodGene = chromosome.dnaArray[(chromosome.genesByPeriod[altPeriod])[0]][(chromosome.genesByPeriod[altPeriod])[1]]

            altPeriodGeneLowerLimit, altPeriodGeneUpperLimit = (chromosome.dnaArray[altPeriodGene.item][altPeriodGene.position]).lowerPeriodLimit, (chromosome.dnaArray[altPeriodGene.item][altPeriodGene.position]).upperPeriodLimit
            if (altPeriodGeneLowerLimit, altPeriodGeneUpperLimit) == (None, None):
                altPeriodGeneLowerLimit, altPeriodGeneUpperLimit = Chromosome.geneLowerUpperLimit(chromosome, altPeriodGene)
                (chromosome.dnaArray[altPeriodGene.item][altPeriodGene.position]).lowerPeriodLimit, (chromosome.dnaArray[altPeriodGene.item][altPeriodGene.position]).upperPeriodLimit = altPeriodGeneLowerLimit, altPeriodGeneUpperLimit

            if (periodGeneLowerLimit <= altPeriod and altPeriod < periodGeneUpperLimit) and (altPeriodGeneLowerLimit <= periodGene.period and periodGene.period < altPeriodGeneUpperLimit):
                LocalSearchEngine.localSearchMemory["content"]["switchables"][(chromosome.stringIdentifier, periodGene.period, altPeriod)] = True
                return True
        else:
            if (periodGeneLowerLimit <= altPeriod and altPeriod < periodGeneUpperLimit):
                LocalSearchEngine.localSearchMemory["content"]["switchables"][(chromosome.stringIdentifier, periodGene.period, altPeriod)] = True
                return True

        LocalSearchEngine.localSearchMemory["content"]["switchables"][(chromosome.stringIdentifier, periodGene.period, altPeriod)] = False
        return False


    @classmethod
    def isSwitchInteresting(cls, chromosome, periodGene, altPeriod):
        """Simply, checking if the new production cost when switch done is lower than the current one
        """

        if (chromosome.stringIdentifier, periodGene.period, altPeriod) in LocalSearchEngine.localSearchMemory["content"]["switch_quality"]:
            return LocalSearchEngine.localSearchMemory["content"]["switch_quality"][(chromosome.stringIdentifier, periodGene.period, altPeriod)]






        # newCost = 0

        # if chromosome.stringIdentifier[altPeriod] == 0:
        #     prevGene0 = Chromosome.prevProdGene(altPeriod, chromosome.dnaArray, chromosome.stringIdentifier)  
        #     # nextGene0 = Chromosome.nextProdGene(altPeriod, chromosome.dnaArray, chromosome.stringIdentifier)
        #     # new changeover cost
        #     if prevGene0 is not None:
        #         if not (prevGene0.item == periodGene.item and prevGene0.position == periodGene.position): 
        #             newCost += InputDataInstance.instance.changeOverCostsArray[prevGene0.item][periodGene.item]
        # else:
        #     altPeriodGene = chromosome.dnaArray[chromosome.genesByPeriod[altPeriod][0]][chromosome.genesByPeriod[altPeriod][1]]
        #     # if (periodGene.prevGene is not None and periodGene.prevGene[0] == altPeriodGene.item and periodGene.prevGene[1] == altPeriodGene.position):
        #     #     newCost += InputDataInstance.instance.changeOverCostsArray[altPeriodGene.prevGene[0]][periodGene.item]
        #     if (altPeriodGene.prevGene is not None and altPeriodGene.prevGene[0] == periodGene.item and altPeriodGene.prevGene[1] == periodGene.position):
        #         newCost += InputDataInstance.instance.changeOverCostsArray[altPeriodGene.item][periodGene.item]
        #     else:
        #         # new changeover cost
        #         if altPeriodGene.prevGene is not None:
        #             newCost += InputDataInstance.instance.changeOverCostsArray[altPeriodGene.prevGene[0]][periodGene.item]
                
        # # new stocking cost
        # newCost += (InputDataInstance.instance.demandsArrayZipped[periodGene.item][periodGene.position] - altPeriod) * InputDataInstance.instance.stockingCostsArray[periodGene.item]

        # # # BEGIN TEST

        # # chromi = Chromosome.createFromIdentifier(LocalSearchEngine.mutationStringIdentifier(chromosome.stringIdentifier, periodGene.period, altPeriod))
        # # if (newCost != (chromi.dnaArray[periodGene.item][periodGene.position]).cost):
        # #     print("Eureeeeeeeeeeeeeekaaaaaaaaaaa ! ", (chromi.dnaArray[periodGene.item][periodGene.position]).cost)

        # # # END TEST

        # # print("is Switch Interesting ? : ", chromosome, " | ", periodGene.period, " | ", periodGene.item, " | ", altPeriod, " | ", newCost, " | ", periodGene.cost)

        # result = (newCost <= periodGene.cost)






        evaluationData = LocalSearchEngine.evaluateItemsSwitch(chromosome, periodGene, altPeriod)
        result = ((evaluationData["variance"] >= 0), None if (evaluationData["variance"] < 0) else evaluationData)



        LocalSearchEngine.localSearchMemory["content"]["switch_quality"][(chromosome.stringIdentifier, periodGene.period, altPeriod)] = result

        return result

    @classmethod
    def setGeneLimits(cls, chromosome, periodGene):
        """
        """

        # for gene in chromosome.dnaArray[periodGene.item]:
        #     (chromosome.dnaArray[gene.item][gene.position]).lowerPeriodLimit, (chromosome.dnaArray[gene.item][gene.position]).upperPeriodLimit = None, None 

        (chromosome.dnaArray[periodGene.item][periodGene.position]).lowerPeriodLimit, (chromosome.dnaArray[periodGene.item][periodGene.position]).upperPeriodLimit = None, None 

        if periodGene.position > 0:
            (chromosome.dnaArray[periodGene.item][periodGene.position - 1]).lowerPeriodLimit, (chromosome.dnaArray[periodGene.item][periodGene.position - 1]).upperPeriodLimit = None, None

        if periodGene.position < (len(InputDataInstance.instance.demandsArrayZipped[periodGene.item]) - 1):
            (chromosome.dnaArray[periodGene.item][periodGene.position + 1]).lowerPeriodLimit, (chromosome.dnaArray[periodGene.item][periodGene.position + 1]).upperPeriodLimit = None, None


    @classmethod
    def switchItems(cls, evaluationData, threadIdentifier = None):
        """ 
        """

        # print("Switching item : ", evaluationData)

        chromosome = evaluationData["chromosome"]
        mutation = Chromosome()
        periodGene = chromosome.dnaArray[(chromosome.genesByPeriod[evaluationData["period"]])[0]][(chromosome.genesByPeriod[evaluationData["period"]])[1]]
        altPeriod = evaluationData["altPeriod"]
        mutation.stringIdentifier = evaluationData["newStringIdentifier"]
        mutation.dnaArray = copy.deepcopy(chromosome.dnaArray)
        mutation.genesByPeriod = copy.deepcopy(chromosome.genesByPeriod)
        mutation.cost = chromosome.cost - evaluationData["variance"]

        period = (mutation.dnaArray[periodGene.item][periodGene.position]).period
        (mutation.dnaArray[periodGene.item][periodGene.position]).period = altPeriod

        cls.setGeneLimits(mutation, periodGene)

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

            cls.setGeneLimits(mutation, altPeriodGene)

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


        # testing the result
        # c = Chromosome.createFromIdentifier(mutation.stringIdentifier)
        # if c.dnaArray != mutation.dnaArray or c.cost != mutation.cost or c.genesByPeriod != mutation.genesByPeriod:
        #     print("Mutation error : ", mutation.cost != c.cost, mutation.genesByPeriod != c.genesByPeriod, mutation.dnaArray != c.dnaArray, "\n",
        #         mutation.cost, c.cost, "\n",
        #         # mutation.genesByPeriod, " --- ", c.genesByPeriod, "\n", 
        #         mutation.dnaArray, c.dnaArray)


        if threadIdentifier is not None: # strategy is not population
            if mutation.stringIdentifier in Chromosome.popByThread[threadIdentifier]["content"]:
                if isinstance(Chromosome.popByThread[threadIdentifier]["content"][mutation.stringIdentifier], PseudoChromosome):
                    Chromosome.popByThread[threadIdentifier]["content"][mutation.stringIdentifier] = mutation
        # else:
        #     print("coco")

        # print("Switch done")
        return mutation


    @classmethod
    def mutationStringIdentifier(cls, stringIdentifier, period, altPeriod):
        """
        """
# 
        stringIdentifier = list(stringIdentifier)
        stringIdentifier[period], stringIdentifier[altPeriod] = stringIdentifier[altPeriod], stringIdentifier[period]

        return tuple(stringIdentifier)


    @classmethod
    def evaluateItemsSwitch(cls, chromosome, periodGene, altPeriod):
        """
        """

        # print("Evaluating : --- ", chromosome, periodGene.period, altPeriod, chromosome.dnaArray)

        evaluationData = {"chromosome": chromosome, "variance": periodGene.cost, "periodGene": {}, "altPeriodGene": {}, "altPeriod": altPeriod, "period": periodGene.period}
        evaluationData["newStringIdentifier"] = LocalSearchEngine.mutationStringIdentifier(chromosome.stringIdentifier, periodGene.period, altPeriod)
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

        # print("Evaluation result : ", chromosome, periodGene.period, altPeriod, " ---> ", evaluationData)

        return evaluationData        
