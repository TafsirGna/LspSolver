from collections import defaultdict
import threading
import copy
from LspAlgorithms.GeneticAlgorithms.Chromosome import Chromosome
from LspAlgorithms.GeneticAlgorithms.LocalSearch.LocalSearchNode import LocalSearchNode
from ParameterSearch.ParameterData import ParameterData
import concurrent.futures
from LspInputDataReading.LspInputDataInstance import InputDataInstance
import random

class LocalSearchEngine:
    """
    """

    genericGeneIndices = None

    def __init__(self) -> None:
        """
        """

        self.chromosome = None
        self.searchDepth = 0
        self.result = None
        self.nullPeriodsOrdered = None
        # self._stopSearchEvent = threading.Event()

        if LocalSearchEngine.genericGeneIndices is None:
            LocalSearchEngine.genericGeneIndices = [(item, position) for item, itemGenes in enumerate(InputDataInstance.instance.demandsArrayZipped) for position, _ in enumerate(itemGenes)]


    def process(self, chromosome, strategy = "simple_mutation"):
        """Process the given chromosome in order to return a mutated version
        strategy: simple_mutation|absolute_mutation|positive_mutation
        """

        # print("mutatiooooooon", strategy, chromosome, chromosome.dnaArray)

        self._visitedNodes = defaultdict(lambda: None)
        self.chromosome = chromosome

        self.searchIndividu(chromosome, strategy)

        return (self.result if self.result is not None else self.chromosome)


    def searchIndividu(self, chromosome, strategy):
        """
        """

        # if strategy == "simple_mutation":
        if self.nullPeriodsOrdered is None:
            self.nullPeriodsOrdered = [period for period, periodValue in enumerate(self.chromosome.stringIdentifier) if periodValue == 0]

        print("nullPeriodsOrdered : ", self.nullPeriodsOrdered)
        random.shuffle(self.nullPeriodsOrdered)

        for nullPeriod in self.nullPeriodsOrdered:
            
            i = 1
            backwardPeriod, forwardPeriod = nullPeriod, nullPeriod
            while True:
                if forwardPeriod is not None:
                    forwardPeriod = nullPeriod + i
                if backwardPeriod is not None:
                    backwardPeriod = nullPeriod - i

                if backwardPeriod is not None and backwardPeriod < 0:
                    backwardPeriod = None

                if forwardPeriod is not None and forwardPeriod > InputDataInstance.instance.nPeriods - 1:
                    forwardPeriod = None

                # print(backwardPeriod, forwardPeriod)
                if backwardPeriod is not None and chromosome.stringIdentifier[backwardPeriod] > 0: 
                    backwardPeriodGene = Chromosome.geneAtPeriod(chromosome, backwardPeriod)

                    backwardPeriodGeneLowerLimit, backwardPeriodGeneUpperLimit = Chromosome.geneLowerUpperLimit(chromosome, backwardPeriodGene)
                    if backwardPeriodGeneLowerLimit <= nullPeriod and nullPeriod < backwardPeriodGeneUpperLimit:
                        print("mutating : ", backwardPeriodGene)
                        mutation = LocalSearchNode.createMutatedChromosome(chromosome, [(backwardPeriodGene.item, backwardPeriodGene.position), (-1, nullPeriod)])
                        print("Mutation : ", mutation)
                        if mutation.cost <= chromosome.cost:
                            self.result = mutation
                            return None
                    else:
                        backwardPeriod = None

                if forwardPeriod is not None and chromosome.stringIdentifier[forwardPeriod] > 0:
                    forwardPeriodGene = Chromosome.geneAtPeriod(chromosome, forwardPeriod)

                    forwardPeriodGeneLowerLimit, forwardPeriodGeneUpperLimit = Chromosome.geneLowerUpperLimit(chromosome, forwardPeriodGene)
                    if forwardPeriodGeneLowerLimit <= nullPeriod and nullPeriod < forwardPeriodGeneUpperLimit:
                        print("mutating : ", forwardPeriodGene)
                        mutation = LocalSearchNode.createMutatedChromosome(chromosome, [(forwardPeriodGene.item, forwardPeriodGene.position), (-1, nullPeriod)])
                        print("Mutation : ", mutation)
                        if mutation.cost <= chromosome.cost:
                            self.result = mutation
                            return None
                    else:
                        forwardPeriod = None

                if backwardPeriod is None and forwardPeriod is None:
                    break

                i += 1


        # switchPartner = self.searchSwitchPartner(gene)



    # def searchSwitchPartner(self, gene):
    #     """
    #     """


    #     index = len(self.chromosome.stringIdentifier[geneLowerLimit:geneUpperLimit]) - 1

    #     possibleSwitches = []
    #     for periodValue in reversed(self.chromosome.stringIdentifier[geneLowerLimit:geneUpperLimit]):
    #         period = index + geneLowerLimit

    #         newGeneCost = 0
    #         if period > 0: # changeOverCost
    #             newGeneCost += InputDataInstance.instance.changeOverCostsArray[self.chromosome.stringIdentifier[period - 1] - 1][gene.item]
    #         # stockingCost
    #         newGeneCost += InputDataInstance.instance.stockingCostsArray[gene.item] * (InputDataInstance.instance.demandsArrayZipped[gene.item][gene.position] - period)

    #         if newGeneCost > gene.cost:
    #             continue

    #         estimation = newGeneCost
    #         if periodValue == 0:
    #             pass
    #         else:
    #             pass

    #         index -= 1


    # @classmethod
    # def estimateSwitchBenefit(self, chromosome, nullPeriod, validPeriod):
    #     """
    #     """
        
    #     return 0






