from collections import defaultdict
import concurrent.futures
from queue import Queue
import threading
from ParameterSearch.ParameterData import ParameterData

class InitNodeGeneratorManager:
    """
    """

    def __init__(self, nodeGenerators) -> None:
        """
        """
        
        self.callers = defaultdict(lambda: 0)
        self.nodeGenerators = nodeGenerators
        self.chromosomes = {"lock": threading.Lock(), "values": set(), "full": threading.Event()}
        self.maxSize = ParameterData.instance.popSize * ParameterData.instance.nPrimaryThreads

        with concurrent.futures.ThreadPoolExecutor() as executor:
            print(list(executor.map(self.startNodeGenerator, self.nodeGenerators)))
            # print(list(executor.map(self.startNodeGenerator, [self.nodeGenerators[0]])))
            # executor.submit(self.startNodeGenerator, self.nodeGenerators[0])


    def startNodeGenerator(self, nodeGenerator):
        """
        """

        nodeGenerator.generate(self.chromosomes, self.maxSize)


    def getInstance(self):
        """
        """
        
        # print("cooooooooooool", self.chromosomes["values"])
        for chromosome in self.chromosomes["values"]:
            yield chromosome
            