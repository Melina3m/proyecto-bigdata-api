import requests
import pandas as pd
import sqlite3
import time
import os
import json
from dotenv import load_dotenv

# Cargar las variables de entorno
load_dotenv()

###############################################################################
# Funciones de enriquecimiento
###############################################################################

def enrich_tmdb_details(db_path: str, headers: dict, params_details: dict, delay: float = 0.15) -> None:
    """
    Enriquecer la información de cada película usando el endpoint de detalles de TMDB.
    
    Lee el listado de películas de la tabla 'movies_cleaned', realiza solicitudes a la API TMDB para
    obtener detalles (como status, belongs_to_collection e imdb_id) y guarda el resultado en la tabla
    'movies_enriched' en la base de datos SQLite.
    
    Args:
        db_path (str): Ruta de la base de datos SQLite.
        headers (dict): Encabezados para la autenticación en la API TMDB.
        params_details (dict): Parámetros adicionales para la solicitud de detalles (por ejemplo, idioma).
        delay (float, optional): Retardo entre solicitudes para evitar sobrecargar la API. Por defecto es 0.15 segundos.
        
    Returns:
        None. Los datos enriquecidos se guardan en la tabla 'movies_enriched'.
    """
    conn = sqlite3.connect(db_path)
    df_movies = pd.read_sql("SELECT * FROM movies_cleaned", conn)
    print(f"Total de películas a enriquecer (TMDB details): {len(df_movies)}")
    
    enriched_data = []
    for index, row in df_movies.iterrows():
        movie_id = row["id"]
        details_url = f"https://api.themoviedb.org/3/movie/{movie_id}"
        try:
            details_response = requests.get(details_url, headers=headers, params=params_details)
            if details_response.status_code == 200:
                movie_details = details_response.json()
                row_dict = row.to_dict()
                row_dict["status"] = movie_details.get("status")
                row_dict["belongs_to_collection"] = movie_details.get("belongs_to_collection")
                row_dict["imdb_id"] = movie_details.get("imdb_id")
                enriched_data.append(row_dict)
                print(f"Película enriquecida: {row_dict.get('original_title', 'N/A')} (ID: {movie_id})")
            else:
                print(f"Error al obtener detalles para la película ID: {movie_id} - Código: {details_response.status_code}")
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
    
    df_enriched = pd.DataFrame(enriched_data)
    df_enriched = df_enriched.applymap(lambda val: json.dumps(val) if isinstance(val, (list, dict)) else val)
    df_enriched.to_sql('movies_enriched', conn, if_exists='replace', index=False)
    print("Tabla 'movies_enriched' creada en la base de datos (TMDB details).")
    conn.close()


def enrich_watch_providers(db_path: str, headers: dict, delay: float = 0.15) -> None:
    """
    Enriquecer la información de Watch Providers para Colombia (código "CO").
    
    Lee el DataFrame desde la tabla 'movies_enriched', consulta el endpoint de Watch Providers para cada
    película y extrae la información correspondiente al país Colombia. Para cada película se agregan las siguientes
    columnas:
      - watch_link_co: Enlace general de visualización para Colombia.
      - provider_type_co: Tipos de servicio disponibles (flatrate, buy, rent) separados por comas.
      - providers_co: Información de proveedores en formato JSON, filtrando para excluir las claves 
                        'logo_path', 'provider_id' y 'display_priority'.
    
    Args:
        db_path (str): Ruta de la base de datos SQLite.
        headers (dict): Encabezados para la autenticación en la API TMDB.
        delay (float, optional): Retardo entre solicitudes. Por defecto es 0.15 segundos.
        
    Returns:
        None. La tabla 'movies_enriched' se actualiza con la información de Watch Providers.
    """
    conn = sqlite3.connect(db_path)
    df_movies = pd.read_sql("SELECT * FROM movies_enriched", conn)
    print(f"Total de películas a enriquecer (Watch Providers): {len(df_movies)}")
    
    enriched_providers = []
    base_url_providers = "https://api.themoviedb.org/3/movie"
    
    for index, row in df_movies.iterrows():
        movie_id = row["id"]
        providers_url = f"{base_url_providers}/{movie_id}/watch/providers"
        try:
            response = requests.get(providers_url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", {})
                co_info = results.get("CO", None)
                if co_info:
                    watch_link = co_info.get("link")
                    provider_types = []
                    provider_data = []
                    for key in ["flatrate", "buy", "rent"]:
                        if key in co_info and co_info[key]:
                            provider_types.append(key)
                            provider_data.extend(co_info[key])
                else:
                    watch_link = None
                    provider_types = []
                    provider_data = []
            else:
                print(f"Error al obtener providers para la película ID {movie_id} - Código: {response.status_code}")
                watch_link = None
                provider_types = []
                provider_data = []
        except Exception as e:
            print(f"Excepción para la película ID {movie_id}: {e}")
            watch_link = None
            provider_types = []
            provider_data = []
        
        row_dict = row.to_dict()
        row_dict["watch_link_co"] = watch_link
        row_dict["provider_type_co"] = ", ".join(provider_types) if provider_types else None
        
        # Filtrar cada proveedor para excluir las claves no deseadas
        cleaned_provider_data = []
        for provider in provider_data:
            cleaned_provider = { key: value for key, value in provider.items() if key not in ["logo_path", "provider_id", "display_priority"] }
            cleaned_provider_data.append(cleaned_provider)
        
        row_dict["providers_co"] = json.dumps(cleaned_provider_data) if cleaned_provider_data else None
        
        enriched_providers.append(row_dict)
        time.sleep(delay)
    
    df_watch_providers = pd.DataFrame(enriched_providers)
    df_watch_providers = df_watch_providers.applymap(lambda val: json.dumps(val) if isinstance(val, (list, dict)) else val)
    df_watch_providers.to_sql('movies_enriched', conn, if_exists='replace', index=False)
    print("Tabla 'movies_enriched' actualizada con información de Watch Providers (CO).")
    conn.close()


def enrich_omdb_details(db_path: str, omdb_api_key: str, delay: float = 0.15) -> None:
    """
    Enriquecer la información de OMDb para cada película que tenga un imdb_id válido.
    
    Lee el DataFrame de la tabla 'movies_enriched', consulta el endpoint de OMDb usando el imdb_id y agrega
    los siguientes campos: imdbVotes, imdbRating, Director_omdb y Awards_omdb. Los datos actualizados se almacenan
    nuevamente en la tabla 'movies_enriched'.
    
    Args:
        db_path (str): Ruta de la base de datos SQLite.
        omdb_api_key (str): Clave de API para acceder a la API OMDb.
        delay (float, optional): Retardo entre solicitudes. Por defecto es 0.15 segundos.
        
    Returns:
        None. La tabla 'movies_enriched' se actualiza con la información de OMDb.
    """
    base_url_omdb = "https://www.omdbapi.com/"
    conn = sqlite3.connect(db_path)
    df_enriched = pd.read_sql("SELECT * FROM movies_enriched", conn)
    print(f"Total de películas a enriquecer (OMDb): {len(df_enriched)}")
    
    enriched_data_omdb = []
    for index, row in df_enriched.iterrows():
        imdb_id = row.get("imdb_id", "")
        if imdb_id and imdb_id != "None":
            omdb_url = f"{base_url_omdb}?apikey={omdb_api_key}&i={imdb_id}"
            try:
                omdb_response = requests.get(omdb_url)
                if omdb_response.status_code == 200:
                    omdb_details = omdb_response.json()
                    imdbVotes = omdb_details.get("imdbVotes")
                    imdbRating = omdb_details.get("imdbRating")
                    Director_omdb = omdb_details.get("Director")
                    Awards_omdb = omdb_details.get("Awards")
                    print(f"OMDb enriquecido: {omdb_details.get('Title', 'N/A')} (imdb_id: {imdb_id})")
                else:
                    print(f"Error OMDb para imdb_id: {imdb_id} - Código: {omdb_response.status_code}")
                    imdbVotes, imdbRating, Director_omdb, Awards_omdb = None, None, None, None
            except Exception as e:
                print(f"Excepción en OMDb para imdb_id: {imdb_id}: {e}")
                imdbVotes, imdbRating, Director_omdb, Awards_omdb = None, None, None, None
        else:
            imdbVotes, imdbRating, Director_omdb, Awards_omdb = None, None, None, None
        
        row_dict = row.to_dict()
        row_dict["imdbVotes"] = imdbVotes
        row_dict["imdbRating"] = imdbRating
        row_dict["Director_omdb"] = Director_omdb
        row_dict["Awards_omdb"] = Awards_omdb
        enriched_data_omdb.append(row_dict)
        time.sleep(delay)
    
    df_enriched_omdb = pd.DataFrame(enriched_data_omdb)
    df_enriched_omdb = df_enriched_omdb.applymap(lambda val: json.dumps(val) if isinstance(val, (list, dict)) else val)
    df_enriched_omdb.to_sql('movies_enriched', conn, if_exists='replace', index=False)
    print("Tabla 'movies_enriched' actualizada con información de OMDb.")
    conn.close()


###############################################################################
# Funciones de exportación y generación de reporte de auditoría
###############################################################################

def export_enriched_dataset(db_path: str, excel_file: str) -> pd.DataFrame:
    """
    Exporta el dataset enriquecido desde la base de datos a archivos Excel.
    
    Args:
        db_path (str): Ruta de la base de datos SQLite.
        excel_file (str): Ruta del archivo Excel a generar.
        
    Returns:
        pd.DataFrame: El DataFrame final enriquecido leído desde la base de datos.
    """
    conn = sqlite3.connect(db_path)
    df_final = pd.read_sql("SELECT * FROM movies_enriched", conn)
    conn.close()
    
    df_final.to_excel(excel_file, index=False)
    print(f"Dataset enriquecido exportado a {excel_file}")
    return df_final


def generate_audit_report(db_path: str, report_file: str) -> None:
    """
    Genera un reporte comparativo de auditoría entre el dataset base y el dataset enriquecido.
    
    Compara el número de registros, las columnas presentes y la integridad de campos clave entre la tabla
    'movies_cleaned' y 'movies_enriched', y guarda el reporte en un archivo de texto.
    
    Args:
        db_path (str): Ruta de la base de datos SQLite.
        report_file (str): Ruta del archivo donde se guardará el reporte de auditoría.
        
    Returns:
        None. El reporte se guarda en el archivo especificado.
    """
    conn = sqlite3.connect(db_path)
    df_base = pd.read_sql("SELECT * FROM movies_cleaned", conn)
    df_enriched = pd.read_sql("SELECT * FROM movies_enriched", conn)
    conn.close()
    
    base_count = df_base.shape[0]
    enriched_count = df_enriched.shape[0]
    
    tmdb_enriched_count = df_enriched["status"].notnull().sum() if "status" in df_enriched.columns else 0
    watch_providers_count = df_enriched["watch_link_co"].notnull().sum() if "watch_link_co" in df_enriched.columns else 0
    omdb_enriched_count = df_enriched["imdbVotes"].notnull().sum() if "imdbVotes" in df_enriched.columns else 0
    
    cols_api = set(df_enriched.columns)
    cols_base = set(df_base.columns)
    
    diff_base_api = cols_api.symmetric_difference(cols_base)
    
    report_lines = [
        "ENRICHMENT REPORT",
        "===========================",
        "",
        f"Dataset base (movies_cleaned) count: {base_count}",
        f"Dataset final (movies_enriched) count: {enriched_count}",
        "",
        "TMDB Details Enrichment:",
        f"- Registros con 'status': {tmdb_enriched_count}",
        "",
        "Watch Providers (Colombia) Enrichment:",
        f"- Registros con 'watch_link_co': {watch_providers_count}",
        "",
        "OMDb Enrichment:",
        f"- Registros con 'imdbVotes' no nulo: {omdb_enriched_count}",
        "",
        "Columnas presentes:",
        f"- Dataset base: {', '.join(sorted(cols_base))}",
        f"- Dataset enriquecido: {', '.join(sorted(cols_api))}",
        "",
        "Diferencias entre columnas (symmetric difference):",
        f"  {', '.join(sorted(diff_base_api)) if diff_base_api else 'No hay diferencias'}",
        "",
        "Verificación de integridad (campos clave):"
    ]
    
    key_fields = ['id', 'original_title']
    for key in key_fields:
        missing_base = df_base[key].isnull().sum() if key in df_base.columns else "No encontrada"
        missing_enriched = df_enriched[key].isnull().sum() if key in df_enriched.columns else "No encontrada"
        report_lines.append(f"  Campo '{key}': Base = {missing_base}, Enriquecido = {missing_enriched}")
    
    report_lines.append("")
    report_lines.append("Observaciones:")
    report_lines.append("- Se realizó el cruce de datos de TMDB para incorporar detalles (status, belongs_to_collection, imdb_id).")
    report_lines.append("- Se integró la información de Watch Providers para Colombia (combinando flatrate, buy y rent).")
    report_lines.append("- La integración con OMDb se efectuó para registros con un imdb_id válido, añadiendo imdbVotes, imdbRating, Director y Awards.")
    report_lines.append("- La combinación de estas fuentes enriquece el dataset con metadatos, datos de streaming y calificaciones externas.")
    
    with open(report_file, "w", encoding="utf-8") as f:
        for line in report_lines:
            f.write(line + "\n")
    
    print(f"Reporte de auditoría generado en: {report_file}")


###############################################################################
# Ejecución principal
###############################################################################
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

if __name__ == "__main__":
    DB_PATH = "src/static/db/ingestion.db"
    OMDB_API_KEY = os.getenv("OMDB_API_KEY")
    
    # Enriquecimiento con detalles de TMDB
    enrich_tmdb_details(DB_PATH, headers, paramsDetails, delay=0.15)
    
    # Enriquecimiento con Watch Providers para Colombia
    enrich_watch_providers(DB_PATH, headers, delay=0.15)
    
    # Enriquecimiento con OMDb (si se dispone de OMDB_API_KEY)
    if OMDB_API_KEY:
        enrich_omdb_details(DB_PATH, OMDB_API_KEY, delay=0.15)
    else:
        print("No se encontró la OMDB_API_KEY. Se omite el enriquecimiento con OMDb.")
    
    # Exportar el dataset final enriquecido a Excel y CSV
    EXCEL_FILE = "src/static/xlsx/enriched_data.xlsx"
    df_final = export_enriched_dataset(DB_PATH, EXCEL_FILE)
    
    # Generar reporte de auditoría comparativa
    REPORT_FILE = "src/static/auditoria/enrichment_report.txt"
    generate_audit_report(DB_PATH, REPORT_FILE)
