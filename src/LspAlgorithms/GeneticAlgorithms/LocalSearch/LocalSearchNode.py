import copy
import random
from LspAlgorithms.GeneticAlgorithms.Chromosome import Chromosome
from LspAlgorithms.GeneticAlgorithms.Gene import Gene
from LspInputDataReading.LspInputDataInstance import InputDataInstance


class LocalSearchNode:
    """
    """

    def __init__(self, chromosome) -> None:
        """
        """

        self.chromosome = chromosome


    def generateChild(self):
        """
        """

        # print("ooooooooooooook")
        genes = [gene for itemGenes in self.chromosome.dnaArray for gene in itemGenes]
        random.shuffle(genes)

        for gene in genes:
            for mutation in LocalSearchNode.generateGeneMutations(gene, self.chromosome):
                chromosome = mutation[1]
                # print("Child : ", chromosome)
                yield LocalSearchNode(chromosome)

        return []


    def children(self):
        """
        """

        children = []

        for child in self.generateChild():
            # print("child : ", child)
            children.append(child)

        children.sort(reverse=True)
        return children


    @classmethod
    def createMutatedChromosome(cls, chromosome, swap, context = "mutation"):
        """
        """

        # print("In createMutatedChromosome", chromosome, swap)

        # Making up the stringIdentifier of the result chromosome
        stringIdentifier = list(chromosome.stringIdentifier)
        dnaArray = None

        gene1Item, gene1Position = swap[0][0], swap[0][1]
        # print("swap : ", swap, chromosome, chromosome.dnaArray)
        if swap[1][0] == -1:
            newPeriod = swap[1][1]
            stringIdentifier[newPeriod] = gene1Item + 1
            stringIdentifier[(chromosome.dnaArray[gene1Item][gene1Position]).period] = 0
            stringIdentifier = tuple(stringIdentifier)
            if Chromosome.pool[stringIdentifier] is not None:
                return Chromosome.pool[stringIdentifier]
            
            dnaArray = copy.deepcopy(chromosome.dnaArray)
            gene1 = dnaArray[gene1Item][gene1Position]

            if gene1 is None: # crossover
                dnaArray[gene1Item][gene1Position] = Gene(gene1Item, newPeriod, gene1Position)
                dnaArray[gene1Item][gene1Position].calculateStockingCost()
            else: # mutation
                cost = chromosome.cost
                cost -= gene1.cost

                if newPeriod + 1 != gene1.period and newPeriod != gene1.period + 1:

                    nextGene1, nextGene0 = LocalSearchNode.nextProdGene(gene1.period, dnaArray, chromosome.stringIdentifier), LocalSearchNode.nextProdGene(newPeriod, dnaArray, chromosome.stringIdentifier)

                    # print("nextGene1, nextGene0 : ", nextGene1, nextGene0)
                    cost -= nextGene1.changeOverCost if nextGene1 is not None else 0
                    cost -= nextGene0.changeOverCost if nextGene0 is not None else 0

                    if nextGene1 is not None:
                        # print("before nextGene1 : ", nextGene1)
                        nextGene1.prevGene = gene1.prevGene
                        nextGene1.calculateChangeOverCost()
                        # print("after nextGene1 : ", nextGene1)
                        cost += nextGene1.changeOverCost

                    if nextGene0 is not None:
                        # print("before nextGene0 : ", nextGene0)
                        nextGene0.prevGene = (gene1.item, gene1.position)
                        nextGene0.calculateChangeOverCost()
                        # print("after nextGene0 : ", nextGene0)
                        cost += nextGene0.changeOverCost

                        (dnaArray[gene1Item][gene1Position]).prevGene = nextGene0.prevGene 
                    else:
                        previousGene = LocalSearchNode.prevProdGene(newPeriod, dnaArray, chromosome.stringIdentifier)
                        (dnaArray[gene1Item][gene1Position]).prevGene = (previousGene.item, previousGene.position)

                (dnaArray[gene1Item][gene1Position]).period = newPeriod
                (dnaArray[gene1Item][gene1Position]).calculateChangeOverCost()
                (dnaArray[gene1Item][gene1Position]).calculateStockingCost()
                (dnaArray[gene1Item][gene1Position]).calculateCost()

                cost += (dnaArray[gene1Item][gene1Position]).cost

                # print("kokooooooooooo : ", cost, stringIdentifier, dnaArray)

        else:
            gene2Item, gene2Position = swap[1][0], swap[1][1]
            period1, period2 = (chromosome.dnaArray[gene1Item][gene1Position]).period, (chromosome.dnaArray[gene2Item][gene2Position]).period 
            stringIdentifier[period1] =  gene2Item + 1
            stringIdentifier[period2] =  gene1Item + 1
            stringIdentifier = tuple(stringIdentifier)

            if Chromosome.pool[stringIdentifier] is not None:
                return Chromosome.pool[stringIdentifier]

            dnaArray = copy.deepcopy(chromosome.dnaArray)

            # fixing the chromosome dnaArray and calculating the cost
            # print("dnaArray : ", dnaArray)
            gene1 = (dnaArray[gene1Item][gene1Position])
            gene2 = (dnaArray[gene2Item][gene2Position])
            
            cost = chromosome.cost

            if context == "mutation":

                cost -= (gene1.cost + gene2.cost)

                # print("preveeees --- : ", gene1.prevGene, gene2.prevGene)

                if gene1.prevGene == (gene2Item, gene2Position):
                    gene1.prevGene = gene2.prevGene
                    gene2.prevGene = (gene1.item, gene1.position)
                    nextGene = LocalSearchNode.nextProdGene(gene1.period, dnaArray, chromosome.stringIdentifier)

                    # print("before before nextGene A: ", nextGene)

                    if nextGene is not None:
                        # print("before nextGene A: ", nextGene, nextGene.changeOverCost)
                        cost -= nextGene.changeOverCost
                        prevGene = (gene2.item, gene2.position)
                        # print("prevGene A: ", prevGene)
                        nextGene.prevGene = prevGene
                        nextGene.calculateChangeOverCost()
                        cost += nextGene.changeOverCost
                        # print("after nextGene A: ", nextGene, nextGene.changeOverCost)

                elif gene2.prevGene == (gene1Item, gene1Position):
                    gene2.prevGene = gene1.prevGene
                    gene1.prevGene = (gene2.item, gene2.position)
                    nextGene = LocalSearchNode.nextProdGene(gene2.period, dnaArray, chromosome.stringIdentifier)

                    # print("before before nextGene B: ", nextGene)

                    if nextGene is not None:
                        # print("before nextGene B: ", nextGene, nextGene.changeOverCost)
                        cost -= nextGene.changeOverCost
                        prevGene = (gene1.item, gene1.position)
                        # print("prevGene B: ", prevGene)
                        nextGene.prevGene = prevGene
                        nextGene.calculateChangeOverCost()
                        cost += nextGene.changeOverCost
                        # print("after nextGene B: ", nextGene, nextGene.changeOverCost)

                else:
                    gene1.prevGene, gene2.prevGene = gene2.prevGene, gene1.prevGene
                    nextGene1, nextGene2 = LocalSearchNode.nextProdGene(gene1.period, dnaArray, chromosome.stringIdentifier), LocalSearchNode.nextProdGene(gene2.period, dnaArray, chromosome.stringIdentifier)

                    # print("before before nextGene1 nextGene2 : ", nextGene1, nextGene2)

                    if nextGene1 is not None:
                        # print("before nextGene1 : ", nextGene1, nextGene1.changeOverCost)
                        cost -= nextGene1.changeOverCost
                        prevGene = (gene2.item, gene2.position)
                        # print("prevGene : ", prevGene)
                        nextGene1.prevGene = prevGene
                        nextGene1.calculateChangeOverCost()
                        cost += nextGene1.changeOverCost 
                        # print("after nextGene1 : ", nextGene1, nextGene1.changeOverCost)

                    if nextGene2 is not None:
                        # print("before nextGene2 : ", nextGene2, nextGene2.changeOverCost)
                        cost -= nextGene2.changeOverCost
                        prevGene = (gene1.item, gene1.position)
                        # print("prevGene : ", prevGene)
                        nextGene2.prevGene = prevGene
                        nextGene2.calculateChangeOverCost()
                        cost += nextGene2.changeOverCost
                        # print("after nextGene2 : ", nextGene2, nextGene2.changeOverCost)

                
            gene1.period, gene2.period = gene2.period, gene1.period

            gene1.calculateStockingCost()
            gene1.calculateChangeOverCost()
            gene1.calculateCost()

            gene2.calculateStockingCost()
            gene2.calculateChangeOverCost()
            gene2.calculateCost()

            cost += (gene1.cost + gene2.cost)

        # print("Coooooost : ", cost, stringIdentifier, dnaArray, Chromosome.createFromIdentifier(stringIdentifier))

        result = Chromosome()
        result.dnaArray = dnaArray
        result.stringIdentifier = stringIdentifier
        if context == "mutation":
            result.cost = cost
            
        return result

    @classmethod
    def nextProdGene(cls, prodPeriod, dnaArray, stringIdentifier):
        """
        """

        # print("nextProdGene : ", prodPeriod, chromosome.stringIdentifier[prodPeriod + 1:])
        for index, item in enumerate(stringIdentifier[prodPeriod + 1:]):
            if item != 0:
                period = (prodPeriod + 1) + index
                item0 = item - 1
                for geneA in dnaArray[item0]:
                    if geneA.period == period:
                        # print('next ', geneA)
                        return geneA
        
        # print('next None')
        return None

    @classmethod
    def prevProdGene(cls, prodPeriod, dnaArray, stringIdentifier):
        """
        """

        # print("nextProdGene : ", prodPeriod, chromosome.stringIdentifier[prodPeriod + 1:])
        for index, item in enumerate(reversed(stringIdentifier[:prodPeriod])):
            if item != 0:
                period = (prodPeriod - 1) - index
                item0 = item - 1
                for geneA in dnaArray[item0]:
                    if geneA.period == period:
                        # print('next ', geneA)
                        return geneA
        
        # print('next None')
        return None

    # @classmethod
    # def allGenePossibleMutations(cls, gene1, chromosome, context = "mutation", strategy = "all"): # strategy can be "all" or "null" only for mutations related to null periods
    #     """
    #     """

    #     mutations = []
    #     for mutation in cls.generateGeneMutations(gene1, chromosome, context, strategy):
    #         mutations.append(mutation)
    #     return mutations


    @classmethod
    def generateGeneMutations(cls, gene1, chromosome, context = "mutation", strategy = "all"):
        """
        """

        # print('gene1 : ', gene1.item, gene1.position, gene1.period, chromosome, chromosome.dnaArray)

        gene1LowerLimit = 0 if gene1.position == 0 else (chromosome.dnaArray[gene1.item][gene1.position - 1]).period + 1
        gene1UpperLimit = InputDataInstance.instance.demandsArrayZipped[gene1.item][gene1.position] + 1 if gene1.position == len(InputDataInstance.instance.demandsArrayZipped[gene1.item]) - 1 else ((chromosome.dnaArray[gene1.item][gene1.position + 1]).period if (chromosome.dnaArray[gene1.item][gene1.position + 1]) is not None else InputDataInstance.instance.demandsArrayZipped[gene1.item][gene1.position] + 1)
        gene1UpperLimit = InputDataInstance.instance.demandsArrayZipped[gene1.item][gene1.position] + 1 if InputDataInstance.instance.demandsArrayZipped[gene1.item][gene1.position] + 1 < gene1UpperLimit else gene1UpperLimit

        # print("lower and upper limit 1 : ", gene1LowerLimit, gene1UpperLimit)

        stringIdentifierSlice = [(index, periodValue) for index, periodValue in enumerate(chromosome.stringIdentifier[gene1LowerLimit:gene1UpperLimit])]
        random.shuffle(stringIdentifierSlice)
        for index, periodValue in stringIdentifierSlice:
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


    def __lt__(self, node) -> bool:
        """
        """
        return self.chromosome < node.chromosome

    def __eq__(self, node) -> bool:
        """
        """
        return self.chromosome == node.chromosome

    def __repr__(self) -> str:
        return str(self.chromosome)