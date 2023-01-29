import streamlit as st
from dataExplorer import dataLineox

dataLineox = dataLineox()

st.set_page_config(
    page_title="Lineox",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.header('Data Explorer')

st.metric("Radio Links", dataLineox.rlnbr)
st.metric("Companies", dataLineox.compnbr)
st.metric("Avg. number of radio links per company", dataLineox.rlperowner)

col1, col2, col3 = st.columns([1,1,1], gap='medium')

with col1:
    options = st.multiselect(
    'Filter Communidad',
    options = dataLineox.comunidadList
    )
    st.write('You selected:', options)

    options = st.multiselect(
    'Filter Localidad',
    options = dataLineox.localidadList
    )
    st.write('You selected:', options)
    
with col2:
    values = st.slider(
    'Range of Frequencies',
    min_value = dataLineox.minFreq, max_value = dataLineox.maxFreq, value = (dataLineox.minFreq, dataLineox.maxFreq)
    )
    st.write('Values:', values)
    
    values = st.slider(
    'Days until contract expiration',
    min_value = dataLineox.minDate, max_value = dataLineox.maxDate, value = (dataLineox.minDate, dataLineox.maxDate)
    )
    st.write('Values:', values)

with col3:
    options = st.multiselect(
    'Filter RadioLink Owner',
    options = dataLineox.companiesList
    )
    st.write('You selected:', options)
    
st.table(data=dataLineox.top10)



