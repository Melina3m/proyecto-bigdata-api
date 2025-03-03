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


## Instrucciones para ejecutar el proyecto

### 1. Requisitos previos

- **Python 3.8+**
- Instalar las librerías requeridas desde `requirements.txt`:
  ```bash
  pip install -r requirements.txt

### 2. Configuración
- ** Crea un archivo .env en la raíz del proyecto con tu token de la API de TMDB:
    TMDB_API_TOKEN=tu_token

### 3. Ejecución
- ** Para ejecutar el script principal: python src/ingestion.py

### 4. Librerias utilizadas
- ** Librerías utilizadas
Numba: Para optimizaciones en la ejecución.
Requests: Para realizar solicitudes HTTP a la API de TMDB.
Pandas: Para manipulación y análisis de datos.
SQLite3: Para gestionar la base de datos SQLite.
ydata_profiling: Para generar informes de auditoría.
dotenv: Para manejar variables de entorno de manera segura.