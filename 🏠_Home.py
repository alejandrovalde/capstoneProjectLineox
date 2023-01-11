import streamlit as st

st.set_page_config(
    page_title="Lineox",
    page_icon="📡",
    #layout="wide",
    initial_sidebar_state="collapsed",
)

col1, col2 = st.columns([3, 1])

with col1:
    st.title('Lineox Radio Links')
    st.header('Acquisition Strategy')
    st.markdown('''
    This project is **really cool**...
    \n
    The project is structured in:
    1. `Explorer`
    2. `Recommender`
    ''')
    st.caption('''
    Built by: Alejandro, Alvaro, Manon, Mishari, and Sahana
    ''')

with col2:
    st.header('')
    st.image('logoLineox.jpeg')
    st.header('')
    st.image('ieLogo.png')