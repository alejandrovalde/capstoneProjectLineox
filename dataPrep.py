import pandas as pd

df = pd.read_csv('rl_data.csv', dtype='object')

# Fill NaN wih previous value for "Provincia_FREQ" and "Municipio"
df['Provincia_FREQ'] = df['Provincia_FREQ'].fillna(method='ffill')
df['Municipio'] = df['Municipio'].fillna(method='ffill')

# "Frecuencia" to float
df['Frecuencia'] = df['Frecuencia'].str.replace(",",".")
df['Frecuencia'] = df['Frecuencia'].astype('float')

#Put all frequencies in MhZ
df.loc[df['Unit'] == 'MHz', 'Frecuencia'] = df['Frecuencia']/1000
df['Unit'] = 'GHz'

# "Dates" to DateTime
df['FConcesion'] = pd.to_datetime(df['FConcesion'], format="%d/%m/%Y", errors='coerce')
df['FCaducidad'] = pd.to_datetime(df['FCaducidad'], format="%d/%m/%Y", errors='coerce')

# Features to homogenize
cols = ['Titular','DomicilioSocial','Localidad','Provincia_RL','CP']

for col in cols:
    # Group by NIF/CIF and "Feature". Sort by count of ocurrences (descending) to get the most used value of that feature for that ID.
    dfGrouped = df.groupby(['NIF/CIF',col], as_index=False)['Ref'].count().sort_values(by=['NIF/CIF','Ref'], ascending=[True,False])

    uniqueValues = {}
    # For each row. If it's different to the previous: take it. Otherwise, go to the next.
    for i,r in dfGrouped.iterrows():
        if i == 0: 
            uniqueValues[r['NIF/CIF']] = r[col]
            prev = r['NIF/CIF']
        else:
            if r['NIF/CIF'] != prev:
                uniqueValues[r['NIF/CIF']] = r[col]
                prev = r['NIF/CIF']
            else: prev = r['NIF/CIF']
    
    # Replace all values of that Feature for each ID with the unique value chosen.
    df[col] = df['NIF/CIF'].replace(uniqueValues)

cut_labels = ['<3GHz', '3-10GHz', '10-13GHz', '13-23.5GHz', '23.5-27.5GHz', '27.5-39.5GHz', '39.5-64GHz','>64GHz']
cut_bins = [0, 3, 10, 13, 23.5, 27.5, 39.5, 64, 10000000]
df['FrequencyBand'] = pd.cut(df['Frecuencia'], bins=cut_bins, labels=cut_labels)

df.to_csv('data.csv',index=False)