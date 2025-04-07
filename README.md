# Proyecto Big Data - TMDB API

## Descripción

Este proyecto consiste en la extracción, almacenamiento y análisis de datos de películas utilizando la API de **The Movie Database (TMDB)**. El objetivo principal es obtener información sobre las películas lanzadas entre 2020 y 2024, almacenarla en una base de datos **SQLite** y realizar una auditoría comparativa de los datos obtenidos de diferentes fuentes (API, SQLite y Excel).

## Funcionalidades

1. **Extracción de datos de películas**:
   - Se extraen datos como título, presupuesto, ingresos, géneros, compañías de producción, duración, etc., desde la API de TMDB.
   - Se utiliza paginación para obtener varias páginas de resultados.

2. **Almacenamiento de datos**:
   - Los datos extraídos de la API se almacenan en dos formatos:
     - **Base de datos SQLite**: Los datos se guardan en la tabla `movies` dentro de un archivo `ingestion.db` ubicado en `src/static/db/`.
     - **Archivo Excel**: Los datos se exportan a un archivo Excel llamado `tmdb_movies.xlsx`, ubicado en `src/static/xlsx/`.

3. **Auditoría de datos**:
   - Se generan informes de auditoría para comparar los datos obtenidos de la API, la base de datos SQLite y el archivo Excel.
   - Los informes de auditoría son generados usando la librería **ydata_profiling** y están disponibles en formato HTML:
     - `sqlite_audit_report.html`: Auditoría de los datos en SQLite.
     - `excel_audit_report.html`: Auditoría de los datos en el archivo Excel.
   - También se genera un informe comparativo en formato de texto: `comparative_audit_report.txt`.

## Limpieza y Procesamiento de Datos

Este proyecto incluye un proceso completo de limpieza y transformación de los datos obtenidos de la API de TMDB.

### Funcionalidades de Limpieza

1. **Operaciones básicas de limpieza**:
   - Eliminación de filas duplicadas
   - Eliminación de columnas innecesarias (overview, genre_ids, poster_path, homepage, backdrop_path)
   - Tratamiento de valores nulos y faltantes

2. **Transformaciones de datos**:
   - Conversión de columnas de listas a cadenas de texto separadas por comas
   - Conversión de fechas al formato datetime de pandas
   - Relleno inteligente de valores faltantes según el tipo de datos:
     - Columnas de texto: 'N/A' o 'No aplica'
     - Columnas numéricas (runtime): 0
     - Fechas: se mantienen como valores nulos (NaT)

3. **Traducción y normalización**:
   - Traducción de géneros cinematográficos al español
   - Traducción de códigos de idioma a nombres completos en español
   - Traducción de nombres de países al español
   - Normalización de campos con problemas de codificación

4. **Almacenamiento de datos limpios**:
   - Creación de una nueva tabla `movies_cleaned` en la base de datos SQLite
   - Exportación a archivo Excel `cleaned_data.xlsx`
   - Generación de informe de auditoría `cleaning_report.txt`

### Estadísticas de limpieza

El proceso documenta métricas importantes como:
- Número de registros antes y después de la limpieza
- Número de columnas procesadas
- Total de valores nulos antes y después del proceso
- Cantidad de filas duplicadas detectadas y eliminadas

## Enriquecimiento de Datos

Tras la limpieza y la normalización, se lleva a cabo un proceso de enriquecimiento que integra información adicional desde **TMDB** (detalles y proveedores de visualización) y **OMDb** (información de IMDb).

Este enriquecimiento se realiza a través de varias funciones:

### `enrich_tmdb_details(db_path, headers, params_details, delay=0.15)`

- Consulta el endpoint de detalles de TMDB:  
  `https://api.themoviedb.org/3/movie/{movie_id}`  
  para cada película y agrega campos como:
  - **status** (Status de la película según TMDB).
  - **belongs_to_collection** (Colección a la que pertenece).
  - **imdb_id** (ID de IMDb para posteriores consultas en OMDb).
- Los datos se guardan en la tabla `movies_enriched` de la base de datos.

### `enrich_watch_providers(db_path, headers, delay=0.15)`

- Consulta los proveedores de visualización en TMDB:  
  `https://api.themoviedb.org/3/movie/{movie_id}/watch/providers`  
  para cada película.
- Agrega información específica para **Colombia** (código "CO"):
  - **watch_link_co**: Enlace general para ver la película en CO.
  - **provider_type_co**: Lista de tipos de servicio disponibles (flatrate, buy, rent).
  - **providers_co**: Información de los proveedores (filtrando datos innecesarios como `logo_path`, `provider_id`, etc.).
- Los datos se actualizan en la misma tabla `movies_enriched`.

### `enrich_omdb_details(db_path, omdb_api_key, delay=0.15)`

- Utiliza el `imdb_id` previamente obtenido para consultar la API de **OMDb**:  
  `https://www.omdbapi.com/`
- Para cada película que tenga un `imdb_id` válido, se añaden:
  - **imdbVotes**
  - **imdbRating**
  - **Director_omdb**
  - **Awards_omdb**
- Se requiere una clave de API específica de OMDb (`OMDB_API_KEY`).
- La tabla `movies_enriched` se actualiza con estos campos.

---

## Exportación de datos enriquecidos y reporte de auditoría final

Después de las operaciones de enriquecimiento, se generan dos salidas principales:

1. **Exportación del dataset enriquecido**  
   La función `export_enriched_dataset(db_path, excel_file)` exporta el contenido de la tabla `movies_enriched` a un archivo Excel (**`enriched_data.xlsx`**).  
   Este archivo se genera en la carpeta `src/static/xlsx/`.

2. **Generación de reporte de auditoría**  
   La función `generate_audit_report(db_path, report_file)` crea un reporte comparativo en texto, **`enrichment_report.txt`**, que incluye:
   - Comparación del número de registros entre la tabla base `movies_cleaned` y la tabla `movies_enriched`.
   - Validación de la cantidad de registros enriquecidos con datos de TMDB (`status`), Watch Providers (`watch_link_co`) y OMDb (`imdbVotes`).
   - Revisión de columnas y diferencias entre ambas tablas.

Este archivo de reporte se genera en la carpeta `src/static/auditoria/`.

## Instrucciones para ejecutar el proyecto

### 1. Requisitos previos

- **Python 3.8+**
- Instalar las librerías requeridas desde `requirements.txt`:
  ```bash
  pip install -r requirements.txt

### 2. Configuración
- ** Crea un archivo .env en la raíz del proyecto con tu token de la API de TMDB:
    TMDB_API_TOKEN=tu_token
    OMDB_API_KEY=tu_clave

### 3. Ejecución
- ** Para ejecutar el script principal: python src/ingestion.py
- ** Para ejecutar el script de limpieza: python src/cleaning.py
- ** Para ejecutar el script de enriquecimiento: python src/enrichement.py

### 4. Librerias utilizadas
- ** Librerías utilizadas
Numba: Para optimizaciones en la ejecución.
Requests: Para realizar solicitudes HTTP a la API de TMDB.
Pandas: Para manipulación y análisis de datos.
SQLite3: Para gestionar la base de datos SQLite.
ydata_profiling: Para generar informes de auditoría.
dotenv: Para manejar variables de entorno de manera segura.