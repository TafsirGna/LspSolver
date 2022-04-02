from LspAlgorithms.GeneticAlgorithms.Chromosome import Chromosome
import random

from LspInputDataReading.LspInputDataInstance import InputDataInstance

class Population:

    def __init__(self, chromosomes) -> None:
        """
        """
        self.chromosomes = chromosomes

    def evolve(self):
        pass

    @classmethod
    def crossOverChromosomes(cls, chromosomeA, chromosomeB) -> Chromosome:
        """
        """
        dnaArrayZipped = [[] for _ in range(0, InputDataInstance.instance.nItems)]
        cost = 0

        for item in range(0, InputDataInstance.instance.nItems):
            i = len(InputDataInstance.instance.demandsArrayZipped[item]) - 1
            while i >= 0:
                itemIndex = (chromosomeA.dnaArrayZipped[item][i] if random.randint(1, 2) == 1 else chromosomeB.dnaArrayZipped[item][i])
                dnaArrayZipped[item].insert(0, itemIndex)

                i -= 1

        result = Chromosome([])
        result.dnaArrayZipped = dnaArrayZipped
        result.unzipDnaArray()
        result.cost = cost

        print(result)

        return result









# dnaArray = [[] for _ in range(0, InputDataInstance.instance.nPeriods)]
# dnaArrayZipped = [[] for _ in range(0, InputDataInstance.instance.nItems)]
# cost = 0

# period = InputDataInstance.instance.nPeriods - 1

# while period >= 0:

#     randomPick = random.randint(1, 2)
#     item = (chromosomeA.dnaArray[period] if randomPick == 1 else chromosomeB.dnaArray[period])
#     dnaArray[period] = item

#     if (item != 0):
#         dnaArrayZipped[item - 1].insert(0, period)

#     period -= 1