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
        self.elitePercentage = 0.1

    def save(self):
        """
        """
        pass