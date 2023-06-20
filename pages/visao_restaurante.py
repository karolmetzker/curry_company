import pandas as pd
import numpy as np
import statistics
import plotly.express as px
from haversine import haversine
import streamlit as st
from PIL import Image
import folium
from streamlit_folium import folium_static
import datetime
import plotly.graph_objects as go

st.set_page_config( page_title='Visão Restaurantes', page_icon='🍽️', layout='wide' )

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

# 6. Removendo os espacos dentro de strings/texto/object

df.loc[:, 'ID'] = df.loc[:, 'ID'].str.strip()
df.loc[:, 'Road_traffic_density'] = df.loc[:, 'Road_traffic_density'].str.strip()
df.loc[:, 'Type_of_order'] = df.loc[:, 'Type_of_order'].str.strip()
df.loc[:, 'Type_of_vehicle'] = df.loc[:, 'Type_of_vehicle'].str.strip()
df.loc[:, 'City'] = df.loc[:, 'City'].str.strip()
df.loc[:, 'Festival'] = df.loc[:, 'Festival'].str.strip()


#Retirando os numeros da coluna Time_taken(min)
df['Time_taken(min)'] = df['Time_taken(min)'].apply(lambda x: x.split( '(min) ')[1])
df['Time_taken(min)'] = df['Time_taken(min)'].str.replace('(', '').str.replace(')', '')
df['Time_taken(min)']  = df['Time_taken(min)'].astype( int )


# Retirando os espaços da coluna Festival
df['Festival'] = df['Festival'].str.strip()

pedidos_dia = df.loc[:,['ID','Order_Date']].groupby( 'Order_Date' ).count().reset_index()
px.bar( pedidos_dia, x = 'Order_Date', y = 'ID')
print('estouaqui')
#=====================
#streamlit
st.header('Marketplace Visão Restaurantes')


#=====================
#Barra lateral
#=====================

image = Image.open('logo.jpg')
st.sidebar.image(image,width=40)
st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('## Best delivery in Town')

st.sidebar.markdown(' ## Selecione uma data para visualizar')
date_slider = st.sidebar.slider('Até qual valor?',
                                value = datetime.datetime(2022, 3, 13),
                                min_value = datetime.datetime(2022, 2, 11 ),
                                max_value = datetime.datetime(2022, 4, 6),
                                format = 'DD-MM-YYYY')
st.header(date_slider)
st.sidebar.markdown('''---''')
traffic_options = st.sidebar.multiselect(
    'Quais as condições de trânsito?',
    ('Baixo', 'Médio','Alto','Congestionamento'))
st.sidebar.markdown('''---''')


#=====================
# Layout
#=====================

tab1, tab2, tab3 = st.tabs(['Visão Cliente', 'Visão Gerencial', 'Visão Geográfica'])

with tab1:
    
    with st.container():
        st.markdown('## Metrics')
        col1, col2 = st.columns (2)
        with col1:
            aux = df.loc[0:10, ['Restaurant_latitude', 'Restaurant_longitude','Delivery_location_latitude', 'Delivery_location_longitude']].apply(lambda x: haversine((x['Restaurant_latitude'], x['Restaurant_longitude']), (x['Delivery_location_latitude'], x['Delivery_location_longitude'])),axis = 1)
            aux = round(aux.mean(), 2)
            col1.metric('Distância média',aux)
            
        
            entregadores = df['Delivery_person_ID'].nunique()
            col1.metric('Entregadores ',entregadores)
            
        with col2:
            aux = round(df.loc[df['Festival'] =='No','Time_taken(min)'].mean(), 2)
            col2.metric('Média de tempo sem Festival',aux)
            
            aux2 = round(df.loc[df['Festival'] =='Yes','Time_taken(min)'].mean(), 2)
            col2.metric('Média de tempo com Festival',aux2)
            
        
    with st.container():
        st.markdown('## Time Taken Mean')   
        aux = df.groupby('City').agg({'Time_taken(min)': ['mean', 'std']}).reset_index()
        aux.columns = ['City', 'Mean', 'Std']
        fig = px.pie(aux, values='Mean', names='City')
        st.plotly_chart(fig, use_container_width=True)
        
with st.container():
        st.markdown( """---""" )
        st.title( "Distribuição do Tempo" )
        
        df_aux = df.loc[:, ['City', 'Time_taken(min)']].groupby( 'City' ).agg( {'Time_taken(min)': ['mean', 'std']} )
        df_aux.columns = ['avg_time', 'std_time']
        df_aux = df_aux.reset_index()

        fig = go.Figure() 
        fig.add_trace( go.Bar( name='Control', x=df_aux['City'], y=df_aux['avg_time'], error_y=dict(type='data', array=df_aux['std_time']))) 
        fig.update_layout(barmode='group') 

        st.plotly_chart( fig )
            
        

        
with st.container():
        st.markdown( """---""" )
        
        
        #col1, col_extra, col2 = st.columns( 3, gap ="large" )
        with col1:
            cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_latitude', 'Restaurant_longitude']
            df['distance'] = df.loc[:, cols].apply( lambda x: 
                                        haversine(  (x['Restaurant_latitude'], x['Restaurant_longitude']), 
                                                    (x['Delivery_location_latitude'], x['Delivery_location_longitude']) ), axis=1 )

            avg_distance = df.loc[:, ['City', 'distance']].groupby( 'City' ).mean().reset_index()
            fig = go.Figure( data=[ go.Pie( labels=avg_distance['City'], values=avg_distance['distance'], pull=[0, 0.1, 0])])
            st.plotly_chart( fig )

            
        with col2:
            df_aux = ( df.loc[:, ['City', 'Time_taken(min)', 'Road_traffic_density']]
                          .groupby( ['City', 'Road_traffic_density'] )
                          .agg( {'Time_taken(min)': ['mean', 'std']} ) )

            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()

            fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='avg_time',
                              color='std_time', color_continuous_scale='RdBu',
                              color_continuous_midpoint=np.average(df_aux['std_time'] ) )
            st.plotly_chart( fig )
        
        
