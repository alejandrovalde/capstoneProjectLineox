import streamlit as st
from dataExplorer import dataLineox
from datetime import datetime
from datetime import date

dataLineox = dataLineox()

st.set_page_config(
    page_title="Lineox",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.header("Data Explorer")

#Cache the dataset csv
@st.cache
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')
csv = convert_df(dataLineox.df)

# SECTION 1: COUNTRY-LEVEL METRICS

st.subheader("Country level metrics")
col1, col2 = st.columns([1,3], gap='small')

with col1:    
    st.markdown("""<span style='color:#00008B'>**Metrics**</span>""",unsafe_allow_html=True)
    st.download_button(label="Download raw data as CSV", data=csv, file_name='ESradiolinks.csv', mime='text/csv',)
    st.metric("Radio links", dataLineox.rlnbr)
    st.metric("Companies", dataLineox.compnbr)
    st.metric("Avg. number of radio links per company", dataLineox.rlperowner)
    
with col2:
    st.markdown("""<span style='color:#00008B'>**Top 10 companies**</span>""",unsafe_allow_html=True)
    st.table(data = dataLineox.top10) 

st.image('banner.png', use_column_width='never')

# SECTION 2: FILTERING

st.subheader("Drilling down")

st.markdown("""<span style='color:#00008B'>**FILTERS**</span>""",unsafe_allow_html=True)
col1, col2 = st.columns([1,1], gap='medium')

with col1:
    with st.expander("Comunidad filter"):
        container = st.container()
        all = st.checkbox("Select all", key='comunidad')
        if all:
            com_op = container.multiselect("Filter Comunidad", dataLineox.comunidadList, default=dataLineox.comunidadList)
        else:
            com_op =  container.multiselect("Filter Comunidad", dataLineox.comunidadList)

    with st.expander("Localidad filter"):
        container = st.container()
        all = st.checkbox("Select all", key='localidad')
        if all:
            loc_op = container.multiselect("Filter Localidad", dataLineox.localidadList, dataLineox.localidadList)
        else:
            loc_op =  container.multiselect("Filter Localidad", dataLineox.localidadList)
        
    with st.expander("Company filter"):
        container = st.container()
        all = st.checkbox("Select all", key='company')
        if all:
            owner_op = container.multiselect("Filter Company", dataLineox.companiesList, dataLineox.companiesList)
        else:
            owner_op =  container.multiselect("Filter Company", dataLineox.companiesList)

with col2:
    lfreq, hfreq = st.slider(
    'Range of Frequencies',
    min_value = dataLineox.minFreq, max_value = dataLineox.maxFreq, value = (dataLineox.minFreq, dataLineox.maxFreq)
    )
    st.write('You selected between', lfreq, 'and', hfreq)
    
    ldays, hdays = st.slider(
    'Days until contract expiration',
    min_value = dataLineox.minDate, max_value = dataLineox.maxDate, value = (dataLineox.minDate, dataLineox.maxDate)
    )
    st.write('You selected between', ldays, 'and', hdays)
    

# Metrics 
col1, col2 = st.columns([1,3], gap='small')

table = dataLineox.df.copy(deep=True)
table['FCaducidad'] = table['FCaducidad'].fillna(datetime.now())
table['Days'] = [int((x.date()-date.today()).days) for x in table['FCaducidad']]
table = table[
        (table['Frecuencia'] >= lfreq) & (table['Frecuencia'] <= hfreq) 
        & (table['Days'] >= ldays) & (table['Days'] <= hdays)
        & (table['Comunidad'].isin(com_op))
        & (table['Localidad'].isin(loc_op))
        & (table['Titular'].isin(owner_op))
        ]

with col1:
    st.markdown("""<span style='color:#00008B'>**Metrics**</span>""",unsafe_allow_html=True)
    st.metric("Radio links", len(table['Ref'].unique()))
    st.metric("Companies", len(table['NIF/CIF'].unique()))
    st.metric("Avg. number of radio links per company", round(len(table['Ref'].unique())/len(table['NIF/CIF'].unique())))
            
#Radio links top 10 table
top = dataLineox.df.groupby(by=['Titular','NIF/CIF','Comunidad','Localidad','Frecuencia','FCaducidad'])['Ref'].count().sort_values(ascending=False).reset_index()
top['Days'] = [int((x.date()-date.today()).days) for x in top['FCaducidad']]
top = top.rename(columns={'Ref': 'Radio links number'})

with col2:

    st.markdown("""<span style='color:#00008B'>**Top 10 radio links groups**</span>""",unsafe_allow_html=True)

    top = dataLineox.df.groupby(by=['Titular','NIF/CIF','Comunidad','Localidad','Frecuencia','FCaducidad'])['Ref'].count().sort_values(ascending=False).reset_index()
    top['Days'] = [int((x.date()-date.today()).days) for x in top['FCaducidad']]
    top = top.rename(columns={'Ref': 'Radio links number'})

    st.table(data = top.loc[
        (top['Frecuencia'] >= lfreq) & (top['Frecuencia'] <= hfreq) 
        & (top['Days'] >= ldays) & (top['Days'] <= hdays)
        & (top['Comunidad'].isin(com_op))
        & (top['Localidad'].isin(loc_op))
        & (top['Titular'].isin(owner_op))
        ,['Titular','NIF/CIF','Frecuencia','Days','Radio links number']].head(10).set_index('Titular')
        )

#Full dataset table
st.markdown("""<span style='color:#00008B'>**Full dataset**</span>""",unsafe_allow_html=True)

with st.expander("Radio links full dataset"):
    st.table(data = top[['Titular','NIF/CIF','Frecuencia','Days','Radio links number']])


