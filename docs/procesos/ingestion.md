# Proceso de ETL de datos desde TMDB

Este documento detalla el proceso ETL (Extracción, Transformación y Carga) aplicado a los datos de películas obtenidos desde la API de TMDB. El proceso integra información adicional mediante llamadas a diferentes endpoints de TMDB, exporta y almacena los datos en una base de datos SQLite, y genera reportes de auditoría que permiten validar la integridad y consistencia de la información.

## Operaciones del proceso

El script realiza las siguientes operaciones:

- **Extracción de datos desde TMDB:**
  - Se utiliza el endpoint "discover" para obtener un listado de películas.
  - Para cada película se consulta el endpoint de detalles para obtener información adicional, incluyendo:
    - Presupuesto (`budget`), ingresos (`revenue`), duración (`runtime`)
    - Géneros (convertidos a una lista de nombres)
    - País de origen (`origin_country`)
    - Compañías y países de producción
    - Idiomas hablados, homepage, tagline, promedio de votos (`vote_average`) y cantidad de votos (`vote_count`)

- **Exportación y almacenamiento:**
  - El conjunto de datos enriquecido se exporta a un archivo Excel.
  - Se guarda el DataFrame en la base de datos SQLite en la tabla `movies`, convirtiendo a string aquellas columnas que contienen listas o diccionarios para asegurar la compatibilidad con SQLite.

- **Generación de reportes de auditoría:**
  - Se generan reportes HTML de auditoría utilizando la herramienta **ydata_profiling** para validar los datos desde la base de datos SQLite y el archivo Excel.
  - Se elabora un reporte comparativo en formato de texto que:
    - Compara el número total de registros entre la API, SQLite y el archivo Excel.
    - Lista las columnas presentes en cada fuente.
    - Señala las diferencias en columnas clave.
    - Verifica la integridad de campos importantes (por ejemplo, `id` y `original_title`).

## Flujo del proceso

1. **Extracción de datos (fetch_tmdb_movies):**  
   Se realiza una solicitud al endpoint "discover" para obtener una lista de películas y se limita el procesamiento a un máximo de 5 páginas. Para cada película, se consulta el endpoint de detalles y se enriquece el registro con información adicional.

2. **Exportación de datos (export_tmdb_data):**  
   El DataFrame resultante se exporta a un archivo Excel (`tmdb_movies.xlsx`) y se almacena en la tabla `movies` de la base de datos SQLite. Durante este proceso, se convierten a cadena de texto las columnas complejas para evitar problemas de compatibilidad.

3. **Generación de reportes de auditoría:**  
   - Se generan reportes HTML utilizando **ydata_profiling** para:
     - La base de datos SQLite (archivo `sqlite_audit_report.html`).
     - El archivo Excel (archivo `excel_audit_report.html`).
   - Se elabora un reporte comparativo en formato de texto (`comparative_audit_report.txt`) que detalla la consistencia de los datos entre la API, SQLite y el archivo Excel, e identifica posibles diferencias o inconsistencias en campos clave.

## Resultados

El proceso ETL genera los siguientes artefactos:

- **Tabla en SQLite:**  
  Los datos enriquecidos se almacenan en la tabla `movies` de la base de datos ubicada en `src/static/db/ingestion.db`.

- **Archivo Excel:**  
  Se crea un archivo `tmdb_movies.xlsx` en la carpeta `src/static/xlsx/` que contiene el conjunto de datos enriquecido.

- **Reportes de auditoría:**  
  - Un reporte HTML para la base de datos SQLite: `sqlite_audit_report.html`.
  - Un reporte HTML para el archivo Excel: `excel_audit_report.html`.
  - Un reporte comparativo en formato de texto: `comparative_audit_report.txt`.