import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="Home",
    page_icon="*",
    layout='wide'
)

#image_path="/Users/eduzz_378/Desktop/repos/"
image=Image.open(image_path + 'logo.png')
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('## Fastest delivery in town')
st.sidebar.markdown("""---""")

st.write("# Curry Company Growth Dashboard")

st.markdown(
    """
    Growth Dashboard foi construido para acompanhar as metricas de crescimento dos entregadores e restaurantes.
    ### como utilizar este GD?
    - visao empresa:
        - visao gerencial: metricas gerais de comportamento
        - visao tatica: indicadores semanais de crescimento
        - visao geografica: insights de geolocalizacao
    - visao entregador:
        - acompanhamento dos indicadores semanais de crescimento
    - visao restaurante:
        - indicadores semanais de crescimento dos restaurantes
    ### ask for help
    - time de data science no Discord
        - @x
        """
)

