import streamlit as st

st.set_page_config(
    page_title="Lineox",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

col1, col2 = st.columns([3, 1])

with col1:
    st.title('Lineox Radio Links')
    st.header('Acquisition Strategy')
    st.markdown('''
    The aim of this project is to help Lineox collect data of the Radiolinks market in Spain to use in their company's acquision strategy
    \n
    The tool is structured in:
    1. `Data Explorer Dashboard`
    - Dashboard to visualize and filter scrapped data from the Spanish Government's Database - "Registro Público de Concesiones".
    - A "csv" file containing the entire database can be downloaded.
    \n
    Link to Database: https://sedeaplicaciones.minetur.gob.es/RPC_Consulta/FrmConsulta.aspx
    
    2. `Acquisition Scenario`
    - The user inputs a series of variables in order to simulate the financials (Cash Flow) of a company's acquisition scenario.
    ''')
    st.caption('''
    Built by: Alejandro, Alvaro, Manon, Mishari, and Sahana
    ''')

with col2:
    st.header('')
    st.image('assets/logoLineox.jpeg')
    st.header('')
    st.image('assets/ieLogo.png')