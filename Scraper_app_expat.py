import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup as bs
from requests import get
import base64
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import streamlit as st
import streamlit.components.v1 as components
from selenium import webdriver 
from selenium.webdriver.common.by import By 

# instantiate a Chrome options object
options = webdriver.ChromeOptions() 
# set the options to use Chrome in headless mode (used for running the script in the background)
options.add_argument("--headless=new") 
# initialize an instance of the Chrome driver (browser) in headless mode
driver = webdriver.Chrome(options=options)


st.markdown("<h1 style='text-align: center; color: black;'>MY DATA SCRAPER APP</h1>", unsafe_allow_html=True)

st.markdown("""
This app performs webscraping of data from expat-dakar over multiples pages. And we can also
download scraped data from the app directly without scraping them.
* **Python libraries:** base64, pandas, streamlit, requests, bs4
* **Data source:** [Expat-Dakar](https://www.expat-dakar.com/).
""")


# Background function
def add_bg_from_local(image_file):
    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url(data:image/{"jpg"};base64,{encoded_string.decode()});
        background-size: cover
    }}
    </style>
    """,
    unsafe_allow_html=True
    )

# Web scraping of Vehicles data on expat-dakar
@st.cache_data

def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

def load(dataframe, title, key, key1) :
    st.markdown("""
    <style>
    div.stButton {text-align:center}
    </style>""", unsafe_allow_html=True)

    if st.button(title,key1):
        # st.header(title)

        st.subheader('Display data dimension')
        st.write('Data dimension: ' + str(dataframe.shape[0]) + ' rows and ' + str(dataframe.shape[1]) + ' columns.')
        st.dataframe(dataframe)

        csv = convert_df(dataframe)

        st.download_button(
            label="Download data as CSV",
            data=csv,
            file_name='Data.csv',
            mime='text/csv',
            key = key)

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Fonction for web scraping vehicle data
def load_vehicle_data(mul_page):
    df = pd.DataFrame()
    for p in range(1, int(mul_page)): 
      url = f'https://www.expat-dakar.com/voitures?page={p}'
      driver.get(url)
      res = driver.page_source
      # res = get(url)
      soup = bs(res, 'html.parser')
      containers = soup.find_all('div', class_ = 'listings-cards__list-item')
      data = []
      for container in containers: 
        try: 
          inf =container.find('div', class_ = 'listing-card__header__tags').find_all('span')
          etat = inf[0].text
          marque = inf[1].text
          annee = inf[2].text
          boit_vitess = inf[3].text
          prix = container.find('span', class_ ='listing-card__price__value 1').text.strip()
          # adresse = container.find('span', class_ ='listing-card__header__location').text.strip()

          obj = {
              "etat": etat, 
              "marque": marque, 
              "annee": annee,
              "boit_vitess": boit_vitess, 
              "prix": prix 
              # "adresse": adresse
          }
          data.append(obj)
        except: 
          pass

      DF = pd.DataFrame(data)
      df = pd.concat([df, DF], axis= 0).reset_index(drop = True)
    return df

def load_motocycle_data(mul_page):
    df = pd.DataFrame()
    for p in range(1, int(mul_page)): 
      url = f'https://www.expat-dakar.com/motos-scooters?page={p}'
      driver.get(url)
      res = driver.page_source
      soup = bs(res, 'html.parser')
      containers = soup.find_all('div', class_ = 'listings-cards__list-item')
      data = []
      for container in containers: 
        try: 

          inf =container.find('div', class_ = 'listing-card__header__tags').find_all('span')
          etat = inf[0].text
          marque = inf[1].text
          annee = inf[2].text
          # boit_vitess = inf[3].text
          prix = container.find('span', class_ ='listing-card__price__value 1').text.strip()
          # adresse = container.find('span', class_ ='listing-card__header__location').text.strip()

          obj = {
              "etat": etat, 
              "marque": marque, 
              "annee": annee,
              # "boit_vitess": boit_vitess
              "prix": prix
              # "adresse": adresse
          }
          data.append(obj)
        except: 
          pass

      DF = pd.DataFrame(data)
      df = pd.concat([df, DF], axis= 0).reset_index(drop = True)
    return df   


st.sidebar.header('User Input Features')
Pages = st.sidebar.selectbox('Pages indexes', list([int(p) for p in np.arange(2, 600)]))
Choices = st.sidebar.selectbox('Options', ['Scrape data using beautifulSoup', 'Download scraped data', 'Dashbord of the data',  'Fill the form'])



add_bg_from_local('img_file3.jpg') 

local_css('style.css')  

if Choices=='Scrape data using beautifulSoup':

    Vehicles_data_mul_pag = load_vehicle_data(Pages)
    Motocycle_data_mul_pag = load_motocycle_data(Pages)
    
    load(Vehicles_data_mul_pag, 'Vehicles data', '1', '101')
    load(Motocycle_data_mul_pag, 'Motocycle data', '2', '102')

elif Choices == 'Download scraped data': 
    Vehicles = pd.read_csv('Vehicles_data.csv')
    Motocycles = pd.read_csv('Motocycles_data.csv') 

    load(Vehicles, 'Vehicles data', '1', '101')
    load(Motocycles, 'Motocycles data', '2', '102')

elif  Choices == 'Dashbord of the data': 
    df1 = pd.read_csv('vehicles_clean_data.csv')
    df2 = pd.read_csv('motocycles_clean_data.csv')

    col1, col2= st.columns(2)

    with col1:
        plot1= plt.figure(figsize=(11,7))
        color = (0.2, # redness
                 0.4, # greenness
                 0.2, # blueness
                 0.6 # transparency
                 )
        plt.bar(df1.marque.value_counts()[:5].index, df1.marque.value_counts()[:5].values, color = color)
        plt.title('cinq marque de vehicules les plus vendus')
        plt.xlabel('marque')
        st.pyplot(plot1)

    with col2:
        plot2 = plt.figure(figsize=(11,7))
        color = (0.5, # redness
         0.7, # greenness
         0.9, # blueness
         0.6 # transparency
         )
        plt.bar(df2.marque.value_counts()[:5].index, df2.marque.value_counts()[:5].values, color = color)
        plt.title('cinq marque de vehicules les plus vendus')
        plt.xlabel('marque')
        st.pyplot(plot2)
    
    col3, col4= st.columns(2)

    with col3:
        plot3= plt.figure(figsize=(11,7))
        sns.lineplot(data=df1, x="annee", y="prix", hue="etat")
        plt.title('Variation du prix suivant les années des catégories de vehicules')
        st.pyplot(plot3)

    with col4:
        plot4 = plt.figure(figsize=(11,7))
        sns.lineplot(data=df2, x="annee", y="prix", hue="etat")
        plt.title('Variation du prix suivant les années des catégories de motos')
        st.pyplot(plot4)



else :
    components.html("""
    <iframe src="https://ee.kobotoolbox.org/i/y3pfGxMz" width="800" height="1100"></iframe>
    """,height=1100,width=800)
















 


