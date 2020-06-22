import streamlit as st
import pandas as pd
from unidecode import unidecode

import config

@st.cache
def load_csv(path, sep=";"):
    return pd.read_csv(path, sep=sep)

st.markdown("# La costa este de USA tiene más nombres de ciudades de UK que la costa oeste?")
st.markdown("## Desafío analítico Data & Analytics")

st.markdown("### Análisis Exploratorio")
st.markdown("""
        Para responder está pregunta utilizamos el dataset World Cities Population disponible 
        en: https://public.opendatasoft.com/explore/dataset/worldcitiespop/export
        """)
st.markdown("""
        Uno de los primeros inconvenientes fue tratar de descargar toda la información de ese dataset 
        ya que disponibiliza información de muchos países. Sin embargo, para este desafío solo necesitamos 
        la información de USA y UK. Para resolver esto, en la sección de descargas se pueden aplicar filtros:
        'us' para USA y 'gb' para UK. La información de muestra a continuación:
        """)

raw_load_state = st.text("Loading data Raw Data...")
raw_data = load_csv(config.RAW_DATA_PATH)
raw_load_state.text("Done! (using st.cache)")

if st.checkbox("Show raw data"):
    st.subheader("Primeras 5 filas")
    st.write(raw_data.iloc[:5, :])

st.markdown("""
        Si bien la documentación del dataset no presenta un detalle sobre el esquema de los datos, por sentido común se puede
        determinar el significado de los siguientes campos que son justamente los que se necesitan para el análisis:
        * Country: País
        * City: Ciudad
        * Region: Región donde se ubica la ciudad
        * Population: Habitantes en esa ciudad
        * Latitude: Latitud de la ciudad
        * Longitude: Longitud de la ciudad

        Hay que destacar que la data no trae duplicados.
        """)

st.markdown("""
        Para entender mejor los datos, a continuación, se muestra la cantidad de ciudades registradas para USA y UK, 
        donde se ve una diferencia significativa entre ambas regiones
""")

countries_counter = raw_data["Country"].value_counts()
original_index = countries_counter.index
countries_counter = countries_counter.reset_index()
countries_counter.columns = ["Country", "Number of Cities"]
countries_counter.index = [x.upper() for x in original_index]
st.bar_chart(countries_counter)

st.markdown("### Procesamiento de Texto")
st.markdown("""
            Para averiguar qué nombres de ciudades de UK existen en USA hay que comparar texto, sin embargo, no se puede asegurar que 
            el nombre de las ciudades venga estandarizado, por lo tanto, hay que aplicar un pipeline de procesamiento para comparar
            el texto con mayor seguridad. En esta oportunidad vamos a aplicar las siguientes transformaciones:
            * Convertir a minúscula
            * Eliminar los espacios delante y al final del nombre
            * Eliminar Caracteres especiales

            Esta nueva columna quedará guardada bajo el nombre: 'city_clean'
            """)

code = '''
def process_text(text):
    if isinstance(text, str):
        return unidecode(text.lower().strip())
    else:
        return ""
'''

st.code(code, language='python')

def process_text(text):
    if isinstance(text, str):
        return unidecode(text.lower().strip())
    else:
        return ""

process_data = raw_data.copy()
process_data["clean_city"] = process_data["City"].apply(lambda x: process_text(x))
if st.checkbox("Show processed data"):
    st.subheader("Primeras 5 filas")
    st.write(process_data.iloc[:5, :])

st.markdown("""
            El siguiente paso es separar el dataset global según la región, es decir, guardar lo que corresponde a USA en un dataframe
            y lo que corresponde a UK en otro (de aquí en adelante cuando se habla de USA y UK se hace alusión a estos 
            dataframes respectivamente)
            """)

USA = process_data[process_data["Country"] == "us"]
UK = process_data[process_data["Country"] == "gb"]

if st.checkbox("Show USA data"):
    st.subheader("Primeras 5 filas")
    st.write(USA.iloc[:5, :])

if st.checkbox("Show UK data"):
    st.subheader("Primeras 5 filas")
    st.write(UK.iloc[:5, :])


UK = UK.drop_duplicates(subset=["clean_city"])
st.markdown(f"""
            El siguiente paso es crucial para que el análisis sea correcto, de lo contrario, podría llevar a conclusiones equivocadas.
            Este paso, consiste en eliminar los duplicados de UK considerando sólo la columna 'clean_city' ya que para responder
            responder la pregunta inicial de este desafío no es importante la ubicación geográfica de la ciudad en UK, pero SI lo es en USA.
            Este proceso deja {UK.shape[0]} nombres únicos en UK.
            """)

shared_cities = UK.merge(USA, how="inner", on="clean_city", suffixes=("_uk","_usa"))
st.markdown(f"""
            Para determinar los nombres de ciudades compartidos, se aplica un inner join entre los nombres únicos de UK y los nombres
            (que pueden estar repetidos) de USA sobre la columna 'clean_city'. Esto deja un total de {shared_cities.shape[0]} ciudades 
            en USA que tienen nombre de alguna ciudad en UK las cuales se pueden ver a continuación:
            """)

shared_cities["latitude"] = shared_cities["Latitude_usa"]
shared_cities["longitude"] = shared_cities["Longitude_usa"]
st.map(shared_cities[["latitude","longitude"]])

st.markdown(f"""
            En el gráfico se pueden ver las zonas geográficas  de USA que tienen nombres en común con UK. Estás se reparten
            entre el territorio estadounidense 'tradicional', Alaska y algunas islas como Puerto Rico donde USA tiene presencia.
            A partir del gráfico, se puede ver una tendencia clara en cómo se distribuyen geográficamente los nombres de ciudades que tienen
            en común USA y UK, donde la costa este tiene una concentración mucho mayor de nombres de ciudades de UK. 
            """)

west = shared_cities[shared_cities["latitude"] < 34.4052687]
east = shared_cities[shared_cities["latitude"] >= 34.4052687]

cuo = round(east.shape[0] / west.shape[0], 3)

st.markdown(f"""
            Asumiendo que estados unidos se puede dividir a verticalmente por la latitud: 34.4052687 (según google maps), 
            se puede establecer que la costa este de USA tiene **{cuo}** veces más nombres en común con UK que la costa oeste.
            Por lo tanto, **la hipótesis presentada en este desafío es cierta**.
            """)