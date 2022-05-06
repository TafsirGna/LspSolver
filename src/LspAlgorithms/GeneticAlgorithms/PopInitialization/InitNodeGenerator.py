from collections import defaultdict
import queue
import uuid

from LspInputDataReading.LspInputDataInstance import InputDataInstance


class InitNodeGenerator:
    
    def __init__(self, queue) -> None:
        """
        """
        self.queue = queue
        self.uuid = uuid.uuid4()


    def generate(self, pipeline):
        """
        """

        while len(self.queue) > 0 and not pipeline.full():
            node = self.queue[-1]
            self.queue = self.queue[:-1]

            children = node.children()
            if len(children) == 0:
                # print("Chromosome --- : ", node.chromosome)
                pipeline.put(node)

            self.queue += children

        return None

