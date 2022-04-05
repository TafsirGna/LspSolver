from functools import total_ordering

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
        self.setElites()


    def evolve(self):
        """
        """

        selectedPopulation = self.applyGeneticOperators()
        population = selectedPopulation

        return population

    
    def setElites(self):
        """
        """
        if len(self.chromosomes) is 0:
            return

        nElites = int(float(len(self.chromosomes)) * ParameterData.instance.elitePercentage)
        nElites = ( 1 if nElites < 1 else nElites)

        # self.chromosomes.sorted(key= lambda chromosome: chromosome.cost) 
        chromosomes = sorted(self.chromosomes, key= (lambda chromosome: chromosome.cost)) # reverse=True

        self.elites = chromosomes[:nElites]
        self.maxChromosomeCost = (chromosomes[-1]).cost + 1


    def add(self, chromosome):
        """
        """
        if ParameterData.instance and len(self.chromosomes) >= ParameterData.instance.popSize:
            self.setElites()
            return None

        self.chromosomes.append(chromosome)
        return chromosome


    def applyGeneticOperators(self, selection_strategy="roulette_wheel"):
        """
        """
        
        if selection_strategy == "roulette_wheel":
            return self.applyRouletteWheel()


    def applyRouletteWheel(self):
        """
        """

        selectedChromosomes = []

        # Calculating fitness value for each chromosome
        # maxChromosomeCost = (max(self.chromosomes, key=lambda c: c.cost)).cost + 1

        totalFitness = 0
        for chromosome in self.chromosomes:
            chromosome.fitnessValue = self.maxChromosomeCost - chromosome.cost
            # print("888 ---> ", chromosome, chromosome.fitnessValue)
            totalFitness += chromosome.fitnessValue
        self.totalFitness = totalFitness
        # print("888 ---> ", self.totalFitness)

        rouletteProbabilities = []
        

        for chromosome in self.chromosomes:
            rouletteProbabilities.append(float(chromosome.fitnessValue)/self.totalFitness)

        while len(selectedChromosomes) < len(self.chromosomes): # selecting two chromosomes at once

            chromosomeA, chromosomeB, chromosomeC, chromosomeD = np.random.choice(self.chromosomes, p=rouletteProbabilities), np.random.choice(self.chromosomes, p=rouletteProbabilities), None, None
            if (random.random() < ParameterData.instance.crossOverRate):
                chromosomeC, chromosomeD = Population.crossOverChromosomes(chromosomeA, chromosomeB)
                # print("+++", chromosomeC, chromosomeD)

                if chromosomeC is not None and (random.random() < ParameterData.instance.mutationRate):
                    chromosomeC.mutate()

                if chromosomeD is not None and (random.random() < ParameterData.instance.mutationRate):
                    chromosomeD.mutate()


            if chromosomeC is not None:
                selectedChromosomes.append(chromosomeC)
                if len(selectedChromosomes) > len(self.chromosomes):
                    population = Population(selectedChromosomes)
                    return population

            if chromosomeD is not None:
                selectedChromosomes.append(chromosomeD)
        
        population = Population(selectedChromosomes)
    
        return population


    def converged(self):
        """
        """
        
        uniques = []
        for chromosome in self.chromosomes:
            if not (chromosome.dnaArrayZipped in uniques):
                uniques.append(chromosome.dnaArrayZipped)

        if (len(uniques) == 1):
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

        if Chromosome.feasible(dnaArrayZipped, InputDataInstance.instance):
            return dnaArrayZipped

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
        """Uniform crossover
        """
        dnaArrayZippedC = [[] for _ in range(InputDataInstance.instance.nItems)]
        dnaArrayZippedD = [[] for _ in range(InputDataInstance.instance.nItems)]

        indicesC, indicesD  = [], []
        for item in range(InputDataInstance.instance.nItems):
            i = len(InputDataInstance.instance.demandsArrayZipped[item]) - 1
            while i >= 0:
                
                itemIndexC, itemIndexD = None, None
                if random.randint(1, 2) == 1:
                    itemIndexC = chromosomeA.dnaArrayZipped[item][i]
                    itemIndexD = chromosomeB.dnaArrayZipped[item][i]
                else: 
                    itemIndexD = chromosomeA.dnaArrayZipped[item][i]
                    itemIndexC = chromosomeB.dnaArrayZipped[item][i]
                
                # making sure there's not the same item index twice in the chromosome dna representation
                if not(itemIndexC in indicesC): 
                    dnaArrayZippedC[item].insert(0, itemIndexC)
                    indicesC.append(itemIndexC)
                    indicesC.sort()
                else:
                    dnaArrayZippedC[item].insert(0, None)

                if not(itemIndexD in indicesD): 
                    dnaArrayZippedD[item].insert(0, itemIndexD)
                    indicesD.append(itemIndexD)
                    indicesD.sort()
                else:
                    dnaArrayZippedD[item].insert(0,None)

                i -= 1

        dnaArrayZippedC, dnaArrayZippedD = Population.repairDna(dnaArrayZippedC), Population.repairDna(dnaArrayZippedD)

        chromosomeC, chromosomeD = None, None
        if dnaArrayZippedC is not None:
            chromosomeC = Chromosome()
            chromosomeC.dnaArrayZipped = dnaArrayZippedC
            chromosomeC.cost = Chromosome.calculateCostZippedDNA(chromosomeC.dnaArrayZipped, InputDataInstance.instance)

        if dnaArrayZippedD is not None:
            chromosomeD = Chromosome()
            chromosomeD.dnaArrayZipped = dnaArrayZippedD
            chromosomeD.cost = Chromosome.calculateCostZippedDNA(chromosomeD.dnaArrayZipped, InputDataInstance.instance)

        return chromosomeC, chromosomeD
