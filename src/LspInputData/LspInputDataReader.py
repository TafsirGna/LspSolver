#!/usr/bin/python3.5
# -*-coding: utf-8 -*

from .LspInputDataInstance import InputDataInstance

class InputDataReader:

    """ Object designed to read different types of input data files and output an instance of the read data
    """

    fileFormatReadingFunctions = []
    format0KeyValueSeparator = " = "
    format0EndOfLineChar = ";"

    def __init__(self):

        self.fileFormatReadingFunctions = [self.useFormat0, self.useFormat1]

        pass

    def getInputFileFormat(self, file):

        f = open(file, "r")
        firstLine = f.readline()
        index = 0 if "Periods" in firstLine else 1
        f.close() 

        return index

    def useFormat0(self, file):

        # Input data's initialization 

        tab = []
        # Here's the first way of reading that i apply to the input file, if it doesn't work, i'm gonna try a second way of reading using another format
        with open(file, 'rt') as fileContent:
            data = ""
            for line in fileContent:
                if self.format0KeyValueSeparator in line:
                    if len(data):
                        value = (data.split(self.format0KeyValueSeparator)[1]).split(self.format0EndOfLineChar)[0]
                        tab.append(value)
                        data = ""
                data = data + line

            value = (data.split(self.format0KeyValueSeparator)[1]).split(self.format0EndOfLineChar)[0]
            tab.append(value)

        tab[3] = tab[3][1:-1]
        tab[3] = tab[3].split(",")
        j = 0
        for c in tab[3]:
            tab[3][j] = int(c)
            j += 1

        for a in [2,4]:

            tab[a] = tab[a].replace('\t', '')
            tab[a] = tab[a].replace('\n', '')
            tab[a] = (tab[a].split('|'))[1:-1]
            i = 0
            for item in tab[a]:
                tmp = (item.strip()).split(',')
                j = 0
                for c in tmp:
                    tmp[j] = int(c)
                    j += 1
                tab[a][i] = tmp
                i += 1

        return InputDataInstance(tab[0], tab[1], tab[2], tab[3], tab[4])


    def useFormat1(self, file):

        # Input data's initialization 
        nbItems = 0
        nbTimes = 0
        demandsGrid = []
        holdingGrid = []
        chanOverGrid = []

        with open(file, 'rt') as instance:

            i = 1
            for line in instance:
                
                if i == 1:
                    nbTimes = int(line)

                if i == 2:
                    nbItems = int(line)

                if i >= 5 and i < (5 + nbItems):
                    data = []
                    data = line.split(" ")
                    chanOverGrid.append(data)

                if i == (5 + nbItems + 1):
                    holdingGrid = line.split(" ")

                if i >= (5 + nbItems + 3) and i < (5 + nbItems*2 + 3):
                    data = []
                    data = line.split(" ")
                    demandsGrid.append(data)

                i += 1

            if nbItems != 0 and nbTimes != 0 and demandsGrid != [] and holdingGrid != [] and chanOverGrid != []:
                return InputDataInstance(nbItems,nbTimes,demandsGrid,holdingGrid,chanOverGrid)
            return 0

    def getReadingFunction(self, file):
        """
        """

        fileFormatIndex = self.getInputFileFormat(file)
        return self.fileFormatReadingFunctions[fileFormatIndex]
            
    def readInput(self, file):
        """
        """

        readFile = self.getReadingFunction(file)
        return readFile(file)
