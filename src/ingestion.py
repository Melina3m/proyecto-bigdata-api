import numba
if not hasattr(numba, 'generated_jit'):
    numba.generated_jit = numba.jit
import requests
import pandas as pd
import time
import sqlite3
import json
from dotenv import load_dotenv
import os
from ydata_profiling import ProfileReport

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

paramsDetails = {
    "language": "es-MX"
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
max_pages = min(total_pages, 5)

# Procesamos la primera página
for record in data.get("results", []):
    movie_id = record.get("id")  # Obtener el ID de la película

    # Solicitar detalles adicionales de la película
    details_url = f"{base_url_details}/{movie_id}"
    details_response = requests.get(details_url, headers=headers, params=paramsDetails)

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


# Función para generar el reporte a partir de un DataFrame
def generar_reporte(df, titulo, nombre_archivo):
    reporte = ProfileReport(df, title=titulo, explorative=True)
    reporte.to_file(nombre_archivo)
    print(f"Reporte guardado en: {nombre_archivo}")

# -----------------------------
# Auditoría de la base de datos SQLite
# -----------------------------
# Conectar a la base de datos y leer la tabla 'movies'
try:
    conn = sqlite3.connect('src/static/db/ingestion.db')
    df_sqlite = pd.read_sql("SELECT * FROM movies", conn)
    conn.close()
    print("Datos cargados correctamente desde SQLite.")
except Exception as e:
    print(f"Error al cargar datos desde SQLite: {e}")
    df_sqlite = pd.DataFrame()  # DataFrame vacío en caso de error

# Generar el informe de auditoría para SQLite (si se cargaron datos)
if not df_sqlite.empty:
    generar_reporte(df_sqlite, "Reporte de Auditoría - SQLite", "sqlite_audit_report.html")
else:
    print("No se generó reporte para SQLite, el DataFrame está vacío.")

# -----------------------------
# Auditoría del archivo Excel
# -----------------------------
try:
    df_excel = pd.read_excel("tmdb_movies.xlsx")
    print("Datos cargados correctamente desde el archivo Excel.")
except Exception as e:
    print(f"Error al cargar datos desde Excel: {e}")
    df_excel = pd.DataFrame()  # DataFrame vacío en caso de error

# Generar el informe de auditoría para Excel (si se cargaron datos)
if not df_excel.empty:
    generar_reporte(df_excel, "Reporte de Auditoría - Excel", "excel_audit_report.html")
else:
    print("No se generó reporte para Excel, el DataFrame está vacío.")
    
    
# -----------------------------
# Comparativa de auditoría entre las fuentes de datos
# -----------------------------

report_lines = []
report_lines.append("Comparative Audit Report")
report_lines.append("========================")
report_lines.append("")

# Número de registros en cada fuente
n_api = len(df)
n_sqlite = len(df_sqlite)
n_excel = len(df_excel)

report_lines.append(f"Total de registros extraídos de la API: {n_api}")
report_lines.append(f"Total de registros en la base de datos SQLite: {n_sqlite}")
report_lines.append(f"Total de registros en el archivo Excel: {n_excel}")
report_lines.append("")

# Comparación de conteo de registros
if n_api == n_sqlite == n_excel:
    report_lines.append("Los conteos de registros son consistentes en todas las fuentes.")
else:
    report_lines.append("¡Atención! Los conteos de registros difieren entre las fuentes.")
report_lines.append("")

# Comparación de columnas
cols_api = set(df.columns)
cols_sqlite = set(df_sqlite.columns)
cols_excel = set(df_excel.columns)

report_lines.append("Columnas presentes en cada fuente:")
report_lines.append(f"- API: {', '.join(sorted(cols_api))}")
report_lines.append(f"- SQLite: {', '.join(sorted(cols_sqlite))}")
report_lines.append(f"- Excel: {', '.join(sorted(cols_excel))}")
report_lines.append("")

# Verificar diferencias en las columnas (campos clave)
diff_sqlite_api = cols_api.symmetric_difference(cols_sqlite)
diff_excel_api = cols_api.symmetric_difference(cols_excel)

if diff_sqlite_api:
    report_lines.append("Diferencias entre columnas de API y SQLite:")
    report_lines.append(f"  {', '.join(sorted(diff_sqlite_api))}")
else:
    report_lines.append("No se encontraron diferencias en las columnas entre API y SQLite.")

if diff_excel_api:
    report_lines.append("Diferencias entre columnas de API y Excel:")
    report_lines.append(f"  {', '.join(sorted(diff_excel_api))}")
else:
    report_lines.append("No se encontraron diferencias en las columnas entre API y Excel.")
report_lines.append("")

# Verificación de integridad para campos clave (por ejemplo, 'id' y 'original_title')
key_fields = ['id', 'original_title']
for key in key_fields:
    report_lines.append(f"Verificación de integridad para el campo '{key}':")
    missing_api = df[key].isnull().sum() if key in df.columns else "Columna no encontrada"
    missing_sqlite = df_sqlite[key].isnull().sum() if key in df_sqlite.columns else "Columna no encontrada"
    missing_excel = df_excel[key].isnull().sum() if key in df_excel.columns else "Columna no encontrada"
    report_lines.append(f"  - Registros faltantes en API: {missing_api}")
    report_lines.append(f"  - Registros faltantes en SQLite: {missing_sqlite}")
    report_lines.append(f"  - Registros faltantes en Excel: {missing_excel}")
    report_lines.append("")

# Guardar el reporte comparativo en un archivo de texto
report_file = "comparative_audit_report.txt"
with open(report_file, "w", encoding="utf-8") as f:
    for line in report_lines:
        f.write(line + "\n")

print(f"Reporte comparativo generado en: {report_file}")

