from functools import total_ordering

import numpy as np
from LspAlgorithms.GeneticAlgorithms.Chromosome import Chromosome
import random

from LspInputDataReading.LspInputDataInstance import InputDataInstance
from ParameterSearch.ParameterData import ParameterData

class Population:

    def __init__(self, chromosomes) -> None:
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
        nElites = int(float(len(self.chromosomes)) * ParameterData.instance.elitePercentage)
        nElites = ( 1 if nElites < 1 else nElites)

        # self.chromosomes.sorted(key= lambda chromosome: chromosome.cost) 
        chromosomes = sorted(self.chromosomes, key= (lambda chromosome: chromosome.cost)) # reverse=True

        self.elites = chromosomes[:nElites]
        self.maxChromosomeCost = (chromosomes[-1]).cost + 1


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
        print(rouletteProbabilities)

        while len(selectedChromosomes) < len(self.chromosomes): # selecting two chromosomes at once

            chromosomeA, chromosomeB, chromosomeC, chromosomeD = np.random.choice(self.chromosomes, p=rouletteProbabilities), np.random.choice(self.chromosomes, p=rouletteProbabilities), None, None
            if (random.random() < ParameterData.instance.crossOverRate):
                chromosomeC, chromosomeD = Population.crossOverChromosomes(chromosomeA, chromosomeB)
                # print("+++", chromosomeC, chromosomeD)

                if (random.random() < ParameterData.instance.mutationRate):
                    chromosomeC.mutate()

                if (random.random() < ParameterData.instance.mutationRate):
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

        # print("=======", dnaArrayZipped, unzippedDNA)
        for item, itemIndices in enumerate(dnaArrayZipped):
            bottomLimit = 0
            for i, itemIndex in enumerate(itemIndices):
                if itemIndex == None:
                    for j, periodValue in enumerate(unzippedDNA[bottomLimit:InputDataInstance.instance.demandsArrayZipped[item][i]]):
                        if periodValue == 0:
                            dnaArrayZipped[item][i] = bottomLimit + j
                bottomLimit = dnaArrayZipped[item][i]

        return dnaArrayZipped


    @classmethod
    def crossOverChromosomes(cls, chromosomeA, chromosomeB) -> Chromosome:
        """Uniform crossover
        """
        dnaArrayZippedC = [[] for _ in range(InputDataInstance.instance.nItems)]
        dnaArrayZippedD = [[] for _ in range(InputDataInstance.instance.nItems)]
        # cost = 0

        # print(chromosomeA.unzipDnaArray(), chromosomeB.unzipDnaArray())
        # print(chromosomeA.dnaArrayZipped, chromosomeB.dnaArrayZipped)

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


        # print("????", dnaArrayZippedC, dnaArrayZippedD)

        chromosomeC, chromosomeD = Chromosome(), Chromosome()
        chromosomeC.dnaArrayZipped = dnaArrayZippedC
        chromosomeD.dnaArrayZipped = dnaArrayZippedD
        
        chromosomeC.cost = Chromosome.calculateCostZippedDNA(chromosomeC.dnaArrayZipped, InputDataInstance.instance)
        chromosomeD.cost = Chromosome.calculateCostZippedDNA(chromosomeD.dnaArrayZipped, InputDataInstance.instance)

        if not Chromosome.feasible(chromosomeC.dnaArrayZipped, InputDataInstance.instance):
            print("oooooooooooooooooooooooooooooooooooooooooooooooooooo", chromosomeC.unzipDnaArray())

        if not Chromosome.feasible(chromosomeD.dnaArrayZipped, InputDataInstance.instance):
            print("oooooooooooooooooooooooooooooooooooooooooooooooooooo", chromosomeD.unzipDnaArray())

        # print(chromosomeA, chromosomeB)
        # print(chromosomeC, chromosomeD)

        return chromosomeC, chromosomeD









# dnaArray = [[] for _ in range(InputDataInstance.instance.nPeriods)]
# dnaArrayZipped = [[] for _ in range(InputDataInstance.instance.nItems)]
# cost = 0

# period = InputDataInstance.instance.nPeriods - 1

# while period >= 0:

#     randomPick = random.randint(1, 2)
#     item = (chromosomeA.dnaArray[period] if randomPick == 1 else chromosomeB.dnaArray[period])
#     dnaArray[period] = item

#     if (item is not 0):
#         dnaArrayZipped[item - 1].insert(0, period)

#     period -= 1