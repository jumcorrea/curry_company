#importar as bibliotecas

from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
from datetime import datetime
from PIL import Image
from streamlit_folium import folium_static
import folium

st.set_page_config(page_title='visao entregadores', page_icon='', layout='wide')

# ----------------------------
# funcoes
# ----------------------------
def clean_code(df1):
    """ esta funcao tem a responsabilidade de limpar o dataframe 

    Tipos de limpeza: 
    1. remocao de dados NaN
    2. mudanca do tipo de coluna de dados
    3. remocao dos espacos das variaveis de texto
    4. formatacao da coluna de datas
    5. limpeza da coluna de tempo (separacao do texto da variavel numerica)

    Input: Dataframe
    Output: Dataframe
    """
    #converter a coluna age de texto para numero
    linhas_selecionadas = (df1['Delivery_person_Age'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()
    
    linhas_selecionadas = (df1['Road_traffic_density'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()
    
    linhas_selecionadas = (df1['City'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()
    
    linhas_selecionadas = (df1['Festival'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()
    
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype( int )
    df1.shape
    
    #converter a coluna ratings de texto para numero decimal (float)
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype( float )
    
    #converter coluna order_date de texto para data
    df1['Order_Date'] = pd.to_datetime (df1['Order_Date'], format='%d-%m-%Y')
    
    #converter multiple_deliveries de texto para numero inteiro (int)
    linhas_selecionadas = (df1['multiple_deliveries'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)
    
    #remover espacos dentro de strings/texto/object
    #df1 = df1.reset_index( drop = True)
    #for i in range (len( df1)):
    #df1.loc[i, 'ID'] = df1.loc[i, 'ID'].strip()
    
    #remover os espacos dentro de strings/texto/object
    df1.loc[:, 'ID']= df1.loc[:, 'ID'].str.strip()
    df1.loc[:, 'Road_traffic_density']= df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_order']= df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle']= df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:, 'City']= df1.loc[:, 'City'].str.strip()
    
    #limpar a coluna time_taken
    
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply( lambda x: x.split ( '(min) ')[1] )
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)
    
    #print (df1.head() )
    return df1


def top_delivers(df1, top_asc):
    df2 = (df1.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']]
              .groupby(['City', 'Delivery_person_ID'] ).mean()
              .sort_values(['City','Time_taken(min)'], ascending=top_asc)
              .reset_index() )
    df_aux01 = df2.loc[df2['City'] == 'Metropolitian', :].head(10)
    df_aux02 = df2.loc[df2['City'] == 'Urban', :].head(10)
    df_aux03 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)
    df3 = pd.concat( [ df_aux01, df_aux02, df_aux03]).reset_index(drop=True)
    return df3


# -----------------------------------------
#importando o arquivo
df = pd.read_csv( 'train.csv' )
df1 = df.copy()

#limpando os dados
df1 =clean_code(df1)

# =====================================
# Barra lateral no streamlit
# =====================================
st.header('marketplace - visao entregadores')

image_path = 'logo.png'
image = Image.open ( image_path )
st.sidebar.image (image, width = 120)

st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('## Fastest delivery in town')
st.sidebar.markdown("""---""")

st.sidebar.markdown('## selecione uma data limite:')

#st.dataframe(df1)

data_slider = st.sidebar.slider(
    'até qual valor?',
    value = datetime(2022, 4, 13),
    min_value = datetime(2022, 2, 11), 
    max_value = datetime(2022, 4, 6),
    format = 'DD-MM-YYYY' )

#st.header( data_slider )

st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect(
    'quais as condicoes de transito?',
    [ 'Low', 'Medium', 'High', 'Jam'],
    default = ['Low', 'Medium', 'High', 'Jam'])

#filtro de data
linhas_selecionadas = df1['Order_Date'] < data_slider
df1 = df1.loc[linhas_selecionadas, :]

#filtro de transito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]

# =====================================
# layout no streamlit
# =====================================

tab1, tab2, tab3 = st.tabs( ['Visao Gerencial', 'x', 'y'] )

with tab1:
        with st.container():
            st.title( 'Overall Metrics')

            col1, col2, col3, col4 = st.columns (4, gap = 'large')
            with col1:
                #st.subheader( 'maior de idade')
                maior_idade= df1.loc[:, 'Delivery_person_Age'].max() 
                col1.metric('maior idade', maior_idade) 
            with col2:
                #st.subheader( 'menor de idade')
                menor_idade= df1.loc[:, 'Delivery_person_Age'].min() 
                col2.metric('menor idade', menor_idade)
            with col3:
                #st.subheader( 'melhor condicao de veiculo')
                melhor_veiculo = df1.loc[:, 'Vehicle_condition'].max()
                col3.metric('melhor condicao', melhor_veiculo)
            with col4:
                #st.subheader( 'pior condicao de veiculo')
                pior_veiculo =df1.loc[:, 'Vehicle_condition'].min()
                col4.metric('pior condicao', pior_veiculo)

        with st.container():
            st.markdown("""---""")
            st.title('avaliacoes')
            
            col1, col2 = st.columns(2)
            with col1:
                #st.subheader('avaliacoes medias por entregador')
                st.markdown('##### avaliacoes medias por entregador')
                df_avg_ratings_deliverer= (df1.loc[:, ['Delivery_person_ID','Delivery_person_Ratings']]
                                           .groupby('Delivery_person_ID').mean().reset_index() )
                st.dataframe( df_avg_ratings_deliverer)
            with col2:
                #st.subheader('avaliacoes medias por transito')
                st.markdown('##### avaliacoes medias por transito')
                avg_traffic = ( df1.loc[:, ['Delivery_person_Ratings', 'Road_traffic_density']]
                                   .groupby('Road_traffic_density').agg( {'Delivery_person_Ratings':['mean','std'] } ) )
                avg_traffic.columns=[ 'delivery_mean', 'delivery_std']
                avg_traffic = avg_traffic.reset_index()
                st.dataframe(avg_traffic)
                
                #st.subheader('avaliacao média por clima')
                st.markdown('##### avaliacoes medias por clima')
                avg_weather = (df1.loc[:, ['Delivery_person_Ratings', 'Weatherconditions']]
                                  .groupby('Weatherconditions').agg( {'Delivery_person_Ratings':['mean','std'] } ))
                avg_weather.columns=[ 'weather_mean', 'weather_std']
                avg_weather = avg_weather.reset_index()
                st.dataframe(avg_weather)
    
        with st.container():
            st.markdown("""---""")
            st.title('velocidade de entrega')
            col1, col2 = st.columns(2)
            with col1:
                st.subheader('top entregadores mais rapidos')
                df3 = top_delivers(df1, top_asc=True)
                st.dataframe(df3)
                
            with col2:
                st.subheader('top entregadores mais lentos')
                df3 = top_delivers(df1, top_asc=False)
                st.dataframe(df3)
                