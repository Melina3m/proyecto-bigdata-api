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

base_url = "https://api.themoviedb.org/3/discover/movie"
results_all = []
delay = 0.15  # Retardo en segundos entre solicitudes para no sobrecargar la API

# Hacemos una primera solicitud para conocer el total de páginas disponibles
params = {
    "page": 1,
    "language": "es-MX",
    "primary_release_date.gte": "2020-01-01",
    "primary_release_date.lte": "2024-12-31",
    "sort_by": "revenue.desc"
}

response = requests.get(base_url, headers=headers, params=params)
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
    record["page"] = 1
results_all.extend(data.get("results", []))
print(f"Página 1 procesada, total resultados acumulados: {len(results_all)}")

# Bucle para procesar las páginas restantes
for page in range(2, max_pages + 1):
    params["page"] = page
    try:
        response = requests.get(base_url, headers=headers, params=params)
        if response.status_code != 200:
            print(f"Error en la página {page}: {response.status_code}")
            continue

        data = response.json()
        # Si no hay resultados, terminamos el bucle
        if not data.get("results"):
            print(f"No se encontraron más resultados en la página {page}.")
            continue

        # Agregar la información de la página a cada registro
        for record in data.get("results", []):
            record["page"] = page

        results_all.extend(data.get("results", []))
        print(f"Página {page} procesada, total resultados acumulados: {len(results_all)}")

    except Exception as e:
        print(f"Excepción en la página {page}: {e}")
        continue

    # Retardo para no saturar la API
    time.sleep(delay)

# Convertir la lista de resultados a un DataFrame de pandas
df = pd.DataFrame(results_all)

# Exportar el DataFrame a un archivo Excel
excel_file = "tmdb_movies.xlsx"
df.to_excel(excel_file, index=False)
print(f"Datos guardados en {excel_file}")

# Convertir a string cualquier columna que tenga listas o diccionarios
for col in df.columns:
    if df[col].apply(lambda x: isinstance(x, list) or isinstance(x, dict)).any():
        df[col] = df[col].apply(lambda x: json.dumps(x) if isinstance(x, (list, dict)) else x)

# Conectar a la base de datos SQLite ubicada en src/static/db/ingestion.db
conn = sqlite3.connect('src/static/db/ingestion.db')

# Guardar el DataFrame en una tabla llamada 'movies'
# if_exists='replace' sobrescribe la tabla, si prefieres agregar datos usa 'append'
df.to_sql('movies', conn, if_exists='replace', index=False)

conn.commit()
conn.close()

print("Datos guardados en la base de datos SQLite 'src/db/ingestion.db' en la tabla 'movies'.")
