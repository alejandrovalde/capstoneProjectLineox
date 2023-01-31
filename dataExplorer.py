import pandas as pd
import numpy as np
from datetime import datetime, date

import folium
from folium.plugins import FastMarkerCluster

class dataLineox:

    def __init__(self):
        # Read Data
        self.df = pd.read_csv('data.csv')
        self.df['FCaducidad'] = pd.to_datetime(self.df['FCaducidad'])
        # Handle Expiration dates
        self.df['FCaducidad'] = self.df['FCaducidad'].fillna(datetime.now())
        self.df['Days'] = [int((x.date()-date.today()).days) for x in self.df['FCaducidad']]

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
    
    def calculateKPI(self, lfreq, hfreq, ldays, hdays, com_op, loc_op, owner_op):
        dfFiltered = self.df.loc[
            (self.df['Frecuencia'] >= lfreq) 
            & (self.df['Frecuencia'] <= hfreq) 
            & (self.df['Days'] >= ldays) 
            & (self.df['Days'] <= hdays)
            & (self.df['Comunidad'].isin(com_op))
            & (self.df['Localidad'].isin(loc_op))
            & (self.df['Titular'].isin(owner_op))
        ,:]

        #Number of radio links
        rlnbr = len(dfFiltered['Ref'].unique())
        #Number of companies
        compnbr = len(dfFiltered['NIF/CIF'].unique())
        #Avg, number of radio links per company
        try: rlperowner = round(rlnbr/compnbr)
        except: rlperowner = 0 

        return rlnbr,compnbr,rlperowner

    def topOwners(self, lfreq, hfreq, ldays, hdays, com_op, loc_op, owner_op):
        top10 = self.df.loc[
            (self.df['Frecuencia'] >= lfreq) 
            & (self.df['Frecuencia'] <= hfreq) 
            & (self.df['Days'] >= ldays) 
            & (self.df['Days'] <= hdays)
            & (self.df['Comunidad'].isin(com_op))
            & (self.df['Localidad'].isin(loc_op))
            & (self.df['Titular'].isin(owner_op))
        ,:]
        rlnbr = len(top10['Ref'].unique())
        top10 = top10.groupby(by=['Titular', 'NIF/CIF'])['Ref'].count().sort_values(ascending=False).reset_index().head(10)
        top10 = top10.rename(columns={'Ref': 'Radio links number'})
        top10['Radio links share'] = round((top10['Radio links number']/rlnbr)*100).astype(str) + '%'
        top10 = top10.set_index('Titular')

        return top10

    def createMap(self, lfreq, hfreq, ldays, hdays, com_op, loc_op, owner_op):
        df = self.df.loc[
            (self.df['Frecuencia'] >= lfreq) 
            & (self.df['Frecuencia'] <= hfreq) 
            & (self.df['Days'] >= ldays) 
            & (self.df['Days'] <= hdays)
            & (self.df['Comunidad'].isin(com_op))
            & (self.df['Localidad'].isin(loc_op))
            & (self.df['Titular'].isin(owner_op))
        ,:]
        if df.shape[0] == 0: return folium.Map(location=[40.416775, -3.703790], zoom_start=6)

        # get coordinates
        dfProvi = pd.read_csv('provincias.csv')
        df = df.groupby(['Provincia_FREQ'], as_index=False)['Ref'].count().rename(columns={'Ref': 'Provincia_Count'})
        df = pd.merge(df, dfProvi, left_on='Provincia_FREQ', right_on='provincias').drop('provincias', axis=1)

        # Create a map centered on Spain
        spain_map = folium.Map(location=[40.416775, -3.703790], zoom_start=6)
        #spain_map = folium.Map(location=[40.416775, -3.703790], zoom_start=6, tiles="Stamen Toner", control_scale=False)

        # Create a linear color map for the number of Radiolinks per Municipio, with red for low values and green for high values
        color_map = folium.LinearColormap(
            colors=['red', 'yellow', 'green'],
            vmin=df['Provincia_Count'].min(),
            vmax=df['Provincia_Count'].max()
        )
        # Add the color map to the map
        color_map.add_to(spain_map)

        # Create a layer for municipalities with the number of Radiolinks, and add it to the map
        provincias = folium.FeatureGroup(name='Provincias')
        for index, row in df.iterrows():
            folium.Circle(
                location=[row['lat'], row['long']],
                popup=f"Prvincia: {row['Provincia_FREQ']}<br>Number of Radiolinks: {row['Provincia_Count']}",
                radius=15000,
                fill=True,
                stroke=False,
                color=color_map(row['Provincia_Count']),
                fill_opacity=0.5
            ).add_to(provincias)

        provincias.add_to(spain_map)

        marker_cluster = FastMarkerCluster(
            data=df[['lat', 'long']].values.tolist(),
            popup=df.apply(lambda x: f"Provincia: {x['Provincia_FREQ']}<br>Number of Radiolinks: {x['Provincia_Count']}", axis=1).tolist()
        ).add_to(spain_map)

        return spain_map
