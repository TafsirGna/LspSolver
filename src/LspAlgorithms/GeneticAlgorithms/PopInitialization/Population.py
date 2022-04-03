from LspAlgorithms.GeneticAlgorithms.Chromosome import Chromosome
import random

from LspInputDataReading.LspInputDataInstance import InputDataInstance
from ParameterSearch.ParameterData import ParameterData

class Population:

    def __init__(self, chromosomes) -> None:
        """
        """
        self.chromosomes = chromosomes
        self.costTotal = None


    def evolve(self):
        """
        """

        selectedPopulation = self.applyGeneticOperators()
        population = selectedPopulation

        return population


    def applyGeneticOperators(self, selection_strategy="roulette_wheel"):
        """
        """
        
        if selection_strategy == "roulette_wheel":
            return self.applyRouletteWheel()


    def applyRouletteWheel(self):
        """
        """

        selectedChromosomes = []

        if self.costTotal == None:
            self.calculateCostTotal()

        rouletteProbabilities = []
        
        partial_sum = 0
        for chromosome in self.chromosomes:
            partial_sum += float(chromosome.cost)/self.costTotal
            rouletteProbabilities.append(partial_sum)

        while len(selectedChromosomes) < len(self.chromosomes): # selecting two chromosomes at once
            randomFloat = random.random()
            for indexA, proba in enumerate(rouletteProbabilities):
                if randomFloat <= proba:
                    indexB = int(indexA + (len(self.chromosomes)/2)) % len(self.chromosomes)
                    # print(indexA, indexB)
                    chromosomeA, chromosomeB = self.chromosomes[indexA], self.chromosomes[indexB]

                    print("---", chromosomeA, chromosomeB)
                    
                    if (random.random() < ParameterData.instance.crossOverRate):
                        chromosomeC, chromosomeD = Population.crossOverChromosomes(chromosomeA, chromosomeB)
                        print("+++", chromosomeC, chromosomeD)

                        if (random.random() < ParameterData.instance.mutationRate):
                            chromosomeC.mutate()

                        if (random.random() < ParameterData.instance.mutationRate):
                            chromosomeD.mutate()

                        selectedChromosomes.append(chromosomeC)
                        selectedChromosomes.append(chromosomeD)
        
        population = Population(selectedChromosomes)
        population.calculateCostTotal()
        
        # print("Pool Size --> ", len(population.chromosomes))
        return population


    def converged(self):
        """
        """
        # ParameterData.instance.popSize
        if (len(set(self.chromosomes)) < (len(self.chromosomes) / 2)):
            return True
        return False

        
    def calculateCostTotal(self):
        """
        """

        self.costTotal = 0
        for chromosome in self.chromosomes:
            self.costTotal += chromosome.cost

        self.costTotal = float(self.costTotal)



    def __repr__(self):
        """
        """
        return "Population : {} : \nCost Total :{} ".format(self.chromosomes, self.costTotal)



    @classmethod
    def crossOverChromosomes(cls, chromosomeA, chromosomeB) -> Chromosome:
        """
        """
        dnaArrayZippedC = [[] for _ in range(InputDataInstance.instance.nItems)]
        dnaArrayZippedD = [[] for _ in range(InputDataInstance.instance.nItems)]
        # cost = 0

        # print(chromosomeA.unzipDnaArray(), chromosomeB.unzipDnaArray())
        # print(chromosomeA.dnaArrayZipped, chromosomeB.dnaArrayZipped)

        for item in range(InputDataInstance.instance.nItems):
            i = len(InputDataInstance.instance.demandsArrayZipped[item]) - 1
            while i >= 0:

                if random.randint(1, 2) == 1:
                    dnaArrayZippedC[item].insert(0, chromosomeA.dnaArrayZipped[item][i])
                    dnaArrayZippedD[item].insert(0, chromosomeB.dnaArrayZipped[item][i])
                else: 
                    dnaArrayZippedD[item].insert(0, chromosomeA.dnaArrayZipped[item][i])
                    dnaArrayZippedC[item].insert(0, chromosomeB.dnaArrayZipped[item][i])

                i -= 1

        print("????", dnaArrayZippedC, dnaArrayZippedD)

        chromosomeC, chromosomeD = Chromosome(), Chromosome()
        chromosomeC.dnaArrayZipped = dnaArrayZippedC
        chromosomeD.dnaArrayZipped = dnaArrayZippedD
        
        # chromosomeC.cost = Chromosome.calculateCostZippedDNA(chromosomeC.dnaArrayZipped, InputDataInstance.instance)
        # chromosomeD.cost = Chromosome.calculateCostZippedDNA(chromosomeD.dnaArrayZipped, InputDataInstance.instance)

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

#     if (item != 0):
#         dnaArrayZipped[item - 1].insert(0, period)

#     period -= 1