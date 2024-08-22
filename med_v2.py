import os
import warnings
import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px
import plotly.figure_factory as ff
import requests
import zipfile
import io

warnings.filterwarnings('ignore')
st.set_page_config(page_title="Medellín Accidents WebApp", page_icon=":racing_motorcycle:", layout="wide")

st.title("Accidentes de Transito en Medellín y su zona Metropolitana 🏍️💥🚗")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)
st.markdown('Esta aplicación es un tablero de control hecho con streamlit que puede ser usado'
            '\npara analizar accidentes de transito ocurridos en Medellín y su area metropolitana en los años 2014 - 2021 🏍️💥🚗')

url = "https://github.com/CJ7MO/streamlit-Med/blob/main/df.zip?raw=true"
response = requests.get(url)
if response.status_code == 200:
    # Crear un objeto ZipFile desde los datos de respuesta
    zip_file = zipfile.ZipFile(io.BytesIO(response.content))

    # Extraer el archivo df.csv del archivo zip
    zip_file.extractall()

    # Cerrar el archivo zip
    zip_file.close()

@st.cache_data(persist=True)
def load_data():
    data = pd.read_csv("df.csv", encoding='UTF-8-SIG', low_memory=False, parse_dates=[['FECHA', 'HORA']])
    data.dropna(subset=['LATITUD', 'LONGITUD'], inplace=True)
    lowercase= lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    data.rename(columns={'fecha_hora': 'fecha/hora','latitud':'lat', 'longitud':'lon'}, inplace=True)
    data.replace('Caída Ocupante','Caída de Ocupante',inplace=True)
    data.replace('Caida Ocupante', 'Caída de Ocupante',inplace=True)
    data.replace('Caida de Ocupante', 'Caída de Ocupante',inplace=True)
    data.replace('Choque ', 'Choque', inplace=True)
    data['fecha/hora'] = pd.to_datetime(data['fecha/hora'], format="%d/%m/%Y %I:%M%p")
    data = data[~data.duplicated(subset=['lat', 'lon'])]
    return data

data=load_data()
months = {1:'ENERO',
          2:'FEBRERO',
          3:'MARZO',
          4:'ABRIL',
          5:'MAYO',
          6:'JUNIO',
          7:'JULIO',
          8:'AGOSTO',
          9:'SEPTIEMBRE',
          10:'OCTUBRE',
          11:'NOVIEMBRE',
          12:'DICIEMBRE'}
data['mes_nombre'] = data['mes'].map(months)

st.header('¿Cual es la clase de accidente más común en Medellín?')
clases = ['Atropello', 'Choque', 'Caída de Ocupante', 'Otro', 'Volcamiento',
       'Incendio', 'Choque y Atropello']
clase = st.selectbox('Selecciona la clase de Accidente: ', clases)
st.map(data.query('clase == @clase')[['lat', 'lon']].dropna(how='any'))

st.header('¿Cuántos accidentes ocurren en Medellín en una hora puntual?')
hora = st.slider('Hora a visualizar: ', 0, 23)
original_data = data
data = data[data['fecha/hora'].dt.hour == hora]

st.markdown('Accidentes ocurridos entre la hora %i:00 y %i:00' % (hora, (hora+1) % 24))

puntomedio = (np.average(data['lat']), np.average(data['lon']))
st.write(pdk.Deck(
    map_style='mapbox://styles/mapbox/light-v9',
    initial_view_state={
        'latitude':puntomedio[0],
        'longitude':puntomedio[1],
        'zoom':11,
        'pitch':50
    },
    layers=[
        pdk.Layer(
            'HexagonLayer',
            data = data[['fecha/hora', 'lat', 'lon']],
            get_position=['lon','lat'],
            radius=100,
            extruded=True,
            pickable=True,
            elevation_scale=10,
            elevation_range=[0,100]
        ),
    ],
))

st.subheader('Desglose por minutos entre %i:00 y %i:00' %(hora, (hora+1)% 24))
filtered = data[
    (data['fecha/hora'].dt.hour >= hora) & (data['fecha/hora'].dt.hour<(hora+1))
]
hist = np.histogram(filtered['fecha/hora'].dt.minute, bins=60, range=(0,60))[0]
chart_data = pd.DataFrame({'minuto': range(60), 'accidentes':hist})
fig = px.bar(chart_data, x='minuto', y='accidentes', hover_data=['minuto', 'accidentes'], height=400)
st.plotly_chart(fig, use_container_width=True)

select = st.selectbox('Gravedad del Accidente', ['HERIDO', 'SOLO DAÑOS', 'MUERTO'])
col1, col2 = st.columns(2)
with col1:
    st.header('Top 10 Direcciones por Gravedad del Accidente')
    if select == 'HERIDO':
        filtered_data = original_data[original_data['gravedad']=='HERIDO']
        st.write(filtered_data['direccion'].value_counts().head(10))
    if select == 'SOLO DAÑOS':
        filtered_data = original_data[original_data['gravedad']=='SOLO DAÑOS']
        st.write(filtered_data['direccion'].value_counts().head(10))
    if select == 'MUERTO':
        filtered_data = original_data[original_data['gravedad']=='MUERTO']
        st.write(filtered_data['direccion'].value_counts().head(10))

with col2:
    st.header('Top 10 Comunas por Gravedad del Accidente')
    if select == 'HERIDO':
        filtered_data = original_data[original_data['gravedad']=='HERIDO']
        st.write(filtered_data['comuna'].value_counts().head(10))
    if select == 'SOLO DAÑOS':
        filtered_data = original_data[original_data['gravedad']=='SOLO DAÑOS']
        st.write(filtered_data['comuna'].value_counts().head(10))
    if select == 'MUERTO':
        filtered_data = original_data[original_data['gravedad']=='MUERTO']
        st.write(filtered_data['comuna'].value_counts().head(10))


if st.checkbox('Mostrar datos', False):
    st.subheader('Datos')
    st.write(data)



