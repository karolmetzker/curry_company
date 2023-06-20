import re
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

st.set_page_config( page_title='Visão Entregadores', page_icon='🚚', layout='wide' )

df_raw = pd.read_csv(r'C:\Users\kmetzker\Downloads\archive(3)\train.csv')
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
df['Time_taken(min)']  = df['Time_taken(min)'].astype( int )


# Retirando os espaços da coluna Festival
df['Festival'] = df['Festival'].str.strip()

pedidos_dia = df.loc[:,['ID','Order_Date']].groupby( 'Order_Date' ).count().reset_index()
px.bar( pedidos_dia, x = 'Order_Date', y = 'ID')
print('estouaqui')
#=====================
#streamlit
st.header('Marketplace Visão Entregadores')



#=====================
#Barra lateral
#=====================

image = Image.open(r'C:\Users\kmetzker\Documents\Projetos\.vscode\logo.jpg')
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
        st.title('## Metrics')
        col1, col2, col3, col4 = st.columns (4)
                
        with col1:
            maior_idade = df['Delivery_person_Age'].max()
            col1.metric('Maior de idade', maior_idade)
                
        with col2:

            menor_idade = df['Delivery_person_Age'].min()
            col2.metric('Menor de idade', menor_idade)
                
        with col3:

            pior_condicao = df['Vehicle_condition'].min()
            col3.metric('Pior condicao', pior_condicao)
                
        with col4:

            melhor_condicao = df['Vehicle_condition'].max()
            col4.metric('Melhor condicao', melhor_condicao)
                 
    with st.container():
        st.markdown('''---''')
        st.title ('Avaliacoes')
        col1, col2 = st.columns (2)
        with col1:
            st.markdown( '##### Avalicao media por Entregador' )
            df_avg_ratings_per_deliver = ( df.loc[:, ['Delivery_person_Ratings', 'Delivery_person_ID']]
                                              .groupby( 'Delivery_person_ID' )
                                              .mean()
                                              .reset_index() )
            st.dataframe( df_avg_ratings_per_deliver )
                
        with col2:
            st.markdown( '##### Avaliacao media por transito' )
            df_avg_std_rating_by_traffic = ( df.loc[:, ['Delivery_person_Ratings', 'Road_traffic_density']]
                                                .groupby( 'Road_traffic_density')
                                                .agg( {'Delivery_person_Ratings': ['mean', 'std' ]} ) )

            # mudanca de nome das colunas
            df_avg_std_rating_by_traffic.columns = ['delivery_mean', 'delivery_std']

            # reset do index
            df_avg_std_rating_by_traffic = df_avg_std_rating_by_traffic.reset_index()
            st.dataframe( df_avg_std_rating_by_traffic )
            
            
            
            st.markdown( '##### Avaliacao media por clima' )
            df_avg_std_rating_by_weather = ( df.loc[:, ['Delivery_person_Ratings', 'Weatherconditions']]
                                                .groupby( 'Weatherconditions')
                                                .agg( {'Delivery_person_Ratings': ['mean', 'std']} ) )

            # mudanca de nome das colunas
            df_avg_std_rating_by_weather.columns = ['delivery_mean', 'delivery_std']

            # reset do index
            df_avg_std_rating_by_weather = df_avg_std_rating_by_weather.reset_index()
            st.dataframe( df_avg_std_rating_by_weather )
            
    
    with st.container():
        st.markdown( """---""" )
        st.title( 'Velocidade de Entrega' )
        
        col1, col2 = st.columns( 2 )
        
        with col1:
            st.markdown( '##### Top Entregadores mais rapidos' )
            df2 = ( df.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']]
                       .groupby( ['City', 'Delivery_person_ID'] )
                       .mean()
                       .sort_values( ['City', 'Time_taken(min)'], ascending=True ).reset_index() )

            df_aux01 = df2.loc[df2['City'] == 'Metropolitian', :].head(10)
            df_aux02 = df2.loc[df2['City'] == 'Urban', :].head(10)
            df_aux03 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)

            df3 = pd.concat( [df_aux01, df_aux02, df_aux03] ).reset_index( drop=True )
            st.dataframe( df3 )
            
        with col2:
            st.markdown( '##### Top Entregadores mais lentos' )
            df2 = ( df.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']]
                       .groupby( ['City', 'Delivery_person_ID'] )
                       .mean()
                       .sort_values( ['City', 'Time_taken(min)'], ascending=False ).reset_index() )

            df_aux01 = df2.loc[df2['City'] == 'Metropolitian', :].head(10)
            df_aux02 = df2.loc[df2['City'] == 'Urban', :].head(10)
            df_aux03 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)

            df3 = pd.concat( [df_aux01, df_aux02, df_aux03] ).reset_index( drop=True )
            st.dataframe( df3 )
        