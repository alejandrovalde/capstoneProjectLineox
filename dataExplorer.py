import pandas as pd
from datetime import date

class dataLineox:

    def __init__(self):
        # Read Data
        self.df = pd.read_csv('data.csv')
        self.df['FCaducidad'] = pd.to_datetime(self.df['FCaducidad'])

        # Max and Min Frequencies for slider
        self.maxFreq = float(self.df['Frecuencia'].max())
        self.minFreq = float(self.df['Frecuencia'].min())

        # Max and Min Expiration date for slider
        self.maxDate = int((self.df['FCaducidad'].max().date()-date.today()).days)
        self.minDate = int((self.df['FCaducidad'].min().date()-date.today()).days)
        
        # Radio Links Companies
        self.companiesList = self.df['Titular'].sort_values().unique()
        
        # Comunidad list
        self.comunidadList = self.df['Comunidad'].sort_values().unique()
        
        # Localidad list
        self.localidadList = self.df['Localidad'].sort_values().unique()
        
        #Number of radio links
        self.rlnbr = len(self.df['Ref'].unique())
        
        #Number of companies
        self.compnbr = len(self.df['NIF/CIF'].unique())
        
        #Avg, number of radio links per company
        self.rlperowner = round(self.rlnbr/self.compnbr,0)
        
        # Top 10 companies
        self.top10 = self.df.groupby(by=['Titular', 'NIF/CIF'])['Ref'].count().sort_values(ascending=False).reset_index().head(10)
        self.top10 = self.top10.rename(columns={'Ref': 'Radio links number'})
        
    def createMap(self):
        pass
        