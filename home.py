# imports


import folium
import inflection
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
import plotly.graph_objects as go

from PIL import Image
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static 


st.set_page_config(
    page_title='Home',
    page_icon='📈',
    layout='wide'
)

st.write( '# Zomato Dashboard' )

st.markdown("""
    ## O melhor lugar para encontrar seu mais novo restaurante favorito!
    ### Temos as seguintes marcas dentro da nossa plataforma:
""")


# --------------------------------------------------------------------------------
# Funções
# --------------------------------------------------------------------------------

# função para desenhar o mapa com os restaurantes
def map_( df1 ):
    columns = ['city', 'aggregate_rating', 'latitude', 'longitude', 'cuisines', 'average_cost_for_two', 'restaurant_name', 'votes']

    data_plot = ( df1.loc[:, columns] )
    
    # Desenhar o mapa
    map_ = folium.Map( zoom_start=11 )

    marker_cluster = MarkerCluster().add_to(map_)

    for index, location_info in data_plot.iterrows():

        folium.Marker( [location_info['latitude'],
                    location_info['longitude']],
                    tiles='Cartodb Positron',
                    icon=folium.Icon(color=df1["color_name"][index], icon="ok-sign"),
                    popup = 'nome:{}<br>cidade:{}<br>nota:{}<br>culinária:{}<br>preço p/ dois:{}<br>votos:{}'.format(df1["restaurant_name"][index], df1["city"][index], df1["aggregate_rating"][index], df1["cuisines"][index], df1["average_cost_for_two"][index], df1["votes"][index] ) ).add_to( marker_cluster )
    mapa = folium_static( map_ )
    return mapa

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
st.sidebar.markdown( """---""" )
image = Image.open( 'logo.png' )
st.sidebar.image( image, width=280 )
st.sidebar.markdown( """---""" )

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
    
    col1, col2, col3, col4, col5= st.columns( 5 )
    
    with col1:
        restaurantes_unicos = df1['restaurant_id'].nunique()
        col1.metric( 'Restaurantes Cadastrados', restaurantes_unicos )
        
    with col2:
        paises_unicos = df1['country_name'].nunique()
        col2.metric( 'Países Cadastrados', paises_unicos )
        
    with col3:
        cidades_unicas = df1['city'].nunique()
        col3.metric( 'Cidades Cdastradas', cidades_unicas )
        
    with col4:
        total_votos = df1['votes'].sum()
        col4.metric( 'Avaliações Feitas na Plataforma', total_votos )
        
    with col5:
        culinarias_unicas = df1['cuisines'].nunique()
        col5.metric( 'Tipos de Culinárias Oferecidos', culinarias_unicas )

        
with st.container():
    mapa = map_( df1 )
    st.map(mapa, use_container_width=True )
