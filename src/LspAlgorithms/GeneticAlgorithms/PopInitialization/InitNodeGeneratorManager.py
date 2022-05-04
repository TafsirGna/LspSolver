from collections import defaultdict
import concurrent.futures
import threading
import uuid

class InitNodeGeneratorManager:
    """
    """

    def __init__(self, nodeGenerators) -> None:
        """
        """
        
        self.callers = defaultdict(lambda: 0)
        self.nodeGenerators = nodeGenerators
        # self._pipeLock = threading.Lock()

    
    def start(self, pipeline):
        """
        """

        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.submit(self.threadTask, pipeline)
            # executor.map(self.threadTask, self.nodeGenerators, [pipeline] * len(self.nodeGenerators))
            # for nodeGenerator in self.nodeGenerators:
            #     executor.submit(self.threadTask, nodeGenerator, pipeline)



    def threadTask(self, pipeline):
        """
        """

        while not pipeline.full():

            node = None
            for nodeGenerator in self.nodeGenerators:
                node = nodeGenerator.generate()
                if node is None:
                    continue
                pipeline.put(node.chromosome)

            if node is None:
                return





