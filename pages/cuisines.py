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

st.set_page_config( page_title='Visão Tipos de Cozinhas', page_icon='🧑‍🍳', layout='wide' )

# --------------------------------------------------------------------------------
# Funções
# --------------------------------------------------------------------------------

# função para plotar gráficos do top 10 melhores/piores tipos culinários
def best_worst_10_restaurant_by_cuisines( df1, condicao ):
    if condicao == 'melhor':
        ordenacao = False
    else:
        ordenacao = True
    
    df_aux = ( df1.loc[:, ['cuisines', 'aggregate_rating']]
                  .groupby( 'cuisines' )
                  .mean()
                  .sort_values( 'aggregate_rating', ascending=ordenacao )
                  .reset_index() )
    df_aux['aggregate_rating'] = np.round( df_aux['aggregate_rating'], 1) 
    df_aux = df_aux.head(10)

    fig = px.bar( df_aux, x='cuisines', y='aggregate_rating', 
                 text='aggregate_rating', 
                 labels=({'cuisines':'Tipos de Culinária', 'aggregate_rating':'Média da Avaliação Média'} ), height=400 )
    fig.update_traces( texttemplate='%{text:.2s}', textposition='outside' )
    fig.update_layout( uniformtext_minsize=8, uniformtext_mode='hide' )
    
    return fig

# função para fazer as métricas dos melhores restaurantes por tipo de culinária e a sua nota
def best_cuisines( df1, culinaria ):
    linhas_selecionadas = df1['cuisines'] == culinaria
    culinaria_italiana_avaliacoes = ( df1.loc[linhas_selecionadas, ['restaurant_name', 'restaurant_id', 'aggregate_rating']]
                                         .sort_values( ['aggregate_rating', 'restaurant_id'], ascending=[False, True] )
                                         .reset_index() )
    text_ = ( culinaria ) + ': ' + ( culinaria_italiana_avaliacoes["restaurant_name"][0] )
    nota = ( culinaria_italiana_avaliacoes["aggregate_rating"][0]).astype( str ) + ( '/5.0' )
    
    return text_, nota


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
image = Image.open( 'logo.png' )
st.sidebar.image( image, width=280 )

st.sidebar.subheader( 'Filtros' )

country_options = st.sidebar.multiselect(
                    'Escolha os países que deseja visulizar as Culinárias',
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
    st.markdown( '### Melhores Restaurantes dos Principais tipos Culinários' )
    
    col1, col2, col3, col4, col5, col6 = st.columns( 6 )
    
    with col1:
        text_, nota = best_cuisines( df1, 'Italian' )
        col1.metric( text_, nota )

    with col2:
        text_, nota = best_cuisines( df1, 'American' )
        col2.metric( text_, nota )
    
    with col3:
        text_, nota = best_cuisines( df1, 'Arabian' )
        col3.metric( text_, nota )
        
    with col4:
        text_, nota = best_cuisines( df1, 'Japanese' )
        col4.metric( text_, nota )
        
    with col5:
        text_, nota = best_cuisines( df1, 'Home-made' )
        col5.metric( text_, nota )
    
    with col6:
        text_, nota = best_cuisines( df1, 'Brazilian' )
        col6.metric( text_, nota )
        
        
with st.container():
    st.markdown( '### Top 20 Melhores Restaurantes' )
    cols = ['restaurant_id', 'restaurant_name', 'country_name', 'city', 'cuisines', 'average_cost_for_two', 'aggregate_rating', 'votes', 'currency']
    df_aux = ( df1.loc[:, cols]
                  .sort_values( ['aggregate_rating', 'votes', 'restaurant_id'], ascending=[False, False, True] )
                  .reset_index() )
    df_aux = df_aux.head(20)
    st.table( df_aux )


with st.container():
    
    col1, col2 = st.columns(2)
    
    with col1:
        col1.markdown('### Top 10 Melhores Tipos de Culinárias')
        fig = best_worst_10_restaurant_by_cuisines( df1, 'melhor' )
        col1.plotly_chart( fig, use_container_width=True )
        
        
    with col2:
        col2.markdown('### Top 10 Piores Tipos de Culinárias')
        fig = best_worst_10_restaurant_by_cuisines( df1, 'pior' )
        col2.plotly_chart( fig, use_container_width=True )
