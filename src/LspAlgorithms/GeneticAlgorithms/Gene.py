from LspInputDataReading.LspInputDataInstance import InputDataInstance

class Gene:
    """
    """

    def __init__(self, item, period, position) -> None:
        """
        """
        self.item = item
        self.period = period
        self.cost = 0
        self.position = position
        self.prevGene, self.nextGene = None, None

    
    def calculateCost(self):
        """
        """
        self.cost = 0
        # Stocking cost
        self.cost += (InputDataInstance.instance.demandsArrayZipped[self.item][self.position] - self.period) * InputDataInstance.instance.stockingCostsArray[self.item]

        # Change over cost
        if (self.prevGene != None):
            self.cost += InputDataInstance.chanOverArray[self.prevGene.item][self.item]


    def __repr__(self):
        """
        """
        return "TODO"



