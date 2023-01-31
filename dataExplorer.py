import pandas as pd
import numpy as np
from datetime import date

#!!pip install geopy
#!!pip install folium
from geopy.geocoders import Nominatim
import folium
from folium.plugins import FastMarkerCluster

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
        self.rlperowner = round(self.rlnbr/self.compnbr)
        
        # Top 10 companies
        self.top10 = self.df.groupby(by=['Titular', 'NIF/CIF'])['Ref'].count().sort_values(ascending=False).reset_index().head(10)
        self.top10 = self.top10.rename(columns={'Ref': 'Radio links number'})
        self.top10['Radio links share'] = round((self.top10['Radio links number']/self.rlnbr)*100).astype(str) + '%'
        self.top10.set_index('Titular', inplace=True)
        
        # Map
        self.spain_map = None
        
    def createMap(self):
        # Read Data
        self.data = pd.read_csv('data.csv')
        
        def get_coordinates(city):
            geolocator = Nominatim(user_agent="spain_explorer")
            location = geolocator.geocode(city) 
            latitude = location.latitude
            longitude = location.longitude
            return latitude, longitude

        # Take a 100 sample of df
        self.df_sample = self.data.sample(100) 
        
        # Create a new dataframe with the coordinates
        self.df_sample['Latitude'], self.df_sample['Longitude'] = zip(*self.df_sample.apply(lambda x: get_coordinates(x['Provincia_FREQ']), axis=1))
        self.df_sample['Num_Radiolinks'] = 1 # Create a column 'Num_Radiolinks'
        # Create df giving the number of radio links per Municipio
        self.df_agg = self.df_sample.groupby(['Provincia_FREQ'])['Num_Radiolinks'].sum().reset_index() # Aggregate by 'Municipio' and sum the 'Num_Radiolinks' column
        self.df_agg.rename(columns={'Num_Radiolinks': 'Municipio_Count'}, inplace=True) # Rename the column 'Num_Radiolinks' to the desired name
        self.df_sample = pd.merge(self.df_sample, self.df_agg, on='Provincia_FREQ') # add the 'Municipio_Count' from df_agg to the df_sample joining by 'Municipio'

        #Assign color to each Titular and put it in a column in the df
        def assign_color(df):
            color_map = {}
            unique_titulars = set(self.df_sample['Titular']) # Create a set of unique values for the 'Titular' column
            for i, titular in enumerate(unique_titulars): # Assign a unique color to each unique value
                color_map[titular] = 'hsl({}, 50%, 50%)'.format(i * 360 / len(unique_titulars)) # Colors must be very distinct to be easily distinguishable
            self.df_sample['Color'] = self.df_sample['Titular'].apply(lambda x: color_map[x]) # Add a new column to the dataframe called 'Color'
            return self.df_sample
        self.df_sample = assign_color(self.df_sample)
        
        # Create a map centered on Spain
        self.spain_map = folium.Map(location=[40.416775, -3.703790], zoom_start=6)
        # Create a linear color map
        color_map = folium.LinearColormap(
            colors=['red', 'yellow', 'green'],
            vmin=self.df_sample['Municipio_Count'].min(),
            vmax=self.df_sample['Municipio_Count'].max())
        # Create a layer for municipalities with the number of Radiolinks
        municipalities = folium.FeatureGroup(name='Municipalities')
        for index, row in self.df_sample.iterrows():
            folium.Circle(
                location=[row['Latitude'], row['Longitude']],
                popup=f"Municipality: {row['Provincia_FREQ']}<br>Number of Radiolinks: {row['Municipio_Count']}",
                radius=30000,
                fill=True,
                stroke=False,
                color=color_map(row['Municipio_Count']),
                fill_opacity=0.5
            ).add_to(municipalities)
        municipalities.add_to(self.spain_map)

        # Add the color map to the map
        color_map.add_to(self.spain_map)

        # Create a layer for the top 3 companies per municipality
        companies = folium.FeatureGroup(name='Top 3 companies per municipality')
        self.df_companies = self.df_sample.groupby(['Provincia_FREQ', 'Titular']).sum().reset_index()
        self.df_companies = self.df_companies.sort_values(by=['Provincia_FREQ','Municipio_Count'], ascending=[True,False])
        self.df_companies = self.df_companies.groupby('Provincia_FREQ').head(3)

        # add the 'Color' column to df_companies joining by 'Titular'
        self.df_companies = pd.merge(self.df_companies, self.df_sample[['Titular', 'Color']], on='Titular')

        for index, row in self.df_companies.iterrows():
            folium.CircleMarker(
                location=[row['Latitude'], row['Longitude']],
                popup=f"Municipality: {row['Provincia_FREQ']}<br>Company: {row['Titular']}<br>Number of Radiolinks: {row['Municipio_Count']}",
                radius=5,
                fill=True,
                stroke=False,
                fill_color=row['Color'],
                fillOpacity=0.8
            ).add_to(companies)
        companies.add_to(self.spain_map)

        # Add the layer control
        folium.LayerControl().add_to(self.spain_map)
        
        return self.spain_map
        