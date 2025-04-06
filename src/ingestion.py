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

###############################################################################
# Variables Globales y Configuración
###############################################################################

# Obtener el token de la variable de entorno
api_token = os.getenv("TMDB_API_TOKEN")
if not api_token:
    print("Error: No se encontró el token de la API. Verifica el archivo .env")
    exit()

# Configuración de headers para las solicitudes a TMDB
headers = {
    "accept": "application/json",
    "Authorization": f"Bearer {api_token}"
}

# URL base para el discover y detalles de las películas en TMDB
base_url_discover = "https://api.themoviedb.org/3/discover/movie"
base_url_details = "https://api.themoviedb.org/3/movie"

# Parámetros para la solicitud "discover"
params = {
    "page": 1,
    "language": "es-MX",
    "primary_release_date.gte": "2020-01-01",
    "primary_release_date.lte": "2024-12-31",
    "sort_by": "revenue.desc"
}

# Parámetros para la solicitud de detalles (se puede ajustar idioma, etc.)
paramsDetails = {
    "language": "es-MX"
}

# Retardo entre solicitudes para no sobrecargar la API
DELAY = 0.15

###############################################################################
# Funciones para el fetch de datos desde TMDB
###############################################################################

def fetch_tmdb_movies() -> pd.DataFrame:
    """
    Realiza solicitudes a la API de TMDB para obtener un conjunto de películas.
    
    Utiliza el endpoint "discover" para obtener la lista de películas y para cada
    película solicita detalles adicionales (budget, revenue, runtime, genres, etc.).
    Limita el número de páginas a procesar (máximo 5).

    Returns:
        pd.DataFrame: DataFrame con todos los registros de películas obtenidos y enriquecidos.
    """
    results_all = []
    # Hacer la primera solicitud para obtener el total de páginas disponibles
    response = requests.get(base_url_discover, headers=headers, params=params)
    if response.status_code != 200:
        print(f"Error en la solicitud inicial: {response.status_code}")
        exit()
    data = response.json()
    total_pages = data.get("total_pages", 1)
    print(f"Total de páginas disponibles: {total_pages}")
    # Limitar a un máximo de 5 páginas (o menor si total_pages es menor)
    max_pages = min(total_pages, 5)
    
    # Procesar la primera página
    for record in data.get("results", []):
        movie_id = record.get("id")
        details_url = f"{base_url_details}/{movie_id}"
        details_response = requests.get(details_url, headers=headers, params=paramsDetails)
        if details_response.status_code == 200:
            movie_details = details_response.json()
            record["budget"] = movie_details.get("budget")
            record["revenue"] = movie_details.get("revenue")
            record["runtime"] = movie_details.get("runtime")
            record["genres"] = [genre['name'] for genre in movie_details.get("genres", [])]
            record["origin_country"] = movie_details.get("origin_country", [])
            record["production_companies"] = [company['name'] for company in movie_details.get("production_companies", [])]
            record["production_countries"] = [country["name"] for country in movie_details.get("production_countries", [])]
            record["spoken_languages"] = [lang["name"] for lang in movie_details.get("spoken_languages", [])]
            record["homepage"] = movie_details.get("homepage")
            record["tagline"] = movie_details.get("tagline")
            record["vote_average"] = movie_details.get("vote_average")
            record["vote_count"] = movie_details.get("vote_count")
        else:
            print(f"Error obteniendo detalles de la película {movie_id}: {details_response.status_code}")
        results_all.append(record)
        print(f"Película procesada: {record['original_title']} (ID: {movie_id})")
        time.sleep(DELAY)
    
    print(f"Página 1 procesada, total resultados acumulados: {len(results_all)}")
    
    # Procesar páginas restantes
    for page in range(2, max_pages + 1):
        params["page"] = page
        try:
            response = requests.get(base_url_discover, headers=headers, params=params)
            if response.status_code != 200:
                print(f"Error en la página {page}: {response.status_code}")
                continue
            data = response.json()
            if not data.get("results"):
                print(f"No se encontraron más resultados en la página {page}.")
                continue
            for record in data.get("results", []):
                movie_id = record.get("id")
                details_url = f"{base_url_details}/{movie_id}"
                details_response = requests.get(details_url, headers=headers)
                if details_response.status_code == 200:
                    movie_details = details_response.json()
                    record["budget"] = movie_details.get("budget")
                    record["revenue"] = movie_details.get("revenue")
                    record["runtime"] = movie_details.get("runtime")
                    record["genres"] = [genre['name'] for genre in movie_details.get("genres", [])]
                    record["origin_country"] = movie_details.get("origin_country", [])
                    record["production_companies"] = [company['name'] for company in movie_details.get("production_companies", [])]
                    record["production_countries"] = [country["name"] for country in movie_details.get("production_countries", [])]
                    record["spoken_languages"] = [lang["name"] for lang in movie_details.get("spoken_languages", [])]
                    record["homepage"] = movie_details.get("homepage")
                    record["tagline"] = movie_details.get("tagline")
                    record["vote_average"] = movie_details.get("vote_average")
                    record["vote_count"] = movie_details.get("vote_count")
                else:
                    print(f"Error obteniendo detalles de la película {movie_id}: {details_response.status_code}")
                results_all.append(record)
            print(f"Página {page} procesada, total resultados acumulados: {len(results_all)}")
        except Exception as e:
            print(f"Excepción en la página {page}: {e}")
            continue
        time.sleep(DELAY)
        
    # Convertir la lista de resultados a un DataFrame
    df = pd.DataFrame(results_all)
    return df

def export_tmdb_data(df: pd.DataFrame, excel_file: str, db_path: str) -> None:
    """
    Exporta el DataFrame obtenido de TMDB a un archivo Excel y lo guarda en la base de datos SQLite en la tabla 'movies'.
    
    Además, convierte a string cualquier columna que tenga listas o diccionarios para asegurar la compatibilidad con SQLite.
    
    Args:
        df (pd.DataFrame): DataFrame con los datos de TMDB.
        excel_file (str): Ruta del archivo Excel donde se exportarán los datos.
        db_path (str): Ruta de la base de datos SQLite.
        
    Returns:
        None.
    """
    df.to_excel(excel_file, index=False)
    print(f"Datos guardados en {excel_file}")
    
    # Convertir columnas complejas a string
    for col in df.columns:
        if df[col].apply(lambda x: isinstance(x, list) or isinstance(x, dict)).any():
            df[col] = df[col].apply(lambda x: json.dumps(x) if isinstance(x, (list, dict)) else x)
    
    conn = sqlite3.connect(db_path)
    df.to_sql('movies', conn, if_exists='replace', index=False)
    conn.commit()
    conn.close()
    print("Datos guardados en la base de datos SQLite en la tabla 'movies'.")

###############################################################################
# Función para generar reportes HTML de auditoría utilizando ydata_profiling
###############################################################################

def generar_reporte(df: pd.DataFrame, titulo: str, nombre_archivo: str) -> None:
    """
    Genera y guarda un reporte HTML a partir del DataFrame utilizando ydata_profiling.
    
    Args:
        df (pd.DataFrame): DataFrame del cual generar el reporte.
        titulo (str): Título que se mostrará en el reporte.
        nombre_archivo (str): Ruta del archivo donde se guardará el reporte HTML.
        
    Returns:
        None.
    """
    reporte = ProfileReport(df, title=titulo, explorative=True)
    reporte.to_file(nombre_archivo)
    print(f"Reporte guardado en: {nombre_archivo}")

###############################################################################
# Funciones para la auditoría y comparativa entre fuentes
###############################################################################

def load_sqlite_table(table: str, db_path: str) -> pd.DataFrame:
    """
    Carga una tabla específica desde una base de datos SQLite y la retorna como DataFrame.
    
    Args:
        table (str): Nombre de la tabla a cargar.
        db_path (str): Ruta de la base de datos SQLite.
        
    Returns:
        pd.DataFrame: DataFrame con los datos de la tabla.
    """
    conn = sqlite3.connect(db_path)
    df = pd.read_sql(f"SELECT * FROM {table}", conn)
    conn.close()
    return df

def load_excel_file(excel_file: str) -> pd.DataFrame:
    """
    Carga un archivo Excel y lo retorna como DataFrame.
    
    Args:
        excel_file (str): Ruta del archivo Excel.
        
    Returns:
        pd.DataFrame: DataFrame con los datos del archivo Excel.
    """
    try:
        df = pd.read_excel(excel_file)
        print("Datos cargados correctamente desde el archivo Excel.")
    except Exception as e:
        print(f"Error al cargar datos desde Excel: {e}")
        df = pd.DataFrame()
    return df

def generate_comparative_audit_report(df_api: pd.DataFrame, df_sqlite: pd.DataFrame, df_excel: pd.DataFrame, report_file: str) -> None:
    """
    Genera un reporte comparativo de auditoría entre las fuentes de datos (API, SQLite y Excel)
    y lo guarda en un archivo de texto.
    
    El reporte incluye:
      - Total de registros en cada fuente.
      - Consistencia en el conteo de registros.
      - Listado de columnas presentes en cada fuente.
      - Diferencias entre columnas clave.
      - Verificación de integridad para campos clave (e.g. 'id', 'original_title').
    
    Args:
        df_api (pd.DataFrame): DataFrame obtenido de la API.
        df_sqlite (pd.DataFrame): DataFrame obtenido de la base de datos SQLite.
        df_excel (pd.DataFrame): DataFrame obtenido del archivo Excel.
        report_file (str): Ruta del archivo donde se guardará el reporte.
        
    Returns:
        None.
    """
    report_lines = []
    report_lines.append("Comparative Audit Report")
    report_lines.append("========================")
    report_lines.append("")
    
    n_api = len(df_api)
    n_sqlite = len(df_sqlite)
    n_excel = len(df_excel)
    
    report_lines.append(f"Total de registros extraídos de la API: {n_api}")
    report_lines.append(f"Total de registros en la base de datos SQLite: {n_sqlite}")
    report_lines.append(f"Total de registros en el archivo Excel: {n_excel}")
    report_lines.append("")
    
    if n_api == n_sqlite == n_excel:
        report_lines.append("Los conteos de registros son consistentes en todas las fuentes.")
    else:
        report_lines.append("¡Atención! Los conteos de registros difieren entre las fuentes.")
    report_lines.append("")
    
    cols_api = set(df_api.columns)
    cols_sqlite = set(df_sqlite.columns)
    cols_excel = set(df_excel.columns)
    
    report_lines.append("Columnas presentes en cada fuente:")
    report_lines.append(f"- API: {', '.join(sorted(cols_api))}")
    report_lines.append(f"- SQLite: {', '.join(sorted(cols_sqlite))}")
    report_lines.append(f"- Excel: {', '.join(sorted(cols_excel))}")
    report_lines.append("")
    
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
    
    key_fields = ['id', 'original_title']
    for key in key_fields:
        report_lines.append(f"Verificación de integridad para el campo '{key}':")
        missing_api = df_api[key].isnull().sum() if key in df_api.columns else "Columna no encontrada"
        missing_sqlite = df_sqlite[key].isnull().sum() if key in df_sqlite.columns else "Columna no encontrada"
        missing_excel = df_excel[key].isnull().sum() if key in df_excel.columns else "Columna no encontrada"
        report_lines.append(f"  - Registros faltantes en API: {missing_api}")
        report_lines.append(f"  - Registros faltantes en SQLite: {missing_sqlite}")
        report_lines.append(f"  - Registros faltantes en Excel: {missing_excel}")
        report_lines.append("")
    
    with open(report_file, "w", encoding="utf-8") as f:
        for line in report_lines:
            f.write(line + "\n")
    
    print(f"Reporte comparativo generado en: {report_file}")

###############################################################################
# Funciones del Pipeline de ETL de TMDB
###############################################################################

def run_tmdb_etl() -> pd.DataFrame:
    """
    Ejecuta el proceso de extracción de datos desde la API de TMDB.

    El proceso realiza:
      1. Solicitudes al endpoint "discover" para obtener un listado de películas.
      2. Para cada película, se solicita detalles adicionales y se enriquece el registro.
      3. Se procesa un máximo de 5 páginas.

    Returns:
        pd.DataFrame: DataFrame con los registros enriquecidos obtenidos de TMDB.
    """
    df = fetch_tmdb_movies()
    return df

###############################################################################
# Función Principal del Pipeline Completo
###############################################################################

def main_pipeline() -> None:
    """
    Ejecuta el pipeline completo de extracción, transformación y carga (ETL) de datos desde TMDB.

    El proceso incluye:
      - Extracción de datos desde la API de TMDB.
      - Exportación de los datos obtenidos a un archivo Excel.
      - Almacenamiento de los datos en una tabla SQLite ('movies').
      - Generación de informes de auditoría en formato HTML y un reporte comparativo en formato de texto.

    Returns:
        None.
    """
    # Rutas de archivos y base de datos
    DB_PATH = "src/static/db/ingestion.db"
    EXCEL_FILE = "src/static/xlsx/tmdb_movies.xlsx"
    SQLITE_AUDIT_REPORT = "src/static/auditoria/sqlite_audit_report.html"
    EXCEL_AUDIT_REPORT = "src/static/auditoria/excel_audit_report.html"
    COMPARATIVE_REPORT = "src/static/auditoria/comparative_audit_report.txt"

    # Ejecutar ETL desde TMDB
    df_api = run_tmdb_etl()
    # Exportar a Excel y guardar en SQLite
    export_tmdb_data(df_api, EXCEL_FILE, DB_PATH)
    
    # Cargar datos desde SQLite y Excel para auditoría
    df_sqlite = load_sqlite_table("movies", DB_PATH)
    df_excel = load_excel_file(EXCEL_FILE)
    
    # Generar reportes de auditoría HTML para SQLite y Excel
    if not df_sqlite.empty:
        generar_reporte(df_sqlite, "Reporte de Auditoría - SQLite", SQLITE_AUDIT_REPORT)
    else:
        print("No se generó reporte para SQLite, el DataFrame está vacío.")
        
    if not df_excel.empty:
        generar_reporte(df_excel, "Reporte de Auditoría - Excel", EXCEL_AUDIT_REPORT)
    else:
        print("No se generó reporte para Excel, el DataFrame está vacío.")
    
    # Generar reporte comparativo entre las tres fuentes
    generate_comparative_audit_report(df_api, df_sqlite, df_excel, COMPARATIVE_REPORT)

if __name__ == "__main__":
    main_pipeline()
