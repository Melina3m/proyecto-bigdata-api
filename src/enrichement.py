import requests
import pandas as pd
import sqlite3
import time
import os
from dotenv import load_dotenv
import json

# Cargar las variables de entorno
load_dotenv()
api_token = os.getenv("TMDB_API_TOKEN")
if not api_token:
    print("Error: No se encontró el token de la API. Verifica el archivo .env")
    exit()

headers = {
    "accept": "application/json",
    "Authorization": f"Bearer {api_token}"
}

# Parámetros para detalles, si los necesitas (por ejemplo, idioma)
paramsDetails = {
    "language": "es-MX"
}

# URL base para detalles de la película
base_url_details = "https://api.themoviedb.org/3/movie"

# Conectar a la base de datos SQLite (ajusta la ruta según corresponda)
conn = sqlite3.connect('src/static/db/ingestion.db')

# Leer el listado de películas de la tabla existente
df_movies = pd.read_sql("SELECT * FROM movies_cleaned", conn)
print(f"Total de películas a enriquecer: {len(df_movies)}")

# Lista para almacenar los datos enriquecidos
enriched_data = []
delay = 0.15  # Retardo entre solicitudes

# Iterar sobre cada película en el DataFrame
for index, row in df_movies.iterrows():
    movie_id = row["id"]
    details_url = f"{base_url_details}/{movie_id}"
    
    try:
        details_response = requests.get(details_url, headers=headers, params=paramsDetails)
        if details_response.status_code == 200:
            movie_details = details_response.json()
            # Extraer el campo 'status'
            status = movie_details.get("status")
            # Puedes extraer otros campos adicionales si lo deseas
            # Por ejemplo: 'belongs_to_collection'
            belongs_to_collection = movie_details.get("belongs_to_collection")
            
            # Convertir la fila a diccionario y agregar los nuevos campos
            row_dict = row.to_dict()
            row_dict["status"] = status
            row_dict["belongs_to_collection"] = belongs_to_collection  # Opcional
            enriched_data.append(row_dict)
            
            print(f"Película enriquecida: {row_dict.get('original_title', 'N/A')} (ID: {movie_id})")
        else:
            print(f"Error al obtener detalles para la película ID: {movie_id} - Código: {details_response.status_code}")
            # Si falla la consulta, se agregan valores nulos para los nuevos campos
            row_dict = row.to_dict()
            row_dict["status"] = None
            row_dict["belongs_to_collection"] = None
            enriched_data.append(row_dict)
    except Exception as e:
        print(f"Excepción para la película ID: {movie_id}: {e}")
        row_dict = row.to_dict()
        row_dict["status"] = None
        row_dict["belongs_to_collection"] = None
        enriched_data.append(row_dict)
    
    time.sleep(delay)

# Convertir la lista enriquecida a un nuevo DataFrame
df_enriched = pd.DataFrame(enriched_data)
print("Enriquecimiento completado.")

def convert_to_str(val):
    if isinstance(val, (list, dict)):
        return json.dumps(val)
    return val

# Convertir todos los valores del DataFrame a tipos compatibles
df_enriched = df_enriched.applymap(convert_to_str)

# Ahora guardar el DataFrame enriquecido en la tabla 'movies_enriched'
df_enriched.to_sql('movies_enriched', conn, if_exists='replace', index=False)
print("Tabla 'movies_enriched' creada en la base de datos.")

# Cerrar la conexión
conn.close()
