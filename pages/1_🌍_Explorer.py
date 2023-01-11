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

col1, col2, col3 = st.columns([1,1,1], gap='medium')

with col1:
    options = st.multiselect(
    'Filter RadioLink Owner',
    options = dataLineox.companiesList
    )
    st.write('You selected:', options)

with col2:
    values = st.slider(
    'Range of Frequncies',
    min_value = dataLineox.minFreq, max_value = dataLineox.maxFreq, value = (dataLineox.minFreq, dataLineox.maxFreq)
    )
    st.write('Values:', values)

with col3:
    st.write('Another Filter...')

st.metric("Radio Links", "110")