import copy
from LspInputDataReading.LspInputDataInstance import InputDataInstance
from .Chromosome import Chromosome


class MutationOperator:
    """
    """

    def __init__(self, chromosome) -> None:
        """
        """

        self.chromosome = chromosome


    def process(self):
        """
        """
        
        mutations = self.searchMutations(self.chromosome.dnaArray)

        [print(mutation) for mutation in mutations]

        betterChromosome = self.bestMutation(self.chromosome, mutations)
		# print("----------------------------------------------------")
        while betterChromosome is not None:
            self.chromosome = betterChromosome
            mutations = self.searchMutations(self.chromosome.dnaArray)
            betterChromosome = self.bestMutation(self.chromosome, mutations)
            print("----------------------------------------------------")
            [print(mutation) for mutation in mutations]

        return self.chromosome


    def searchMutations(self, dnaArray):
        """
        """

        mutations = []

        genesList = sorted([gene for itemProdGenes in dnaArray for gene in itemProdGenes], key= lambda gene: gene.cost, reverse=True)

        for gene in genesList:
            mutations += self.genePossibleMutations(gene, dnaArray)
        
        return mutations


    def bestMutation(self, chromosome, mutations):
        """
        """

        if len(mutations) == 0:
            return None

        mutation = min(mutations, key=lambda pair:pair[1])

        if (mutation[1] >= chromosome.cost):
            return None

        result = Chromosome()
        result.dnaArray = mutation[0]
        result.cost = mutation[1]

        return result


    def genePossibleMutations(self, gene1, dnaArray, strategy = "all"): # strategy can be "all" or "null" only for mutations related to null periods
        """
        """
        mutations = []

        gene1LowerLimit = 0 if gene1.position == 0 else (dnaArray[gene1.item][gene1.position - 1]).period + 1
        gene1UpperLimit = InputDataInstance.instance.demandsArrayZipped[gene1.item][gene1.position] + 1 if gene1.position == len(InputDataInstance.instance.demandsArrayZipped[gene1.item]) - 1 else (dnaArray[gene1.item][gene1.position + 1]).period

        for index, periodValue in enumerate(Chromosome.sliceDna(dnaArray, gene1LowerLimit, gene1UpperLimit)):
            period = index + gene1LowerLimit
            if periodValue == 0:
                mutation = self.evaluateMutation(dnaArray, gene1.item, gene1.position, -1, period)
                mutations.append(mutation)
            else:
                if strategy == "all":
                    item2 = periodValue - 1
                    if item2 != gene1.item:
                        gene2 = [gene for gene in dnaArray[item2] if gene.period == period]
                        gene2 = gene2[0]

                        gene2LowerLimit = 0 if gene2.position == 0 else (dnaArray[gene2.item][gene2.position - 1]).period + 1
                        gene2UpperLimit = InputDataInstance.instance.demandsArrayZipped[gene2.item][gene2.position] + 1 if gene2.position == len(InputDataInstance.instance.demandsArrayZipped[gene2.item]) - 1 else (dnaArray[gene2.item][gene2.position + 1]).period
                        
                        if (gene2LowerLimit <= gene1.period and gene1.period < gene2UpperLimit) and (gene1LowerLimit <= gene2.period and gene2.period < gene1UpperLimit):
                            mutation = self.evaluateMutation(dnaArray, gene1.item, gene1.position, gene2.item, gene2.position)
                            mutations.append(mutation)

        return mutations


    def evaluateMutation(self, dnaArray, item1, position1, item2, position2):
        """
        """

        dnaArray = [[copy.deepcopy(gene) for gene in itemGenes] for itemGenes in dnaArray]

        gene1 = dnaArray[item1][position1] 

        if item2 == -1:
            gene1.period = position2
            gene1.calculateStockingCost()
        else:
            gene2 = dnaArray[item2][position2] 
            gene1.period, gene2.period = gene2.period, gene1.period
            gene1.calculateStockingCost()
            gene2.calculateStockingCost()

        genesList = sorted([gene for itemProdGenes in dnaArray for gene in itemProdGenes], key= lambda gene: gene.period)

        prevGene = None
        cost = 0
        for gene in genesList:
            if ((gene.item, gene.position) in [(item1, position1), (item2, position2)]):
                gene.prevGene = (prevGene.item, prevGene.position) if prevGene is not None else None 
                gene.calculateChangeOverCost()             
                gene.calculateCost()
            cost += gene.cost
            prevGene = gene

        return dnaArray, cost