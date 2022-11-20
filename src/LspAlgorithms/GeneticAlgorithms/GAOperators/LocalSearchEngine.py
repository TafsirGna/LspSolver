from collections import defaultdict
import threading
import copy
from LspAlgorithms.GeneticAlgorithms.PopInitialization.Chromosome import Chromosome
from LspAlgorithms.GeneticAlgorithms.PopInitialization.PseudoChromosome import PseudoChromosome
# from ParameterSearch.ParameterData import ParameterData
# import concurrent.futures
from LspInputDataReading.LspInputDataInstance import InputDataInstance
import random
import numpy as np
from LspAlgorithms.GeneticAlgorithms.LspRuntimeMonitor import LspRuntimeMonitor

class LocalSearchEngine:
    """
    """

    localSearchMemory = {"lock": threading.Lock(), "content": defaultdict(lambda: None)}

    def __init__(self) -> None:
        """
        """

        self.result = None

        if LocalSearchEngine.localSearchMemory["content"]["visited_genes"] is None:
            LocalSearchEngine.localSearchMemory["content"]["visited_genes"] = dict()


    def process(self, chromosome, strategy = "random", args = None):
        """Process the given chromosome in order to return a mutated version
        """

        print("mutatiooon", strategy, chromosome, chromosome.dnaArray if (isinstance(chromosome, Chromosome)) else None)

        self.searchVicinity(chromosome, strategy, args)

        print("Mutation results : ", strategy, chromosome, self.result)
        return self.result


    def searchVicinity(self, chromosome, strategy, args = None):
        """
        """

        if isinstance(chromosome, PseudoChromosome):
            chromosome = LocalSearchEngine.switchItems(chromosome.value, args["threadId"])

        results = set()
        selectedGenes = [gene for itemGenes in chromosome.dnaArray for gene in itemGenes]
        random.shuffle(selectedGenes)

        # print("selected : ", selectedGenes)
        for periodGene in selectedGenes:
            self.improveGene(chromosome, periodGene, strategy, results, args)  
        
        # if strategy == "refinement":
        #     self.result = chromosome
        
        if strategy == "population":
            self.result = list(results)

        print("Search ended")



    def improveGene(self, chromosome, periodGene, strategy, results, args):
        """
        """

        periodGeneLowerLimit, periodGeneUpperLimit = Chromosome.geneLowerUpperLimit(chromosome, periodGene)
        periods = list(range(periodGeneLowerLimit, periodGeneUpperLimit))
        random.shuffle(periods)

        for period in periods:
            if period == periodGene.period:
                continue

            if strategy == "crossover":
                if not Chromosome.gettingCloser(chromosome, args["target"], periodGene, period):
                    print("not getting closer *** ")
                    continue
                print("yes getting closer *** ")

            result = self.handleAltPeriod(chromosome, strategy, periodGene, period, periodGeneLowerLimit, periodGeneUpperLimit, results, args)
            if result == "RETURN":
                return

            random.shuffle(periods)


    # def improveGeneCrossOverStrategy(self, chromosome, periodGene, strategy, results, args):
    #     """
    #     """

    #     # print("gene : ", periodGene)
    #     periodGeneLowerLimit, periodGeneUpperLimit = Chromosome.geneLowerUpperLimit(chromosome, periodGene)
        
    #     increment = 0
    #     backwardPeriod, forwardPeriod = args["altPeriod"], args["altPeriod"]
    #     while True:
    #         if forwardPeriod is not None:
    #             forwardPeriod = args["altPeriod"] + increment
    #         if backwardPeriod is not None:
    #             backwardPeriod = args["altPeriod"] - increment

    #         if backwardPeriod is not None and backwardPeriod < 0:
    #             backwardPeriod = None

    #         if forwardPeriod is not None and forwardPeriod > InputDataInstance.instance.nPeriods - 1:
    #             forwardPeriod = None

    #         # print(backwardPeriod, forwardPeriod)

    #         if forwardPeriod is not None :
    #             if forwardPeriod != periodGene.period:
    #                 result = self.handleAltPeriod(chromosome, strategy, periodGene, forwardPeriod, periodGeneLowerLimit, periodGeneUpperLimit, results, args)
    #                 if result == "RETURN":
    #                     return None
    #                 elif result == "SET_ALT_PERIOD_NONE":
    #                     forwardPeriod = None

    #         if backwardPeriod is not None :
    #             if backwardPeriod != periodGene.period:
    #                 result = self.handleAltPeriod(chromosome, strategy, periodGene, backwardPeriod, periodGeneLowerLimit, periodGeneUpperLimit, results, args)
    #                 if result == "RETURN":
    #                     return None
    #                 elif result == "SET_ALT_PERIOD_NONE":
    #                     backwardPeriod = None

    #         if backwardPeriod is None and forwardPeriod is None:
    #             break

    #         increment += 1


    def handleAltPeriod(self, chromosome, strategy, periodGene, altPeriod, periodGeneLowerLimit, periodGeneUpperLimit, results, args):
        """
        """

        mStringIdentifier = LocalSearchEngine.mutationStringIdentifier(chromosome.stringIdentifier, periodGene.period, altPeriod)

        # making sure the process doesn't take a path already taken before
        inPool = True
        with Chromosome.pool["lock"]:
            if mStringIdentifier not in Chromosome.pool["content"]:
                inPool = False

        if inPool:
            #     if strategy != "population":
            popChromosome = None
            if args["threadId"] not in Chromosome.pool["content"][mStringIdentifier]:
                for threadIdentifier in Chromosome.pool["content"][mStringIdentifier]:
                    popChromosome = Chromosome.popByThread[threadIdentifier]["content"][mStringIdentifier]
                    if isinstance(popChromosome, Chromosome):
                        break
                Chromosome.copyToThread(args["threadId"], popChromosome)

            popChromosome = Chromosome.popByThread[args["threadId"]]["content"][mStringIdentifier]

            # if popChromosome > chromosome:
            #     return
                
            if popChromosome.stringIdentifier in LocalSearchEngine.localSearchMemory["content"]["visited_genes"] \
                and len(LocalSearchEngine.localSearchMemory["content"]["visited_genes"][popChromosome.stringIdentifier]) == 0:
                return

            # else
            if self.onSelectedStrategy(strategy, chromosome, popChromosome, args) == "RETURN":
                return "RETURN"

        else:

            if LocalSearchEngine.areItemsSwitchable(chromosome, periodGene, altPeriod, (periodGeneLowerLimit, periodGeneUpperLimit)):

                # trying to craft a heuristic
                if not LocalSearchEngine.isSwitchInteresting(chromosome, periodGene, altPeriod):
                    return

                evaluationData = LocalSearchEngine.evaluateItemsSwitch(chromosome, periodGene, altPeriod)

                if strategy == "population":
                    chromosome = LocalSearchEngine.switchItems(evaluationData)
                    results.add(chromosome)
                else:
                    pseudoChromosome = PseudoChromosome(evaluationData)
                    Chromosome.addToPop(args["threadId"], pseudoChromosome)

                if strategy == "crossover":
                    if evaluationData["variance"] > 0:
                        self.result = pseudoChromosome
                        return "RETURN"

                # if strategy == "refinement":
                #     if evaluationData["variance"] > 0:
                #         self.searchVicinity(pseudoChromosome, strategy, args)
                #         return "RETURN"
                
                if strategy == "random":
                    self.result = pseudoChromosome
                    return "RETURN"

        # else:
        #     return "SET_ALT_PERIOD_NONE"



    def onSelectedStrategy(self, strategy, chromosome, popChromosome, args):
        """
        """

        if strategy == "crossover":
            if popChromosome < chromosome:
                self.result = popChromosome
                return "RETURN"

        # if strategy == "refinement":
        #     if popChromosome < chromosome:
        #         self.searchVicinity(popChromosome, strategy, args)
        #         return "RETURN"

        if strategy == "random":
            self.result = popChromosome
            return "RETURN"


    @classmethod
    def areItemsSwitchable(cls, chromosome, periodGene, altPeriod, periodGeneLimits = None):
        """
        """

        periodGeneLowerLimit, periodGeneUpperLimit = periodGeneLimits if periodGeneLimits is not None else Chromosome.geneLowerUpperLimit(chromosome, periodGene)

        if chromosome.stringIdentifier[altPeriod] > 0: 
            altPeriodGene = chromosome.dnaArray[(chromosome.genesByPeriod[altPeriod])[0]][(chromosome.genesByPeriod[altPeriod])[1]]
            altPeriodGeneLowerLimit, altPeriodGeneUpperLimit = Chromosome.geneLowerUpperLimit(chromosome, altPeriodGene)

            if (periodGeneLowerLimit <= altPeriod and altPeriod < periodGeneUpperLimit) and (altPeriodGeneLowerLimit <= periodGene.period and periodGene.period < altPeriodGeneUpperLimit):
                return True
        else:
            if (periodGeneLowerLimit <= altPeriod and altPeriod < periodGeneUpperLimit):
                return True

        return False


    @classmethod
    def isSwitchInteresting(cls, chromosome, periodGene, altPeriod):
        """Simply, checking if the new production cost when switch done is lower than the current one
        """

        newCost = 0

        if chromosome.stringIdentifier[altPeriod] == 0:
            prevGene0 = Chromosome.prevProdGene(altPeriod, chromosome.dnaArray, chromosome.stringIdentifier)  
            # nextGene0 = Chromosome.nextProdGene(altPeriod, chromosome.dnaArray, chromosome.stringIdentifier)
            # new changeover cost
            if prevGene0 is not None:
                if not (prevGene0.item == periodGene.item and prevGene0.position == periodGene.position): 
                    newCost += InputDataInstance.instance.changeOverCostsArray[prevGene0.item][periodGene.item]
        else:
            altPeriodGene = chromosome.dnaArray[chromosome.genesByPeriod[altPeriod][0]][chromosome.genesByPeriod[altPeriod][1]]
            # if (periodGene.prevGene is not None and periodGene.prevGene[0] == altPeriodGene.item and periodGene.prevGene[1] == altPeriodGene.position):
            #     newCost += InputDataInstance.instance.changeOverCostsArray[altPeriodGene.prevGene[0]][periodGene.item]
            if (altPeriodGene.prevGene is not None and altPeriodGene.prevGene[0] == periodGene.item and altPeriodGene.prevGene[1] == periodGene.position):
                newCost += InputDataInstance.instance.changeOverCostsArray[altPeriodGene.item][periodGene.item]
            else:
                # new changeover cost
                if altPeriodGene.prevGene is not None:
                    newCost += InputDataInstance.instance.changeOverCostsArray[altPeriodGene.prevGene[0]][periodGene.item]
                
        # new stocking cost
        newCost += (InputDataInstance.instance.demandsArrayZipped[periodGene.item][periodGene.position] - altPeriod) * InputDataInstance.instance.stockingCostsArray[periodGene.item]

        # # BEGIN TEST

        # chromi = Chromosome.createFromIdentifier(LocalSearchEngine.mutationStringIdentifier(chromosome.stringIdentifier, periodGene.period, altPeriod))
        # if (newCost != (chromi.dnaArray[periodGene.item][periodGene.position]).cost):
        #     print("Eureeeeeeeeeeeeeekaaaaaaaaaaa ! ", (chromi.dnaArray[periodGene.item][periodGene.position]).cost)

        # # END TEST

        # print("is Switch Interesting ? : ", chromosome, " | ", periodGene.period, " | ", periodGene.item, " | ", altPeriod, " | ", newCost, " | ", periodGene.cost)

        return (newCost < periodGene.cost)


    @classmethod
    def switchItems(cls, evaluationData, threadIdentifier = None):
        """ 
        """

        print("Switching item : ", evaluationData)

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

        print("Switch done")
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

        print("Evaluating : --- ", chromosome, periodGene.period, altPeriod, chromosome.dnaArray)

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

        print("Evaluation result : ", chromosome, periodGene.period, altPeriod, " ---> ", evaluationData)

        return evaluationData        
