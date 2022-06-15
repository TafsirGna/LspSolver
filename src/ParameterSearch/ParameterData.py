#!/usr/bin/python3.5
# -*-coding: utf-8 -*

class ParameterData:
    """
    """
    instance = None

    def __init__(self) -> None:
        """
        """

        self.popSize = 50
        self.mutationRate = 0.05
        self.crossOverRate = 0.8
        self.elitePercentage = 0.01
        self.nReplicaThreads = 2
        self.nPrimaryThreads = 1
        self.nMigrants = 1
        self.popUniquesPercentage25 = 0.25
        self.popUniquesPercentage50 = 0.5
        self.popUniquesPercentage10 = 0.1
        self.simpleMutationDepthIndex = 1
        self.nReplicaSubThreads = 2
        self.nIdleGenerations = 5
        self.localSearchTriggerSize = 0.1
        self.nInitPopLocalOptima = 3

    def save(self):
        """
        """

        pass
