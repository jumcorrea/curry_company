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

st.set_page_config(page_title='visao empresa', page_icon='', layout='wide')

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

def order_metric(df1): 
    #order metric
    # fazer uma contagem das colunas "ID", agrupado por "Order Date" e usar uma biblioteca de visualizaçao para mostrar o gráfico de barras
    cols = ['ID', 'Order_Date']
    #selecao de linhas
    df_aux = df1.loc[:, cols].groupby('Order_Date').count().reset_index()
    fig = px.bar(df_aux, x='Order_Date', y = 'ID')
    return fig

def traffic_order_share (df1):
    df_aux = df1.loc[:,['ID','Road_traffic_density']].groupby('Road_traffic_density').count().reset_index()
    df_aux.head()
    df_aux= df_aux.loc[df_aux['Road_traffic_density'] != 'NaN', :]
    df_aux['entregas_perc']=df_aux['ID'] / df_aux['ID'].sum()
    #df_aux
    fig2 = px.pie(df_aux, values='entregas_perc', names = 'Road_traffic_density')
    return fig2

def traffic_order_city(df1):
    df_aux = (df1.loc[:, ['ID', 'City', 'Road_traffic_density']]
                .groupby( [ 'City','Road_traffic_density']).count().reset_index())
    fig3 = px.scatter(df_aux, x = 'City', y='Road_traffic_density', size = 'ID' , color = 'City')
    return fig3    

def order_by_week(df1):        
    # criar a coluna de semana
    df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')
    #df1.head()
    df_aux = df1.loc[:, ['ID', 'week_of_year']].groupby( 'week_of_year').count().reset_index()
    #df_aux.head()
    fig4= px.line( df_aux, x='week_of_year', y='ID')
    return fig4

def order_share_by_week( df1): 
    # qtde de pedidos por semana / numero unico de entregadores por semana
    df_aux1 = df1.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
    df_aux2= df1.loc[:, ['Delivery_person_ID', 'week_of_year']].groupby('week_of_year').nunique().reset_index()
    #df_aux1
    #df_aux2
    df_aux= pd.merge( df_aux1, df_aux2, how = 'inner')
    df_aux[ 'order_by_deliver']= df_aux['ID']/df_aux[ 'Delivery_person_ID']
    #df_aux
    fig5= px.line( df_aux, x= 'week_of_year', y='order_by_deliver')
    return fig5

def country_maps(df1):    
    df_aux = (df1.loc[:, ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']]
              .groupby(['City', 'Road_traffic_density']).median().reset_index())
    df_aux= df_aux.loc[df_aux['City'] != 'NaN', :]
    df_aux= df_aux.loc[df_aux['Road_traffic_density'] != 'NaN', :]
    #df_aux = df_aux.head()
    map1 = folium.Map()
    for index, location_info in df_aux.iterrows():
        folium.Marker( [location_info['Delivery_location_latitude'],
                      location_info['Delivery_location_longitude']],
                     popup=location_info[['City', 'Road_traffic_density']] ).add_to(map1)
    folium_static( map1, width=1024, height=600 )
    return None
# --------------------- inicio da estruturacao logica do codigo -----------------------------------------

#importando o arquivo
df = pd.read_csv( 'train.csv' )
df1 = df.copy()

#limpando os dados
df1 = clean_code(df1)

# =====================================
# Barra lateral no streamlit
# =====================================
st.header('marketplace - visao cliente')

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
tab1, tab2, tab3 = st.tabs( ['Visao Gerencial', 'Visao Tatica', 'Visao Geografica'] )

with tab1:
    with st.container():
        #order metric
        st.markdown("# Orders by Day")
        fig = order_metric(df1)
        st.plotly_chart(fig, use_container_width = True)
        
    with st.container():
        col1, col2 = st.columns (2)
        
        with col1:
            st.header('Traffic Order Share')
            fig2 = traffic_order_share(df1)
            st.plotly_chart( fig2, user_container_width = True)

        with col2: 
            st.header('Traffic Order City')
            fig3=traffic_order_city(df1)
            st.plotly_chart( fig3, user_container_width = True)     
    
with tab2:
    with st.container():
        st.markdown("# order by week")
        fig4 = order_by_week(df1)
        st.plotly_chart(fig4, user_container_width = True)
        
    with st.container():
        st.markdown("# order share by week")
        fig5=order_share_by_week(df1)
        st.plotly_chart( fig5, user_container_width= True)

with tab3:
    st.markdown("# Country Maps")
    country_maps(df1)


        
