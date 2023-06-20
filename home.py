import streamlit as st
from PIL import Image

st.set_page_config(
    page_title = 'Home',
    page_icon = '🎲'
)

image = Image.open(r'C:\Users\kmetzker\Documents\Projetos\.vscode\logo.jpg')
st.sidebar.image(image,width=40)
st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('## Best delivery in Town')

st.sidebar.markdown ('Curry Company')
st.sidebar.markdown ('## Fastest Delivery in town')
st.sidebar.markdown ('''---''')

st.write ('## Curry Company Growth Dashboard')

st.markdown(
    """
    Growth Dashboard foi construído para acompanhar as métricas de crescimento dos Entregadores e Restaurantes.
    ### Como utilizar esse Growth Dashboard?
    - Visão Empresa:
        - Visão Gerencial: Métricas gerais de comportamento.
        - Visão Tática: Indicadores semanais de crescimento.
        - Visão Geográfica: Insights de geolocalização.
    - Visão Entregador:
        - Acompanhamento dos indicadores semanais de crescimento
    - Visão Restaurante:
        - Indicadores semanais de crescimento dos restaurantes
    ### Ask for Help
    - Time de Data Science no Discord

""" )
