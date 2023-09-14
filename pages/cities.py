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

st.set_page_config( page_title='Visão Cidades', page_icon='🏙️', layout='wide' )

# --------------------------------------------------------------------------------
# Funções
# --------------------------------------------------------------------------------
def top_10_best_or_worst_restaurant_by_city( df1, nota, maior_ou_menor ):
    if maior_ou_menor == 'maior':
        linhas_selecionadas = df1['aggregate_rating'] >= nota
        ordenador = False
    else:
        linhas_selecionadas = df1['aggregate_rating'] <= nota
        ordenador = True
    
    #linhas_selecionadas = df1['aggregate_rating'] operador nota
    df_aux = ( df1.loc[linhas_selecionadas, ['city', 'country_name', 'restaurant_id']]
              .groupby( ['city', 'country_name'] )
              .nunique()
              .sort_values( 'restaurant_id', ascending=ordenador )
              .reset_index() )
    df_aux = df_aux.head( 10 )
    fig = px.bar( df_aux, x='city', y='restaurant_id', 
                 text='restaurant_id', 
                 color='country_name',
                 labels=({'city':'País', 'restaurant_id':'Quantidade de Restaurantes', 'country_name': 'País'} ), height=400 )
    fig.update_traces( texttemplate='%{text:.2s}', textposition='outside' )
    fig.update_layout( uniformtext_minsize=8, uniformtext_mode='hide' )
    return fig


def top_10_restaurant_or_cuisines_by_cities( df1, coluna ):
    if coluna == 'restaurant_id':
        label = 'Quantidade de Restaurantes'
    else:
        label = 'Quantidade de Tipos de Culinários Únicos'
    
    df_aux = ( df1.loc[:, ['city', 'country_name', coluna]]
              .groupby( ['city', 'country_name'] )
              .nunique()
              .sort_values( coluna, ascending=False )
              .reset_index() )
    df_aux = df_aux.head( 10 )
    fig = px.bar( df_aux, x='city', y=coluna, 
                 text=coluna, 
                 color='country_name', 
                 labels=( {'city':'País', coluna:label, 'country_name': 'País'} ), height=400 )
    fig.update_traces( texttemplate='%{text:.2s}', textposition='outside' )
    fig.update_layout( uniformtext_minsize=8, uniformtext_mode='hide' )
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
                    'Escolha os países que deseja visulizar as Cidades',
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
    st.markdown( '### Top 10 Cidades com mais Restaurantes na Base de Dados' )
    fig = top_10_restaurant_or_cuisines_by_cities( df1, 'restaurant_id' )
    st.plotly_chart( fig, use_contanier_width=True )
    
with st.container():
    
    col1, col2 = st.columns( 2 )
    
    with col1:
        st.markdown( '### Quantidade de Restaurantes com nota maior que 4 Registrados por Cidade' )
        fig = top_10_best_or_worst_restaurant_by_city( df1, 4, 'maior' )
        st.plotly_chart( fig, use_container_width=True )
    
    
    with col2:
        st.markdown( '### Quantidade de Restaurantes com nota menor que 2.5 Registrados por Cidade' )
        fig = top_10_best_or_worst_restaurant_by_city( df1, 2.5, 'menor' )
        st.plotly_chart( fig, use_container_width=True )


with st.container():
    st.markdown( '###Top 10 Cidades com o maior quantidade de Tipo Culinários Distintos' )
    fig = top_10_restaurant_or_cuisines_by_cities( df1, 'cuisines' )
    st.plotly_chart( fig, use_contanier_width=True )