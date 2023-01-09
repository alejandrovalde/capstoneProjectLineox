import pandas as pd # import pandas
from playwright.sync_api import sync_playwright # import playwright
#from bs4 import BeautifulSoup # import beautifulsoup
import requests # import requests
import math 
import time

# 1. Set the list of communes we want to scrape
l=[]
for x in list(range(20))[1:]:
    l.append("%02d" % x)

# 2. Main code
with sync_playwright() as p: #close browser
    
    # general table
    main = []
    # freq tables
    freq=[]
   
    browser = p.chromium.launch(headless = False, slow_mo=50)
    page = browser.new_page()
    for com in l: # FOR EACH COMMUNE
        page.goto('https://sedeaplicaciones.minetur.gob.es/RPC_Consulta/FrmConsulta.aspx') #go to url
        page.click('input#MainContent_rblTipoServicio_1') # click on Servicio fijo
        page.click('select#MainContent_cmbComunidad')     
        page.select_option('select#MainContent_cmbComunidad', com) # select the commune
        page.click('input#MainContent_btnBuscar') # click search
        page.wait_for_selector('table#MainContent_gridConcesiones') # wait until the page loads
        numRL = page.evaluate("document.getElementById('MainContent_lblTotal').textContent") # extract the number of radio links in that commune
        numRL = int(numRL.split(' ')[0]) # only keep the number out of the text
        numPages = math.ceil(numRL/10) # get the number of pages
        #print(numPages) #-> to use in the loop
        communidad = page.evaluate("document.getElementById('MainContent_lblFiltro').textContent") # get the commune name
        communidad = communidad[11:]
        
        for n in range(1,numPages+1): # FOR EACH PAGE
            if n != 1:
                page.evaluate(f"__doPostBack('ctl00$MainContent$gridConcesiones','Page${n}')") # click on page number if other page than 1st
                time.sleep(2) # wait 2 sec for page to load
            table = page.query_selector('table#MainContent_gridConcesiones')
            rows = table.query_selector_all('tr') # each row is referenced with 'tr'

    # 2a. Scrape data in main table to populate main list
            for row in rows: # FOR EACH ROW
                text = row.inner_text() # extract all text of 1 row
                if 'Referencia' not in text and '...' not in text: # exclude headers and numbering
                    main.append(f"{communidad}\t{text}") # append each row text to the main list
    
    # 2b. Scrape data in freq subtable to populate freq list        
            filas = len(rows)-3 # number of rows removing headers and page numbering ones
            for i in range(0,filas): # FOR EACH ROW
                ref = f"a#MainContent_gridConcesiones_lnkFrecuencias_{i}" # ref for text in col 1 of each row
                page.click(ref)
                page.wait_for_selector('table#MainContent_gridFrecuencias')
                # get reference title
                reference = page.evaluate("document.getElementById('MainContent_lblExpediente').textContent")
                reference = reference.split(':')[1].strip()
                table = page.query_selector('table#MainContent_gridFrecuencias')
                rows = table.query_selector_all('tr')  # each row is referenced with 'tr'
                for row in rows: # FOR EACH ROW OF FREQ SUBTABLE
                    text = row.inner_text()
                    if 'Comunidad' not in text: # exclude headers
                        freq.append(f"{reference}\t{text}") # append reference + each row to the freq list
                page.click('input#MainContent_btnCerrar') # close the subtable

# 3. Transform lists to pandas dataframe
   
    # 3a. Freq list
freq = [elem.split('\t') for elem in freq]
dfFreq = pd.DataFrame(freq, columns=['Ref','Comunidad','Provincia_FREQ','Municipio','Frecuencia'])
dfFreq = dfFreq.drop(['Comunidad'], axis=1) # Remove unecessary column
dfFreq[['Frecuencia', 'Unit']] = dfFreq.Frecuencia.str.split(" ", 1, expand = True) # Put the unit into a seperate column
dfFreq.to_csv("dfFreq.csv", index=False)

    # 3b. Main list
main = [elem.split('\t') for elem in main]
dfCompanies = pd.DataFrame(main, columns=['Comunidad','Ref','Titular','NIF/CIF','DomicilioSocial','Localidad','Provincia_RL','CP','FConcesion','FCaducidad','SusceptibleConcesion','SusceptibleMutualizacion','Transferencia'])
dfCompanies.to_csv("dfCompanies.csv", index=False)

# 4. Join the dataframes on 'Ref'
rl_data = pd.merge(dfCompanies, dfFreq, on="Ref", how="outer")
rl_data.to_csv("rl_data.csv", index=False)

