import pandas as pd

class dataLineox:

    def __init__(self):
        # Read Data
        self.df = pd.read_csv('data.csv')

        # Max and Min Frequencies for slider
        self.maxFreq = float(self.df['Frecuencia'].max())
        self.minFreq = float(self.df['Frecuencia'].min())

        # Radio Links Companies
        self.companiesList = self.df['Titular'].sort_values().unique()

    def createMap(self):
        pass