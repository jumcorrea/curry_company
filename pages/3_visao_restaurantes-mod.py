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

import numpy as np

st.set_page_config(page_title='visao restaurantes', page_icon='', layout='wide')

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
    # converter a coluna age de texto para numero
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

def distance(df1,fig):
    if fig == False:
        cols = ([ 'Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude',
                     'Delivery_location_longitude'])
        df1['distance'] = ( df1.loc[:, cols].apply( lambda x: 
                             haversine( (x['Restaurant_latitude'], x['Restaurant_longitude']), 
                                        (x['Delivery_location_latitude'],x['Delivery_location_longitude'])),axis=1) )
        avg_distance = np.round(df1['distance'].mean(), 2)
        return avg_distance
    else:
        cols = ([ 'Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude',
                     'Delivery_location_longitude'])
        df1['distance'] = ( df1.loc[:, cols].apply( lambda x: 
                             haversine( (x['Restaurant_latitude'], x['Restaurant_longitude']), 
                                        (x['Delivery_location_latitude'],x['Delivery_location_longitude'])),axis=1) )
        avg_distance=df1.loc[:,['City', 'distance']].groupby('City').mean().reset_index()
        fig1= go.Figure(data=[go.Pie(labels=avg_distance[ 'City'], values = avg_distance['distance'], pull=[0,0.1,0])])
        return fig

def avg_std_time_delivery(df1, festival, op):
    """esta funcao calcula o tempo medio e o desvio padrao do tempo de entrega.
    Parametros:
        Input:
        - df: dataframe com os dados para o calculo
        - op: tipo de operacao a ser calculada
            - 'avg_time': calcula o tempo medio
            - 'std_time': calcula o desvio padrao do tempo
        Output: 
        - df: data frame com duas colunas e uma linha
    """
    dfaux = ( df1.loc[:, ['Time_taken(min)', 'Festival']]
                 .groupby(['Festival'])
                 .agg({'Time_taken(min)': ['mean', 'std']}) ) 
    dfaux.columns = ['avg_time', 'std_time' ]
    dfaux = dfaux.reset_index()
    dfaux = np.round(dfaux.loc[dfaux['Festival'] == festival, op], 2)
    return dfaux

def avg_std_time_graph(df1):
    df_aux=df1.loc[ :, ['City', 'Time_taken(min)']].groupby('City').agg( { 'Time_taken(min)': [ 'mean', 'std']})     
    df_aux.columns = [ 'avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    fig= go.Figure()
    fig.add_trace(go.Bar( name = 'Control', x=df_aux['City'], y=df_aux['avg_time'],
                            error_y=dict(type='data', array=df_aux['std_time'])))
    fig.update_layout(barmode='group')
    return fig

def avg_std_time_on_traffic(df1):
    df_aux=(df1.loc[:, ['City', 'Time_taken(min)', 'Road_traffic_density']]
               .groupby(['City','Road_traffic_density'])
               .agg({ 'Time_taken(min)': ['mean', 'std']}))
    df_aux.columns=['avg_time','std_time']
    df_aux= df_aux.reset_index()
    fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='avg_time',
                               color='std_time', color_continuous_scale= 'RdBu',
                               color_continuous_midpoint=np.average(df_aux['std_time']))
    return fig


#--------------------------------
#importando o arquivo
df = pd.read_csv( 'train.csv' )

df1 = df.copy()

#limpando a base de dados
df1 = clean_code (df1)
# =====================================
# Barra lateral no streamlit
# =====================================
st.header('marketplace - visao restaurantes')

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
tab1, tab2, tab3 = st.tabs( [ 'visao gerencial', 'x', 'y'] )

with tab1:
    with st.container():
        st.title( 'overall metrics')

        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            #st.markdown('##### Entregadores Unicos')
            delivery_unique = len ( df1.loc[:, 'Delivery_person_ID'].unique() )
            col1.metric( 'entregadores unicos', delivery_unique)
       
        with col2:
            #st.markdown('##### coluna 2')
            avg_distance = distance(df1, fig=False)
            col2.metric('distancia media entregas', avg_distance)
            
        with col3:
            #st.markdown('##### coluna 3')
            dfaux=avg_std_time_delivery(df1, 'Yes', 'avg_time')    
            col3.metric('tempo medio com festival', dfaux)
       
        with col4:
            #st.markdown('##### coluna 4')
            dfaux=avg_std_time_delivery(df1, 'Yes', 'std_time') 
            col4.metric('dp tempo com festival', dfaux)
            
        with col5:
            #st.markdown('##### coluna 5')
            dfaux=avg_std_time_delivery(df1, 'No', 'avg_time') 
            col5.metric('tempo medio sem festival', dfaux)
            
        with col6:    
            #st.markdown('##### coluna 6')
            dfaux=avg_std_time_delivery(df1, 'No', 'std_time') 
            col6.metric('dp tempo sem festival', dfaux)
            
    with st.container():    
        st.markdown("""---""")
        st.title( 'tempo medio entrega por cidade')
        fig=distance(df1, fig=True)
        st.plotly_chart(fig)
        
    with st.container():    
        st.markdown("""---""")
        st.title( 'distribuicao tempo')
        
        col1,col2 = st.columns(2)
        
        with col1:
            #st.markdown(' ###### col1')
            fig= avg_std_time_graph(df1)
            st.plotly_chart(fig)
           
        with col2:
            #st.markdown(' ###### col2')
            fig = avg_std_time_on_traffic(df1)
            st.plotly_chart(fig)
            
    with st.container():
        st.markdown("""---""")
        st.title("distribuicao da distancia")
        cols= [ 'City', 'Time_taken(min)', 'Type_of_order']
        df_aux= df1.loc[:, cols].groupby(['City','Type_of_order']).agg({'Time_taken(min)': [ 'mean', 'std']})
        df_aux.columns=['avg_time','std_time']
        df_aux=df_aux.reset_index()
        st.dataframe(df_aux)
        st.markdown("""---""")