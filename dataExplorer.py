import pandas as pd
import numpy as np
import numpy_financial as nf
from datetime import datetime, date
import plotly.express as px

import folium
from dataEntries import formulaParameters

class dataLineox:

    def __init__(self):
        # Read Data
        self.df = pd.read_csv('data.csv')
        self.df['FCaducidad'] = pd.to_datetime(self.df['FCaducidad'])
        # Handle Expiration dates
        self.df['FCaducidad'] = self.df['FCaducidad'].fillna(datetime.now())
        self.df['Days'] = [int((x.date()-date.today()).days) for x in self.df['FCaducidad']]

        # Max and Min Number of Radiolinks
        self.maxRadioLinks = int(self.df.groupby(by=['NIF/CIF'])['Ref'].count().max())
        self.minRadioLinks = int(self.df.groupby(by=['NIF/CIF'])['Ref'].count().min())

        # Max and Min Frequencies for slider
        self.maxFreq = float(self.df['Frecuencia'].max())
        self.minFreq = float(self.df['Frecuencia'].min())
        
        # Categories of frequencies for filter
        self.freqList = {
            '<3GHz':[0,3], 
            '3-10GHz':[3,10], 
            '10-13GHz':[10,13], 
            '13-23.5GHz':[13,23.5], 
            '23.5-27.5GHz':[23.5,27.5], 
            '27.5-39.5GHz':[27.5,39.5], 
            '39.5-64GHz':[39.5,64],
            '>64GHz':[64,100000000]
        }

        # Max and Min Expiration date for slider
        self.maxDate = int((self.df['FCaducidad'].max().date()-date.today()).days)
        self.minDate = int((self.df['FCaducidad'].min().date()-date.today()).days)
        
        # Radio Links Companies
        self.companiesList = self.df['Titular'].sort_values().unique()
        
        # Provincia list
        self.provinciaList = self.df['Provincia_FREQ'].sort_values().unique()
        
        # Municipio list
        self.municipioList = self.df['Municipio'].sort_values().unique()

        # tax formula parameters
        self.taxFormulaParameters = formulaParameters
    
    ### Methods for Explorer

    def filterDf(self, freq_op, ldays, hdays, prov_op, mun_op, owner_op, lnumRadio, hnumRadio):
        # Filter for number of radiolinks per company
        radiolinksOwned = self.df.groupby('Titular', as_index=False)['Ref'].count()
        ownersFiltered = radiolinksOwned.loc[(radiolinksOwned['Ref'] <= hnumRadio) & (radiolinksOwned['Ref'] >= lnumRadio), 'Titular']

        dfFiltered = self.df.loc[
            (self.df['FrequencyBand'].isin(freq_op))  
            & (self.df['Days'] >= ldays) 
            & (self.df['Days'] <= hdays)
            & (self.df['Provincia_FREQ'].isin(prov_op))
            & (self.df['Municipio'].isin(mun_op))
            & (self.df['Titular'].isin(owner_op))
            & (self.df['Titular'].isin(ownersFiltered))
        ,:]
        return dfFiltered
    
    def calculateKPI(self, freq_op, ldays, hdays, prov_op, mun_op, owner_op, lnumRadio, hnumRadio):
        df = self.filterDf(freq_op, ldays, hdays, prov_op, mun_op, owner_op, lnumRadio, hnumRadio)
        #Number of radio links - num rows
        rlnbr = df.shape[0]
        #Number of companies
        compnbr = len(df['NIF/CIF'].unique())
        #Avg, number of radio links per company
        try: rlperowner = round(rlnbr/compnbr)
        except: rlperowner = 0 

        return rlnbr,compnbr,rlperowner

    def topOwners(self, freq_op, ldays, hdays, prov_op, mun_op, owner_op, lnumRadio, hnumRadio):
        df = self.filterDf(freq_op, ldays, hdays, prov_op, mun_op, owner_op, lnumRadio, hnumRadio)

        rlnbr = df.shape[0]
        df = df.groupby(by=['Titular', 'NIF/CIF'])['Ref'].count().sort_values(ascending=False).reset_index()
        df = df.rename(columns={'Ref': 'Radio links number'})
        df['Radio links share'] = round((df['Radio links number']/rlnbr)*100).astype(str) + '%'

        return df

    def createBarplot(self, freq_op, ldays, hdays, prov_op, mun_op, owner_op, lnumRadio, hnumRadio):
        df = self.filterDf(freq_op, ldays, hdays, prov_op, mun_op, owner_op, lnumRadio, hnumRadio)
        
        aggr = df.groupby(by = ['Provincia_FREQ', 'FrequencyBand'], as_index=False)['Ref'].count()
        aggr = aggr.rename(columns={'Provincia_FREQ':"Provincia", 'Ref': 'Number of radio links'})

        orderProv = list(df.groupby(['Provincia_FREQ'])['Ref'].count().sort_values(ascending=False).index)

        cat = {
            'FrequencyBand': list(self.freqList.keys()),
            'Provincia': orderProv
        }
        
        barplot = px.bar(aggr, x='Provincia', y='Number of radio links', color='FrequencyBand', height=500, color_discrete_sequence=px.colors.qualitative.Prism, category_orders=cat)
        barplot.update_layout(legend=dict(orientation="h",y= 1.2))
        return barplot
    
    def createPieChart(self, freq_op, ldays, hdays, prov_op, mun_op, owner_op, lnumRadio, hnumRadio):
        df = self.filterDf(freq_op, ldays, hdays, prov_op, mun_op, owner_op, lnumRadio, hnumRadio)
        
        df = df.groupby(pd.cut(df['Days'],[-np.inf, 365, 730, 1095, 1460, np.inf], labels=['0-1y','1-2y','2-3y','3-4y','>4y']))['Ref'].count().reset_index()
        df['Data'] = 'Data'
        df = df.rename({'Ref':'Count', 'Days':'Time'}, axis=1)
        
        order = {'Time': ['0-6m','6m-1y','1y-2y','>2y']}

        plot = px.pie(df, values='Count', names='Time', category_orders=order, height=270, color_discrete_sequence=px.colors.qualitative.Prism)
        plot.update_layout(legend=dict(orientation="h",y= 1.6))
        return plot
    
    def createMap(self, freq_op, ldays, hdays, prov_op, mun_op, owner_op, lnumRadio, hnumRadio):
        df = self.filterDf(freq_op, ldays, hdays, prov_op, mun_op, owner_op, lnumRadio, hnumRadio)
        if df.shape[0] == 0: return folium.Map(location=[40.416775, -3.703790], zoom_start=6)

        # get coordinates
        dfProvi = pd.read_csv('provincias.csv')
        df = df.groupby(['Provincia_FREQ'], as_index=False)['Ref'].count().rename(columns={'Ref': 'Provincia_Count'})
        df = pd.merge(df, dfProvi, left_on='Provincia_FREQ', right_on='provincias').drop('provincias', axis=1)

        # Create a map centered on Spain
        spain_map = folium.Map(location=[40.416775, -3.703790], zoom_start=6)

        # Create a linear color map for the number of Radiolinks per Municipio, with red for low values and green for high values
        color_map = folium.LinearColormap(
            colors=['red', 'yellow', 'green'],
            vmin=df['Provincia_Count'].min(),
            vmax=df['Provincia_Count'].max(),
        )
        # Add the color map to the map
        color_map.add_to(spain_map)

        # Create a layer for municipalities with the number of Radiolinks, and add it to the map
        provincias = folium.FeatureGroup(name='Provincias')
        for index, row in df.iterrows():
            folium.Circle(
                location=[row['lat'], row['long']],
                popup=f"Provincia: {row['Provincia_FREQ']} \n Radiolinks: {row['Provincia_Count']}",
                radius=25000,
                fill=True,
                stroke=False,
                color=color_map(row['Provincia_Count']),
                fill_opacity=0.8
            ).add_to(provincias)

        provincias.add_to(spain_map)

        return spain_map


    ### Methods for Acquisition Scenario

    def numRadioLinks(self, owner_op, freqExemptedRange):
        radiolinksOwned = self.df.loc[self.df['Titular'] == owner_op, :].shape[0]
        radiolinksOwnedLineoxFreq = self.df.loc[
            (self.df['Titular'] == owner_op)
            & (self.df['Frecuencia'] >= freqExemptedRange[0]) 
            & (self.df['Frecuencia'] <= freqExemptedRange[1]) 
        , :].shape[0]
        return radiolinksOwned, radiolinksOwnedLineoxFreq

    def tableFees(self, owner_op, freqExemptedRange):
        bins = [float(i.split('-')[0]) for i in self.taxFormulaParameters.keys()]+[np.inf]
        labels=list(self.taxFormulaParameters.keys())
        dfNotOwned = self.df.loc[
            (self.df['Titular'] == owner_op)
            & 
            ( (self.df['Frecuencia'] < freqExemptedRange[0]) | (self.df['Frecuencia'] > freqExemptedRange[1]) ) 
        , :].groupby(pd.cut(self.df['Frecuencia'],bins,labels=labels)).apply(lambda x: pd.Series({
            'Num RL': x['Frecuencia'].count(), 
            'Num Freq.': x['Frecuencia'].nunique(), 
        })) 
        dfNotOwned.index = dfNotOwned.index.rename('Range')
        dfNotOwned = dfNotOwned.reset_index()
        dfNotOwned['Fees'] = dfNotOwned.apply(lambda x: x['Num Freq.'] * self.taxFormulaParameters[x['Range']]['B'] * self.taxFormulaParameters[x['Range']]['S'] * np.prod(self.taxFormulaParameters[x['Range']]['C']) / 166.386 , axis=1)
        dfNotOwned['Fees'] = dfNotOwned['Fees'].round(0)
        dfNotOwned['Migrate'] = ['No'] * len(labels)
        return dfNotOwned
    
### Other functions for Acquisiton Scenario

def generateCashFlow(radioLinksOwned, periodsList, dfMigratedData, dfInitialUpdatedData, costs):
    dfInitialUpdated = pd.DataFrame(dfInitialUpdatedData).set_index('index')
    dfMigrated = pd.DataFrame(dfMigratedData)
    df = pd.DataFrame(columns=periodsList)
    # Get balance of Add/Churned Number of Radiolinks for each period
    addChurned = [0] + [y - x for x, y in zip(dfInitialUpdated.loc['Active RadioLinks',:].values, dfInitialUpdated.loc['Active RadioLinks',:].values[1:])]
    ### Revenues
    df.loc['REVENUES',:] = [None] * len(periodsList)
    df.loc['Service Revenue',:] = dfInitialUpdated.loc['Active RadioLinks',:].values * dfInitialUpdated.loc['Monthly Fee',:].values * 12
    df.loc['Relocation Radiolinks',:] = dfInitialUpdated.loc['Active RadioLinks',:].values * dfInitialUpdated.loc['% Relocated',:].values/100 * costs['setUpCost']
    ### OPEX
    df.loc['OPEX',:] = [None] * len(periodsList)
    df.loc['Operations & Maintenance',:] = - dfInitialUpdated.loc['Active RadioLinks',:].values * costs['opsMaintAnnual']
    df.loc['IT Costs',:] = - costs['itTotalAnnual']
    yearlyFees = dfMigrated.loc[dfMigrated['Migrate'] == 'No', 'Fees'].sum()
    df.loc['Spectrum Licence',:] = [- yearlyFees] * len(periodsList)
    df.loc['Other Costs',:] = - df.loc['Service Revenue',:].values * costs['otherCostsPct']/100
    ### CAPEX
    df.loc['CAPEX',:] = [None] * len(periodsList)
    df.loc['Acquisition Costs',:] = [- costs['upfrontOffer']*radioLinksOwned] + [0]*(len(periodsList)-1)
    radiolinksMigrated = dfMigrated.loc[dfMigrated['Migrate'] != 'No', 'Num RL'].sum()
    df.loc['Outside Band Transfer',:] = [-costs['bandTransfer']*radiolinksMigrated] + [0]*(len(periodsList)-1)
    df.loc['Churned Radiolinks',:] = [ i*costs['costChurned'] if i < 0 else 0 for i in addChurned ]
    df.loc['IT SetUp',:] = [- costs['itSetUpCapex']] + [0]*(len(periodsList)-1)

    ## UPDATE INFLATION
    for colid in range(len(periodsList)-1):
        inf = dfInitialUpdated.loc['% Inflation',:].values[colid]
        df.iloc[df.index.get_loc('Operations & Maintenance'), colid+1] = df.iloc[df.index.get_loc('Operations & Maintenance'), colid] * (1+inf/100)
        df.iloc[df.index.get_loc('IT Costs'), colid+1] = df.iloc[df.index.get_loc('IT Costs'), colid] * (1+inf/100)
        df.iloc[df.index.get_loc('Spectrum Licence'), colid+1] = df.iloc[df.index.get_loc('Spectrum Licence'), colid] * (1+inf/100)

    ### TOTAL
    df.loc['TOTAL',:] = [None] * len(periodsList)
    
    ### EBITDA MARGIN
    revenues = df.loc['Service Revenue',:] + df.loc['Relocation Radiolinks',:]
    opex = df.loc['Operations & Maintenance',:] + df.loc['IT Costs',:] + df.loc['Other Costs',:] + df.loc['Spectrum Licence',:]
    df.loc['EBITDA MARGIN',:] = (revenues + opex)*100/revenues
    df.loc['EBITDA MARGIN',:] = df.loc['EBITDA MARGIN',:].astype(float).apply(lambda x: f"{round(x,2)}%")

    df.loc['Cash Flow',:] = df.loc[~df.index.isin(['EBITDA MARGIN']), :].sum()
    df.loc[~df.index.isin(['EBITDA MARGIN']), :] = df.loc[~df.index.isin(['EBITDA MARGIN']), :].astype(float).round(2)

    for row in df.index.to_list():
        if row not in ['REVENUES','OPEX','CAPEX','EBITDA MARGIN','TOTAL']:
            df.loc[row,:] = df.loc[row,:].map("{:,}".format)
    return df.reset_index()

def calculateFinancials(cashFlowData, discountRate):
    df = pd.DataFrame(cashFlowData).set_index('index')
    npv = nf.npv(discountRate/100, df.loc['Cash Flow',:].str.replace(',', '').astype(float).values)
    irr = nf.irr(df.loc['Cash Flow',:].str.replace(',', '').astype(float).values)
    return npv, irr
