import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode

from definitions import definitions
from dataExplorer import dataLineox, generateCashFlow, calculateFinancials

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

st.header('Acquisition Scenario')

# Acquisition Definition of Parameters
col1, col2, col3, col4 = st.columns([2,1,1,1], gap='medium')
with col1:
    st.markdown('**Range of Frequencies Exempted from Tax**')
    freqExemptedRange = st.slider('Select:',min_value=0,max_value=100, value=[13,25])

    st.markdown('**Select Company to Acquire**')
    owner_op = st.selectbox('Company:', options= dataLineox.companiesList, index=15)

    radiolinksOwned, radiolinksOwnedLineoxFreq = dataLineox.numRadioLinks(owner_op, freqExemptedRange)
    st.text(f"Owned Radiolinks = {radiolinksOwned} (Within Lineox's Range = {radiolinksOwnedLineoxFreq})")

    st.markdown('**Frequencies Outside Lineox Range**')
    st.text("Choose which radiolinks to migrate by changing 'No' to 'Yes'")
    if radiolinksOwnedLineoxFreq == radiolinksOwned:
        st.write('No spectrum fees needed...')
    else:
        dfNotOwned = dataLineox.tableFees(owner_op, freqExemptedRange)
        dfMigrated = AgGrid(
            dfNotOwned,
            fit_columns_on_grid_load = True,
            theme='balham',
            editable = True,
        )
    
with col2:
    st.markdown('**Cash Flow Inputs**')
    periods = st.number_input('Length (Years)', value=definitions['periods']['value'], help=definitions['periods']['def'])
    discountRate = st.number_input('Discount Rate (%)', value=definitions['discountRate']['value'], help=definitions['discountRate']['def'])
    inflationRate = st.number_input('Inflation Rate (%)', value=definitions['inflationRate']['value'], help=definitions['inflationRate']['def'])
    st.write(' ')
    st.markdown('**Revenue Inputs**')
    monthlyCharge = st.number_input('Monthly Charge (Radiolink)', value=definitions['monthlyCharge']['value'], help=definitions['monthlyCharge']['def'])
    setUpCost = st.number_input('Set-Up Cost Churn/Add (Radiolink)', value=definitions['setUpCost']['value'], help=definitions['setUpCost']['def'])

with col3:
    st.markdown('**OPEX Inputs**')
    opsMaintAnnual = st.number_input('Annual Ops. & Maint. (Radiolink)', value=definitions['opsMaintAnnual']['value'], help=definitions['opsMaintAnnual']['def'])
    itTotalAnnual = st.number_input('Annual IT Costs (Total Base)', value=definitions['itTotalAnnual']['value'], help=definitions['itTotalAnnual']['def'])
    otherCostsPct = st.number_input('Other Costs (% of Revenue)', value=definitions['otherCostsPct']['value'], help=definitions['otherCostsPct']['def'])

with col4:
    st.markdown('**CAPEX Inputs**')
    upfrontOffer = st.number_input('Upfront Offer (Radiolink)', value=definitions['upfrontOffer']['value'], help=definitions['upfrontOffer']['def'])
    bandTransfer = st.number_input('Migration Cost (Radiolink)', value=definitions['bandTransfer']['value'], help=definitions['bandTransfer']['def'])
    costChurned = st.number_input('Churned Radiolinks', value=definitions['costChurned']['value'], help=definitions['costChurned']['def'])
    itSetUpCapex = st.number_input('IT Set-Up (Total Base)', value=definitions['itSetUpCapex']['value'], help=definitions['itSetUpCapex']['def'])

### Initial Table with Periods + Active Radiolinks + Monthly Charge
# Updates with number of periods defined + monthly charge defined as base
periodsList = [str(i) for i in range(0,periods)]
numActiveRL = [[inflationRate,monthlyCharge,radiolinksOwned,0]]*periods
dfInitial = pd.DataFrame(dict(map(lambda i,j : (i,j) , periodsList, numActiveRL)), index=['% Inflation','Monthly Fee','Active RadioLinks','% Relocated'])
for colid in range(len(periodsList)-1):
    inf = dfInitial.loc['% Inflation',:].values[colid]
    dfInitial.iloc[dfInitial.index.get_loc('Monthly Fee'), colid+1] = round(dfInitial.iloc[dfInitial.index.get_loc('Monthly Fee'), colid] * (1+inf/100),2)
dfInitial = dfInitial.reset_index()

st.markdown('**Define Recurring Active RadioLinks & Monthly Charge**')
dfInitialUpdated = AgGrid(
    dfInitial,
    fit_columns_on_grid_load = True,
    theme='balham',
    editable = True,
)
calculate = st.button("CALCULATE")

st.subheader('Cash Flow')

costs = {
    'setUpCost': setUpCost,
    'opsMaintAnnual': opsMaintAnnual,
    'itTotalAnnual' : itTotalAnnual,
    'otherCostsPct' : otherCostsPct,
    'upfrontOffer' : upfrontOffer,
    'bandTransfer': bandTransfer,
    'costChurned': costChurned,
    'itSetUpCapex': itSetUpCapex
}

if calculate:
    # Get Data Frame
    dfCashFlow = generateCashFlow(radiolinksOwned, periodsList, dfMigrated['data'], dfInitialUpdated['data'], costs)
    # Table Costumization
    gd = GridOptionsBuilder.from_dataframe(dfCashFlow)
    cellstyle_jscode = JsCode("""
        function(params){
            if (params.value < '0') {
                return{
                    'color': 'red',
                }
            }
        }
    """)
    gd.configure_columns(dfCashFlow, cellStyle= cellstyle_jscode)
    grid_options = gd.build()
    # Show Table
    cashFlow = AgGrid(
        dfCashFlow,
        gridOptions = grid_options,
        allow_unsafe_jscode= True,
        fit_columns_on_grid_load = True,
        theme='balham',
    )

    # Calculate NPV and IRR and Show
    npv, irr = calculateFinancials(cashFlow['data'], discountRate)
    col1, col2, col3 = st.columns([1,1,4])
    with col1:
        st.metric('NPV', f"{round(npv):,} €")
    with col2:
        st.metric('IRR', f"{round(irr*100,2)} %")

else:
    st.write("Press Calculate...")