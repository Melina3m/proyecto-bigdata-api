# Proceso de limpieza de datos

Este documento detalla el proceso de limpieza aplicado a los datos extraídos de TMDB.

## Operaciones de limpieza

El script `cleaning.py` realiza las siguientes operaciones:

- Eliminación de filas duplicadas
- Conversión de columnas de listas a cadenas de texto
- Eliminación de columnas innecesarias
- Relleno de valores nulos
- Traducción y normalización de datos

## Flujo del proceso

1. Lectura de datos desde la base SQLite
2. Aplicación de transformaciones
3. Validación de resultados
4. Almacenamiento de datos limpios
5. Generación de reportes de auditoría

## Resultados

El proceso genera:
- Una nueva tabla `movies_cleaned` en la base de datos
- Un archivo Excel con los datos limpios
- Un reporte de auditoría detallando las transformaciones realizadas