from collections import defaultdict
import concurrent.futures
from queue import Queue
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
        # self.pipelines = defaultdict(lambda: Queue(maxsize=1))

        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(self.startNodeGenerator, self.nodeGenerators)
            # executor.submit(self.startNodeGenerator, self.nodeGenerators[1])


    def startNodeGenerator(self, nodeGenerator):
        """
        """
        nodeGenerator.generate(self.pipelines[nodeGenerator.uuid])


    def getInstance(self):
        """
        """
        
        empties = []
        while len(empties) < len(self.pipelines):
            for key in self.pipelines.keys():
                if self.pipelines[key].empty():
                    if key not in empties:
                        empties.append(key)
                else:
                    instance = self.pipelines[key].get()                    
                    yield instance

        yield None
            