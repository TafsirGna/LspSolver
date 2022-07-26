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
        self.nextGene = None

        self.changeOverCost = 0
        self.stockingCost = 0
        # self.calculateCost()
    
    def calculateCost(self):
        """
        """

        self.cost = self.changeOverCost + self.stockingCost

    def calculateStockingCost(self):
        """
        """

        self.stockingCost = (InputDataInstance.instance.demandsArrayZipped[self.item][self.position] - self.period) * InputDataInstance.instance.stockingCostsArray[self.item]

    def calculateChangeOverCost(self):
        """
        """

        self.changeOverCost = 0
        if (self.prevGene is not None):
            self.changeOverCost = InputDataInstance.instance.changeOverCostsArray[self.prevGene[0]][self.item]
            # print("calculate change cost ", self.changeOverCost, self.prevGene)



    # def __lt__(self, gene):
    #     """
    #     """
    #     return self.cost < gene.cost

    def __eq__(self, gene):
        """
        """
        return self.item == gene.item and self.position == gene.position and self.period == gene.period and self.prevGene == gene.prevGene and self.nextGene == gene.nextGene and self.changeOverCost == gene.changeOverCost and self.stockingCost == gene.stockingCost and self.cost == gene.cost
        
    def __repr__(self):
        """
        """
        # return "it:{}|pos:{}|peri:{}|cos:{}|prev:({}, {})".format(self.item, self.position, self.period, self.cost, self.prevGene[0] if self.prevGene != None else None, self.prevGene[1] if self.prevGene != None else None)
        # return "{} ({}, {}) ${}".format(self.period, self.prevGene[0] if self.prevGene != None else None, self.prevGene[1] if self.prevGene != None else None, self.cost)
        return "{}-{}-{}|{} p({}, {}) n({}, {})".format(self.item, self.position, self.period, self.cost, self.prevGene[0] if self.prevGene != None else None, self.prevGene[1] if self.prevGene != None else None, self.nextGene[0] if self.nextGene != None else None, self.nextGene[1] if self.nextGene != None else None)


    def __hash__(self) -> int:
        return hash((self.item, self.position, self.period, self.prevGene, self.nextGene, self.changeOverCost, self.stockingCost)) #, self.cost



