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

            self.nextNode(node, pipeline)

        return None


    def nextNode(self, node, pipeline):
        """
        """
        if node.period < 0:
            if pipeline.full():
                return None

            pipeline.put(node)
            return None

        for child in node.generateChild():
            if pipeline.full():
                return None
            self.nextNode(child, pipeline)

        return None


