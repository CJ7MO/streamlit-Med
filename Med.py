import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px
url = r'C:\Users\CJMO7\PycharmProjects\streamlit-med\df.csv'

st.title('Accidentes de Transito en Medellín y su zona Metropolitana')
st.markdown('Esta aplicación es un tablero de control hecho con streamlit que puede ser usado'
            '\npara analizar accidentes de transito ocurridos en Medellín y su area metropolitana en los años 2014 - 2021 🏍️💥🚗')

@st.cache_data(persist=True)
def load_data(nrows):
    data = pd.read_csv(url, encoding='UTF-8-SIG', low_memory=False, nrows=nrows, parse_dates=[['FECHA', 'HORA']])
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

data=load_data(350000)

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
st.write(fig)

st.header('Top 5 Direcciones por Gravedad del Accidente')
select = st.selectbox('Gravedad del Accidente', ['HERIDO', 'SOLO DAÑOS', 'MUERTO'])

if select == 'HERIDO':
    filtered_data = original_data[original_data['gravedad']=='HERIDO']
    st.write(filtered_data['direccion'].value_counts().head())
if select == 'SOLO DAÑOS':
    filtered_data = original_data[original_data['gravedad']=='SOLO DAÑOS']
    st.write(filtered_data['direccion'].value_counts().head())
if select == 'MUERTO':
    filtered_data = original_data[original_data['gravedad']=='MUERTO']
    st.write(filtered_data['direccion'].value_counts().head())

st.header('Top 5 Comunas por Gravedad del Accidente')
if select == 'HERIDO':
    filtered_data = original_data[original_data['gravedad']=='HERIDO']
    st.write(filtered_data['comuna'].value_counts().head())
if select == 'SOLO DAÑOS':
    filtered_data = original_data[original_data['gravedad']=='SOLO DAÑOS']
    st.write(filtered_data['comuna'].value_counts().head())
if select == 'MUERTO':
    filtered_data = original_data[original_data['gravedad']=='MUERTO']
    st.write(filtered_data['comuna'].value_counts().head())


if st.checkbox('Mostrar datos', False):
    st.subheader('Datos')
    st.write(data)
