from LspInputDataReading.LspInputDataInstance import InputDataInstance

class Gene:
    """
    """

    def __init__(self, item, period, position, prevGene = None) -> None:
        """
        """
        self.item = item
        self.period = period
        self.cost = 0
        self.position = position
        self.prevGene, self.nextGene = prevGene, None

    
    def calculateCost(self):
        """
        """
        self.cost = 0
        # Stocking cost
        self.stockingCost = (InputDataInstance.instance.demandsArrayZipped[self.item][self.position] - self.period) * InputDataInstance.instance.stockingCostsArray[self.item]
        self.cost += self.stockingCost

        # Change over cost
        if (self.prevGene != None):
            self.changeOverCost = InputDataInstance.instance.changeOverCostsArray[self.prevGene[0]][self.item]
            self.cost += self.changeOverCost


    # def __lt__(self, gene):
    #     """
    #     """
    #     return self.cost < gene.cost


    def __repr__(self):
        """
        """
        return "{}|{}|{}|{}".format(self.item, self.position, self.period, self.cost)



