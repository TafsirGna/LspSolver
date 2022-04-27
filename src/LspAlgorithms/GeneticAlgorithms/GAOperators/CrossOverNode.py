import copy
from LspAlgorithms.GeneticAlgorithms.Chromosome import Chromosome
from LspAlgorithms.GeneticAlgorithms.LocalSearchNode import LocalSearchNode
from LspInputDataReading.LspInputDataInstance import InputDataInstance
import random

class CrossOverNode:
    """
    """

    def __init__(self, parentChromosomes) -> None:
        """
        """
        self.parentChromosomes = parentChromosomes
        self.chromosome = Chromosome()
        self.pointer = (0, 0)


    def children(self):
        """
        """
        return self.childrenApproach2()


    def childrenApproach2(self):
        """
        """
        children = []

        # print("node ", self.chromosome)

        if self.pointer == (None, None):
            return children

        item, position = self.pointer[0], self.pointer[1]
        pointer = self.nextPointer()

        # [print('Parent : ', chromosome.dnaArray) for chromosome in self.parentChromosomes]

        # print("child : ", self.pointer, self.chromosome.dnaArray)
        
        genes = [chromosome.dnaArray[item][position] for chromosome in self.parentChromosomes]

        lowerLimit = 0 if position == 0 else (self.chromosome.dnaArray[item][position - 1]).period + 1
        upperLimit = InputDataInstance.instance.demandsArrayZipped[item][position] + 1

        # print("Genes List", genes)

        for gene in genes:
            # print("Gene - ", gene.item + 1, gene.position, gene.period)
            searchMutation = False
            if self.chromosome.stringIdentifier[gene.period] == "0":
                if (lowerLimit <= gene.period and gene.period < upperLimit):

                    node = CrossOverNode(self.parentChromosomes)
                    node.pointer = pointer

                    dnaArray = copy.deepcopy(self.chromosome.dnaArray)
                    dnaArray[item][position] = gene
                    node.chromosome.dnaArray = dnaArray

                    stringIdentifier = self.chromosome.stringIdentifier
                    stringIdentifier = stringIdentifier[:gene.period] + str(gene.item + 1) + stringIdentifier[gene.period + 1:]
                    node.chromosome.stringIdentifier = stringIdentifier

                    children.append(node)
                else:
                    searchMutation = True
            else:
                searchMutation = True


            if searchMutation:

                # print("search mutations")
                mutations = LocalSearchNode.genePossibleMutations(gene, self.chromosome, False, "null")
                # print(mutations)

                for mutation in mutations:

                    node = CrossOverNode(self.parentChromosomes)
                    node.pointer = pointer
                    node.chromosome = mutation[1]

                    # newPeriod = mutation[1][1][1]
                    # stringIdentifier = self.chromosome.stringIdentifier
                    # stringIdentifier = stringIdentifier[:newPeriod] + str(gene.item + 1) + stringIdentifier[newPeriod + 1:]
                    # node.chromosome.stringIdentifier = stringIdentifier
                    
                    children.append(node)

        random.shuffle(children)
        # print("children ", children)
        return children

    
    def nextPointer(self):
        """
        """
        item, position = self.pointer[0], self.pointer[1]
        if position < len(InputDataInstance.instance.demandsArrayZipped[item]) - 1:
            item, position = item, position + 1
        else:
            if item < InputDataInstance.instance.nItems - 1:
                item, position = item + 1, 0
            else:
                item, position = None, None
                 
        return (item, position)


    def childrenApproach3(self):
        """
        """

        children = []

        # chromosomeA, chromosomeB = (self.parentChromosomes[0], self.parentChromosomes[1]) if self.parentChromosomes[0] < self.parentChromosomes[1] else (self.parentChromosomes[1], self.parentChromosomes[0])
        # genesList = sorted([gene for itemProdGenes in chromosomeA.dnaArray for gene in itemProdGenes], key= lambda gene: gene.cost)

        # visitedPeriods = []
        # for geneA in genesList:
        #     geneB = chromosomeB.dnaArray[geneA.item][geneA.position]
        #     geneA, geneB = (geneA, geneB) if geneA.stockingCost <= geneB.stockingCost else (geneB, geneA)
        #     if dnaArray[geneA.item][geneA.position] == None:
        #         if not(geneA.period in visitedPeriods):
        #             dnaArray[geneA.item][geneA.position] = geneA
        #             visitedPeriods.append(geneA.period)
        #         elif not(geneB.period in visitedPeriods):
        #             dnaArray[geneB.item][geneB.position] = geneB
        #             visitedPeriods.append(geneB.period)

        return children

    def __repr__(self):
        return "{}".format(self.chromosome)

    def __lt__(self, node):
        return self.chromosome.cost < node.chromosome.cost

    def __eq__(self, node):
        return self.chromosome.stringIdentifier == node.chromosome.stringIdentifier