# Datos originales

Ubicar en esta carpeta los archivos CSV oficiales de delitos correspondientes a los años 2016–2025.

El notebook:

1. detecta todos los archivos `.csv`;
2. infiere el año desde el nombre;
3. identifica encoding y separador;
4. homologa las columnas;
5. conserva el nombre del archivo como variable de trazabilidad.

Los archivos originales no deben sobrescribirse durante el procesamiento. Las versiones consolidadas se generan en `data/processed/`.
