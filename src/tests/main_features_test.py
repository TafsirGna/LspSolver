from LspAlgorithms.GeneticAlgorithms.PopInitialization.Chromosome import Chromosome
from LspAlgorithms.GeneticAlgorithms.GAOperators.LocalSearchEngine import LocalSearchEngine
# from LspAlgorithms.GeneticAlgorithms.GAOperators.MutationOperator import MutationOperator
from LspAlgorithms.GeneticAlgorithms.GAOperators.CrossOverOperator import CrossOverOperator
from LspInputDataReading.LspInputDataInstance import InputDataInstance
# from LspAlgorithms.GeneticAlgorithms.LspRuntimeMonitor import LspRuntimeMonitor
from LspInputDataReading.LspInputDataReader import InputDataReader
# from LspAlgorithms.GeneticAlgorithms.PopInitialization.Population import Population
from LspAlgorithms.GeneticAlgorithms.PopInitialization.PopInitializer import PopInitializer
from ParameterSearch.ParameterData import ParameterData

class TestMainFeatures:
    """
    """

    def test_crossover(self):
        """
        """

        self.setUpInput()

        # cA, cB = Chromosome.createFromIdentifier(stringIdentifier=(2, 1, 1, 2, 0)), Chromosome.createFromIdentifier(stringIdentifier=(2, 1, 0, 1, 2))
        cA, cB = Chromosome.createFromIdentifier(stringIdentifier=(0, 1, 2, 2, 0, 2, 3, 1)), Chromosome.createFromIdentifier(stringIdentifier=(0, 0, 2, 2, 1, 2, 3, 1))
        # cA, cB = Chromosome.createFromIdentifier(stringIdentifier=(3, 3, 3, 2, 2, 5, 4, 5, 5, 2, 1, 1, 3, 4, 2, 4, 1, 2, 2, 1)), Chromosome.createFromIdentifier(stringIdentifier=(4, 4, 3, 3, 2, 5, 2, 5, 5, 2, 1, 1, 1, 1, 2, 3, 2, 3, 4, 2))
        # [(5, 6, 10, 8, 0, 0, 9, 7, 0, 4, 4, 2, 1, 1, 3) : 1811, (7, 2, 8, 5, 10, 9, 0, 0, 0, 4, 4, 6, 1, 1, 3) : 1857]

        print(cA, "\n", cB, "\n -----------------------------")
        print((CrossOverOperator()).mate([cA, cB]))

        assert 0


    def test_feasability(self):
        """
        """
        self.setUpInput()


    def test_popInitialization(self):
        """
        """

        self.setUpInput()

        (PopInitializer()).process()

        assert 0


    def test_localSearch(self):
        """
        """

        self.setUpInput()

        c = Chromosome.createFromIdentifier(stringIdentifier=(4, 4, 2, 5, 5, 5, 2, 1, 3, 2, 1, 3, 2, 1, 1, 3, 3, 2, 2, 4))
        # c = Chromosome.createFromIdentifier(stringIdentifier=(0, 2, 2, 3, 0, 1, 2, 1))
        # (0, 0, 0, 9, 10, 8, 7, 5, 6, 4, 4, 2, 1, 1, 3)
        print("Input : ", c)
        # print("Output : ", (LocalSearchEngine()).process(c, "fitter_than", {"fittest": Chromosome.createFromIdentifier((0, 2, 2, 2, 3, 1, 0, 1))}))
        print("Output : ", (LocalSearchEngine()).process(c, "simple_mutation", {"threadId": 1}))

        assert 0


    def setUpInput(self):
        """
        """

        inputFile = "data/input/clspInst02.data"
        # inputFile = "data/input/pigment15b.dzn"
        # inputFile = "data/input/instancesWith20periods/1"
        # inputFile = "data/input/ps-200-10-80.dzn"
        # LspRuntimeMonitor.verbose = True
        inputDataReader = InputDataReader()
        inputDataInstance = inputDataReader.readInput(inputFile)

        ParameterData.instance = ParameterData()
