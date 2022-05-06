from collections import defaultdict
import concurrent.futures
from queue import Queue
import threading
import uuid
from ParameterSearch.ParameterData import ParameterData

class InitNodeGeneratorManager:
    """
    """

    def __init__(self, nodeGenerators) -> None:
        """
        """
        
        self.callers = defaultdict(lambda: 0)
        self.nodeGenerators = nodeGenerators
        self.pipelines = defaultdict(lambda: Queue(maxsize=ParameterData.instance.popSize))

        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(self.startNodeGenerator, self.nodeGenerators)


    def startNodeGenerator(self, nodeGenerator):
        """
        """
        nodeGenerator.generate(self.pipelines[nodeGenerator.uuid])


    def getNode(self):
        """
        """
        
        empties = []
        while len(empties) < len(self.pipelines):
            for key in self.pipelines.keys():
                if self.pipelines[key].empty():
                    if key not in empties:
                        empties.append(key)
                else:
                    node = self.pipelines[key].get()                    
                    yield node

        yield None
            