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
        self.offsprings = {0: None, 1: None}
        # self.population = None        
        self.threadIdentifier = 1

        if LocalSearchEngine.localSearchMemory["content"]["simple_mutation"] is None:
            LocalSearchEngine.localSearchMemory["content"]["simple_mutation"] = dict()

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
        while len(queue) > 0:
            chromosome = queue[-1]
            # offspring = chromosome
            self.offsprings[offspringIndex] = chromosome
            queue = queue[:-1] 

            if isinstance(chromosome, PseudoChromosome):
                chromosome = LocalSearchEngine.switchItems(chromosome.value, self.population.threadIdentifier)

            genesByPeriod = sorted([period for period in target.genesByPeriod])

            localSearchMemoryKey = None
            for period in reversed(genesByPeriod):

                print("mmmmmmmmmmmmmmmmmmmmmmmmmmm : ", period, chromosome)
                targetGene = target.dnaArray[target.genesByPeriod[period][0]][target.genesByPeriod[period][1]]
                gene = chromosome.dnaArray[targetGene.item][targetGene.position]

                if targetGene.period != gene.period:
                    print("Different values !!!!!!!!!!!!!!!!! ", gene)

                    with LocalSearchEngine.localSearchMemory["lock"]:
                        if (chromosome.stringIdentifier, gene.period, targetGene.period) in LocalSearchEngine.localSearchMemory["content"]["simple_mutation"]:
                            if self.threadIdentifier not in LocalSearchEngine.localSearchMemory["content"]["simple_mutation"][(chromosome.stringIdentifier, gene.period, targetGene.period)]:
                                threadIdentifier = list(LocalSearchEngine.localSearchMemory["content"]["simple_mutation"][(chromosome.stringIdentifier, gene.period, targetGene.period)])[0]
                                mStringIdentifier = LocalSearchEngine.mutationStringIdentifier(chromosome.stringIdentifier, gene.period, targetGene.period)
                                popChromosome = Chromosome.popByThread[threadIdentifier]["content"][mStringIdentifier]
                                Chromosome.copyToThread(self.threadIdentifier, popChromosome)
                                LocalSearchEngine.registerMove((chromosome.stringIdentifier, gene.period, targetGene.period), self.threadIdentifier)
                            continue

                    if LocalSearchEngine.areItemsSwitchable(chromosome, gene, targetGene.period):
                        print("Switchable !!!!!!!!!!!!!!!!!!! ")
                        localSearchMemoryKey = (chromosome.stringIdentifier, gene.period, targetGene.period)

                        mStringIdentifier = LocalSearchEngine.mutationStringIdentifier(chromosome.stringIdentifier, gene.period, targetGene.period)
                        inPool = True
                        with Chromosome.pool["lock"]:
                            if mStringIdentifier not in Chromosome.pool["content"]:
                                inPool =  False

                        if inPool:
                            # print("Resultiiiiiiii : ", result)
                            if self.threadIdentifier not in Chromosome.pool["content"][mStringIdentifier]:
                                Chromosome.copyToThread(self.threadIdentifier, popChromosome)
                                popChromosome = Chromosome.popByThread[self.threadIdentifier]["content"][mStringIdentifier]
                                if popChromosome < chromosome:
                                    queue.append(popChromosome)
                                    break
                            else:
                                continue

                        else:
                            evaluationData = LocalSearchEngine.evaluateItemsSwitch(chromosome, gene, targetGene.period)
                            pseudoChromosome = PseudoChromosome(evaluationData)

                            with Chromosome.pool["lock"]:
                                if mStringIdentifier not in Chromosome.pool["content"]:
                                    Chromosome.addToPop(self.threadIdentifier, pseudoChromosome)
                                else:
                                    popChromosome = Chromosome.popByThread[list(Chromosome.pool["content"][mStringIdentifier])[0]]["content"][mStringIdentifier]
                                    Chromosome.copyToThread(self.threadIdentifier, popChromosome)
                                    continue

                            if evaluationData["variance"] > 0:
                                queue.append(pseudoChromosome)
                                break
                    else:
                        pass
                        

            if len(queue) > 0:
                LocalSearchEngine.registerMove(localSearchMemoryKey, self.threadIdentifier)


        if (self.offsprings[offspringIndex]).stringIdentifier in Chromosome.popByThread[self.threadIdentifier]["content"]:
            self.offsprings[offspringIndex] = None

        # return offspring