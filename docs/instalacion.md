# Guía de instalación y ejecución

## Requisitos

- Python 3.11 o versión compatible.
- Git.
- JupyterLab o Jupyter Notebook.
- Conexión a internet para la descarga inicial de dependencias, la obtención de la red de OpenStreetMap y la geocodificación de direcciones.
- Espacio suficiente para los CSV históricos y los artefactos geoespaciales.

## Preparación del entorno

Desde la raíz del repositorio:

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Linux o macOS:

```bash
source .venv/bin/activate
```

Instalar las dependencias:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Preparación de los datos

Ubicar los archivos CSV correspondientes al período 2016–2025 en:

```text
data/raw/
```

El notebook detecta automáticamente los archivos `.csv`, identifica el año desde el nombre y genera un inventario de estructura y calidad.

## Ejecución del notebook

```bash
jupyter lab
```

Abrir:

```text
notebooks/01_pipeline_analitico.ipynb
```

Reiniciar el kernel y ejecutar todas las celdas en orden. El flujo genera:

- datasets consolidados en `data/processed/`;
- tablas en `outputs/tables/`;
- figuras en `outputs/figures/`;
- superficies y grafos en `outputs/models/`;
- copias de los artefactos requeridos por Streamlit dentro de `app/`.

## Ejecución de Streamlit

Verificar la existencia de:

```text
app/grafo_peatonal_con_ier.pkl
app/segmentos_ier_wgs84.pkl
```

Luego ejecutar:

```bash
streamlit run app/app.py
```

La aplicación estará disponible normalmente en:

```text
http://localhost:8501
```

## Problemas frecuentes

### No se detectan CSV

Confirmar que los archivos se encuentren directamente dentro de `data/raw/` y posean extensión `.csv`.

### Error al cargar los archivos `.pkl`

Ejecutar nuevamente la sección de exportación del notebook usando el mismo entorno de Python con el que se iniciará Streamlit.

### Error de geocodificación

Verificar la conexión a internet o ingresar las ubicaciones directamente como coordenadas `latitud, longitud`.

### El grafo no existe

La primera ejecución descarga la red peatonal desde OpenStreetMap y la guarda localmente. Esta operación requiere conexión a internet y puede demorar.
