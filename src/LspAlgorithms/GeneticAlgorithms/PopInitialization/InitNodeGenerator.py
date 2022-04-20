import queue
import random

class InitNodeGenerator:

    instance = None
    
    def __init__(self, queue) -> None:
        """
        """
        self.queue = queue

    def generate(self):
        """
        """
        
        while len(self.queue) > 0:

            node = self.queue[-1]
            self.queue = self.queue[:- 1]

            children = node.children()
            if len(children) == 0: # leaf node
                return node

            self.queue += children

        return None
    