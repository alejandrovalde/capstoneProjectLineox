import streamlit as st
from streamlit_folium import st_folium
from dataExplorer import dataLineox

st.set_page_config(
    page_title="Lineox",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Cache entire class
#@st.cache
def getClass():
    return dataLineox()
dataLineox = getClass()

st.header("Data Explorer")

#Filters
st.markdown("""<span style='color:#00008B'>**FILTERS**</span>""",unsafe_allow_html=True)
col1, col2 = st.columns([1,1], gap='medium')

with col1:
    with st.expander("Provincia Filter"):
        container = st.container()
        all = st.checkbox("Select all", value = True, key='1')
        if all:
            prov_op = dataLineox.provinciaList
        else:
            prov_op =  container.multiselect(" ", dataLineox.provinciaList, key='provincia')

    with st.expander("Municipio Filter"):
        container = st.container()
        all = st.checkbox("Select all", value = True, key='2')
        if all:
            mun_op = dataLineox.municipioList
        else:
            mun_op =  container.multiselect(" ", dataLineox.municipioList, key='municipio')
        
    with st.expander("Company Filter"):
        container = st.container()
        all = st.checkbox("Select all", value = True, key='3')
        if all:
            owner_op = dataLineox.companiesList
        else:
            owner_op =  container.multiselect(" ", dataLineox.companiesList, key='company')

with col2:
    with st.expander("Frecuencia Filter"):
        container = st.container()
        all = st.checkbox("Select all", value = True, key='4')
        if all:
            freq_op = dataLineox.freqList
            lfreq=0
            hfreq=1000000
        else:
            freq_op =  container.multiselect(" ", dataLineox.freqList, key='frecuencia')
            try: lfreq = dataLineox.freqmap(freq_op)[0]
            except: lfreq = 0
            try: hfreq = dataLineox.freqmap(freq_op)[1]
            except: hfreq = 0
    
    ldays, hdays = st.slider(
    'Days until Contract Expiration',
    min_value = dataLineox.minDate, max_value = dataLineox.maxDate, value = (dataLineox.minDate, dataLineox.maxDate),
    )

col1, col2 = st.columns([1,3], gap='small')

# Metrics 
with col1:
    st.markdown("""<span style='color:#00008B'>**Metrics**</span>""",unsafe_allow_html=True)
    st.metric("Radio links", dataLineox.calculateKPI(lfreq, hfreq, ldays, hdays, prov_op, mun_op, owner_op)[0]) 
    st.metric("Companies", dataLineox.calculateKPI(lfreq, hfreq, ldays, hdays, prov_op, mun_op, owner_op)[1])
    st.metric("Avg. Number Radio Links", dataLineox.calculateKPI(lfreq, hfreq, ldays, hdays, prov_op, mun_op, owner_op)[2])
            
#Radio links top 10 table
with col2:
    st.markdown("""<span style='color:#00008B'>**Top 10 radio links groups**</span>""",unsafe_allow_html=True)
    st.table(data = dataLineox.topOwners(lfreq, hfreq, ldays, hdays, prov_op, mun_op, owner_op))

#Bar plot
st.plotly_chart(dataLineox.createBarplot(lfreq, hfreq, ldays, hdays, prov_op, mun_op, owner_op), use_container_width=True)
            
#Map
mapdata = st_folium(dataLineox.createMap(lfreq, hfreq, ldays, hdays, prov_op, mun_op, owner_op), width=1500, height=500)

#Download button
st.download_button(label="Download All Raw Data (csv)", data=dataLineox.df.to_csv().encode('utf-8'), file_name='ESradiolinks.csv', mime='text/csv',)
st.image('banner.png')
