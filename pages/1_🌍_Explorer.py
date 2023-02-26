import streamlit as st
from streamlit_folium import st_folium
from st_aggrid import AgGrid, GridOptionsBuilder

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

# Filters Section
col1, col2, col3 = st.columns([2,1,4], gap='medium')

with col1:
    st.markdown("""<span style='color:#00008B'>**FILTERS**</span>""",unsafe_allow_html=True)
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
    
    with st.expander("Frecuencia Filter"):
        container = st.container()
        all = st.checkbox("Select all", value = True, key='4')
        if all:
            freq_op = list(dataLineox.freqList.keys())
        else:
            freq_op =  container.multiselect(" ", list(dataLineox.freqList.keys()), key='frecuencia')
    
    lnumRadio, hnumRadio = st.slider(
    'Number of Radiolinks Owned',
    min_value = dataLineox.minRadioLinks, max_value = dataLineox.maxRadioLinks, value = (dataLineox.minRadioLinks, dataLineox.maxRadioLinks),
    )
    
    ldays, hdays = st.slider(
    'Days Until Contract Expiration',
    min_value = dataLineox.minDate, max_value = dataLineox.maxDate, value = (dataLineox.minDate, dataLineox.maxDate),
    )

# Metrics Section + Pie Chart for Expiration Distribution
with col2:
    st.markdown("""<span style='color:#00008B'>**METRICS**</span>""",unsafe_allow_html=True)
    st.metric("Radiolinks", dataLineox.calculateKPI(freq_op, ldays, hdays, prov_op, mun_op, owner_op, lnumRadio, hnumRadio)[0])
    st.metric("Companies", dataLineox.calculateKPI(freq_op, ldays, hdays, prov_op, mun_op, owner_op, lnumRadio, hnumRadio)[1])
    st.metric("Avg. Number Radio Links", dataLineox.calculateKPI(freq_op, ldays, hdays, prov_op, mun_op, owner_op, lnumRadio, hnumRadio)[2])

    st.markdown("""<span style='color:#00008B'>**EXPIRATION DISTRIBUTION**</span>""",unsafe_allow_html=True)
    st.plotly_chart(dataLineox.createPieChart(freq_op, ldays, hdays, prov_op, mun_op, owner_op, lnumRadio, hnumRadio), use_container_width=True, config = {'displayModeBar': False})

# Stacked Barplot for Frequency Band Distribution by Province
with col3:
    st.markdown("""<span style='color:#00008B'>**FREQUENCY BAND DISTRIBUTION**</span>""",unsafe_allow_html=True)
    st.plotly_chart(dataLineox.createBarplot(freq_op, ldays, hdays, prov_op, mun_op, owner_op, lnumRadio, hnumRadio), use_container_width=True)


col1, col2 = st.columns([4,5], gap='medium')
with col1:
    #Map
    st.markdown("""<span style='color:#00008B'>**GEOGRAPHIC DISTRIBUTION**</span>""",unsafe_allow_html=True)
    mapdata = st_folium(dataLineox.createMap(freq_op, ldays, hdays, prov_op, mun_op, owner_op, lnumRadio, hnumRadio), height=500, width=600)
            
#Radio links table
gb = GridOptionsBuilder.from_dataframe(dataLineox.topOwners(freq_op, ldays, hdays, prov_op, mun_op, owner_op, lnumRadio, hnumRadio))
gb.configure_pagination(paginationAutoPageSize=True, paginationPageSize=5)
gridOptions = gb.build()
with col2:
    st.markdown("""<span style='color:#00008B'>**TOP RADIOLINK OWNERS**</span>""",unsafe_allow_html=True)
    grid_response = AgGrid(
        dataLineox.topOwners(freq_op, ldays, hdays, prov_op, mun_op, owner_op, lnumRadio, hnumRadio),
        gridOptions = gridOptions,
        height= 500,
        fit_columns_on_grid_load = True,
        theme='balham',
    )

#Download button
st.download_button(label="Download All Raw Data (csv)", data=dataLineox.df.to_csv().encode('utf-8'), file_name='ESradiolinks.csv', mime='text/csv',)
st.image('assets/banner.png')
