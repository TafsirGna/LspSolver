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

    # crossOverMemory = {"lock": threading.Lock(), "content": defaultdict(lambda: None)}

    def __init__(self) -> None:
        """
        """

        self.parentChromosomes = None
        self.offsprings = {0: None, 1: None}
        self.population = None 

        if LocalSearchEngine.localSearchMemory["content"]["simple_mutation"] is None:
            LocalSearchEngine.localSearchMemory["content"]["simple_mutation"] = dict()

        # self._stopSearchEvents = {0: threading.Event(), 1: threading.Event()}


    def process(self, population):
        """
        """

        chromosomes = set()
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
                chromosomes.add(chromosomeC)

            if len(chromosomes) < Population.popSizes[population.threadIdentifier]:
                if chromosomeD is None:
                    print("chromosomeD None")
                else:
                    chromosomes.add(chromosomeD)

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

        self.setOffsprings()

        print("Cross Over result : ", [self.parentChromosomes, self.offsprings])

        return tuple(self.offsprings.values())


    def setOffsprings(self):
        """
        """
        
        for i in [0, 1]:
            self.searchOffspring(i)


    def searchOffspring(self, offspringIndex):
        """
        """

        threadIdentifier = self.population.threadIdentifier if self.population is not None else 1

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
                    localSearchMemoryKey = (chromosome.stringIdentifier, gene.period, targetGene.period)
                    mStringIdentifier = None

                    with LocalSearchEngine.localSearchMemory["lock"]:
                        if localSearchMemoryKey in LocalSearchEngine.localSearchMemory["content"]["simple_mutation"]:
                            if threadIdentifier not in LocalSearchEngine.localSearchMemory["content"]["simple_mutation"][localSearchMemoryKey]:
                                mStringIdentifier = LocalSearchEngine.mutationStringIdentifier(chromosome.stringIdentifier, gene.period, targetGene.period)
                                popChromosome = None
                                for threadIdentifier in LocalSearchEngine.localSearchMemory["content"]["simple_mutation"][localSearchMemoryKey]:
                                    popChromosome = Chromosome.popByThread[threadIdentifier]["content"][mStringIdentifier]
                                    if isinstance(popChromosome, Chromosome):
                                        break
                                Chromosome.copyToThread(threadIdentifier, popChromosome)
                                # LocalSearchEngine.registerMove(memKey, threadIdentifier)

                                if isinstance(popChromosome, Chromosome):
                                    continue
                                # else is instance of PseudoChromosome 
                                queue.append(popChromosome)
                                break

                    if LocalSearchEngine.areItemsSwitchable(chromosome, gene, targetGene.period):
                        print("Switchable !!!!!!!!!!!!!!!!!!! ")

                        if mStringIdentifier is None:
                            mStringIdentifier = LocalSearchEngine.mutationStringIdentifier(chromosome.stringIdentifier, gene.period, targetGene.period)

                        inPool = True
                        with Chromosome.pool["lock"]:
                            if mStringIdentifier not in Chromosome.pool["content"]:
                                inPool =  False

                        if inPool:
                            # print("Resultiiiiiiii : ", result)
                            if threadIdentifier not in Chromosome.pool["content"][mStringIdentifier]:
                                Chromosome.copyToThread(threadIdentifier, popChromosome)
                                popChromosome = Chromosome.popByThread[threadIdentifier]["content"][mStringIdentifier]
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
                                    Chromosome.addToPop(threadIdentifier, pseudoChromosome)
                                else:
                                    popChromosome = Chromosome.popByThread[list(Chromosome.pool["content"][mStringIdentifier])[0]]["content"][mStringIdentifier]
                                    Chromosome.copyToThread(threadIdentifier, popChromosome)
                                    continue

                            if evaluationData["variance"] > 0:
                                queue.append(pseudoChromosome)
                                break
                    else:
                        pass
                        

            if len(queue) > 0:
                LocalSearchEngine.registerMove(localSearchMemoryKey, threadIdentifier)

        # return offspring