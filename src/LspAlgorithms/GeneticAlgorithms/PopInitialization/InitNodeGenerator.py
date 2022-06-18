import uuid
from LspAlgorithms.GeneticAlgorithms.Chromosome import Chromosome
from LspAlgorithms.GeneticAlgorithms.LocalSearch.LocalSearchEngine import LocalSearchEngine
from ParameterSearch.ParameterData import ParameterData
import threading
from queue import Queue


class InitNodeGenerator:
    """
    """

    def __init__(self, queue) -> None:
        """
        """
        self.queue = queue
        self.uuid = uuid.uuid4()
        self.resultQueue = Queue(maxsize = 1)


    def generate(self, chromosomes, maxSize):
        """
        """

        while len(self.queue) > 0 and not (chromosomes["full"]).is_set():
            node = self.queue[-1]
            self.queue = self.queue[:-1]

            self.nextNode(node, chromosomes, maxSize)

        return None


    def nextNode(self, node, chromosomes, maxSize):
        """
        """

        # print("------ : ", node.chromosome, node.itemsToOrder, len(node.chromosome.stringIdentifier))
        if node.period < 0:

            # if not Chromosome.feasible(node.chromosome):
            #     print("/////////////////////////////////////////////////", node.chromosome)

            node.chromosome.stringIdentifier = tuple(node.chromosome.stringIdentifier)
            # print("chromosome created : ", node.chromosome)

            #
            # results = (LocalSearchEngine().process(node.chromosome, "population"))
            # with chromosomes["lock"]:
            #     if (chromosomes["full"]).is_set():
            #         return None

            #     # print("Pop size : ",len(chromosomes["values"]), maxSize)

            #     nLeft = maxSize - len(chromosomes["values"])
            #     # print("leeeeeeeeeeeeeft : ", results[:nLeft], nLeft)    
            #     for chromosome in results[:nLeft]:
            #         # print("Dataaaaaa : ", chromosomes["values"])
            #         chromosomes["values"].add(chromosome)
            #         # print("Dataaaaaa : ", chromosome)

            self.resultQueue.put(node.chromosome)

            if self.resultQueue.full():
                with chromosomes["lock"]:
                    while not self.resultQueue.empty() and len(chromosomes["values"]) < maxSize:
                        chromosomes["values"].add(self.resultQueue.get())

                    if len(chromosomes["values"]) >= maxSize:
                        (chromosomes["full"]).set()
                        return None

            return None

        for child in node.generateChild():
            if (chromosomes["full"]).is_set():
                return None
            self.nextNode(child, chromosomes, maxSize)

        return None


