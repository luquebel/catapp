import streamlit as st 
import pandas as pd 
import matplotlib.pyplot as plt 
import numpy as np
import altair as alt
import plotly.express as px
import requests
import streamlit as st
import time

from streamlit_lottie import st_lottie
from wordcloud import WordCloud




# A continuacion la URL original desde donde se tomo el archivo a trabajar:
# https://www.kaggle.com/ruchi798/movies-on-netflix-prime-video-hulu-and-disney/version/2?select=MoviesOnStreamingPlatforms_updated.csv

# Carga de los datos:
streams_df = pd.read_csv('MoviesOnStreamingPlatforms_updated.csv')
original_df=streams_df

# Definicion de la funcion categoriaunica(genero), la cual nos servira para el filtrado por categoria unica de los datos, es decir, si una pelicula es considerada que pertenece a mas de una categoria, por ejemplo, comica y de suspenso, esta se descarta ya que se quiere el estudio solo a las categorias unicas.


def categoriaunica(genero):
    if int(len(genero.split(sep=",")))  == 1:
        return 0
    else:
        return 1
    
    
# Se procede a borrar las columnas que no nos interesan para el estudio a realizar, que no son relevantes:
streams_df=streams_df.drop(['ID','Runtime','Type','Country','Language','Age'], axis=1)


# Se procede a visualizar la cantidad de nulos que presentan el dataframe
a=streams_df.isnull().sum()

source=streams_df.isnull().sum().reset_index()
source.columns.values[0] = "Categorias"
source.columns.values[1] = "Total Nulos"
a=source.columns

# Se procede a eliminar los datos nulos que pueda presentar el dataframe
streams_df=streams_df.dropna()

# A continuacion delimitamos el estudio a categorias de peliculas unicas entre los años 1990 y 2020:

streams_df=streams_df[(streams_df['Year']>=1990) & (streams_df['Year']<=2020) & (streams_df['Genres'].apply(categoriaunica)  ==0) ]


# Visualizamos si tenemos datos duplicados:
dups=streams_df.duplicated(['Title','Year','Netflix','Hulu','Prime Video','Disney+'])
a=streams_df[dups]





#La funcion crearwordsclouds(seleccion,df) se encarga se crear un WordCloud a partir de los datos o parametros dados, en base a las  categorias de peliculas segun el proveedor de streaming.


def crearwordsclouds(seleccion,df):  
    acambiar=df[df[seleccion]==1].groupby(['Genres'])['Genres'].count().idxmax()  
    listastring=df[df[seleccion]==1].groupby(['Genres'])['Genres'].head().tolist()
    categoriaswc = " ".join(listastring)  
    #La categoria que prevalece, a fin de resaltar en el WordCloud, se convierte a Mayuscula
    categoriaswc=categoriaswc.replace(acambiar,acambiar.upper())    

    wordcloud = WordCloud(width=580, height=350, margin=0,contour_width=8, contour_color='firebrick',
                      background_color = "white",max_font_size=120).generate(categoriaswc) 
    fig, ax = plt.subplots()
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")    
    return fig


# A continuacion tenemos a la funcion gbarras(df), la cual genera un grafico de barras, resaltando la categoria que prevalece, segun el proveedor de streaming seleccionado, cuya puntuacion IMDb sea mayor a 6 puntos, calificando de esta manera la categoria de la pelicula como mejor calificacion del publico.

def gbarras(df):
    #dataf=df[(df['IMDb']>6) & (df[opcion]==1)].groupby(['Genres'])[opcion].count().sort_values(ascending=False).head()
    dataf=df[(df['IMDb']>6) & (df[opcion]==1)][['IMDb','Title']].sort_values(by='IMDb',ascending=False).head()
    
    #dataf=dataf.reset_index() 

    mayorcat=dataf['Title'].head(1).max(axis = 0)

    #mayorcat="Drama"
    
    #ver=df[(df['IMDb']>6) & (df[opcion]==1) &(df['Genres']==mayorcat)].groupby(['IMDb','Title','Genres']).count().sort_values(by=['IMDb'],ascending=False)
    #ver=ver.reset_index()

    #nombrepeli=ver['Title'].head(1).max(axis = 0)  

    barra= alt.Chart(dataf).mark_bar().encode( 
           x=dataf.columns[0],
           y=dataf.columns[1],    
           color=alt.condition(
          # f"datum.Genres == '{mayorcat}'",                     
           f"datum.Title == '{mayorcat}'",                     
           alt.value('#154734'),     # highlight a bar with green.
           alt.value('lightgrey'))   # And grey for the rest of the bars    
           ).properties(height=300,width=650) #,title="El Titulo de la pelicula es:    " + nombrepeli)
   
    texto = barra.mark_text(
    align='left',
    baseline='middle',
    dx=4  # Nudges text to right so it doesn't appear on top of the bar
    ).encode(
    text= 'IMDb:N'
    )

    return barra + texto


# Se crea la funcion convstring(cadena), la cual convierte la columna 'Rotten Tomatoes' a numeros enteros, a fin de que se pueda graficar   
def convstring(cadena):
    cadena=cadena.rstrip("%")
    cadena=int(cadena)
    return cadena

# Definicion de la funcion top_pelicula(df,opcion), la cual nos genera un grafico del tipo Sunburst que nos muestra el nombre de la pelicula con la puntuacion mayor en cuanto a calificacion del publico segun el proveedor de streaming

def top_pelicula(df,opcion):
    df=df[df[opcion]==1][['Rotten Tomatoes','Title','Genres','Year']].sort_values(by='Rotten Tomatoes',ascending=False).head()
    df['Rotten Tomatoes'] = df['Rotten Tomatoes'].apply(convstring)     
    fig = px.sunburst(df, path=['Genres','Title'],  values='Rotten Tomatoes', color='Rotten Tomatoes')
    return fig

    
# La siguiente Funcion top_director(df,seleccion) nos permite mostrar atraves de un wordcloud unico ( A fin de resaltar el nombre del director) del director con mayor presencia y puntuacion mas alta, tanto del publico en general como de la critica especializada con mayor presencia en la plataforma seleccionada.

def top_director(df,seleccion):   
    agrupando=df[df[seleccion]==1].groupby(['Directors','IMDb','Rotten Tomatoes']).count() 
    agrupando=agrupando.reset_index() 
    director=agrupando['Directors'].head(1).max()
    director= director.upper()

    wordcloud = WordCloud(width=580, height=350, margin=0,contour_width=8, contour_color='firebrick',
                      background_color = "white",max_font_size=None).generate(director) 
    fig, ax = plt.subplots()
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    return fig  

# la funcion gcirculo(df,valores), nos permite generar un grafico tipo circulo, mostrandonos la Categoria por porcentaje de las peliculas 

def gcirculo(df,valores):
    x = df[valores]
    fig, ax = plt.subplots(figsize=(4, 4))
    ax.pie(x, labels=df['Genres'], autopct='%.1f%%',
       wedgeprops={'linewidth': 1.0, 'edgecolor': 'white'},
       textprops={'size': 8},startangle=140)
    ax.set_title(valores, fontsize=18)
    return fig


# Se define la funcion cargar_urllottie(url), la cual procesa la imagen Lottie segun URL proporcionado por parametro, mientras no ocurra algun error

def cargar_urllottie(url):
    r = requests.get(url)
    if r.status_code != 200:
         return None
    return r.json() 

def intro(dataf,pag):
    st.write("""#### Preponderancia de categorías de películas en las plataformas de streamings, así como las  más votadas a nivel del público en general y expertos del cine.""")    
    
    st.markdown(
    """ 
Se nos presenta un conjunto de datos de películas emitidas por distintos proveedores de streaming, 
por popularidad y críticas, tanto del publico en general (IMDb) como expertos del Cine (Tomatoes Rotten)
por distintas Categorías. Se procede a realizar un análisis a fin de conocer y profundizar en los 
diversos aspectos de entretenimiento por Streaming, como por ejemplo:

    • ¿Cuál categoría es la más ofertada por proveedor de entretenimiento vía 
       streaming (Netflix, Amazon Prime, HULU, ¿Disney+)?

    • ¿Cuál categoría recibe mejores críticas de los expertos del Cine, 
       segmentados por proveedor de entretenimiento?
    
    • ¿Cuál es la película con la mejor critica del público en general, 
       segmentados por proveedor de entretenimiento, específicamente en 
       Netflix, Amazon Prime, HULU, Disney+ ?
    
    • ¿Cuál es la película con mejor critica de los expertos del Cine que
       se visualiza por proveedor de streaming?
    
    • ¿Cuál es el director con mejor critica, tanto del público en general,
       como de los expertos del Cine por proveedor de streaming?

Por lo tanto, comenzamos por la carga de datos, los cuales fueron obtenidos
de la URL https://www.kaggle.com/ruchi798/movies-on-netflix-prime-video-hulu-and-disney/version/2?select=MoviesOnStreamingPlatforms_updated.csv")  

    """
    ) 
    
    st.write(dataf)
    
    st.markdown(
    """ 
    
    Se procede a eliminar las columnas que consideramos irrelevantes para el estudio a realizar:
    """)
    dataf=dataf.drop(['ID','Runtime','Type','Country','Language','Age'], axis=1)
    st.write(dataf)
    
    st.markdown(
    """ 
    Visualizamos la cantidad de nulos del dataframe:
    """)
    st.write(dataf.isnull().sum())

    st.markdown(
    """ 
    Se eliminan los datos nulos que pueda presentar este:
    """)
    dataf=dataf.dropna()
    st.write(dataf.isnull().sum())
    
    st.markdown(
    """ 
    A continuación delimitamos el estudio a categorías únicas de películas comprendidas entre los años 1990 y 2020:
    """)
    dataf=dataf[(dataf['Year']>=1990) & (dataf['Year']<=2020) & (dataf['Genres'].apply(categoriaunica)  ==0) ]
    st.write(dataf)
 
    st.write('-'*10)
    st.write('Total peliculas globales: ',dataf.shape[0])
    st.write('-'*10)
    st.write('Cantidad de variables del DataSet: ',dataf.shape[1])
    st.write('-'*10)
    st.write('Nombre de las columnas que conforman el dataset: \n')
    st.write(dataf.columns)
    st.write('-'*10)
    
    st.markdown(
    """ 
    Visualizamos si tenemos datos duplicados:
    """)
    duplicados=dataf.duplicated(['Title','Year','Netflix','Hulu','Prime Video','Disney+'])
    st.write(dataf[duplicados])
    
    st.markdown(
    """
    Ya al tener la data depurada, con datos limpios, continuamos en las siguientes paginas o sección del proyecto,     visualizando las  respuestas o informaciones obtenidas según las preguntas formuladas al inicio del presente análisis.
    """)
    
#--------------------------------------------------------------------------------------------------------------------
#********************************************************************************************************************
#st.set_page_config(initial_sidebar_state="collapsed",)


st.set_page_config(
     page_title="BootCamp en Ciencias de Datos",
     layout="centered",
     initial_sidebar_state="expanded",
     menu_items={
         'About': "## BootCamp en Ciencias de Datos - Proyecto final"
     }
 )


#st.markdown("## Este es un markdown h2")

   
# A partir de aqui se encuentra el codigo principal de la pagina principal, con su respectivo menu:


imagen_lottie= cargar_urllottie("https://assets1.lottiefiles.com/packages/lf20_yJ8wNO.json")



st.sidebar.title("Comencemos...") 
pagina = st.sidebar.radio(
     'Seleccione contenido a visualizar:...',
     ('Home Page', 'Introduccion', 'Pagina 1','Pagina 2', 'Pagina 3', 'Pagina 4','Pagina 5'),index=0)


if pagina== "Home Page":
    st.title("Bootcamp de Ciencia de Datos")
    #st.markdown('"Preponderancia de categorías de películas en las plataformas de streamings, así como las  más votadas a nivel del público en general y expertos del cine."')
    st.subheader("CódigoFacilito")
    st_lottie(imagen_lottie,width=600,height=550,key="coding")

elif pagina== "Introduccion":
    intro(original_df,pagina)
    #st.dataframe(original_df)

    
elif pagina== "Pagina 1":
    st.success("¿Cuál categoría es la mas ofertada por proveedor de entretenimiento via streaming (Netflix, Amazon Prime, HULU, Disney+) ?")
    opcion = st.selectbox('Seleccione',('','Netflix','Hulu','Prime Video','Disney+'),index=0)
    if opcion != "": 
        st.write(crearwordsclouds(opcion,streams_df))
        opcion = ""
            
elif pagina== "Pagina 2":
    st.success("¿Cuál categoría recibe mejores criticas de los expertos del Cine, segmentados por proveedor de entretenimiento?")
    opcion = st.selectbox('Seleccione',('','Netflix','Hulu','Prime Video','Disney+'),index=0)
    if opcion != "": 
        datosgraficos=streams_df[(streams_df['Rotten Tomatoes']>'70') & (streams_df[opcion]==1)].groupby(['Genres'])                        [opcion].count().sort_values(ascending=False).head()
        datosgraficos=datosgraficos.reset_index()
        st.write(gcirculo(datosgraficos,opcion))  
        opcion = ""
        
elif pagina== "Pagina 3":
    st.success("¿Cuál es la película con la mejor critica del publico en general, segmentados por proveedor de entretenimiento, específicamente en Netflix, Amazon Prime, HULU, Disney+ ?")
    opcion = st.selectbox('Seleccione',('','Netflix','Hulu','Prime Video','Disney+'),index=0)
    if opcion != "": 
        st.write(gbarras(streams_df)) 
    else: opcion = ""
    
elif pagina== "Pagina 4":
    st.info("¿Cuál es la película con mejor critica de los expertos del Cine que se visualiza por proveedor de streaming?")
    opcion = st.selectbox('Seleccione',('','Netflix','Hulu','Prime Video','Disney+'),index=0)
    if opcion != "":
        st.write(top_pelicula(streams_df,opcion))   
        opcion = ""
    
elif pagina == "Pagina 5":
    st.success("¿Cuál es el director con mejor critica, tanto del publico en general, como de los expertos del Cine por proveedor de streaming?")
    opcion = st.selectbox('Seleccione',('','Netflix','Hulu','Prime Video','Disney+'),index=0)
    if opcion != "":
        st.write(top_director(streams_df,opcion))
