# Generación de rutas peatonales con un Índice de Exposición al Riesgo

Prototipo desarrollado como Trabajo Final de Grado para comparar una ruta peatonal base, optimizada por distancia, con una alternativa que incorpora un **Índice de Exposición al Riesgo (IER)** calculado a partir de registros delictivos históricos de la Ciudad Autónoma de Buenos Aires.

La solución integra datos abiertos de delitos de 2016 a 2025, una red peatonal obtenida mediante OSMnx y OpenStreetMap, superficies de densidad espacial y una interfaz interactiva construida con Streamlit y Folium.

> El IER es una medida relativa basada en registros históricos oficiales. No representa una probabilidad individual de victimización ni garantiza la seguridad de un recorrido.

## Resultados principales

- 10 archivos históricos integrados, correspondientes al período 2016–2025.
- 1.387.622 registros originales consolidados.
- 1.353.037 registros utilizables para el análisis espacial general (97,51 %).
- 1.350.831 registros utilizables para el análisis por franjas horarias (97,35 %).
- Red peatonal de 45.291 nodos y 139.972 segmentos dirigidos.
- Reducción media del IER de 10,61 % con un incremento medio de distancia de 2,48 % en la validación general.
- Modificación del recorrido en 83,33 % de los 30 casos de prueba.

## Parámetros seleccionados

| Parámetro | Valor |
|---|---:|
| Tamaño de celda | 100 m |
| Bandwidth del KDE | 750 m |
| Margen de la grilla | 3000 m |
| Paso de muestreo por segmento | 25 m |
| Agregación del IER por segmento | Media |
| Alpha de la función de costo | 3 |

La función de costo utilizada para la ruta alternativa es:

```text
costo_segmento = longitud × (1 + alpha × IER)
```

## Estructura del repositorio

```text
.
├── app/
│   ├── app.py
│   ├── grafo_peatonal_con_ier.pkl
│   └── segmentos_ier_wgs84.pkl
├── config/
│   └── parametros_finales.json
├── data/
│   ├── raw/
│   └── processed/
├── docs/
│   ├── instalacion.md
│   └── metodologia.md
├── notebooks/
│   └── 01_pipeline_analitico.ipynb
├── outputs/
│   ├── figures/
│   ├── tables/
│   └── models/
├── .gitignore
├── README.md
└── requirements.txt
```

Los archivos binarios de la aplicación se generan al ejecutar el notebook y se copian automáticamente dentro de `app/`.

## Instalación

```bash
git clone <URL_DEL_REPOSITORIO>

python -m venv .venv
```

Activación del entorno en Windows:

```bash
.venv\Scripts\activate
```

Activación en Linux o macOS:

```bash
source .venv/bin/activate
```

Instalación de dependencias:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Ejecución del flujo analítico

1. Colocar los CSV originales en `data/raw/`.
2. Abrir `notebooks/01_pipeline_analitico.ipynb`.
3. Reiniciar el kernel y ejecutar todas las celdas en orden.
4. Verificar la generación de tablas, figuras y artefactos.
5. Confirmar que los archivos `.pkl` hayan sido copiados a `app/`.

```bash
jupyter lab
```

## Ejecución de la aplicación

```bash
streamlit run app/app.py
```

La interfaz permite ingresar un origen y un destino, seleccionar una franja horaria, comparar las rutas y consultar las métricas de distancia e IER.

## Flujo metodológico

1. Inventario y homologación de los archivos históricos.
2. Evaluación de calidad y exclusión documentada de registros no utilizables.
3. Proyección de coordenadas a un sistema métrico.
4. Análisis exploratorio espacial, temporal y categórico.
5. Construcción y calibración de superficies KDE.
6. Normalización global del IER entre franjas horarias.
7. Obtención y validación de la red peatonal.
8. Muestreo del IER a lo largo de cada segmento.
9. Calibración del peso relativo del riesgo.
10. Validación sobre múltiples recorridos y exportación de artefactos.

La metodología completa y sus decisiones se encuentran documentadas en el notebook y en `docs/metodologia.md`.

## Fuentes de datos

- Registros delictivos históricos: portal Buenos Aires Data.
- Red vial y peatonal: OpenStreetMap, consultada mediante OSMnx.

Los CSV originales no se incluyen por defecto en el repositorio. `data/raw/README.md` describe la estructura esperada.

## Limitaciones

- Los registros oficiales pueden presentar subregistro, cambios de clasificación y diferencias entre años.
- Los hechos sin coordenadas válidas no participan del análisis espacial.
- El KDE suaviza la distribución observada y no modela barreras urbanas de manera explícita.
- El modelo base no pondera de forma diferenciada las tipologías delictivas.
- Los datos disponibles se limitan a CABA, por lo que las áreas cercanas a sus límites deben interpretarse con cautela.
- La aplicación es un prototipo académico y no una herramienta de navegación con garantías de seguridad.

## Autor

Agustín Vidaurreta.
Contexto de Trabajo Final de Grado.
