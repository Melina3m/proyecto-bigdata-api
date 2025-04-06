# Proyecto Big Data TMDB

Esta documentación detalla el proceso ETL (Extracción, Transformación y Carga) para datos de películas obtenidos de la API de TMDB (The Movie Database).

## Características principales

- **Extracción de datos**: Obtención automatizada de información detallada de películas desde la API de TMDB
- **Limpieza y transformación**: Procesamiento completo para normalizar, traducir y estandarizar los datos
- **Enriquecimiento**: Integración con fuentes adicionales para complementar la información
- **Almacenamiento**: Persistencia en base de datos SQLite y archivos Excel
- **Auditoría**: Generación de reportes detallados del proceso ETL

## Tecnologías utilizadas

- Python 3.12
- SQLite
- Pandas
- GitHub Actions para automatización

## Primeros pasos

Para ejecutar el proyecto:

1. Clona el repositorio
2. Instala las dependencias: `pip install -r requirements.txt`
3. Ejecuta la secuencia de scripts: ingestion → cleaning → enrichment
