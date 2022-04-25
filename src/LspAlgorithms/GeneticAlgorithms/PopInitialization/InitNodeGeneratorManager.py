from collections import defaultdict

class InitNodeGeneratorManager:
    """
    """

    def __init__(self, nodeGenerators, strategy = "diversified") -> None:
        """
        """
        
        self.callers = defaultdict(lambda: 0)
        self.nodeGenerators = nodeGenerators

    
    def newInstance(self, callerId):
        """
        """

        for _ in range(len(self.nodeGenerators)):

            callerGeneratorIndex = self.callers[callerId]
            nodeGenerator = self.nodeGenerators[callerGeneratorIndex]
            # reinitializing the counter
            self.callers[callerId] = callerGeneratorIndex + 1 if callerGeneratorIndex < len(self.nodeGenerators) - 1 else 0

            node = nodeGenerator.generate()
            if node is not None:
                return node

        return None



