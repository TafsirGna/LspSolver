from functools import total_ordering
from threading import Thread, local
import threading

import numpy as np
from LspAlgorithms.GeneticAlgorithms.Chromosome import Chromosome
import random
from LspInputDataReading.LspInputDataInstance import InputDataInstance
from ParameterSearch.ParameterData import ParameterData

class Population:

    def __init__(self, chromosomes = []) -> None:
        """
        """
        self.chromosomes = chromosomes
        self.elites = []
        self.setElites()
        self.nextPopulation = None
        self._nextPopLock = threading.Lock()
        self.maxChromosomeCost = None

    def evolve(self):
        """
        """

        self.nextPopulation = Population([])
        self.applyGeneticOperators()
        return self.nextPopulation

    
    def setElites(self):
        """
        """
        # if len(self.elites) > 0 or len(self.chromosomes) is 0:
        #     return

        # nElites = int(float(len(self.chromosomes)) * ParameterData.instance.elitePercentage)
        # nElites = ( 1 if nElites < 1 else nElites)

        # # self.chromosomes.sorted(key= lambda chromosome: chromosome.cost) 
        # chromosomes = sorted(self.chromosomes)

        # self.elites = chromosomes[:nElites]


    def add(self, chromosome):
        """
        """
        if ParameterData.instance and len(self.chromosomes) >= ParameterData.instance.popSize:
            self.setElites()
            return None

        self.chromosomes.append(chromosome)

        # setting population max cost
        if self.maxChromosomeCost == None:
            self.maxChromosomeCost = chromosome.cost
        else:
            cost = chromosome.cost + 1
            if self.maxChromosomeCost < cost:
                self.maxChromosomeCost = cost
        return chromosome


    def threadTask(self, rouletteProbabilities):
        """
        """

        while len(self.nextPopulation.chromosomes) < len(self.chromosomes):

            chromosomeA, chromosomeB, chromosome = np.random.choice(self.chromosomes, p=rouletteProbabilities), np.random.choice(self.chromosomes, p=rouletteProbabilities), None

            if (random.random() < ParameterData.instance.crossOverRate):
                chromosome = Population.crossOverChromosomes(chromosomeA, chromosomeB)
                # print("+++", chromosome)

                if chromosome is not None and (random.random() < ParameterData.instance.mutationRate):
                    chromosome.mutate()

            if chromosome is not None:
                with self._nextPopLock:
                    self.nextPopulation.add(chromosome)
                    if len(self.nextPopulation.chromosomes) > len(self.chromosomes):
                        return
            


    def applyGeneticOperators(self, selection_strategy="roulette_wheel"):
        """
        """
        
        if selection_strategy == "roulette_wheel":
            self.applyRouletteWheel()


    def applyRouletteWheel(self):
        """
        """

        totalFitness = 0
        for chromosome in self.chromosomes:
            chromosome.fitnessValue = self.maxChromosomeCost - chromosome.cost
            # print("888 ---> ", chromosome, chromosome.fitnessValue)
            totalFitness += chromosome.fitnessValue
        self.totalFitness = totalFitness
        # print("888 ---> ", self.totalFitness)

        rouletteProbabilities = [float(chromosome.fitnessValue)/self.totalFitness for chromosome in self.chromosomes]

        for i in range(ParameterData.instance.nReplicaThreads):
            thread_T = Thread(target=self.threadTask, args=(rouletteProbabilities,))
            thread_T.start()
            thread_T.join()


    def preprocess(self):
        """
        """
        pass


    def converged(self):
        """
        """
        uniques, unique_counts, fittest = [], [], self.chromosomes[0]

        for chromosome in self.chromosomes:
            if not (chromosome.dnaArray in uniques):
                uniques.append(chromosome.dnaArray)
                unique_counts.append(0)
            else:
                unique_counts[uniques.index(chromosome.dnaArray)] += 1

            if chromosome.cost < fittest.cost:
                fittest = chromosome

        localOptimal = uniques[unique_counts.index(max(unique_counts))]

        # Setting the threshold under which a populatioin is set to have converged
        threshold = int(ParameterData.instance.convergenceThresholdPercentage * len(self.chromosomes))
        threshold = 1 if threshold < 1 else threshold

        if len(uniques) <= threshold and localOptimal == fittest.dnaArray:
            return True
        return False


    def __repr__(self):
        """
        """
        return "Population : {} : \nCost Total :{} ".format(self.chromosomes, 0)


    @classmethod
    def repairDna(cls, dnaArrayZipped):
        """
        """

        unzippedDNA = Chromosome.classUnzipDnaArray(dnaArrayZipped)

        # print("=== Before ", dnaArrayZipped, unzippedDNA , ' | ', InputDataInstance.instance.demandsArrayZipped)

        for item, itemIndices in enumerate(dnaArrayZipped):
            bottomLimit = 0
            for i, itemIndex in enumerate(itemIndices):
                # print("item : ", item, 'index : ', itemIndex, "None : ", itemIndex is None, "indices : ", itemIndices)
                if itemIndex is None:
                    # print("Portion : ", unzippedDNA[bottomLimit:(InputDataInstance.instance.demandsArrayZipped[item][i]+1)])

                    j = (InputDataInstance.instance.demandsArrayZipped[item][i])
                    while j >= bottomLimit:

                        periodValue = unzippedDNA[j]
                        # print("periodValue : ", periodValue)
                        if periodValue == 0:
                            dnaArrayZipped[item][i] = j
                            unzippedDNA = Chromosome.classUnzipDnaArray(dnaArrayZipped)
                            # print("result 1 : ", dnaArrayZipped)
                            break
                        else:
                            repaired = False
                            # print("not a list ", dnaArrayZipped[periodValue - 1], (j))
                            indexPeriodValue = dnaArrayZipped[periodValue - 1].index(j)
                            demandPeriod = InputDataInstance.instance.demandsArrayZipped[periodValue - 1][indexPeriodValue]
                            # print("demande period : ", demandPeriod, "Second portion : ", unzippedDNA[(j + bottomLimit):demandPeriod + 1])
                            
                            k = demandPeriod
                            while k >= (j + bottomLimit):

                                periodVal = unzippedDNA[k]
                                # print("Second period : ", periodVal)
                                if periodVal == 0:
                                    dnaArrayZipped[periodValue - 1][indexPeriodValue] = k
                                    dnaArrayZipped[item][i] = (j + bottomLimit)
                                    unzippedDNA = Chromosome.classUnzipDnaArray(dnaArrayZipped)
                                    # print("result 2 : ", dnaArrayZipped)
                                    repaired = True
                                    break

                                k -= 1
                                
                            
                            if repaired:
                                break

                        j -= 1

                    # if it still none then 
                    if dnaArrayZipped[item][i] is None:
                        return None
                bottomLimit = dnaArrayZipped[item][i] + 1
        
        # print("=== After ", dnaArrayZipped, unzippedDNA)

        return dnaArrayZipped


    @classmethod
    def crossOverChromosomes(cls, chromosomeA, chromosomeB) -> Chromosome:
        """
        """

        dnaArray = [[ None for _ in row ] for row in InputDataInstance.instance.demandsArrayZipped]
        chromosomeA, chromosomeB = (chromosomeA, chromosomeB) if chromosomeA < chromosomeB else (chromosomeB, chromosomeA)

        genesList = sorted([gene for itemProdGenes in chromosomeA.dnaArray for gene in itemProdGenes], key= lambda gene: gene.cost)

        visitedPeriods = []
        for geneA in genesList:
            geneB = chromosomeB.dnaArray[geneA.item][geneA.position]
            geneA, geneB = (geneA, geneB) if geneA.stockingCost <= geneB.stockingCost else (geneB, geneA)
            if dnaArray[geneA.item][geneA.position] == None:
                if not(geneA.period in visitedPeriods):
                    dnaArray[geneA.item][geneA.position] = geneA
                    visitedPeriods.append(geneA.period)
                elif not(geneB.period in visitedPeriods):
                    dnaArray[geneB.item][geneB.position] = geneB
                    visitedPeriods.append(geneB.period)
        
        # print(dnaArray, '       ', Chromosome.classRenderDnaArray(dnaArray), Chromosome.feasible(dnaArray, InputDataInstance.instance))
        repairedDnaArray = dnaArray
        if not Chromosome.feasible(dnaArray, InputDataInstance.instance):
            print("Boooooooooooooooooooooooooooooo", Chromosome.classRenderDnaArray(chromosomeA.dnaArray), Chromosome.classRenderDnaArray(chromosomeB.dnaArray), dnaArray)
            repairedDnaArray = Population.repairDna(dnaArray)

        genesList = sorted([gene for itemProdGenes in repairedDnaArray for gene in itemProdGenes], key= lambda gene: gene.period)

        prevGene = None
        cost = 0
        for index, gene in enumerate(genesList):
            gene.changeOverCost = 0 if index == 0 else InputDataInstance.instance.changeOverCostsArray[prevGene.item][gene.item]
            gene.cost = gene.stockingCost + gene.changeOverCost    
            gene.prevGene = (prevGene.item, prevGene.position) if prevGene != None else (None, None)        
            prevGene = gene
            cost += gene.cost

        chromosome = None
        if repairedDnaArray != None:
            chromosome = Chromosome()
            chromosome.dnaArray = repairedDnaArray
            chromosome.cost = cost

        # print(chromosome)

        return chromosome
