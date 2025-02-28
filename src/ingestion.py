import requests
import pandas as pd
import time
import sqlite3
import json
from dotenv import load_dotenv
import os

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Obtener el token de la variable de entorno
api_token = os.getenv("TMDB_API_TOKEN")

if not api_token:
    print("Error: No se encontró el token de la API. Verifica el archivo .env")
    exit()

# Configuración: utiliza el token de autenticación cargado desde .env
headers = {
    "accept": "application/json",
    "Authorization": f"Bearer {api_token}"
}

# URL base para el discover y detalles de las películas
base_url_discover = "https://api.themoviedb.org/3/discover/movie"
base_url_details = "https://api.themoviedb.org/3/movie"
results_all = []
delay = 0.15  # Retardo en segundos entre solicitudes para no sobrecargar la API

# Parámetros de la primera API (discover)
params = {
    "page": 1,
    "language": "es-MX",
    "primary_release_date.gte": "2020-01-01",
    "primary_release_date.lte": "2024-12-31",
    "sort_by": "revenue.desc"
}

# Hacemos una primera solicitud para conocer el total de páginas disponibles
response = requests.get(base_url_discover, headers=headers, params=params)
if response.status_code != 200:
    print(f"Error en la solicitud inicial: {response.status_code}")
    exit()

data = response.json()
total_pages = data.get("total_pages", 1)
print(f"Total de páginas disponibles: {total_pages}")

# Limitar el número de páginas a procesar si total_pages es mayor a 500
max_pages = min(total_pages, 1)

# Procesamos la primera página
for record in data.get("results", []):
    movie_id = record.get("id")  # Obtener el ID de la película

    # Solicitar detalles adicionales de la película
    details_url = f"{base_url_details}/{movie_id}"
    details_response = requests.get(details_url, headers=headers)

    if details_response.status_code == 200:
        movie_details = details_response.json()

        # Obtener más detalles: budget, revenue, runtime, genres...
        record["budget"] = movie_details.get("budget")
        record["revenue"] = movie_details.get("revenue")
        record["runtime"] = movie_details.get("runtime")
        record["genres"] = [genre['name'] for genre in movie_details.get("genres", [])]
        record["production_companies"] = [company['name'] for company in movie_details.get("production_companies", [])]
        record["spoken_languages"] = [lang['name'] for lang in movie_details.get("spoken_languages", [])]
        record["homepage"] = movie_details.get("homepage")
        record["tagline"] = movie_details.get("tagline")
        record["vote_average"] = movie_details.get("vote_average")
        record["vote_count"] = movie_details.get("vote_count")

    else:
        print(f"Error obteniendo detalles de la película {movie_id}: {details_response.status_code}")

    # Agregar el registro completo con detalles a la lista de resultados
    results_all.append(record)
    print(f"Película procesada: {record['original_title']} (ID: {movie_id})")

    # Retardo para no saturar la API
    time.sleep(delay)

print(f"Página 1 procesada, total resultados acumulados: {len(results_all)}")

# Bucle para procesar las páginas restantes
for page in range(2, max_pages + 1):
    params["page"] = page
    try:
        response = requests.get(base_url_discover, headers=headers, params=params)
        if response.status_code != 200:
            print(f"Error en la página {page}: {response.status_code}")
            continue

        data = response.json()
        # Si no hay resultados, terminamos el bucle
        if not data.get("results"):
            print(f"No se encontraron más resultados en la página {page}.")
            continue

        # Procesamos cada película en la página
        for record in data.get("results", []):
            movie_id = record.get("id")  # Obtener el ID de la película

            # Solicitar detalles adicionales de la película
            details_url = f"{base_url_details}/{movie_id}"
            details_response = requests.get(details_url, headers=headers)

            if details_response.status_code == 200:
                movie_details = details_response.json()

                # Obtener más detalles: budget, revenue, runtime, genres...
                record["budget"] = movie_details.get("budget")
                record["revenue"] = movie_details.get("revenue")
                record["runtime"] = movie_details.get("runtime")
                record["genres"] = [genre['name'] for genre in movie_details.get("genres", [])]
                record["production_companies"] = [company['name'] for company in movie_details.get("production_companies", [])]
                record["spoken_languages"] = [lang['name'] for lang in movie_details.get("spoken_languages", [])]
                record["homepage"] = movie_details.get("homepage")
                record["tagline"] = movie_details.get("tagline")
                record["vote_average"] = movie_details.get("vote_average")
                record["vote_count"] = movie_details.get("vote_count")

            else:
                print(f"Error obteniendo detalles de la película {movie_id}: {details_response.status_code}")

            # Agregar el registro completo con detalles a la lista de resultados
            results_all.append(record)

        print(f"Página {page} procesada, total resultados acumulados: {len(results_all)}")

    except Exception as e:
        print(f"Excepción en la página {page}: {e}")
        continue

    # Retardo para no saturar la API
    time.sleep(delay)

# Convertir la lista de resultados a un DataFrame de pandas
df = pd.DataFrame(results_all)

# Exportar el DataFrame al archivo Excel existente
excel_file = "tmdb_movies.xlsx"
df.to_excel(excel_file, index=False)
print(f"Datos guardados en {excel_file}")

# Solo si hay datos en el DataFrame, guarda en SQLite
if not df.empty:
    # Convertir a string cualquier columna que tenga listas o diccionarios
    for col in df.columns:
        if df[col].apply(lambda x: isinstance(x, list) or isinstance(x, dict)).any():
            df[col] = df[col].apply(lambda x: json.dumps(x) if isinstance(x, (list, dict)) else x)

    # Conectar a la base de datos SQLite ubicada en src/static/db/ingestion.db
    conn = sqlite3.connect('src/static/db/ingestion.db')

    # Guardar el DataFrame en la tabla llamada 'movies' (la tabla ya existente)
    df.to_sql('movies', conn, if_exists='replace', index=False)

    conn.commit()
    conn.close()

    print("Datos guardados en la base de datos SQLite 'src/static/db/ingestion.db' en la tabla 'movies'.")
