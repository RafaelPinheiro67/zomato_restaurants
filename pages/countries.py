# imports

from PIL import Image

import inflection
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
import plotly.graph_objects as go

st.set_page_config( page_title='Visão Países', page_icon='🌎', layout='wide' )

# --------------------------------------------------------------------------------
# Funções
# --------------------------------------------------------------------------------

def country_by_votes_or_cost_for_two( df1, coluna ):
    df_aux = df1.loc[:, ['country_name', coluna]].groupby( 'country_name' ).mean().sort_values( coluna, ascending=False ).reset_index()
    
    
    # definição do label y
    if coluna == 'votes':
        label = 'Quantidade Média de Avaliações'
    else:
        label = 'Média de Preço de um prato para duas pessoas'
    fig = px.bar( df_aux, x='country_name', y=coluna, 
                 text=coluna,
                 labels=({'country_name':'País', coluna:label}), height=500 )
    fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
    fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
    return fig

def country_by_restaurant_or_city( df1, coluna ):
    # Quantidade de restaurantes/cidades por país
    df_aux = df1.loc[:, ['country_name', coluna]].groupby( 'country_name' ).nunique().sort_values( coluna, ascending=False ).reset_index()

    # definição do label y
    if coluna == 'restaurant_id':
        label = 'Restaurantes'
    else:
        label = 'Cidades'
    # gráfico
    fig = px.bar( df_aux, x='country_name', y=coluna, 
                 text=coluna, 
                 labels=( {'country_name':'País', coluna:f'Quantidade de {label}'} ), height=500 )
    fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
    fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
    return fig


# função para excluir colunas com um único valor, removação de dados duplicados, remoção de dados faltantes e definindo apenas um tipo de culinária para a coluna 'cuisines'
def clean_code( df1 ):
    
    # removendo a coluna ['Switch to order menu'] pois só tem um único valor
    df1 = df1.drop( 'switch_to_order_menu', axis=1 )
    
    # removendo os dados duplicados
    df1 = df1.drop_duplicates()
    
    # removendo os dados faltantes
    df1 = df1.dropna( axis = 0, how ='any' )
    
    # categorizando todos os restaurantes somente por um tipo de culinária
    df1["cuisines"] = df1.loc[:, "cuisines"].apply( lambda x: x.split( "," )[0] )
    
    return df1
    
# função para renomear as colunas
def rename_columns( df1 ):
    df = df1.copy()
    title = lambda x: inflection.titleize( x )
    snakecase = lambda x: inflection.underscore( x )
    spaces = lambda x: x.replace( " ", "" )
    cols_old = list( df.columns )
    cols_old = list( map( title, cols_old ) )
    cols_old = list( map( spaces, cols_old ) )
    cols_new = list( map( snakecase, cols_old ) )
    df.columns = cols_new
    return df

# função para criar a coluna ['color_name'] fazendo com que o código da cor vire um cor de fato
COLORS = {
    "3F7E00": "darkgreen",
    "5BA829": "green",
    "9ACD32": "lightgreen",
    "CDD614": "orange",
    "FFBA00": "red",
    "CBCBC8": "darkred",
    "FF7800": "darkred",
}
def color_name( color_code ):
    return COLORS[color_code]

# função para criar a coluna ['country_name'] fazendo com que o código do país vire um país
COUNTRIES = {
    1: "India",
    14: "Australia",
    30: "Brazil",
    37: "Canada",
    94: "Indonesia",
    148: "New Zeland",
    162: "Philippines",
    166: "Qatar",
    184: "Singapure",
    189: "South Africa",
    191: "Sri Lanka",
    208: "Turkey",
    214: "United Arab Emirates",
    215: "England",
    216: "United States of America",
}
def country_name( country_id ):
    return COUNTRIES[country_id]

# função para criação da coluna ['price_type'] baseado na coluna ['price_range']
def create_price_type( price_range ):
    if price_range == 1:
        return 'cheap'
    elif price_range == 2:
        return 'normal'
    elif price_range == 3:
        return 'expensive'
    else:
        return 'gourmet'

    
# ===================================================================================================
# --------------------------------- Inicio da Estrutura lógica do código ----------------------------
# ===================================================================================================
# -----------------------
# import dataset
# -----------------------
df = pd.read_csv( 'dataset/zomato.csv' )

# renomeando as colunas
df1 = rename_columns( df )

# limpando os dados
df1 = clean_code( df1 )

# executando a função color_name para a criação da coluna ['color_name']
df1['color_name'] = df1.loc[:, 'rating_color'].apply( lambda x: color_name( x ) )

# executando a função contry_name para a criação da coluna ['country_name']
df1['country_name'] = df1.loc[:, 'country_code'].apply( lambda x: country_name( x ) )

# executando a função create_price_type para a criação da coluna ['price_type']
df1['price_type'] = df1.loc[:, 'price_range'].apply( lambda x: create_price_type( x ) )


# =======================================
# Barra Lateral
# =======================================
st.header( 'Fome Zero!!!' )

st.sidebar.title( 'Fome Zero' )
image = Image.open( '../logo.png' )
st.sidebar.image( image, width=280 )

st.sidebar.subheader( 'Filtros' )

country_options = st.sidebar.multiselect(
                    'Escolha os países que deseja visulizar os Restaurantes',
                    ['Philippines', 'Brazil', 'Australia', 'United States of America',
                    'Canada', 'Singapure', 'United Arab Emirates', 'India',
                    'Indonesia', 'New Zeland', 'England', 'Qatar', 'South Africa',
                    'Sri Lanka', 'Turkey'],
                    default=['Philippines', 'Brazil', 'Australia', 'United States of America',
                    'Canada', 'Singapure', 'United Arab Emirates', 'India',
                    'Indonesia', 'New Zeland', 'England', 'Qatar', 'South Africa',
                    'Sri Lanka', 'Turkey'] )

# filtro de países
linhas_selecionadas = df1['country_name'].isin( country_options )
df1 = df1.loc[linhas_selecionadas, :]

# =======================================
# Layout no Streamlit
# =======================================


with st.container():
    st.markdown( '### Quantidade de Restaurantes Registrado por País' )
    fig = country_by_restaurant_or_city( df1, 'restaurant_id' )
    st.plotly_chart( fig, use_container_width=True )
    
with st.container():
    st.markdown( '### Quantidade de Cidades Registrado por País' )
    fig = country_by_restaurant_or_city( df1, 'city' )
    st.plotly_chart( fig, use_container_width=True )

    
    
with st.container():
    
    col1, col2 = st.columns( 2 )
    
    with col1:
        st.markdown( '### Média de Avaliações feitas por País' )
        fig = country_by_votes_or_cost_for_two( df1, 'votes' )
        st.plotly_chart( fig, use_container_width=True )
        
    with col2:
        st.markdown( '### Média de Preço de um prato para duas pessoas por País' )
        fig = country_by_votes_or_cost_for_two( df1, 'average_cost_for_two' )
        st.plotly_chart( fig, use_container_width=True )
