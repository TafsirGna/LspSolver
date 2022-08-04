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
        # self.mutationRate = 0.05
        self.crossOverRate = 0.8
        # self.elitePercentage = 0.01
        self.nReplicaThreads = 1
        self.nPrimaryThreads = 1
        # self.nMigrants = 1
        self.maxSimpleMutationDepthIndex = 1
        self.nReplicaSubThreads = 1
        self.nIdleGenerations = 5


    def save(self):
        """
        """

        pass
