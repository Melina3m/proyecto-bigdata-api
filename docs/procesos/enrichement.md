# Proceso de enriquecimiento de datos

Este documento detalla el proceso de enriquecimiento aplicado a los datos de películas extraídos de TMDB, integrando información adicional proveniente de tres fuentes:

1. **Detalles adicionales de TMDB:** Se consulta el endpoint de detalles de TMDB para incorporar información extra (como status, belongs_to_collection e imdb_id) a cada registro.
2. **Watch Providers para Colombia:** Se consulta el endpoint de Watch Providers para obtener, para cada película, el enlace de visualización y los tipos de servicios disponibles (flatrate, buy y rent) para el país Colombia, filtrando detalles específicos de cada proveedor.
3. **Enriquecimiento con OMDb:** Para aquellas películas que cuentan con un imdb_id válido, se consulta la API de OMDb para obtener información complementaria como imdbVotes, imdbRating, Director y Awards.

## Operaciones de enriquecimiento

El pipeline de enriquecimiento realiza las siguientes operaciones:

- **TMDB Details Enrichment:**  
  Se obtienen detalles adicionales para cada película consultando el endpoint de TMDB. Se agregan a cada registro campos como `status`, `belongs_to_collection` e `imdb_id`.

- **Watch Providers Enrichment (Colombia):**  
  Se consulta el endpoint de Watch Providers de TMDB para cada película y se extrae la información correspondiente al país Colombia (código "CO"). De esta fuente se agregan:
  - `watch_link_co`: Enlace general para visualizar la película en Colombia.
  - `provider_type_co`: Tipos de servicios disponibles (se combinan los valores de `flatrate`, `buy` y `rent` separados por comas).
  - `providers_co`: Detalles de los proveedores en formato JSON, excluyendo las claves `logo_path`, `provider_id` y `display_priority`.

- **OMDb Enrichment:**  
  Para cada película que cuente con un `imdb_id` válido, se consulta la API de OMDb. Se incorporan campos adicionales como `imdbVotes`, `imdbRating`, `Director_omdb` y `Awards_omdb`.

## Flujo del proceso

1. **Carga de datos:**  
   Se leen los registros desde la tabla `movies_cleaned` de la base de datos SQLite.

2. **Enriquecimiento con TMDB:**  
   Se iteran los registros y se consultan los detalles adicionales para cada película. Los datos se guardan en la tabla `movies_enriched`.

3. **Enriquecimiento con Watch Providers:**  
   Se actualiza la tabla `movies_enriched` añadiendo la información de Watch Providers para Colombia.

4. **Enriquecimiento con OMDb:**  
   Se consulta la API de OMDb para aquellos registros con un `imdb_id` válido y se agregan los campos adicionales.

5. **Exportación y generación de reporte de auditoría:**  
   Se exporta el dataset final enriquecido a un archivo Excel y se genera un reporte de auditoría comparativo entre el dataset base y el enriquecido.

## Resultados

El proceso de enriquecimiento genera:
- Una tabla `movies_enriched` en la base de datos SQLite que consolida la información enriquecida de TMDB, Watch Providers y OMDb.
- Un archivo Excel (`enriched_data.xlsx`) con el dataset final enriquecido.
- Un reporte de auditoría (`enrichment_report.txt`) que documenta:
  - El número de registros en el dataset base y el enriquecido.
  - Las diferencias en columnas y la integridad de campos clave (por ejemplo, `id` y `original_title`).
  - Observaciones sobre las integraciones realizadas de cada fuente.