import pandas as pd
import numpy as np
import statistics
import plotly.express as px
from haversine import haversine
import streamlit as st
from PIL import Image
import folium
from streamlit_folium import folium_static
st.set_page_config( page_title='Visão Empresa', page_icon='📈', layout='wide' )

st.session_state['answer'] = ''
if  st.session_state['answer'] in realans:
        answerStat = "correct"
elif st.session_state['answer'] not in realans:
        answerStat = "incorrect"

df_raw = pd.read_csv('train.csv')
df = df_raw.copy()

# Remover spaco da string
df['ID'] = df['ID'].str.strip()
df['Delivery_person_ID'] = df['Delivery_person_ID'].str.strip()

# Excluir as linhas com a idade dos entregadores vazia
# ( Conceitos de seleção condicional )
linhas_vazias = df['Delivery_person_Age'] != 'NaN '
df = df.loc[linhas_vazias, :]

# Conversao de texto/categoria/string para numeros inteiros
df['Delivery_person_Age'] = df['Delivery_person_Age'].astype( int )

# Conversao de texto/categoria/strings para numeros decimais
df['Delivery_person_Ratings'] = df['Delivery_person_Ratings'].astype( float )

# Conversao de texto para data
df['Order_Date'] = pd.to_datetime( df['Order_Date'], format='%d-%m-%Y' )

# Remove as linhas da culuna multiple_deliveries que tenham o 
# conteudo igual a 'NaN '
linhas_vazias = df['multiple_deliveries'] != 'NaN '
df = df.loc[linhas_vazias, :]
df['multiple_deliveries'] = df['multiple_deliveries'].astype( int )

# Comando para remover o texto de números
df = df.reset_index( drop=True )

# Retirando os numeros da coluna Time_taken(min)
#df['Time_taken(min)'] = df['Time_taken(min)'].apply(lambda x: re.findall( r'\d+', x))

# Retirando os espaços da coluna Festival
df['Festival'] = df['Festival'].str.strip()

pedidos_dia = df.loc[:,['ID','Order_Date']].groupby( 'Order_Date' ).count().reset_index()
px.bar( pedidos_dia, x = 'Order_Date', y = 'ID')
print('estouaqui')

#=====================
#streamlit
st.header('Marketplace Visão do cliente')

#=====================
#Barra lateral
#=====================

image = Image.open(r'C:\Users\kmetzker\Documents\Projetos\.vscode\logo.jpg')
st.sidebar.image(image,width=40)
st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('## Best delivery in Town')

st.sidebar.markdown(' ## Selecione uma data para visualizar')
date_slider = st.sidebar.slider('Até qual valor?',
                                value = pd.datetime(2022, 3, 13),
                                min_value = pd.datetime(2022, 2, 11 ),
                                max_value = pd.datetime(2022, 4, 6),
                                format = 'DD-MM-YYYY')
st.header(date_slider)
st.sidebar.markdown('''---''')
traffic_options = st.sidebar.multiselect(
    'Quais as condições de trânsito?',
    ('Baixo', 'Médio','Alto','Congestionamento'))
st.sidebar.markdown('''---''')

linhas_selecionadas = df['Order_Date'] < date_slider #filtrar do inicio até essa data
df= df.loc[linhas_selecionadas, :]
#st.dataframe ( df )

'''linhas_selecionadas =  df['Road_traffic_density'].isin( traffic_options )
df= df.loc[linhas_selecionadas, :]
'''
st.dataframe ( df )


#=====================
# Layout
#=====================
tab1, tab2, tab3 = st.tabs(['Visão Cliente', 'Visão Gerencial', 'Visão Geográfica'])

with tab1:
    with st.container():
        st.markdown('## Orders by day')
        pedidos_dia = df.loc[:,['ID','Order_Date']].groupby( 'Order_Date' ).count().reset_index()
        fig = px.bar ( pedidos_dia, x = 'Order_Date', y = 'ID')
        st.plotly_chart(fig, use_container_width=True)
        
        with st.container():
            col1, col2 = st.columns (2)
            with col1:
                st.markdown('## Orders by City')
                aux = df.loc[:, ['ID','City', 'Road_traffic_density']].groupby(['Road_traffic_density', 'City']).count().reset_index()
                fig = px.scatter(aux, x= 'City', y= 'ID')
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                st.markdown('## Orders by Traffic')
                aux = df[['ID', 'Road_traffic_density']].groupby('Road_traffic_density').count().reset_index()
                fig = px.pie(aux, values = 'ID', names = 'Road_traffic_density')
                st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.markdown('## Order by Week')
    with st.container():
        df['week_of_year'] = df['Order_Date'].dt.strftime('%U')
        aux1 = df.loc[:,['ID','week_of_year']].groupby('week_of_year').count().reset_index()
        aux2 = df.loc[:,['Delivery_person_ID','week_of_year']].groupby('week_of_year').nunique().reset_index()

        aux = pd.merge( aux1, aux2, how = 'inner')
        aux ['order_by_delivery'] = aux['ID']/aux['Delivery_person_ID']
        fig = px.line( aux, y = 'order_by_delivery' , x = 'week_of_year')
        
        st.plotly_chart( fig, use_container_width=True)
        
        aux = df.loc[:,['week_of_year', 'ID']].groupby('week_of_year').count().reset_index()
        fig = px.bar (aux, x= 'week_of_year', y = 'ID')
        st.plotly_chart( fig, use_container_width=True)
        
with tab3:
    st.markdown('Country Maps')

    aux = df.loc[:,['City', 'Road_traffic_density','Delivery_location_latitude','Delivery_location_longitude']].groupby(['City', 'Road_traffic_density']).median().reset_index()
    aux = aux.loc[aux['City'] != 'Nan', :]
    aux = aux.loc[aux['Road_traffic_density'] != 'Nan', :]

    map = folium.Map()
    
    for index, location_info in aux.iterrows():
        folium.Marker( [location_info['Delivery_location_latitude'],
                      location_info['Delivery_location_longitude']],
                      popup = location_info[['City','Road_traffic_density']] ).add_to( map )
    folium_static (map, width = 1024 , height = 600)  
