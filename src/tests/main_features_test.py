from LspAlgorithms.GeneticAlgorithms.Chromosome import Chromosome
from LspAlgorithms.GeneticAlgorithms.LocalSearch.LocalSearchEngine import LocalSearchEngine
from LspAlgorithms.GeneticAlgorithms.GAOperators.MutationOperator import MutationOperator
from LspAlgorithms.GeneticAlgorithms.GAOperators.CrossOverOperator import CrossOverOperator
from LspInputDataReading.LspInputDataInstance import InputDataInstance
from LspRuntimeMonitor import LspRuntimeMonitor
from LspInputDataReading.LspInputDataReader import InputDataReader
from LspAlgorithms.GeneticAlgorithms.PopInitialization.Population import Population
from LspAlgorithms.GeneticAlgorithms.PopInitialization.PopInitializer import PopInitializer
from ParameterSearch.ParameterData import ParameterData

class TestMainFeatures:
    """
    """        

    def test_mutation(self):
        """
        """

        self.setUpInput()

        # c = Chromosome.createFromIdentifier(stringIdentifier=(2, 1, 0, 1, 2))
        # c = Chromosome.createFromIdentifier(stringIdentifier=(0, 2, 2, 2, 3, 1, 0, 1))
        c = Chromosome.createFromIdentifier(stringIdentifier=(0, 2, 2, 2, 3, 1, 1, 0)) 
        # c = Chromosome.createFromIdentifier(stringIdentifier=(0, 2, 2, 2, 1, 1, 3, 0))
        print("Chromosome ", c)
        # # [2, 1, 2, 0, 1]
        LspRuntimeMonitor.mutation_strategy = "simple_mutation"
        result = (MutationOperator()).process(c)
        print("1 -- ", result, (Chromosome.createFromIdentifier(result.stringIdentifier)))

        assert 0

    
    def test_crossover(self):
        """
        """

        self.setUpInput()

        # cA, cB = Chromosome.createFromIdentifier(stringIdentifier=(2, 1, 1, 2, 0)), Chromosome.createFromIdentifier(stringIdentifier=(2, 1, 0, 1, 2))
        cA, cB = Chromosome.createFromIdentifier(stringIdentifier=(2, 0, 2, 3, 2, 1, 1, 0)), Chromosome.createFromIdentifier(stringIdentifier=(0, 2, 3, 2, 2, 1, 0, 1))
        # cA, cB = Chromosome.createFromIdentifier(stringIdentifier=(9, 5, 0, 3, 0, 8, 4, 10, 0, 4, 6, 2, 1, 1, 7)), Chromosome.createFromIdentifier(stringIdentifier=(0, 0, 4, 6, 10, 8, 7, 9, 0, 4, 5, 2, 1, 1, 3))
        # [(5, 6, 10, 8, 0, 0, 9, 7, 0, 4, 4, 2, 1, 1, 3) : 1811, (7, 2, 8, 5, 10, 9, 0, 0, 0, 4, 4, 6, 1, 1, 3) : 1857] 

        print(cA, "\n", cB, "\n -----------------------------")
        print((CrossOverOperator([cA, cB])).process())

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


    def test_localSearchPopulation(self):
        """
        """

        self.setUpInput()

        # c = Chromosome.createFromRawDNA([2, 1, 0, 2, 1])
        c, population = Chromosome.createFromRawDNA([1, 2, 2, 2, 1, 3, 0, 0]), Population([])
        # c, population = Chromosome.createFromIdentifier("36735108634444444144410748754494456471077677765131062777310822666693622666691810555996653211088261109661061512333111010101010910182821010810251292222552188881538111111913393555990000000000000000000000000000000000000000] : 82009, [36753108634444444144410748754494456471077677765131062777310822666693622666691810555996653211088261109661061512333111010101010910182821010810251292222552188881538111111913393555990000000000000000000000000000000000000000"), Population([])
        # [36735108634444444144410748754494456471077677765131062777310822666693622666691810555996653211088261109661061512333111010101010910182821010810251292222552188881538111111913393555990000000000000000000000000000000000000000] : 82009, [36753108634444444144410748754494456471077677765131062777310822666693622666691810555996653211088261109661061512333111010101010910182821010810251292222552188881538111111913393555990000000000000000000000000000000000000000]
        print(c)
        (LocalSearchEngine()).populate(c, [0, population])
        print(population)

        assert 0


    def test_evaluateDnaArray(self):
        """
        """

        self.setUpInput()

        chromosome = Chromosome.createFromIdentifier(stringIdentifier=(10, 0, 0, 0, 9, 8, 7, 6, 5, 4, 4, 2, 1, 1, 3))
        print(Chromosome.evaluateDnaArray(chromosome.dnaArray))

        assert 0


    def test_localSearch(self):
        """
        """

        self.setUpInput()

        c = Chromosome.createFromIdentifier("11222300")
        print(c)
        print((LocalSearchEngine()).process(c, "positive_mutation"))

        assert 0


    def setUpInput(self):
        """
        """ 

        inputFile = "data/input/clspInst02.data"
        # inputFile = "data/input/pigment15b.dzn"
        # inputFile = "data/input/ps-200-10-80.dzn"
        LspRuntimeMonitor.verbose = True
        inputDataReader = InputDataReader()
        inputDataInstance = inputDataReader.readInput(inputFile)

        ParameterData.instance = ParameterData()

