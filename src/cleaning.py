import sqlite3
import pandas as pd
import ast
import os
import json
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

###############################################################################
# Diccionarios globales para traducciones
###############################################################################

# Diccionario de traducciones de géneros (inglés -> español)
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

# Diccionario de códigos de idioma a nombres completos en español
language_map_es = {
    'en': 'Inglés',
    'fr': 'Francés',
    'nl': 'Neerlandés',
    'cn': 'Chino',
    'ru': 'Ruso',
    'es': 'Español',
    'zh': 'Chino',
    'sv': 'Sueco',
    'sr': 'Serbio',
    'it': 'Italiano',
    'de': 'Alemán',
    'ja': 'Japonés',
    'no': 'Noruego',
    'fa': 'Persa',
    'pt': 'Portugués',
    'da': 'Danés',
    'xx': 'Desconocido',
    'bs': 'Bosnio',
    'cs': 'Checo',
    'ko': 'Coreano',
    'el': 'Griego',
    'hi': 'Hindi',
    'pl': 'Polaco',
    'ps': 'Pastún',
    'fi': 'Finlandés',
    'ro': 'Rumano',
    'hu': 'Húngaro',
    'he': 'Hebreo',
    'af': 'Afrikáans',
    'th': 'Tailandés',
    'bo': 'Tibetano',
    'la': 'Latín',
    'vi': 'Vietnamita',
    'ca': 'Catalán',
    'bm': 'Bambara',
    'tr': 'Turco',
    'ta': 'Tamil',
    'bg': 'Búlgaro',
    'nb': 'Noruego Bokmål',
    'id': 'Indonesio',
    'lv': 'Letón',
    'ku': 'Kurdo',
    'ml': 'Malabar',
    'lo': 'Lao',
    'ar': 'Árabe',
    'kn': 'Canarés',
    'is': 'Islandés',
    'sl': 'Esloveno',
    'et': 'Estonio',
    'mr': 'Maratí',
    'sq': 'Albanés',
    'te': 'Telugu',
    'uk': 'Ucraniano',
    'ur': 'Urdú'
}

# Diccionario de traducción de idiomas (para la función translate_languages)
language_translation = {
    '?????': 'Desconocido',
    'Afrikaans': 'Afrikáans',
    'Bahasa indonesia': 'Indonesio',
    'Bahasa melayu': 'Malayo',
    'Bamanankan': 'Bambara',
    'BokmÃ¥l': 'Bokmål',
    'Bosanski': 'Bosnio',
    'CatalÃ': 'Catalán',
    'Cymraeg': 'Galés',
    'Dansk': 'Danés',
    'Deutsch': 'Alemán',
    'Eesti': 'Estonio',
    'English': 'Inglés',
    'EspaÃ±ol': 'Español',
    'Esperanto': 'Esperanto',
    'FranÃ§ais': 'Francés',
    'Gaeilge': 'Irlandés',
    'Galego': 'Gallego',
    'Hausa': 'Hausa',
    'Hrvatski': 'Croata',
    'Italiano': 'Italiano',
    'Kinyarwanda': 'Kinyarwanda',
    'Kiswahili': 'Swahili',
    'Latin': 'Latín',
    'LatvieÅ¡u': 'Letón',
    'Lietuvikai': 'Lituano',
    'Magyar': 'Húngaro',
    'Malti': 'Maltés',
    'Nederlands': 'Neerlandés',
    'No Language': 'Sin Idioma',
    'Norsk': 'Noruego',
    'Polski': 'Polaco',
    'PortuguÃªs': 'Portugués',
    'PÑÑÑÐºÐ¸Ð¹': 'Ruso',
    'RomÃ¢nÄ': 'Rumano',
    'SlovenÄina': 'Eslovaco',
    'SlovenÅ¡Äina': 'Esloveno',
    'Somali': 'Somalí',
    'Srpski': 'Serbio',
    'Tiáº¿ng Viá»t': 'Vietnamita',
    'TÃ¼rkÃ§e': 'Turco',
    'euskera': 'Euskera',
    'isiZulu': 'Zulú',
    'shqip': 'Albanés',
    'suomi': 'Finlandés',
    'svenska': 'Sueco',
    'Ãslenska': 'Islandés',
    'ÄeskÃ½': 'Checo',
    'ÎµÎ»Î»Î·Î½Î¹ÎºÎ¬': 'Griego',
    'Ð£ÐºÑÐ°ÑÐ½ÑÑÐºÐ¸Ð¹': 'Ucraniano',
    'Ð±ÐµÐ»Ð°ÑÑÑÑÐºÐ°Ñ Ð¼Ð¾Ð²Ð°': 'Bielorruso',
    'Ð±ÑÐ»Ð³Ð°ÑÑÐºÐ¸ ÐµÐ·Ð¸Ðº': 'Búlgaro',
    'ÒÐ°Ð·Ð°Ò': 'Kazajo',
    '×¢Ö´×Ö°×¨Ö´××ª': 'Hebreo',
    'Ø§Ø±Ø¯Ù': 'Urdú',
    'Ø§ÙØ¹Ø±Ø¨ÙØ©': 'Árabe',
    'ÙØ§Ø±Ø³Û': 'Persa',
    'Ù¾ÚØªÙ': 'Pastún',
    'à¤¹à¤¿à¤¨à¥à¤¦à¥': 'Hindi',
    'à¦¬à¦¾à¦à¦²à¦¾': 'Bengalí',
    'à¨ªà©°à¨à¨¾à¨¬à©': 'Panyabí',
    'à®¤à®®à®¿à®´à¯': 'Tamil',
    'à°¤à±à°²à±à°à±': 'Telugu',
    'à¸ à¸²à¸©à¸²à¹à¸à¸¢': 'Tailandés',
    'á¥áá áá£áá': 'Georgiano',
    'å¹¿å·è¯ / å»£å·è©±': 'Cantonés',
    'æ¥æ¬èª': 'Japonés',
    'æ®éè¯': 'Chino Mandarín',
    'íêµ­ì´/ì¡°ì ë§': 'Coreano',
    "Español": "Español",
    "Français": "Francés", 
    "Português": "Portugués",
    "Pусский": "Ruso",
    "العربية": "Árabe",
    "हिन्दी": "Hindi",
    "ਪੰਜਾਬੀ": "Panyabí",
    "广州话 / 廣州話": "Cantonés",
    "日本語": "Japonés",
    "普通话": "Chino Mandarín",
    "한국어/조선말": "Coreano",
    "ภาษาไทย": "Tailandés",
}

# Diccionario de traducción de países (global)
country_translation = {
    'Afghanistan': 'Afganistán',
    'Algeria': 'Argelia',
    'Angola': 'Angola',
    'Argentina': 'Argentina',
    'Aruba': 'Aruba',
    'Australia': 'Australia',
    'Austria': 'Austria',
    'Bahamas': 'Bahamas',
    'Belarus': 'Bielorrusia',
    'Belgium': 'Bélgica',
    'Bolivia': 'Bolivia',
    'Bosnia and Herzegovina': 'Bosnia y Herzegovina',
    'Botswana': 'Botsuana',
    'Brazil': 'Brasil',
    'Bulgaria': 'Bulgaria',
    'Burkina Faso': 'Burkina Faso',
    'Cambodia': 'Camboya',
    'Canada': 'Canadá',
    'Chile': 'Chile',
    'China': 'China',
    'Colombia': 'Colombia',
    'Costa Rica': 'Costa Rica',
    'Croatia': 'Croacia',
    'Cuba': 'Cuba',
    'Cyprus': 'Chipre',
    'Czech Republic': 'República Checa',
    'Denmark': 'Dinamarca',
    'Dominican Republic': 'República Dominicana',
    'Ecuador': 'Ecuador',
    'Egypt': 'Egipto',
    'Estonia': 'Estonia',
    'Ethiopia': 'Etiopía',
    'Finland': 'Finlandia',
    'France': 'Francia',
    'Georgia': 'Georgia',
    'Germany': 'Alemania',
    'Ghana': 'Ghana',
    'Gibraltar': 'Gibraltar',
    'Greece': 'Grecia',
    'Guatemala': 'Guatemala',
    'Honduras': 'Honduras',
    'Hong Kong': 'Hong Kong',
    'Hungary': 'Hungría',
    'Iceland': 'Islandia',
    'India': 'India',
    'Indonesia': 'Indonesia',
    'Iran': 'Irán',
    'Iraq': 'Irak',
    'Ireland': 'Irlanda',
    'Israel': 'Israel',
    'Italy': 'Italia',
    'Jamaica': 'Jamaica',
    'Japan': 'Japón',
    'Kazakhstan': 'Kazajistán',
    'Kenya': 'Kenia',
    "Lao People's Democratic Republic": 'Laos',
    'Latvia': 'Letonia',
    'Libyan Arab Jamahiriya': 'Libia',
    'Liechtenstein': 'Liechtenstein',
    'Lithuania': 'Lituania',
    'Luxembourg': 'Luxemburgo',
    'Macedonia': 'Macedonia',
    'Malaysia': 'Malasia',
    'Mali': 'Malí',
    'Malta': 'Malta',
    'Mexico': 'México',
    'Monaco': 'Mónaco',
    'Morocco': 'Marruecos',
    'Namibia': 'Namibia',
    'Netherlands': 'Países Bajos',
    'New Zealand': 'Nueva Zelanda',
    'Nicaragua': 'Nicaragua',
    'Nigeria': 'Nigeria',
    'Norway': 'Noruega',
    'Pakistan': 'Pakistán',
    'Panama': 'Panamá',
    'Paraguay': 'Paraguay',
    'Peru': 'Perú',
    'Philippines': 'Filipinas',
    'Poland': 'Polonia',
    'Portugal': 'Portugal',
    'Puerto Rico': 'Puerto Rico',
    'Qatar': 'Catar',
    'Romania': 'Rumanía',
    'Russia': 'Rusia',
    'Rwanda': 'Ruanda',
    'Serbia': 'Serbia',
    'Serbia and Montenegro': 'Serbia y Montenegro',
    'Singapore': 'Singapur',
    'Slovakia': 'Eslovaquia',
    'Slovenia': 'Eslovenia',
    'South Africa': 'Sudáfrica',
    'South Korea': 'Corea del Sur',
    'Spain': 'España',
    'Sweden': 'Suecia',
    'Switzerland': 'Suiza',
    'Taiwan': 'Taiwán',
    'Thailand': 'Tailandia',
    'Tunisia': 'Túnez',
    'Turkey': 'Turquía',
    'Uganda': 'Uganda',
    'Ukraine': 'Ucrania',
    'United Arab Emirates': 'Emiratos Árabes Unidos',
    'United Kingdom': 'Reino Unido',
    'United States of America': 'Estados Unidos',
    'Uruguay': 'Uruguay',
    'Venezuela': 'Venezuela'
}

###############################################################################
# Funciones de traducción de datos
###############################################################################

def translate_genres(genres_str: str) -> str:
    """
    Traduce los géneros de películas del inglés al español.

    Args:
        genres_str (str): Cadena de géneros separados por comas, por ejemplo "Action, Comedy".

    Returns:
        str: Cadena con los géneros traducidos al español separados por comas.
    """
    genres_list = [g.strip() for g in genres_str.split(",")]
    translated_list = [genre_translation.get(g, g) for g in genres_list]
    return ", ".join(translated_list)


def translate_languages(language_string: str) -> str:
    """
    Traduce una cadena de idiomas (separados por comas) a sus nombres en español.

    Args:
        language_string (str): Cadena con idiomas separados por comas.

    Returns:
        str: Cadena con los nombres de idiomas traducidos al español.
    """
    if isinstance(language_string, str):
        return ", ".join([language_translation.get(lang.strip(), 'Desconocido') for lang in language_string.split(',')])
    return language_string


def translate_countries(countries_string: str) -> str:
    """
    Traduce una cadena de códigos de países a sus nombres completos en español.

    Args:
        countries_string (str): Cadena con códigos de país separados por comas.

    Returns:
        str: Cadena con los nombres de países traducidos al español.
    """
    if isinstance(countries_string, str):
        return ", ".join([country_translation.get(country.strip(), country.strip()) for country in countries_string.split(',')])
    return countries_string

###############################################################################
# Funciones del pipeline de limpieza y auditoría
###############################################################################

def load_movies_from_db(db_path: str) -> pd.DataFrame:
    """
    Carga toda la información de la tabla 'movies' desde una base de datos SQLite.

    Args:
        db_path (str): Ruta de la base de datos SQLite.

    Returns:
        pd.DataFrame: DataFrame con los datos de la tabla 'movies'.
    """
    conn = sqlite3.connect(db_path)
    df = pd.read_sql("SELECT * FROM movies", conn)
    conn.close()
    return df

def clean_movies_df(df: pd.DataFrame) -> (pd.DataFrame, dict):
    """
    Realiza las operaciones de limpieza en el DataFrame de películas.

    Las operaciones incluyen:
      - Eliminación de filas duplicadas.
      - Conversión de columnas que contienen listas (en formato string) a cadenas de texto.
      - Traducción de géneros, países de producción y lenguajes hablados.
      - Eliminación de columnas innecesarias.
      - Relleno de valores nulos en columnas específicas.
      - Conversión de 'release_date' a formato datetime.
      - Relleno de valores faltantes en 'runtime' y 'release_date'.
      - Reemplazo de 'tagline' vacío o solo con espacios por 'N/A'.

    Args:
        df (pd.DataFrame): DataFrame original con los datos de películas.

    Returns:
        tuple: (df_cleaned, metrics) donde:
            - df_cleaned (pd.DataFrame): DataFrame limpio.
            - metrics (dict): Diccionario con métricas de la limpieza:
                - before_count: Número de registros antes de la limpieza.
                - after_count: Número de registros después de la limpieza.
                - before_columns: Número de columnas antes de la limpieza.
                - after_columns: Número de columnas después de la limpieza.
                - null_values_before: Número total de valores nulos antes de la limpieza.
                - null_values_after: Número total de valores nulos después de la limpieza.
                - duplicate_count: Número total de filas duplicadas eliminadas.
    """
    # Métricas iniciales
    null_values_before = df.isnull().sum().sum()
    before_count = df.shape[0]
    before_columns = len(df.columns)

    # Contar duplicados basados en todas las columnas y eliminarlos
    duplicate_rows = df.duplicated(keep=False)
    duplicate_count = duplicate_rows.sum()
    print(f"Número total de filas duplicadas: {duplicate_count}")
    df = df.drop_duplicates()

    # Convertir columnas de listas a cadenas de texto
    columns_to_format = ['genres', 'production_companies', 'spoken_languages', 'production_countries', 'origin_country']
    for col in columns_to_format:
        df[col] = df[col].apply(lambda x: ', '.join(ast.literal_eval(x)) if isinstance(x, str) and x.strip() != "" else x)

    # Aplicar traducciones a columnas específicas
    df["genres"] = df["genres"].apply(translate_genres)
    df['origin_country'] = df['origin_country'].apply(translate_countries)
    df['spoken_languages'] = df['spoken_languages'].apply(translate_languages)

    # Configurar pandas para mostrar todas las columnas y sin limitar ancho
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_colwidth', None)

    # Eliminar columnas innecesarias
    cols_to_drop = ['overview', 'genre_ids', 'poster_path', 'homepage', 'backdrop_path']
    df.drop(cols_to_drop, axis=1, errors='ignore', inplace=True)

    # Rellenar valores nulos en columnas específicas
    df['production_companies'] = df['production_companies'].fillna('No aplica')
    df['production_countries'] = df['production_countries'].fillna('No aplica')

    # Rellenar valores nulos en columnas de texto existentes con 'N/A'
    text_columns = ['overview', 'tagline', 'original_title', 'original_language', 'title', 
                    'spoken_languages', 'production_companies', 'production_countries', 'origin_country', 'genres']
    existing_text_cols = [col for col in text_columns if col in df.columns]
    df[existing_text_cols] = df[existing_text_cols].fillna('N/A')

    # Dejar los valores vacíos en las columnas de fechas sin modificar (NaN)
    date_columns = ['release_date']
    df[date_columns] = df[date_columns]

    # Convertir la columna "release_date" a formato datetime (errores a NaT)
    df["release_date"] = pd.to_datetime(df["release_date"], errors='coerce')

    # Rellenar 'runtime' con 0 para valores faltantes y 'release_date' con pd.NA para vacíos
    df['runtime'] = df['runtime'].fillna(0)
    df['release_date'] = df['release_date'].fillna(pd.NA)

    # Reemplazar 'tagline' vacío o sólo con espacios por 'N/A'
    df['tagline'] = df['tagline'].replace(r'^["\s]*$', 'N/A', regex=True)
    df['tagline'] = df['tagline'].fillna('N/A')

    # Métricas finales
    null_values_after = df.isnull().sum().sum()
    after_count = df.shape[0]
    after_columns = len(df.columns)

    metrics = {
        "before_count": before_count,
        "after_count": after_count,
        "before_columns": before_columns,
        "after_columns": after_columns,
        "null_values_before": null_values_before,
        "null_values_after": null_values_after,
        "duplicate_count": duplicate_count
    }
    
    return df, metrics

def export_cleaned_data(df: pd.DataFrame, excel_file: str, db_path: str) -> None:
    """
    Exporta el DataFrame limpio a un archivo Excel y lo guarda en la tabla 'movies_cleaned'
    de la base de datos SQLite.

    Args:
        df (pd.DataFrame): DataFrame limpio.
        excel_file (str): Ruta del archivo Excel donde se exportará el DataFrame.
        db_path (str): Ruta de la base de datos SQLite.

    Returns:
        None.
    """
    df.to_excel(excel_file, index=False)
    print(f"Datos limpios guardados en {excel_file}")
    
    conn = sqlite3.connect(db_path)
    df.to_sql('movies_cleaned', conn, if_exists='replace', index=False)
    conn.commit()
    conn.close()
    print("Datos guardados en la base de datos SQLite en la tabla 'movies_cleaned'.")

def generate_cleaning_report(metrics: dict, report_file: str) -> None:
    """
    Genera un archivo de auditoría con el reporte de limpieza de datos.

    El reporte incluye el número de registros y columnas antes y después de la limpieza,
    el total de valores nulos, y el número de filas duplicadas, además de las operaciones realizadas.

    Args:
        metrics (dict): Diccionario con métricas de limpieza.
        report_file (str): Ruta del archivo donde se guardará el reporte.

    Returns:
        None.
    """
    report = f"""\nREPORTE DE LIMPIEZA DE DATOS
============================
- Número de registros antes de la limpieza: {metrics['before_count']}
- Número de registros después de la limpieza: {metrics['after_count']}
- Número de columnas antes de la limpieza: {metrics['before_columns']}
- Número de columnas después de la limpieza: {metrics['after_columns']}
- Número total de valores nulos antes de la limpieza: {metrics['null_values_before']}
- Número total de valores nulos después de la limpieza: {metrics['null_values_after']}
- Número total de filas duplicadas: {metrics['duplicate_count']}

OPERACIONES REALIZADAS:
- Eliminación de filas duplicadas.
- Conversión de columnas de listas a cadenas de texto: genres, production_companies, spoken_languages, production_countries, origin_country.
- Eliminación de columnas: overview, genre_ids, poster_path, homepage, backdrop_path.
- Relleno de valores nulos en 'production_companies' y 'production_countries' con 'No aplica'.
- Relleno de valores nulos en columnas de texto con 'N/A'.
- Conversión de 'release_date' a formato datetime (con errores a NaT).
- Relleno de 'runtime' con 0 para valores faltantes.
- Traducción de códigos de idioma en 'original_language' a nombres en español.
- Traducción de géneros en la columna 'genres' a español.
- Traducción de países en la columna 'production_countries' a español.
- Traducción de códigos de país en 'origin_country' a español.
- Reemplazo de 'tagline' vacío o solo con espacios por 'N/A'.
- Creación de la tabla 'movies_cleaned' en la base de datos SQLite.
- Exportación del DataFrame limpio a 'cleaned_data.xlsx'.
"""
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"Archivo de auditoría '{report_file}' generado correctamente.")

###############################################################################
# Función principal del pipeline de limpieza
###############################################################################

def main_cleaning_pipeline() -> None:
    """
    Ejecuta el pipeline completo de limpieza de datos.

    El pipeline realiza los siguientes pasos:
      1. Carga el dataset desde la tabla 'movies' en la base de datos SQLite.
      2. Aplica operaciones de limpieza y traducción sobre los datos.
      3. Guarda el dataset limpio en la tabla 'movies_cleaned' de la base de datos.
      4. Exporta el dataset limpio a un archivo Excel.
      5. Genera un reporte de auditoría de la limpieza en un archivo de texto.

    Returns:
        None.
    """
    DB_PATH = "src/static/db/ingestion.db"
    EXCEL_FILE = "src/static/xlsx/cleaned_data.xlsx"
    REPORT_FILE = "src/static/auditoria/cleaning_report.txt"

    # Cargar datos desde la base de datos
    df_movies = load_movies_from_db(DB_PATH)
    
    # Guardar métricas iniciales (antes de la limpieza) si se desea usarlas en otro proceso
    before_count = df_movies.shape[0]
    before_columns = len(df_movies.columns)
    
    # Realizar la limpieza y obtener métricas
    df_cleaned, metrics = clean_movies_df(df_movies)
    
    # Exportar el DataFrame limpio
    export_cleaned_data(df_cleaned, EXCEL_FILE, DB_PATH)
    
    # Generar el reporte de auditoría
    generate_cleaning_report(metrics, REPORT_FILE)

if __name__ == "__main__":
    main_cleaning_pipeline()
