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
        self.prevGene = prevGene

        # self.changeOverCost = None
        # self.stockingCost = None
        # self.calculateCost()
    
    def calculateCost(self):
        """
        """
        self.cost = 0
        # Stocking cost
        self.calculateStockingCost()
        self.cost += self.stockingCost

        # Change over cost
        self.calculateChangeOverCost()
        self.cost += self.changeOverCost

    def calculateStockingCost(self):
        """
        """
        self.stockingCost = (InputDataInstance.instance.demandsArrayZipped[self.item][self.position] - self.period) * InputDataInstance.instance.stockingCostsArray[self.item]


    def calculateChangeOverCost(self):
        """
        """
        self.changeOverCost = 0
        if (self.prevGene != None):
            self.changeOverCost = InputDataInstance.instance.changeOverCostsArray[self.prevGene[0]][self.item]



    # def __lt__(self, gene):
    #     """
    #     """
    #     return self.cost < gene.cost


    def __repr__(self):
        """
        """
        return "it:{}|pos:{}|peri:{}|cos:{}|prev:({}, {})".format(self.item, self.position, self.period, self.cost, self.prevGene[0] if self.prevGene != None else None, self.prevGene[1] if self.prevGene != None else None)



