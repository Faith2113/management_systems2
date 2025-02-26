import streamlit as st
import pandas as pd
import plotly.express as px

# Carregar o arquivo atualizado
df = pd.read_csv("ubs_atualizado.csv", sep=";")

# Verificar e remover linhas com valores nulos nas colunas de Latitude e Longitude
df = df.dropna(subset=['LATITUDE', 'LONGITUDE'])

# Contar a frequência de UBS por estado
df_freq = df['Nome_UF'].value_counts().reset_index()
df_freq.columns = ['Estado', 'Frequência']

# Contar a quantidade de UBS por município
df_municipio_freq = df['Nome_Município'].value_counts().reset_index()
df_municipio_freq.columns = ['Nome_Município', 'Quantidade de UBS']

# Criar o dashboard
st.title("Dashboard de Unidades Básicas de Saúde (UBS)")

# Gráfico de barras - Frequência de UBS por estado
grafico = px.bar(df_freq, x='Estado', y='Frequência', 
                 title='Frequência de UBS por Estado', 
                 labels={'Estado': 'Estado', 'Frequência': 'Número de UBS'},
                 text_auto=True)
st.plotly_chart(grafico)

# Gráfico de pizza - Distribuição percentual de UBS por estado
grafico_pizza = px.pie(df_freq, 
                       names='Estado', 
                       values='Frequência', 
                       title='Distribuição Percentual de UBS por Estado',
                       labels={'Estado': 'Estado', 'Frequência': 'Número de UBS'},
                       hole=0.3)  # Adicionando o "buraco" no meio para torná-lo um gráfico de pizza
st.plotly_chart(grafico_pizza)

# Filtro para estados específicos
estados = st.multiselect("Selecione os estados", df_freq['Estado'].unique())
if estados:
    df_filtrado = df[df['Nome_UF'].isin(estados)]
    st.write(df_filtrado)
    
    # Criar mapa interativo de dispersão
    mapa = px.scatter_geo(df_filtrado, lat='LATITUDE', lon='LONGITUDE', 
                          hover_name='Nome_UF', 
                          scope="south america",  # Pode ser ajustado para outras regiões
                          labels={'Nome_UF': 'Estado'},
                          opacity=0.7, 
                          template="plotly_dark",
                          projection="natural earth")  # Melhor projeção para exibir grandes áreas

    # Ajustar o zoom e a centralização do mapa para exibir todas as UBS
    mapa.update_geos(
        visible=True, 
        resolution=110, 
        showcoastlines=True, 
        coastlinecolor="Black", 
        showland=True, 
        landcolor="white", 
        showsubunits=True, 
        subunitcolor="grey"
    )
    
    st.plotly_chart(mapa)
else:
    st.write("Selecione pelo menos um estado para visualizar as UBS no mapa.")

# Controle deslizante para filtrar municípios com um número mínimo de UBS
min_ubs = st.slider("Selecione o número mínimo de UBS por município", 
                    min_value=int(df_municipio_freq['Quantidade de UBS'].min()), 
                    max_value=int(df_municipio_freq['Quantidade de UBS'].max()), 
                    value=0, step=1)

# Filtrar municípios com o número mínimo de UBS
df_municipio_filtrado = df_municipio_freq[df_municipio_freq['Quantidade de UBS'] >= min_ubs]

# Gráfico de histograma da quantidade de UBS por município
grafico_histograma = px.histogram(df_municipio_filtrado, 
                                   x='Quantidade de UBS', 
                                   title='Histograma da Quantidade de UBS por Município',
                                   labels={'Quantidade de UBS': 'Número de UBS'},
                                   nbins=30)
st.plotly_chart(grafico_histograma)
