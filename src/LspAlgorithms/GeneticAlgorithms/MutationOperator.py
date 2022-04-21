import copy
import random
from LspAlgorithms.GeneticAlgorithms.Gene import Gene
from LspInputDataReading.LspInputDataInstance import InputDataInstance
from ParameterSearch.ParameterData import ParameterData
from .Chromosome import Chromosome


class MutationOperator:
    """
    """

    def __init__(self, chromosome) -> None:
        """
        """

        self.chromosome = chromosome
        self.genes = [gene for itemProdGenes in self.chromosome.dnaArray for gene in itemProdGenes]


    def process(self, strategy = "medium"): # strategy :  medium/advanced
        """
        """

        print("advanced ----", self.chromosome)
        
        mutations = self.searchMutations(strategy)
        chromosome = self.selectOneMutation(mutations)

        if strategy == "medium":
            if chromosome is not None:
                self.chromosome = chromosome

        else:
            if strategy == "advanced":
                while chromosome is not None:
                    self.chromosome = chromosome
                    mutations = self.searchMutations(strategy)
                    chromosome = self.selectOneMutation(mutations)

		# print("----------------------------------------------------")
        # while betterChromosome is not None:
        #     self.chromosome = betterChromosome
        #     mutations = self.searchMutations(self.chromosome.dnaArray)
        #     betterChromosome = self.bestMutation(self.chromosome, mutations)
        #     # print("----------------------------------------------------")
        #     # [print(mutation) for mutation in mutations]

        return self.chromosome


    def mediumMutationsSearch(self):
        """
        """
        mutations = []
        while len(mutations) == 0 and len(self.genes) > 0: 
            gene = random.choice(self.genes)
            mutations = self.genePossibleMutations(gene, self.chromosome.dnaArray)
            self.genes.remove(gene)

        return mutations

    def advancedMutationsSearch(self):
        """
        """
        mutations = []
        for gene in self.genes:
            mutations += self.genePossibleMutations(gene, self.chromosome.dnaArray)

        return mutations

    def searchMutations(self, strategy = "medium"):
        """
        """

        mutations = []

        if strategy == "medium":
            muatations = self.mediumMutationsSearch()

        else: 
            if strategy == "advanced":
                mutations = self.advancedMutationsSearch()
        
        return mutations


    def selectOneMutation(self, mutations, strategy = "best"): # strategy : random/best
        """
        """

        if len(mutations) == 0:
            return None

        # mutation = min(mutations, key=lambda pair:pair[2])
        if strategy ==  "random":
            mutation = random.choice(mutations)
        else:
            if strategy == "best":
                mutation = min(mutations, key=lambda mutation: mutation[2] )

        result = Chromosome()
        result.dnaArray = mutation[0]
        result.stringIdentifier = mutation[1]
        result.cost = mutation[2]

        return result

    @classmethod
    def genePossibleMutations(cls, gene1, dnaArray, evaluate = True, strategy = "all"): # strategy can be "all" or "null" only for mutations related to null periods
        """
        """

        mutations = []

        gene1LowerLimit = 0 if gene1.position == 0 else (dnaArray[gene1.item][gene1.position - 1]).period + 1
        gene1UpperLimit = InputDataInstance.instance.demandsArrayZipped[gene1.item][gene1.position] + 1 if gene1.position == len(InputDataInstance.instance.demandsArrayZipped[gene1.item]) - 1 else ((dnaArray[gene1.item][gene1.position + 1]).period if (dnaArray[gene1.item][gene1.position + 1]) is not None else InputDataInstance.instance.demandsArrayZipped[gene1.item][gene1.position] + 1)

        # print("Kill ", dnaArray, gene1.item, gene1.position, Chromosome.classRenderDnaArray(dnaArray))
        for index, periodValue in enumerate(Chromosome.sliceDna(dnaArray, gene1LowerLimit, gene1UpperLimit)):
            # print("Slice ", Chromosome.sliceDna(dnaArray, gene1LowerLimit, gene1UpperLimit))
            period = index + gene1LowerLimit
            if periodValue == 0:
                mutatedDnaArray = cls.formMutatedDnaArray(dnaArray, gene1.item, gene1.position, -1, period)
                focus = [(gene1.item, gene1.position), ( -1, period)]
                mutation = Chromosome.evaluateDnaArray(mutatedDnaArray, focus) if evaluate else [mutatedDnaArray, focus]
                mutations.append(mutation)
            else:
                if strategy == "all":
                    item2 = periodValue - 1
                    if item2 != gene1.item:
                        # print(dnaArray[item2], item2, period)
                        gene2 = [gene for gene in dnaArray[item2] if gene.period == period]
                        gene2 = gene2[0]

                        gene2LowerLimit = 0 if gene2.position == 0 else (dnaArray[gene2.item][gene2.position - 1]).period + 1
                        gene2UpperLimit = InputDataInstance.instance.demandsArrayZipped[gene2.item][gene2.position] + 1 if gene2.position == len(InputDataInstance.instance.demandsArrayZipped[gene2.item]) - 1 else (dnaArray[gene2.item][gene2.position + 1]).period
                        
                        if (gene2LowerLimit <= gene1.period and gene1.period < gene2UpperLimit) and (gene1LowerLimit <= gene2.period and gene2.period < gene1UpperLimit):
                            mutatedDnaArray = cls.formMutatedDnaArray(dnaArray, gene1.item, gene1.position, gene2.item, gene2.position)
                            mutation = Chromosome.evaluateDnaArray(mutatedDnaArray, [(gene1.item, gene1.position), (gene2.item, gene2.position)]) if evaluate else mutatedDnaArray
                            mutations.append(mutation)

        return mutations

    @classmethod
    def formMutatedDnaArray(cls, dnaArray, item1, position1, item2, position2):
        """
        """

        dnaArray = [[copy.deepcopy(gene) for gene in itemGenes] for itemGenes in dnaArray]

        gene1 = dnaArray[item1][position1] 

        if item2 == -1:
            if gene1 is None:
                dnaArray[item1][position1] = Gene(item1, position2, position1)
            else:
                (dnaArray[item1][position1]).period = position2
            dnaArray[item1][position1].calculateStockingCost()
        else:
            gene2 = dnaArray[item2][position2] 
            gene1.period, gene2.period = gene2.period, gene1.period
            gene1.calculateStockingCost()
            gene2.calculateStockingCost()

        return dnaArray