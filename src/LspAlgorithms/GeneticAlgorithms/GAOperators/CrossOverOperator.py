from collections import defaultdict
import random
import threading
from LspAlgorithms.GeneticAlgorithms.PopInitialization.Chromosome import Chromosome
from LspInputDataReading.LspInputDataInstance import InputDataInstance
# import concurrent.futures
# import copy
# from LspAlgorithms.GeneticAlgorithms.PopInitialization.Gene import Gene
from .LocalSearchEngine import LocalSearchEngine
from ..PopInitialization.Population import Population
from ParameterSearch.ParameterData import ParameterData
from .LocalSearchEngine import LocalSearchEngine
from LspAlgorithms.GeneticAlgorithms.PopInitialization.PseudoChromosome import PseudoChromosome
from LspAlgorithms.GeneticAlgorithms.LspRuntimeMonitor import LspRuntimeMonitor

class CrossOverOperator:
    """
    """

    crossOverMemory = {"lock": threading.Lock(), "content": defaultdict(lambda: None)}

    def __init__(self) -> None:
        """
        """

        self.parentChromosomes = None
        self.offsprings = {0: Chromosome(), 1: Chromosome()}
        # self.population = None        
        self.threadIdentifier = 1

        # self._stopSearchEvents = {0: threading.Event(), 1: threading.Event()}


    def process(self, population):
        """
        """

        chromosomes = list()
        self.threadIdentifier = population.threadIdentifier
        self.population = population

        while len(chromosomes) < Population.popSizes[population.threadIdentifier]:

            chromosomeA, chromosomeB = population.selectionOperator.select()

            if isinstance(chromosomeA, PseudoChromosome):
                chromosomeA = LocalSearchEngine.switchItems(chromosomeA.value, population.threadIdentifier)
            if isinstance(chromosomeB, PseudoChromosome):
                chromosomeB = LocalSearchEngine.switchItems(chromosomeB.value, population.threadIdentifier)

            chromosomeC, chromosomeD = None, None

            if (random.random() <= ParameterData.instance.crossOverRate):
                try:
                    chromosomeC, chromosomeD = self.mate([chromosomeA, chromosomeB])
                except Exception as e:
                    raise e
            else:
                # print("No crossover")
                chromosomeC, chromosomeD = chromosomeA, chromosomeB

            if chromosomeC is None:
                print("chromosomeC None")
            else:
                chromosomes.append(chromosomeC)

            if len(chromosomes) < Population.popSizes[population.threadIdentifier]:
                if chromosomeD is None:
                    print("chromosomeD None")
                else:
                    chromosomes.append(chromosomeD)

            print("chromosomes length : ", len(chromosomes), Population.popSizes[population.threadIdentifier])

        population.chromosomes = chromosomes
        return chromosomes


    def mate(self, parentChromosomes, offspring_result = 2):
        """
        """

        self.parentChromosomes = parentChromosomes

        if offspring_result not in [1, 2]:
            # TODO: throw an error
            return None, None

        if self.parentChromosomes[0] == self.parentChromosomes[1]:
            return (self.parentChromosomes[0], self.parentChromosomes[1])

        # print("Crossover : ", self.parentChromosomes, self.parentChromosomes[0].dnaArray, self.parentChromosomes[1].dnaArray)
        print("Crossover : ", self.parentChromosomes)

        # checking the crossover memory for previous occurences of this context
        memoryResult = None
        with CrossOverOperator.crossOverMemory["lock"]:
            memoryResult = CrossOverOperator.crossOverMemory["content"][((self.parentChromosomes[0]).stringIdentifier, (self.parentChromosomes[1]).stringIdentifier)] if CrossOverOperator.crossOverMemory["content"][((self.parentChromosomes[0]).stringIdentifier, (self.parentChromosomes[1]).stringIdentifier)] is not None else \
                                (CrossOverOperator.crossOverMemory["content"][((self.parentChromosomes[1]).stringIdentifier, (self.parentChromosomes[0]).stringIdentifier)] if CrossOverOperator.crossOverMemory["content"][((self.parentChromosomes[1]).stringIdentifier, (self.parentChromosomes[0]).stringIdentifier)] is not None else None)
        if  memoryResult is not None:
            print("Retrieving crossover results : ", memoryResult)
            # for offspring in memoryResult:
            #     LocalSearchEngine().process(offspring, "simple_mutation", {"threadId": self.threadIdentifier})
            return memoryResult

        self.setOffsprings()

        print("Cross Over result : ", [self.parentChromosomes, self.offsprings])

        # storing this result in the crossover memory before returning 
        with CrossOverOperator.crossOverMemory["lock"]:
            CrossOverOperator.crossOverMemory["content"][((self.parentChromosomes[0]).stringIdentifier, (self.parentChromosomes[1]).stringIdentifier)] = tuple(self.offsprings.values())

        return tuple(self.offsprings.values())


    def setOffsprings(self):
        """
        """
        
        for i in [0, 1]:
            self.searchOffspring(i)


    def searchOffspring(self, offspringIndex):
        """
        """

        target = self.parentChromosomes[0] if offspringIndex == 1 else self.parentChromosomes[1]

        print("Begiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiinnnnnnn", self.parentChromosomes[offspringIndex], target)

        queue = [self.parentChromosomes[offspringIndex]]
        currentPeriod = InputDataInstance.instance.nPeriods
        while len(queue) > 0:
            chromosome = queue[-1]
            # offspring = chromosome
            self.offsprings[offspringIndex] = chromosome
            queue = queue[:-1] 

            if isinstance(chromosome, PseudoChromosome):
                chromosome = LocalSearchEngine.switchItems(chromosome.value, self.population.threadIdentifier)

            period = None
            for period in reversed(range(currentPeriod)):

                print("mmmmmmmmmmmmmmmmmmmmmmmmmmm : ", period, chromosome)
                item = target.stringIdentifier[period] - 1
                if item >= 0 and target.stringIdentifier[period] != chromosome.stringIdentifier[period]:
                    periodGene = chromosome.dnaArray[target.genesByPeriod[period][0]][target.genesByPeriod[period][1]]
                    periodGeneLowerLimit, periodGeneUpperLimit = Chromosome.geneLowerUpperLimit(chromosome, periodGene)
                    print("Different values !!!!!!!!!!!!!!!!! ", periodGene, "------", item, period)

                    if LocalSearchEngine.areItemsSwitchable(chromosome, periodGene, period, periodGeneLowerLimit, periodGeneUpperLimit):
                        print("Switchable !!!!!!!!!!!!!!!!!!! ")

                        mStringIdentifier = LocalSearchEngine.mutationStringIdentifier(chromosome.stringIdentifier, periodGene.period, period)
                        inPool = True
                        with Chromosome.pool["lock"]:
                            if mStringIdentifier not in Chromosome.pool["content"]:
                                inPool =  False

                        if inPool:
                            # print("Resultiiiiiiii : ", result)
                            popChromosome = None
                            if self.threadIdentifier not in Chromosome.pool["content"][mStringIdentifier]:
                                Chromosome.copyToThread(self.threadIdentifier, popChromosome)
                            popChromosome = Chromosome.popByThread[self.threadIdentifier]["content"][mStringIdentifier]

                            if popChromosome < chromosome:
                                queue.append(popChromosome)
                                break

                        else:
                            evaluationData = LocalSearchEngine.evaluateItemsSwitch(chromosome, periodGene, period)
                            pseudoChromosome = PseudoChromosome(evaluationData)

                            popChromosome = None
                            with Chromosome.pool["lock"]:
                                if mStringIdentifier not in Chromosome.pool["content"]:
                                    Chromosome.addToPop(self.threadIdentifier, pseudoChromosome)
                                else:
                                    popChromosome = Chromosome.popByThread[Chromosome.pool["content"][mStringIdentifier]]["content"][mStringIdentifier]

                            if popChromosome is None:
                                if evaluationData["variance"] > 0:
                                    # LocalSearchEngine.localSearchMemory["content"]["simple_mutation"][chromosome.stringIdentifier]["genes"] = selectedGenes
                                    # LocalSearchEngine.localSearchMemory["content"]["simple_mutation"][chromosome.stringIdentifier]["results"][mStringIdentifier] = pseudoChromosome.cost
                                    queue.append(pseudoChromosome)
                                    break
                            else:
                                if popChromosome < chromosome:
                                    queue.append(popChromosome)
                                    break
                    else:
                        pass

            currentPeriod = period
        # return offspring