from collections import defaultdict
import copy
from LspAlgorithms.GeneticAlgorithms.Chromosome import Chromosome
from LspAlgorithms.GeneticAlgorithms.Gene import Gene
from LspInputDataReading.LspInputDataInstance import InputDataInstance


class MutationNode:
    """
    """

    def __init__(self, chromosome, visitedChromosomes = None) -> None:
        """
        """

        self.chromosome = chromosome
        self.visitedChromosomes = defaultdict(lambda: None) if visitedChromosomes is None else visitedChromosomes


    def children(self):
        """
        """

        # print("Parent     : ", self.chromosome)

        children = []

        if self.visitedChromosomes[self.chromosome.stringIdentifier] is not None:
            return children

        self.visitedChromosomes[self.chromosome.stringIdentifier] = self.chromosome

        for itemGenes in self.chromosome.dnaArray:
            for gene in itemGenes:
                mutations = MutationNode.genePossibleMutations(gene, self.chromosome)
                for mutation in mutations:
                    chromosome = mutation[1]
                    node = MutationNode(chromosome, self.visitedChromosomes)
                    # print("Child : ", chromosome)
                    children.append(node)

        children.sort(reverse=True)
        return children


    @classmethod
    def createMutatedChromosome(cls, chromosome, swap, context = "mutation"):
        """
        """

        # print("In createMutatedChromosome", chromosome, swap)

        # Making up the stringIdentifier of the result chromosome
        stringIdentifier = chromosome.stringIdentifier

        gene1Item, gene1Position = swap[0][0], swap[0][1]
        if swap[1][0] == -1:
            newPeriod = swap[1][1]
            stringIdentifier = stringIdentifier[:newPeriod] + str(gene1Item + 1) + stringIdentifier[newPeriod + 1:]
            if Chromosome.pool[stringIdentifier] is not None:
                return Chromosome.pool[stringIdentifier]
            
            dnaArray = copy.deepcopy(chromosome.dnaArray)
            gene1 = dnaArray[gene1Item][gene1Position]

            if gene1 is None:
                dnaArray[gene1Item][gene1Position] = Gene(gene1Item, newPeriod, gene1Position)
            else:
                (dnaArray[gene1Item][gene1Position]).period = newPeriod
            dnaArray[gene1Item][gene1Position].calculateStockingCost()

            result = None
            if context == "mutation":
                result = Chromosome.evaluateDnaArray(dnaArray)
            else:
                result = Chromosome()
                result.dnaArray = dnaArray
                result.stringIdentifier = stringIdentifier
            return result

        else:
            gene2Item, gene2Position = swap[1][0], swap[1][1]
            period1, period2 = (chromosome.dnaArray[gene1Item][gene1Position]).period, (chromosome.dnaArray[gene2Item][gene2Position]).period 
            stringIdentifier = stringIdentifier[:period1] + str(gene2Item + 1) + stringIdentifier[period1 + 1:]
            stringIdentifier = stringIdentifier[:period2] + str(gene1Item + 1) + stringIdentifier[period2 + 1:]

            if Chromosome.pool[stringIdentifier] is not None:
                return Chromosome.pool[stringIdentifier]

            dnaArray = copy.deepcopy(chromosome.dnaArray)
            gene1 = dnaArray[gene1Item][gene1Position]
            gene2 = dnaArray[gene2Item][gene2Position]

            gene1.period, gene2.period = gene2.period, gene1.period
            gene1.calculateStockingCost()
            gene2.calculateStockingCost()

            result = None
            if context == "mutation":
                result = Chromosome.evaluateDnaArray(dnaArray)
            else:
                result = Chromosome()
                result.dnaArray = dnaArray
                result.stringIdentifier = stringIdentifier
            return result
            


    @classmethod
    def genePossibleMutations(cls, gene1, chromosome, context = "mutation", strategy = "all"): # strategy can be "all" or "null" only for mutations related to null periods
        """
        """

        mutations = []
        # print('gene1 : ', gene1.item, gene1.position, gene1.period, chromosome)

        gene1LowerLimit = 0 if gene1.position == 0 else (chromosome.dnaArray[gene1.item][gene1.position - 1]).period + 1
        gene1UpperLimit = InputDataInstance.instance.demandsArrayZipped[gene1.item][gene1.position] + 1 if gene1.position == len(InputDataInstance.instance.demandsArrayZipped[gene1.item]) - 1 else ((chromosome.dnaArray[gene1.item][gene1.position + 1]).period if (chromosome.dnaArray[gene1.item][gene1.position + 1]) is not None else InputDataInstance.instance.demandsArrayZipped[gene1.item][gene1.position] + 1)
        gene1UpperLimit = InputDataInstance.instance.demandsArrayZipped[gene1.item][gene1.position] + 1 if InputDataInstance.instance.demandsArrayZipped[gene1.item][gene1.position] + 1 < gene1UpperLimit else gene1UpperLimit

        # print("lower and upper limit 1 : ", gene1LowerLimit, gene1UpperLimit)

        for index, periodValue in enumerate(Chromosome.sliceDna(chromosome.dnaArray, gene1LowerLimit, gene1UpperLimit)):
            period = index + gene1LowerLimit
            if periodValue == 0:
                swap = [(gene1.item, gene1.position), ( -1, period)]
                mutation = [chromosome, cls.createMutatedChromosome(chromosome, swap, context), swap]
                mutations.append(mutation)
            else:
                if strategy == "all":
                    item2 = periodValue - 1
                    if item2 != gene1.item:
                        gene2 = [gene for gene in chromosome.dnaArray[item2] if gene.period == period]
                        gene2 = gene2[0]
                        # print('gene2 : ', gene2.item, gene2.position, gene2.period)

                        gene2LowerLimit = 0 if gene2.position == 0 else (chromosome.dnaArray[gene2.item][gene2.position - 1]).period + 1
                        gene2UpperLimit = InputDataInstance.instance.demandsArrayZipped[gene2.item][gene2.position] + 1 if gene2.position == len(InputDataInstance.instance.demandsArrayZipped[gene2.item]) - 1 else (chromosome.dnaArray[gene2.item][gene2.position + 1]).period
                        gene2UpperLimit = InputDataInstance.instance.demandsArrayZipped[gene2.item][gene2.position] + 1 if InputDataInstance.instance.demandsArrayZipped[gene2.item][gene2.position] + 1 < gene2UpperLimit else gene2UpperLimit
                        # print("lower and upper limit 2 : ", gene2LowerLimit, gene2UpperLimit)

                        if (gene2LowerLimit <= gene1.period and gene1.period < gene2UpperLimit) and (gene1LowerLimit <= gene2.period and gene2.period < gene1UpperLimit):
                            swap = [(gene1.item, gene1.position), (gene2.item, gene2.position)]
                            mutation = [chromosome, cls.createMutatedChromosome(chromosome, swap, context), swap]
                            mutations.append(mutation)

        return mutations


    def __lt__(self, node) -> bool:
        """
        """
        return self.chromosome.cost < node.chromosome.cost

    # def __eq__(self, node) -> bool:
    #     """
    #     """
    #     return None

    def __repr__(self) -> str:
        pass