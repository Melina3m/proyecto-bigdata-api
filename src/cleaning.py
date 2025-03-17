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

# Configura pandas para mostrar todas las columnas
pd.set_option('display.max_columns', None)

#Configura pandas para mostrar el total de todas las filas
pd.set_option('display.max_colwidth', None)

#Eliminar la columna de overview(descripción de la película)
df_movies.drop('overview', axis=1, errors='ignore', inplace=True)

#Eliminar la columna genre_ids
df_movies.drop('genre_ids', axis=1, errors='ignore', inplace=True)

#Eliminar la columna poster_path
df_movies.drop('poster_path', axis=1, errors='ignore', inplace=True)

#Eliminar la columna homepage
df_movies.drop('homepage', axis=1, errors='ignore', inplace=True)

#Eliminar la columna backdrop_path
df_movies.drop('backdrop_path', axis=1, errors='ignore', inplace=True)

# Rellenar valores faltantes para columnas de texto específicas
df_movies['production_companies'] = df_movies['production_companies'].fillna('No aplica')
df_movies['production_countries'] = df_movies['production_countries'].fillna('No aplica')

# Lista de columnas de texto
text_columns = ['overview', 'tagline', 'original_title', 'original_language', 'title', 'spoken_languages', 'production_companies', 'production_countries', 'origin_country', 'genres']

# Verificar qué columnas de la lista están en el DataFrame
existing_columns = [col for col in text_columns if col in df_movies.columns]

# Rellenar solo las columnas existentes con 'N/A'
df_movies[existing_columns] = df_movies[existing_columns].fillna('N/A')

# Dejar los valores vacíos en las columnas de fechas
# Verificar si tienes columnas con fechas y dejarlas como están si están vacías
date_columns = ['release_date']  # Lista de columnas de fechas
df_movies[date_columns] = df_movies[date_columns]  # Dejamos NaN en las fechas

# Convertir la columna "release_date" en formato de texto a un formato de fecha manejable por pandas
# El parámetro 'errors="coerce"' se utiliza para evitar errores en caso de que pandas no pueda convertir algún valor.
# Si alguna fecha no puede ser convertida (por ejemplo, si está malformada o vacía), se asignará un valor NaT (Not a Time).
df_movies["release_date"] = pd.to_datetime(df_movies["release_date"], errors='coerce')

# Verificar si hay filas con valores completamente vacíos
empty_rows = df_movies.isnull().all(axis=1)
print(f"Cantidad de filas completamente vacías: {empty_rows.sum()}")

# Verificar si aún quedan valores faltantes en las columnas importantes
print(df_movies.isnull().sum())

# Rellenar 'runtime' con 0 para los valores faltantes
df_movies['runtime'] = df_movies['runtime'].fillna(0)

# Dejar 'release_date' con NaT (pd.NA) para los valores faltantes
df_movies['release_date'] = df_movies['release_date'].fillna(pd.NA)

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

# Reemplazar las siglas con los nombres completos en español en la columna
df_movies['original_language'] = df_movies['original_language'].replace(language_map_es)

# Verificar el resultado
# print(df_movies['original_language'].unique())

# Dividir los valores separados por coma y aplanar la lista
all_countries = df_movies['production_countries'].dropna().str.split(',').explode()

# Eliminar espacios en blanco adicionales alrededor de los nombres de los países
all_countries = all_countries.str.strip()

# Contar los países únicos
unique_countries_count = all_countries.nunique()

print(f"Número de países únicos: {unique_countries_count}")

# Obtener el listado de países únicos
unique_countries = all_countries.unique()

# Mostrar el listado ordenado alfabéticamente
unique_countries_sorted = sorted(unique_countries)
print("Listado de países únicos:")
for country in unique_countries_sorted:
    print(country)
    
# Diccionario de traducción de países (como el definido previamente)
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

# Reemplazar los países en la columna del DataFrame
def translate_countries(countries_string):
    if isinstance(countries_string, str):  # Verificar que no sea NaN
        return ", ".join([country_translation.get(country.strip(), country.strip()) for country in countries_string.split(',')])
    return countries_string  # Si es NaN, devolver el valor original

# Aplicar la función de traducción a la columna
df_movies['production_countries'] = df_movies['production_countries'].apply(translate_countries)