"""
Imagia que esta API es una biblioteca de peliculas:
La funcion load_movies() es  como una biblioteca que carga el catalogo de libros(peliculas) cuando se abre la biblioteca
la funcion get_movies() muestra todo el catalogo cuando alguien lo pide.
La funcion get_movie(id) es como si alguien preguntara por un libro en especifico, es decir, por un codigo de identificacion.
La funcion chatbot(query) es un asistente que busca peliculas segun palabras clave y sinonimo
La funcion get_movies_by_category(category) ayuda a encontrar peliculas segun su genero (accion, comedia, etc...)
"""

# Importamos las herramientas necesarias para continuar nuestra API
from fastapi import FastAPI, HTTPException # FastAPI nos ayuda a crear la API, HTTPException nos ayuda a manejar errores  # noqa: F401
from fastapi.responses import HTMLResponse, JSONResponse # HTMLResponse nos ayuda a manejar respuestas HTML, JSONResponse nos ayuda a manejar respuestas en formato JSON
import pandas as pd # type: ignore # pandas nos ayuda a manejar datos en tablas como si fuera un Excel
import nltk # type: ignore # nltk es una libreria para procesar texto y analizar palabras
from nltk.tokenize import word_tokenize # type: ignore # word_tokenize nos ayuda a tokenizar texto, es decir, a convertirlo en palabras
from nltk.corpus import wordnet # type: ignore # wordnet es una libreria para analizar sinonimos


#indicamos la ruta donde nltk buscara los datos descargados en nuestro computador
nltk.data.path.append("/home/axchisan/nltk_data")
nltk.download("punkt") #es un paquete para dividddir frases en palabras
nltk.download("wordnet") #paqiete para encontrar sinonimos

def load_movies():
    # leemos el archivo que contiene información de peliculas y selecciónamos las columnas mas importantes
     df = pd.read_csv("./Dataset/netflix_titles.csv")[['show_id','title','release_year','listed_in','rating','description']]
     
     #renombramos las columnas para que sean mas faciles de usar
     df.columns = ['id', 'title', 'year', 'category', 'rating', 'description']
    
    #llenamos los espacios vacios con texto vacio y convirtimos  los datos en una lista de diccionarios
     return df.fillna('').to_dict(orient='records') 
 
 #Cargamos las peliculas al iniciar la API para no leer el archivo cada ve que alguien pregunta por ellas 
movies_list = load_movies()

#funcion para encontrar sinonimos de una palabra
def get_synonymus(word):
    #usamos wordnet para encontrar distintas palabras que significan lo mismo
    return{lemma.name().lower() for syn in wordnet.synsets(word) for lemma in syn.lemmas()} 

#Creamos la aplicacion FastAPI 
app = FastAPI(title="Mi app de Peliculas", version="1.0",)


#ruta de inicio: cuando alguieen accede a la API, le mostramos un mensaje de bienvenida

@app.get('/', tags=["Home"])
def home():
    #cuando entremos en el navegador a http://127.0.0.1:8000/ veremos un mensaje de bienvenida
    return HTMLResponse("<h1>Bienvenido a la API de Peliculas</h1>")
#obteniendo la lista de peliculas 
#creamos una ruta para obtener todas las peliculas
#rruta para obtener todas las peliculas

@app.get('/movies', tags=["Movies"])
def get_movies():
    #si hay peliculas, las enviamos, si no enviamos un error
    return movies_list or HTTPException(status_code=500, detail="No hay datos de peliculas disponibles")

#ruta para obtener una pelicula en especifica segun su id
@app.get('/movies/{id}', tags=["Movies"])
def get_movie(id: str):
    #buscamos en la lista de peliculas por su id
    return next(m for m in movies_list if m['id'] == id), {"detail": "Pelicula no encontrada"}

#ruta del chatbot que responde con peliculas segun palabras clave de la categoria
@app.get('/chatbot', tags=["Chatbot"])
def chatbot(query: str):
    #dividimos la consulta en palabras clave para entender mejor la intencion del usuario
    query_words = word_tokenize(query.lower())
    #buscamos sinonimos de las palabras clave para ampliar la busqueda
    
    synonyms = {word for q in query_words for word in get_synonymus(q)} | set(query_words)
    
    #filtramos las peliculas buscando coincidencias en la categoria
    results = [m for m in movies_list if any (s in m['category'].lower() for s in synonyms)]
    
    #si encontramos peliculas, las enviamos, si no enviamos un mesaje de que no se encontraron coindcidencias
    
    return JSONResponse (content={
        "respuesta": "Aqui tienes algunas peliculas relacionadas." if results else "Lo siento, no se encontraron peliculas en esa categoria.",
        "peliculas": results 
    })
#ruta para obtener peliculas por categoria
@app.get('/movies/by_category', tags=["Movies"])
def get_movies_by_category(category: str):
    #filtramos la lista de peliculas segun la categoria ingresada
    return [m for m in movies_list if category.lower() in m['category'].lower()] 

    


