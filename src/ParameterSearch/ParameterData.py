#!/usr/bin/python3.5
# -*-coding: utf-8 -*

class ParameterData:
    """
    """
    instance = None

    def __init__(self) -> None:
        """
        """
        self.popSize = 30
        self.mutationRate = 0.05
        self.crossOverRate = 0.8
        self.elitePercentage = 0.01
        self.nReplicaThreads = 3
        self.nPrimaryThreads = 1
        self.nMigrants = 1
        self.popUniquesPercentage25 = 0.25
        self.popUniquesPercentage10 = 0.10
        self.simpleMutationDepthIndex = 1

    def save(self):
        """
        """
        pass