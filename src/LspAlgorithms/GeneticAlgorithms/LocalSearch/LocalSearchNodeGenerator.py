from collections import defaultdict
import copy
from LspAlgorithms.GeneticAlgorithms.Chromosome import Chromosome
from LspAlgorithms.GeneticAlgorithms.Gene import Gene
from LspAlgorithms.GeneticAlgorithms.LocalSearch.LocalSearchNode import LocalSearchNode
from LspInputDataReading.LspInputDataInstance import InputDataInstance


class LocalSearchNodeGenerator:
    """
    """

    def __init__(self, chromosome) -> None:
        """
        """

        self.node = LocalSearchNode(chromosome)


    def generate(self):
        """
        """ 

        for itemGenes in self.node.chromosome.dnaArray:
            for gene in itemGenes:
                for mutation in LocalSearchNodeGenerator.getGeneMutations(gene, self.node.chromosome):
                    chromosome = mutation[1]
                    # print("Child : ", chromosome)
                    yield LocalSearchNode(chromosome)

        return []


    @classmethod
    def getGeneMutations(cls, gene1, chromosome, context = "mutation", strategy = "all"):
        """
        """

        # print('gene1 : ', gene1.item, gene1.position, gene1.period, chromosome)

        gene1LowerLimit = 0 if gene1.position == 0 else (chromosome.dnaArray[gene1.item][gene1.position - 1]).period + 1
        gene1UpperLimit = InputDataInstance.instance.demandsArrayZipped[gene1.item][gene1.position] + 1 if gene1.position == len(InputDataInstance.instance.demandsArrayZipped[gene1.item]) - 1 else ((chromosome.dnaArray[gene1.item][gene1.position + 1]).period if (chromosome.dnaArray[gene1.item][gene1.position + 1]) is not None else InputDataInstance.instance.demandsArrayZipped[gene1.item][gene1.position] + 1)
        gene1UpperLimit = InputDataInstance.instance.demandsArrayZipped[gene1.item][gene1.position] + 1 if InputDataInstance.instance.demandsArrayZipped[gene1.item][gene1.position] + 1 < gene1UpperLimit else gene1UpperLimit

        # print("lower and upper limit 1 : ", gene1LowerLimit, gene1UpperLimit)

        for index, periodValue in enumerate(Chromosome.sliceDna(chromosome.dnaArray, gene1LowerLimit, gene1UpperLimit)):
            period = index + gene1LowerLimit
            if periodValue == 0:
                swap = [(gene1.item, gene1.position), ( -1, period)]
                mutation = [chromosome, LocalSearchNode.createMutatedChromosome(chromosome, swap, context), swap]
                yield mutation
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
                            mutation = [chromosome, LocalSearchNode.createMutatedChromosome(chromosome, swap, context), swap]
                            yield mutation

        return []