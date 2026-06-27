# Generación de rutas peatonales con un Índice de Exposición al Riesgo

Prototipo desarrollado como Trabajo Final de Grado para comparar una ruta peatonal base, optimizada por distancia, con una ruta alternativa que incorpora un **Índice de Exposición al Riesgo (IER)** calculado a partir de registros delictivos históricos de la Ciudad Autónoma de Buenos Aires.

> **Importante:** el IER es una medida relativa basada en registros históricos oficiales. No representa una probabilidad individual de victimización ni garantiza la seguridad de un recorrido.

---

## Probar la aplicación en línea

La forma más sencilla de utilizar el prototipo es mediante la aplicación publicada en Streamlit Community Cloud. No requiere instalar Python ni descargar archivos.

### [Abrir el prototipo web](https://tfg-agustin-vidaurreta-rutas-peatonales.streamlit.app/)

La interfaz permite:

- ingresar un origen y un destino;
- seleccionar una franja horaria;
- calcular la ruta de menor distancia;
- calcular una ruta alternativa ponderada por el IER;
- visualizar ambas rutas sobre un mapa;
- comparar distancia, IER y variaciones porcentuales.

---

## Ejecución local en Windows mediante CMD

### Requisitos

- Windows 10 u 11;
- Python 3.11;
- Git;
- conexión a internet para instalar dependencias y geocodificar direcciones.

Abrir **Símbolo del sistema de Windows (CMD)** y copiar el siguiente bloque completo:

```bat
git clone <INCORPORAR_URL_DEL_REPOSITORIO>
cd <INCORPORAR_NOMBRE_DEL_REPOSITORIO>
python -m venv .venv
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m streamlit run app\app.py
```

La aplicación se abrirá normalmente en:

```text
http://localhost:8501
```

Para detenerla, volver a la consola y presionar:

```text
Ctrl + C
```

### Ejecuciones posteriores

Después de completar la instalación una vez, abrir CMD dentro de la carpeta del repositorio y ejecutar:

```bat
call .venv\Scripts\activate.bat
python -m streamlit run app\app.py
```

### Descarga como ZIP

También puede ejecutarse sin utilizar Git:

1. En GitHub, seleccionar **Code → Download ZIP**.
2. Descomprimir el archivo.
3. Abrir CMD dentro de la carpeta descomprimida.
4. Copiar y ejecutar:

```bat
python -m venv .venv
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m streamlit run app\app.py
```

Los artefactos procesados necesarios para iniciar la interfaz ya se incluyen dentro de `app\`, por lo que no es necesario ejecutar el notebook para probar la aplicación.

---

## Ejecución automatizada opcional mediante archivo BAT

El repositorio incluye el archivo:

```text
ejecutar_proyecto.bat
```

Este archivo automatiza la creación del entorno virtual, la instalación de dependencias, la ejecución completa del notebook y el inicio de la aplicación Streamlit.

Puede ejecutarse mediante doble clic o desde CMD:

```bat
ejecutar_proyecto.bat
```

### Posible bloqueo de Windows

Windows puede bloquear archivos `.bat` descargados de internet aunque provengan de una fuente confiable.

En ese caso:

1. hacer clic derecho sobre `ejecutar_proyecto.bat`;
2. seleccionar **Propiedades**;
3. en la pestaña **General**, marcar **Desbloquear** o **Unblock**, si la opción está disponible;
4. presionar **Aplicar** y luego **Aceptar**;
5. volver a ejecutar el archivo.

No se recomienda desactivar Smart App Control, Windows Defender ni otras medidas de seguridad del sistema. Si el archivo continúa bloqueado, deben utilizarse los comandos manuales indicados en la sección anterior.

---

## Reproducción completa del flujo analítico

La aplicación puede utilizarse directamente con los artefactos incluidos. Sin embargo, el flujo metodológico completo también puede reproducirse desde los archivos originales.

Desde la raíz del repositorio:

```bat
call .venv\Scripts\activate.bat
jupyter nbconvert --to notebook --execute notebooks\01_pipeline_analitico.ipynb --inplace --ExecutePreprocessor.timeout=-1
```

Este proceso:

1. integra los archivos delictivos ubicados en `data\raw\`;
2. ejecuta los controles de calidad;
3. genera los análisis exploratorios;
4. construye las superficies KDE;
5. calcula el IER por segmento;
6. valida los parámetros seleccionados;
7. exporta las tablas, figuras y artefactos consumidos por la aplicación.

Las salidas se generan en:

```text
data\processed\
outputs\figures\
outputs\tables\
outputs\models\
app\
```

---

## Archivos principales

```text
.
├── README.md
├── requirements.txt
├── ejecutar_proyecto.bat
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
└── outputs/
    ├── figures/
    ├── tables/
    └── models/
```

---

## Metodología

El flujo analítico incluyó:

1. integración de los archivos delictivos correspondientes al período 2016–2025;
2. evaluación de calidad y exclusión documentada de registros no utilizables;
3. proyección de coordenadas a un sistema métrico;
4. análisis exploratorio espacial, temporal y categórico;
5. construcción y calibración de superficies KDE;
6. normalización global del IER entre franjas horarias;
7. obtención y validación de la red peatonal;
8. muestreo del IER a lo largo de cada segmento;
9. calibración del peso relativo del riesgo;
10. validación sobre múltiples recorridos.

La documentación ampliada se encuentra en:

```text
docs\metodologia.md
```

---

## Parámetros finales

| Parámetro | Valor |
|---|---:|
| Tamaño de celda | 100 m |
| Bandwidth del KDE | 750 m |
| Margen de la grilla | 3000 m |
| Paso de muestreo por segmento | 25 m |
| Agregación del IER por segmento | Media |
| Alpha de la función de costo | 3 |

La función de costo utilizada para ponderar cada segmento es:

$$
C_e = L_e\left(1 + \alpha \cdot IER_e\right)
$$

donde:

- $C_e$ es el costo ponderado del segmento;
- $L_e$ es su longitud;
- $IER_e$ es su exposición relativa estimada;
- $\alpha$ controla la influencia del IER sobre la ruta.

---

## Resultados principales

- 10 archivos históricos integrados, correspondientes al período 2016–2025.
- 1.387.622 registros originales consolidados.
- 1.353.037 registros utilizables para el análisis espacial general.
- 1.350.831 registros utilizables para el análisis por franjas horarias.
- Reducción media del IER de 10,61 % en la validación general.
- Incremento medio de distancia de 2,48 %.
- Modificación del recorrido en 83,33 % de los casos evaluados.

---

## Problemas frecuentes

### `python` no se reconoce como un comando

Python no está instalado o no fue agregado a `PATH`.

### No se encuentra `requirements.txt`

La consola no está ubicada en la raíz del repositorio.

Ejemplo:

```bat
cd /d "C:\ruta\al\repositorio"
```

### No se encuentra un archivo `.pkl`

Verificar que existan:

```text
app\grafo_peatonal_con_ier.pkl
app\segmentos_ier_wgs84.pkl
```

### La geocodificación no responde

Verificar la conexión a internet. Como alternativa, la interfaz admite coordenadas con el formato:

```text
latitud, longitud
```

### La aplicación no se abre automáticamente

Abrir manualmente:

```text
http://localhost:8501
```

---

## Recursos de la entrega

- **Aplicación web:** [Abrir el prototipo](https://tfg-agustin-vidaurreta-rutas-peatonales.streamlit.app/)
- **Repositorio de GitHub:** [Ver el código](<INCORPORAR_URL_DEL_REPOSITORIO>)
- **Paquete completo y video demostrativo:** [Abrir Google Drive](<INCORPORAR_URL_DE_GOOGLE_DRIVE>)

---

## Autor

**Agustín Vidaurreta**  
Trabajo Final de Grado. 
Prototipado tecnológico.
