import sqlite3
import pandas as pd
import ast

# Conectar a la base de datos SQLite ubicada en src/static/db/ingestion.db
conn = sqlite3.connect('src/static/db/ingestion.db')

# Agregar el código para extraer toda la información de la tabla 'movies' a un DataFrame
df_movies = pd.read_sql("SELECT * FROM movies", conn)

# Crear una nueva tabla 'movies_cleaned' con los datos limpios
#df_movies.to_sql('movies_cleaned', conn, if_exists='replace', index=False)

# Cerrar la conexión a la base de datos
conn.close()

# Convertir la columna a una lista de strings
columns_to_format = ['genres', 'production_companies', 'spoken_languages', 'production_countries']
for col in columns_to_format:
    df_movies[col] = df_movies[col].apply(lambda x: ', '.join(ast.literal_eval(x)))

# Paso 1: diccionario de traducciones inglés -> español
genre_translation = {
    "Action": "Acción",
    "Adventure": "Aventura",
    "Animation": "Animación",
    "Comedy": "Comedia",
    "Crime": "Crimen",
    "Documentary": "Documental",
    "Drama": "Drama",
    "Family": "Familia",
    "Fantasy": "Fantasía",
    "History": "Historia",
    "Horror": "Terror",
    "Music": "Música",
    "Mystery": "Misterio",
    "Romance": "Romance",
    "Science Fiction": "Ciencia ficción",
    "Thriller": "Suspenso",
    "War": "Guerra",
    "Suspense": "Suspenso",
}

def translate_genres(genres_str):
    """
    Recibe una cadena de géneros separados por comas (p.ej. "Action, Comedy")
    y devuelve la cadena con cada género traducido al español.
    """
    # Separamos por coma
    genres_list = [g.strip() for g in genres_str.split(",")]
    
    # Traducimos cada género si está en el diccionario, si no, lo dejamos igual
    translated_list = [genre_translation.get(g, g) for g in genres_list]
    
    # Unimos con coma y espacio
    return ", ".join(translated_list)

# Paso 2: aplicar la función de traducción a la columna
df_movies["genres"] = df_movies["genres"].apply(translate_genres)

print(df_movies["genres"].unique())