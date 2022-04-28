from LspAlgorithms.GeneticAlgorithms.Chromosome import Chromosome
from LspAlgorithms.GeneticAlgorithms.LocalSearchEngine import LocalSearchEngine
from LspAlgorithms.GeneticAlgorithms.GAOperators.MutationOperator import MutationOperator
from LspAlgorithms.GeneticAlgorithms.GAOperators.CrossOverOperator import CrossOverOperator
from LspRuntimeMonitor import LspRuntimeMonitor
from LspInputDataReading.LspInputDataReader import InputDataReader

class TestGAOperators:
    """
    """        

    def test_mutation(self):
        """
        """

        self.setUpInput()

        print("ooooooooooooooooooooooooooooo")

        c = Chromosome.createFromRawDNA([2, 1, 0, 1, 2])
        # c = Chromosome.createFromRawDNA([2, 2, 2, 3, 1, 0, 0, 1])
        # [3, 2, 2, 2, 1, 1, 0, 0]
        # [2, 2, 2, 3, 1, 0, 0, 1]
        print("Chromosome ", c)
        # # [2, 1, 2, 0, 1]
        print("1 -- ", (MutationOperator()).process(c, strategy="advanced"))

        assert 1

    
    def test_crossover(self):
        """
        """

        self.setUpInput()

        cA, cB = Chromosome.createFromRawDNA([2, 1, 0, 2, 1]), Chromosome.createFromRawDNA([2, 1, 2, 0, 1])
        cA, cB = Chromosome.createFromRawDNA([1, 2, 2, 2, 1, 3, 0, 0]), Chromosome.createFromRawDNA([2, 2, 2, 3, 1, 1, 0, 0])
        print(cA, "\n", cB, "\n -----------------------------")
        print((CrossOverOperator([cA, cB])).process())


    def test_feasability(self):
        """
        """
        self.setUpInput()


    def test_localSearch(self):
        """
        """

        self.setUpInput()

        c = Chromosome.createFromRawDNA([2, 1, 0, 2, 1])
        (LocalSearchEngine()).process(c)


    def setUpInput(self):
        """
        """ 

        inputFile = "data/input/clspInst01.data"
        LspRuntimeMonitor.verbose = True
        inputDataReader = InputDataReader()
        inputDataInstance = inputDataReader.readInput(inputFile)

