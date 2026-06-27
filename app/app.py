from __future__ import annotations

from pathlib import Path
from textwrap import dedent
from typing import Any, Callable
import pickle
import re

import branca.colormap as bcm
import folium
import geopandas as gpd
import networkx as nx
import numpy as np
import osmnx as ox
import pandas as pd
import streamlit as st
from shapely.geometry import LineString, MultiLineString
from streamlit_folium import st_folium


# ============================================================
# CONFIGURACIÓN GENERAL
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

GRAPH_PATH = BASE_DIR / "grafo_peatonal_con_ier.pkl"
EDGES_PATH = BASE_DIR / "segmentos_ier_wgs84.pkl"

CENTRO_CABA = (-34.6037, -58.3816)

COLOR_RUTA_BASE = "#cc1111"
COLOR_RUTA_IER = "#25e000"

st.set_page_config(
    page_title="Generador de Rutas Peatonales",
    page_icon="🚶",
    layout="wide",
)


# ============================================================
# RENDERIZADO HTML
# ============================================================

def compactar_html(contenido: str) -> str:
    """
    Compacta el HTML para evitar que versiones antiguas de Streamlit
    interpreten accidentalmente líneas indentadas como bloques de código.
    """
    contenido_limpio = dedent(contenido).strip()

    return re.sub(
        r"\s+",
        " ",
        contenido_limpio,
    )


def render_html(contenido: str) -> None:
    """
    Utiliza st.html cuando está disponible.
    Incluye fallback para versiones anteriores de Streamlit.
    """
    contenido_limpio = dedent(contenido).strip()

    if hasattr(st, "html"):
        st.html(
            contenido_limpio
        )

    else:
        st.markdown(
            compactar_html(
                contenido_limpio
            ),
            unsafe_allow_html=True,
        )


# ============================================================
# ESTILOS
# ============================================================

render_html(
    """
    <style>
        [data-testid="stAppViewContainer"] .main .block-container {
            padding-top: 2rem !important;
            padding-bottom: 2rem !important;
            max-width: 1500px;
        }

        h1, h2, h3 {
            color: #1f1f1f;
        }

        .titulo-principal {
            border: 1px solid #d7d7d7;
            border-radius: 8px;
            text-align: center;
            font-size: 1.55rem;
            font-weight: 750;
            padding: 0.75rem 1rem;
            margin-bottom: 1.2rem;
            background: #ffffff;
        }

        .subtitulo-seccion {
            font-size: 1.55rem;
            font-weight: 750;
            margin-bottom: 0.8rem;
        }

        .tarjeta-ruta {
            border: 1px solid #e0e0e0;
            border-radius: 10px;
            padding: 0.72rem 0.9rem;
            background: #ffffff;
            min-height: 112px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
        }

        .tarjeta-base {
            border-top: 5px solid #ef8f8f;
        }

        .tarjeta-ier {
            border-top: 5px solid #9be56f;
        }

        .titulo-tarjeta {
            font-size: 1.08rem;
            font-weight: 750;
            margin-bottom: 0.8rem;
        }

        .fila-metrica {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 1rem;
            padding: 0.45rem 0;
            border-bottom: 1px solid #eeeeee;
            font-size: 0.98rem;
        }

        .fila-metrica:last-child {
            border-bottom: none;
        }

        .nombre-metrica {
            font-weight: 650;
            color: #333333;
        }

        .valor-metrica {
            font-weight: 700;
            color: #222222;
        }

        .valor-positivo {
            color: #178f20;
            font-weight: 750;
        }

        .valor-advertencia {
            color: #a88c00;
            font-weight: 750;
        }

        .caja-info {
            border: 1px solid #cde3fb;
            border-radius: 9px;
            padding: 0.72rem 0.9rem;
            background: #f6fbff;
            font-size: 0.86rem;
            line-height: 1.32;
            min-height: 112px;
        }

        .caja-comparacion {
            border: 1px solid #e0e0e0;
            border-radius: 10px;
            padding: 0.72rem 0.9rem;
            background: #ffffff;
            min-height: 110px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
        }

        .caja-escala {
            border: 1px solid #e0e0e0;
            border-radius: 10px;
            padding: 0.72rem 0.9rem;
            background: #ffffff;
            min-height: 110px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
        }

        .escala-ier {
            width: 100%;
            height: 28px;
            border-radius: 7px;
            border: 1px solid #777777;
            background: linear-gradient(
                90deg,
                #8ff08a 0%,
                #d9d37e 50%,
                #ff6666 100%
            );
            margin-top: 0.65rem;
            margin-bottom: 0.35rem;
        }

        .escala-numeros {
            display: flex;
            justify-content: space-between;
            font-size: 0.82rem;
            font-weight: 700;
            margin-bottom: 0.15rem;
        }

        .escala-extremos {
            display: flex;
            justify-content: space-between;
            gap: 1rem;
            font-size: 0.8rem;
            font-weight: 600;
        }

        .escala-extremos span:last-child {
            text-align: right;
        }

        .aviso-final {
            text-align: center;
            font-size: 0.9rem;
            font-weight: 650;
            padding: 0.72rem;
            border-radius: 8px;
            background: #fff8df;
            border: 1px solid #f2df8d;
            margin-top: 1.1rem;
        }

        div[data-testid="stForm"] {
            border: 1px solid #e3e3e3;
            border-radius: 10px;
            padding: 1rem;
        }
        .pastilla-metrica {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            min-width: 86px;
            padding: 0.35rem 0.55rem;
            border: 1px solid;
            border-radius: 8px;
            font-weight: 750;
            line-height: 1;
        }

        .pastilla-valor {
            font-size: 1rem;
        }

        .detalle-equilibrio {
            padding-top: 0.38rem;
            margin-top: 0.35rem;
            border-top: 1px solid #eeeeee;
            color: #666666;
            font-size: 0.76rem;
            line-height: 1.25;
        }
        /* ==========================================================
           AJUSTES DE DISEÑO COMPACTO
           ========================================================== */

        /* Menos espacio vacío antes del título */
        [data-testid="stAppViewContainer"] .main .block-container {
            padding-top: 3.15rem !important;
            padding-bottom: 0.65rem !important;
        }

        /* Título más compacto */
        .titulo-principal {
            padding: 0.48rem 0.75rem !important;
            margin-top: 0 !important;
            margin-bottom: 0.55rem !important;
            font-size: 1.28rem !important;
        }

        /* Menor separación vertical general entre componentes */
        [data-testid="stVerticalBlock"] {
            gap: 0.48rem !important;
        }

        /* Menor separación horizontal entre columnas */
        [data-testid="stHorizontalBlock"] {
            gap: 0.8rem !important;
        }

        /* Formulario más compacto */
        div[data-testid="stForm"] {
            padding: 0.68rem !important;
        }

        div[data-testid="stForm"] [data-testid="stVerticalBlock"] {
            gap: 0.42rem !important;
        }

        /* Menor espacio en el título de resultados */
        .subtitulo-seccion {
            margin-top: 0 !important;
            margin-bottom: 0.35rem !important;
            font-size: 1.32rem !important;
        }

        /* Tarjetas más bajas */
        .tarjeta-ruta,
        .caja-info,
        .caja-comparacion,
        .caja-escala {
            min-height: 0 !important;
            padding: 0.58rem 0.72rem !important;
        }

        /* Menos altura interna entre métricas */
        .fila-metrica {
            padding: 0.27rem 0 !important;
        }

        /* Gradiente un poco más compacto */
        .escala-ier {
            height: 20px !important;
            margin-top: 0.42rem !important;
            margin-bottom: 0.18rem !important;
        }

        /* Aviso final más discreto */
        .aviso-final {
            margin-top: 0.42rem !important;
            padding: 0.46rem !important;
            font-size: 0.82rem !important;
        }

        /* Separador personalizado compacto */
        .separador-compacto {
            border: none;
            border-top: 1px solid #dddddd;
            margin: 0.45rem 0 0.5rem 0;
        }
    </style>
    """
)


# ============================================================
# CARGA DE DATOS
# ============================================================

@st.cache_resource
def cargar_datos() -> tuple[Any, gpd.GeoDataFrame]:
    if not GRAPH_PATH.exists():
        raise FileNotFoundError(
            f"No se encontró el grafo exportado: {GRAPH_PATH}"
        )

    if not EDGES_PATH.exists():
        raise FileNotFoundError(
            f"No se encontraron los segmentos exportados: {EDGES_PATH}"
        )

    with GRAPH_PATH.open("rb") as archivo:
        grafo = pickle.load(
            archivo
        )

    segmentos = pd.read_pickle(
        EDGES_PATH
    )

    return grafo, segmentos


try:
    G, segmentos_ier_gdf = cargar_datos()

    FRANJAS_DISPONIBLES = [
        "General",
        "Madrugada",
        "Mañana",
        "Tarde",
        "Noche",
    ]


    def construir_mapas_ier_por_franja(
        segmentos: gpd.GeoDataFrame,
    ) -> dict[
        str,
        dict[
            tuple[int, int, int],
            float,
        ],
    ]:
        mapas = {}

        for franja in FRANJAS_DISPONIBLES:
            subconjunto = segmentos[
                segmentos["franja_agregada"] == franja
            ]

            mapas[franja] = {
                (
                    fila.u,
                    fila.v,
                    fila.key,
                ): float(
                    np.nan_to_num(
                        fila.valor_ier,
                        nan=0.0,
                    )
                )
                for fila in subconjunto[
                    [
                        "u",
                        "v",
                        "key",
                        "valor_ier",
                    ]
                ].itertuples(
                    index=False
                )
            }

        return mapas


    MAPAS_IER_POR_FRANJA = (
        construir_mapas_ier_por_franja(
            segmentos_ier_gdf
        )
    )

except Exception as error:
    st.error(
        "No fue posible cargar los datos del prototipo. "
        "Ejecutá nuevamente la celda de exportación desde el notebook."
    )

    st.exception(
        error
    )

    st.stop()


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def formato_decimal(
    valor: float,
    decimales: int = 2,
) -> str:
    return f"{valor:.{decimales}f}".replace(
        ".",
        ",",
    )

def rgb_a_hex(
    rgb: tuple[int, int, int],
) -> str:
    return "#{:02x}{:02x}{:02x}".format(
        *rgb
    )


def rgb_a_rgba(
    rgb: tuple[int, int, int],
    alpha: float,
) -> str:
    return (
        f"rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, {alpha})"
    )


def interpolar_rgb(
    valor: float,
    puntos: list[
        tuple[
            float,
            tuple[int, int, int],
        ]
    ],
) -> tuple[int, int, int]:
    """
    Devuelve un color interpolado entre distintos puntos
    de referencia definidos por valor y RGB.
    """
    puntos_ordenados = sorted(
        puntos,
        key=lambda elemento: elemento[0],
    )

    if valor <= puntos_ordenados[0][0]:
        return puntos_ordenados[0][1]

    if valor >= puntos_ordenados[-1][0]:
        return puntos_ordenados[-1][1]

    for (
        valor_inferior,
        color_inferior,
    ), (
        valor_superior,
        color_superior,
    ) in zip(
        puntos_ordenados[:-1],
        puntos_ordenados[1:],
    ):
        if valor_inferior <= valor <= valor_superior:
            proporcion = (
                (
                    valor
                    - valor_inferior
                )
                / (
                    valor_superior
                    - valor_inferior
                )
            )

            return tuple(
                round(
                    componente_inferior
                    + proporcion
                    * (
                        componente_superior
                        - componente_inferior
                    )
                )
                for componente_inferior, componente_superior
                in zip(
                    color_inferior,
                    color_superior,
                )
            )

    return puntos_ordenados[-1][1]


def metadata_incremento_distancia(
    incremento: float,
) -> dict[str, Any]:
    """
    Evalúa el desvío adicional generado por la ruta ponderada.

    Escala orientativa:
    - 0 a 5 %: desvío mínimo
    - 5 a 15 %: desvío moderado
    - 15 a 30 %: desvío elevado
    - más de 30 %: desvío alto
    """
    color = interpolar_rgb(
        valor=max(
            incremento,
            0.0,
        ),
        puntos=[
            (
                0.0,
                (
                    30,
                    145,
                    65,
                ),
            ),
            (
                5.0,
                (
                    115,
                    180,
                    70,
                ),
            ),
            (
                15.0,
                (
                    220,
                    185,
                    65,
                ),
            ),
            (
                30.0,
                (
                    232,
                    125,
                    55,
                ),
            ),
            (
                50.0,
                (
                    190,
                    35,
                    35,
                ),
            ),
        ],
    )

    if incremento <= 5:
        etiqueta = "Desvío mínimo"

    elif incremento <= 15:
        etiqueta = "Desvío moderado"

    elif incremento <= 30:
        etiqueta = "Desvío elevado"

    else:
        etiqueta = "Desvío alto"

    return {
        "color": color,
        "etiqueta": etiqueta,
    }


def metadata_reduccion_ier(
    reduccion: float,
) -> dict[str, Any]:
    """
    Evalúa la mejora relativa del IER.

    Escala orientativa:
    - menor que 0 %: empeora el IER
    - 0 a 10 %: reducción leve
    - 10 a 25 %: reducción moderada
    - más de 25 %: reducción alta
    """
    color = interpolar_rgb(
        valor=reduccion,
        puntos=[
            (
                -20.0,
                (
                    175,
                    25,
                    25,
                ),
            ),
            (
                0.0,
                (
                    225,
                    80,
                    55,
                ),
            ),
            (
                10.0,
                (
                    220,
                    185,
                    65,
                ),
            ),
            (
                25.0,
                (
                    115,
                    180,
                    70,
                ),
            ),
            (
                50.0,
                (
                    30,
                    145,
                    65,
                ),
            ),
        ],
    )

    if reduccion < 0:
        etiqueta = "El IER aumenta"

    elif reduccion < 10:
        etiqueta = "Reducción leve"

    elif reduccion < 25:
        etiqueta = "Reducción moderada"

    else:
        etiqueta = "Reducción alta"

    return {
        "color": color,
        "etiqueta": etiqueta,
    }


def metadata_equilibrio(
    incremento: float,
    reduccion: float,
) -> dict[str, Any]:
    """
    Calcula cuántos puntos porcentuales de reducción relativa
    del IER se obtienen por cada punto porcentual adicional
    de distancia.

    La métrica es descriptiva y comparativa:
    no representa una clasificación absoluta de calidad.
    """
    if reduccion < 0:
        return {
            "texto_valor": "IER aumenta",
            "detalle": (
                "La ruta ponderada presenta un IER superior "
                "al de la ruta base."
            ),
            "color": (
                175,
                25,
                25,
            ),
        }

    if incremento <= 0.1:
        if reduccion > 0:
            return {
                "texto_valor": "Sin desvío medible",
                "detalle": (
                    "La alternativa reduce el IER sin aumentar "
                    "de manera apreciable la distancia."
                ),
                "color": (
                    30,
                    145,
                    65,
                ),
            }

        return {
            "texto_valor": "Sin cambios",
            "detalle": (
                "La ruta alternativa no modifica de manera "
                "relevante la distancia ni el IER."
            ),
            "color": (
                120,
                120,
                120,
            ),
        }

    eficiencia = (
        reduccion
        / incremento
    )

    color = interpolar_rgb(
        valor=eficiencia,
        puntos=[
            (
                0.0,
                (
                    210,
                    75,
                    45,
                ),
            ),
            (
                0.5,
                (
                    220,
                    170,
                    60,
                ),
            ),
            (
                1.0,
                (
                    175,
                    185,
                    65,
                ),
            ),
            (
                2.0,
                (
                    80,
                    165,
                    70,
                ),
            ),
            (
                4.0,
                (
                    30,
                    145,
                    65,
                ),
            ),
        ],
    )

    return {
        "texto_valor": (
            f"{formato_decimal(eficiencia, 2)} a 1"
        ),
        "detalle": (
            f"Por cada 1 % adicional de distancia, "
            f"la ruta alternativa obtiene aproximadamente "
            f"{formato_decimal(eficiencia, 2)} puntos porcentuales "
            f"de reducción relativa del IER."
        ),
        "color": color,
    }


def pastilla_metrica_html(
    valor: str,
    color: tuple[int, int, int],
) -> str:
    """
    Genera una pastilla de formato condicional.
    El color facilita la lectura visual, pero no agrega
    clasificaciones subjetivas al resultado.
    """
    color_hex = rgb_a_hex(
        color
    )

    fondo = rgb_a_rgba(
        color,
        0.13,
    )

    borde = rgb_a_rgba(
        color,
        0.38,
    )

    return f"""
        <span
            class="pastilla-metrica"
            style="
                color: {color_hex};
                background-color: {fondo};
                border-color: {borde};
            "
        >
            <span class="pastilla-valor">
                {valor}
            </span>
        </span>
    """


def normalizar_texto_ubicacion(
    texto: str,
) -> str:
    texto = texto.strip()

    if not texto:
        raise ValueError(
            "Ingresá una ubicación."
        )

    return texto


def interpretar_coordenadas(
    texto: str,
) -> tuple[float, float] | None:
    """
    Admite coordenadas en formato:
        -34.6037, -58.3816

    Devuelve:
        (latitud, longitud)
    """
    patron = (
        r"^\s*(-?\d+(?:[.,]\d+)?)"
        r"\s*[,;]\s*"
        r"(-?\d+(?:[.,]\d+)?)\s*$"
    )

    coincidencia = re.match(
        patron,
        texto,
    )

    if not coincidencia:
        return None

    latitud = float(
        coincidencia.group(1).replace(
            ",",
            ".",
        )
    )

    longitud = float(
        coincidencia.group(2).replace(
            ",",
            ".",
        )
    )

    if not (-90 <= latitud <= 90):
        return None

    if not (-180 <= longitud <= 180):
        return None

    return latitud, longitud


@st.cache_data(
    show_spinner=False,
)
def geocodificar(
    texto: str,
) -> tuple[float, float]:
    """
    Acepta una dirección o coordenadas.
    Para direcciones utiliza el geocodificador de OSMnx.
    """
    texto = normalizar_texto_ubicacion(
        texto
    )

    coordenadas = interpretar_coordenadas(
        texto
    )

    if coordenadas is not None:
        return coordenadas

    consulta = (
        f"{texto}, Ciudad Autónoma de Buenos Aires, Argentina"
    )

    latitud, longitud = ox.geocode(
        consulta
    )

    return float(latitud), float(longitud)


def actualizar_costos(
    grafo: Any,
    alpha: float,
    franja_seleccionada: str,
) -> None:
    mapa_ier = MAPAS_IER_POR_FRANJA[
        franja_seleccionada
    ]

    for u, v, key, datos in grafo.edges(
        keys=True,
        data=True,
    ):
        longitud = float(
            datos.get(
                "length",
                0.0,
            )
        )

        valor_ier = float(
            mapa_ier.get(
                (
                    u,
                    v,
                    key,
                ),
                0.0,
            )
        )

        datos["valor_ier"] = valor_ier

        datos["costo_seguridad"] = (
            longitud
            * (
                1
                + alpha
                * valor_ier
            )
        )


def seleccionar_arista(
    grafo: Any,
    origen: int,
    destino: int,
    atributo_peso: str,
) -> tuple[int, dict[str, Any]]:
    """
    Selecciona la arista paralela con menor costo.
    """
    alternativas = grafo.get_edge_data(
        origen,
        destino,
    )

    if not alternativas:
        raise nx.NetworkXNoPath(
            f"No existe una arista entre {origen} y {destino}."
        )

    key, datos = min(
        alternativas.items(),
        key=lambda item: float(
            item[1].get(
                atributo_peso,
                np.inf,
            )
        ),
    )

    return key, datos


def obtener_aristas_ruta(
    grafo: Any,
    nodos_ruta: list[int],
    atributo_peso: str,
) -> list[tuple[int, int, int, dict[str, Any]]]:
    aristas = []

    for origen, destino in zip(
        nodos_ruta[:-1],
        nodos_ruta[1:],
    ):
        key, datos = seleccionar_arista(
            grafo=grafo,
            origen=origen,
            destino=destino,
            atributo_peso=atributo_peso,
        )

        aristas.append(
            (
                origen,
                destino,
                key,
                datos,
            )
        )

    return aristas


def calcular_metricas_ruta(
    aristas: list[
        tuple[int, int, int, dict[str, Any]]
    ],
) -> dict[str, float]:
    distancia_total = 0.0
    riesgo_ponderado = 0.0

    for _, _, _, datos in aristas:
        longitud = float(
            datos.get(
                "length",
                0.0,
            )
        )

        valor_ier = float(
            np.nan_to_num(
                datos.get(
                    "valor_ier",
                    0.0,
                ),
                nan=0.0,
            )
        )

        distancia_total += longitud

        riesgo_ponderado += (
            longitud
            * valor_ier
        )

    ier_promedio = (
        riesgo_ponderado / distancia_total
        if distancia_total > 0
        else 0.0
    )

    return {
        "distancia_metros": distancia_total,
        "ier_promedio": ier_promedio,
    }


def coordenadas_geometria(
    geometria: Any,
) -> list[list[tuple[float, float]]]:
    """
    Convierte LineString o MultiLineString
    al formato esperado por Folium:
        [(latitud, longitud), ...]
    """
    if geometria is None:
        return []

    if isinstance(
        geometria,
        LineString,
    ):
        return [
            [
                (
                    latitud,
                    longitud,
                )
                for longitud, latitud in geometria.coords
            ]
        ]

    if isinstance(
        geometria,
        MultiLineString,
    ):
        return [
            [
                (
                    latitud,
                    longitud,
                )
                for longitud, latitud in linea.coords
            ]
            for linea in geometria.geoms
        ]

    return []


def coordenadas_arista(
    grafo: Any,
    origen: int,
    destino: int,
    datos: dict[str, Any],
) -> list[list[tuple[float, float]]]:
    geometria = datos.get(
        "geometry"
    )

    if geometria is not None:
        return coordenadas_geometria(
            geometria
        )

    return [
        [
            (
                float(
                    grafo.nodes[origen]["y"]
                ),
                float(
                    grafo.nodes[origen]["x"]
                ),
            ),
            (
                float(
                    grafo.nodes[destino]["y"]
                ),
                float(
                    grafo.nodes[destino]["x"]
                ),
            ),
        ]
    ]


def crear_mapa_base(
    centro: tuple[float, float] = CENTRO_CABA,
    zoom: int = 13,
) -> folium.Map:
    return folium.Map(
        location=centro,
        zoom_start=zoom,
        tiles="CartoDB positron",
        control_scale=True,
    )


def agregar_segmentos_ier_cercanos(
    mapa: folium.Map,
    segmentos: gpd.GeoDataFrame,
    coordenadas_rutas: list[tuple[float, float]],
    franja_seleccionada: str,
) -> int:
    """
    Muestra una única capa GeoJson con segmentos cercanos.

    Esto evita agregar miles de PolyLine individuales,
    reduciendo el tiempo de preparación del mapa.
    """
    if not coordenadas_rutas:
        return 0

    latitudes = [
        latitud
        for latitud, _ in coordenadas_rutas
    ]

    longitudes = [
        longitud
        for _, longitud in coordenadas_rutas
    ]

    margen = 0.006

    xmin = min(longitudes) - margen
    xmax = max(longitudes) + margen
    ymin = min(latitudes) - margen
    ymax = max(latitudes) + margen

    segmentos_filtrados = segmentos[
        segmentos[
            "franja_agregada"
        ] == franja_seleccionada
    ]

    subconjunto = segmentos_filtrados.cx[
        xmin:xmax,
        ymin:ymax,
    ].copy()

    if subconjunto.empty:
        return 0

    subconjunto["valor_ier"] = (
        pd.to_numeric(
            subconjunto["valor_ier"],
            errors="coerce",
        )
        .fillna(0.0)
        .clip(0.0, 1.0)
        .astype(float)
    )

    subconjunto["ier_tooltip"] = (
        subconjunto["valor_ier"]
        .map(
            lambda valor: formato_decimal(
                valor,
                3,
            )
        )
    )

    subconjunto = subconjunto[
        [
            "valor_ier",
            "ier_tooltip",
            "geometry",
        ]
    ]

    escala = bcm.LinearColormap(
        colors=[
            "#83ea7a",
            "#e3c583",
            "#f26060",
        ],
        vmin=0.0,
        vmax=1.0,
    )

    capa = folium.GeoJson(
        data=subconjunto.__geo_interface__,
        name="IER por segmento",
        style_function=lambda feature: {
            "color": escala(
                feature[
                    "properties"
                ][
                    "valor_ier"
                ]
            ),
            "weight": 3,
            "opacity": 0.34,
        },
        tooltip=folium.GeoJsonTooltip(
            fields=[
                "ier_tooltip",
            ],
            aliases=[
                "IER del segmento:",
            ],
            sticky=False,
        ),
    )

    capa.add_to(
        mapa
    )

    return len(
        subconjunto
    )


def agregar_ruta(
    mapa: folium.Map,
    grafo: Any,
    aristas: list[
        tuple[int, int, int, dict[str, Any]]
    ],
    color: str,
    etiqueta: str,
    grosor: int,
) -> list[tuple[float, float]]:
    coordenadas_completas = []

    for origen, destino, _, datos in aristas:
        grupos_coordenadas = coordenadas_arista(
            grafo=grafo,
            origen=origen,
            destino=destino,
            datos=datos,
        )

        for coordenadas in grupos_coordenadas:
            folium.PolyLine(
                locations=coordenadas,
                color=color,
                weight=grosor,
                opacity=0.94,
                tooltip=etiqueta,
            ).add_to(
                mapa
            )

            coordenadas_completas.extend(
                coordenadas
            )

    return coordenadas_completas


def construir_mapa_resultado(
    grafo: Any,
    segmentos: gpd.GeoDataFrame,
    franja_seleccionada: str,
    ruta_base_aristas: list[
        tuple[int, int, int, dict[str, Any]]
    ],
    ruta_ier_aristas: list[
        tuple[int, int, int, dict[str, Any]]
    ],
    coordenadas_origen: tuple[float, float],
    coordenadas_destino: tuple[float, float],
    mostrar_red_ier: bool,
) -> tuple[folium.Map, int]:
    mapa = crear_mapa_base(
        centro=coordenadas_origen,
        zoom=14,
    )

    coordenadas_base = []

    for origen, destino, _, datos in ruta_base_aristas:
        for grupo in coordenadas_arista(
            grafo,
            origen,
            destino,
            datos,
        ):
            coordenadas_base.extend(
                grupo
            )

    coordenadas_ier = []

    for origen, destino, _, datos in ruta_ier_aristas:
        for grupo in coordenadas_arista(
            grafo,
            origen,
            destino,
            datos,
        ):
            coordenadas_ier.extend(
                grupo
            )

    cantidad_segmentos_ier = 0

    if mostrar_red_ier:
        cantidad_segmentos_ier = agregar_segmentos_ier_cercanos(
            mapa=mapa,
            franja_seleccionada=franja_seleccionada,
            segmentos=segmentos,
            coordenadas_rutas=(
                coordenadas_base
                + coordenadas_ier
            ),
        )

    agregar_ruta(
        mapa=mapa,
        grafo=grafo,
        aristas=ruta_base_aristas,
        color=COLOR_RUTA_BASE,
        etiqueta="Ruta base por distancia",
        grosor=6,
    )

    agregar_ruta(
        mapa=mapa,
        grafo=grafo,
        aristas=ruta_ier_aristas,
        color=COLOR_RUTA_IER,
        etiqueta="Ruta ponderada por IER",
        grosor=7,
    )

    folium.Marker(
        location=coordenadas_origen,
        tooltip="Origen",
        popup="Origen",
        icon=folium.Icon(
            color="green",
            icon="play",
        ),
    ).add_to(
        mapa
    )

    folium.Marker(
        location=coordenadas_destino,
        tooltip="Destino",
        popup="Destino",
        icon=folium.Icon(
            color="red",
            icon="stop",
        ),
    ).add_to(
        mapa
    )

    todas_las_coordenadas = (
        coordenadas_base
        + coordenadas_ier
        + [
            coordenadas_origen,
            coordenadas_destino,
        ]
    )

    if todas_las_coordenadas:
        mapa.fit_bounds(
            todas_las_coordenadas
        )

    folium.LayerControl(
        collapsed=False
    ).add_to(
        mapa
    )

    return mapa, cantidad_segmentos_ier


def calcular_resultado(
    origen_texto: str,
    destino_texto: str,
    alpha: float,
    franja_seleccionada: str,
    progreso: Callable[[int, str], None] | None = None,
) -> dict[str, Any]:
    def informar(
        porcentaje: int,
        mensaje: str,
    ) -> None:
        if progreso is not None:
            progreso(
                porcentaje,
                mensaje,
            )

    informar(
        10,
        "1 de 6 · Geocodificando origen y destino...",
    )

    coordenadas_origen = geocodificar(
        origen_texto
    )

    coordenadas_destino = geocodificar(
        destino_texto
    )

    informar(
        25,
        "2 de 6 · Asociando ubicaciones con la red peatonal...",
    )

    nodo_origen = ox.distance.nearest_nodes(
        G,
        X=coordenadas_origen[1],
        Y=coordenadas_origen[0],
    )

    nodo_destino = ox.distance.nearest_nodes(
        G,
        X=coordenadas_destino[1],
        Y=coordenadas_destino[0],
    )

    informar(
        40,
        "3 de 6 · Calculando costos relativos por segmento...",
    )

    actualizar_costos(
        grafo=G,
        alpha=alpha,
        franja_seleccionada=franja_seleccionada,
    )

    informar(
        55,
        "4 de 6 · Generando ruta base y alternativa ponderada...",
    )

    ruta_base_nodos = nx.shortest_path(
        G,
        source=nodo_origen,
        target=nodo_destino,
        weight="length",
    )

    ruta_ier_nodos = nx.shortest_path(
        G,
        source=nodo_origen,
        target=nodo_destino,
        weight="costo_seguridad",
    )

    ruta_base_aristas = obtener_aristas_ruta(
        grafo=G,
        nodos_ruta=ruta_base_nodos,
        atributo_peso="length",
    )

    ruta_ier_aristas = obtener_aristas_ruta(
        grafo=G,
        nodos_ruta=ruta_ier_nodos,
        atributo_peso="costo_seguridad",
    )

    informar(
        70,
        "5 de 6 · Calculando métricas comparativas...",
    )

    metricas_base = calcular_metricas_ruta(
        ruta_base_aristas
    )

    metricas_ier = calcular_metricas_ruta(
        ruta_ier_aristas
    )

    distancia_base = metricas_base[
        "distancia_metros"
    ]

    distancia_ier = metricas_ier[
        "distancia_metros"
    ]

    ier_base = metricas_base[
        "ier_promedio"
    ]

    ier_alternativa = metricas_ier[
        "ier_promedio"
    ]

    incremento_distancia = (
        (
            distancia_ier
            - distancia_base
        )
        / distancia_base
        * 100
        if distancia_base > 0
        else 0.0
    )

    reduccion_ier = (
        (
            ier_base
            - ier_alternativa
        )
        / ier_base
        * 100
        if ier_base > 0
        else 0.0
    )

    return {
        "coordenadas_origen": coordenadas_origen,
        "coordenadas_destino": coordenadas_destino,
        "nodo_origen": nodo_origen,
        "nodo_destino": nodo_destino,
        "ruta_base_aristas": ruta_base_aristas,
        "ruta_ier_aristas": ruta_ier_aristas,
        "metricas_base": metricas_base,
        "metricas_ier": metricas_ier,
        "incremento_distancia": incremento_distancia,
        "reduccion_ier": reduccion_ier,
        "franja_seleccionada": franja_seleccionada,
        "alpha": alpha,
    }


def tarjeta_ruta(
    titulo: str,
    distancia_metros: float,
    ier: float,
    clase: str,
) -> str:
    return f"""
        <div class="tarjeta-ruta {clase}">
            <div class="titulo-tarjeta">
                {titulo}
            </div>

            <div class="fila-metrica">
                <span class="nombre-metrica">
                    Distancia
                </span>

                <span class="valor-metrica">
                    {formato_decimal(distancia_metros / 1000, 2)} km
                </span>
            </div>

            <div class="fila-metrica">
                <span class="nombre-metrica">
                    IER
                </span>

                <span class="valor-metrica">
                    {formato_decimal(ier, 3)}
                </span>
            </div>
        </div>
    """


# ============================================================
# ENCABEZADO
# ============================================================

render_html(
    """
    <div class="titulo-principal">
        Generador de Rutas Peatonales · CABA ·
        Criterios de Seguridad Basados en Datos Delictivos Históricos
    </div>
    """
)


# ============================================================
# FORMULARIO
# ============================================================

estado_carga = None
barra_carga = None

col_controles, col_mapa = st.columns(
    [
        0.95,
        2.1,
    ],
    gap="small",
)

with col_controles:
    with st.form(
        "formulario_rutas"
    ):
        st.markdown(
            "#### Consulta de recorrido"
        )

        origen = st.text_input(
            "🟢 Origen",
            placeholder=(
                "Ej.: Plaza Italia "
                "o -34.5812, -58.4208"
            ),
        )

        destino = st.text_input(
            "🔴 Destino",
            placeholder=(
                "Ej.: Obelisco "
                "o -34.6037, -58.3816"
            ),
        )

        franja_seleccionada = st.selectbox(
            "Franja horaria",
            options=FRANJAS_DISPONIBLES,
            index=0,
        )

        mostrar_red_ier = st.checkbox(
            "Mostrar IER sobre segmentos cercanos",
            value=True,
        )

        with st.expander(
            "Configuración experimental"
        ):
            alpha = st.slider(
                "Peso relativo del IER",
                min_value=0.0,
                max_value=10.0,
                value=3.0,
                step=0.5,
                help=(
                    "Valores más altos priorizan una "
                    "mayor reducción del IER, aunque pueden "
                    "generar desvíos más largos."
                ),
            )

        procesar = st.form_submit_button(
            "Generar rutas",
            use_container_width=True,
            type="primary",
        )

    if procesar:
        st.session_state.pop(
            "resultado",
            None,
        )

        st.session_state.pop(
            "mapa_resultado",
            None,
        )

        estado_carga = st.status(
            "Procesando consulta...",
            expanded=True,
        )

        barra_carga = estado_carga.progress(
            3,
            text="Iniciando procesamiento...",
        )

        def actualizar_progreso(
            porcentaje: int,
            mensaje: str,
        ) -> None:
            barra_carga.progress(
                porcentaje,
                text=mensaje,
            )

            estado_carga.write(
                mensaje
            )

        try:
            resultado_calculado = calcular_resultado(
                origen_texto=origen,
                destino_texto=destino,
                alpha=alpha,
                franja_seleccionada=franja_seleccionada,
                progreso=actualizar_progreso,
            )

            actualizar_progreso(
                82,
                "6 de 6 · Preparando capas cartográficas...",
            )

            mapa_resultado, cantidad_segmentos_ier = (
                construir_mapa_resultado(
                    grafo=G,
                    franja_seleccionada=resultado_calculado[
                        "franja_seleccionada"
                    ],
                    segmentos=segmentos_ier_gdf,
                    ruta_base_aristas=resultado_calculado[
                        "ruta_base_aristas"
                    ],
                    ruta_ier_aristas=resultado_calculado[
                        "ruta_ier_aristas"
                    ],
                    coordenadas_origen=resultado_calculado[
                        "coordenadas_origen"
                    ],
                    coordenadas_destino=resultado_calculado[
                        "coordenadas_destino"
                    ],
                    mostrar_red_ier=mostrar_red_ier,
                )
            )

            resultado_calculado[
                "segmentos_ier_visualizados"
            ] = cantidad_segmentos_ier

            st.session_state[
                "resultado"
            ] = resultado_calculado

            st.session_state[
                "mapa_resultado"
            ] = mapa_resultado

            st.session_state[
                "mostrar_red_ier"
            ] = mostrar_red_ier

            actualizar_progreso(
                92,
                "Actualizando mapa e interfaz...",
            )

        except nx.NetworkXNoPath:
            estado_carga.update(
                label=(
                    "No fue posible encontrar "
                    "una conexión peatonal válida."
                ),
                state="error",
                expanded=True,
            )

            st.error(
                "No fue posible encontrar una conexión "
                "peatonal válida entre los puntos indicados."
            )

        except Exception as error:
            estado_carga.update(
                label="No fue posible procesar la consulta.",
                state="error",
                expanded=True,
            )

            st.error(
                "No fue posible procesar la consulta. "
                "Revisá las ubicaciones ingresadas."
            )

            with st.expander(
                "Detalle técnico del error"
            ):
                st.exception(
                    error
                )


# ============================================================
# MAPA
# ============================================================

resultado = st.session_state.get(
    "resultado"
)

with col_mapa:
    if resultado:
        mapa = st.session_state.get(
            "mapa_resultado"
        )

        if mapa is None:
            mapa, cantidad_segmentos_ier = (
                construir_mapa_resultado(
                    grafo=G,
                    franja_seleccionada=resultado[
                        "franja_seleccionada"
                    ],
                    segmentos=segmentos_ier_gdf,
                    ruta_base_aristas=resultado[
                        "ruta_base_aristas"
                    ],
                    ruta_ier_aristas=resultado[
                        "ruta_ier_aristas"
                    ],
                    coordenadas_origen=resultado[
                        "coordenadas_origen"
                    ],
                    coordenadas_destino=resultado[
                        "coordenadas_destino"
                    ],
                    mostrar_red_ier=st.session_state.get(
                        "mostrar_red_ier",
                        True,
                    ),
                )
            )

            resultado[
                "segmentos_ier_visualizados"
            ] = cantidad_segmentos_ier

            st.session_state[
                "mapa_resultado"
            ] = mapa

    else:
        mapa = crear_mapa_base()

        folium.Marker(
            location=CENTRO_CABA,
            tooltip=(
                "Ingresá un origen y un destino "
                "para generar recorridos."
            ),
        ).add_to(
            mapa
        )

    st_folium(
        mapa,
        width=None,
        height=520,
        returned_objects=[],
        use_container_width=True,
    )


# ============================================================
# RESULTADOS
# ============================================================

if resultado:
    st.divider()

    render_html(
        """
        <div class="subtitulo-seccion">
            Resultados
        </div>
        """
    )

    metricas_base = resultado[
        "metricas_base"
    ]

    metricas_ier = resultado[
        "metricas_ier"
    ]

    columna_base, columna_ier, columna_info = st.columns(
        [
            1,
            1,
            1.45,
        ],
        gap="small",
    )

    with columna_base:
        render_html(
            tarjeta_ruta(
                titulo="Ruta base por distancia",
                distancia_metros=metricas_base[
                    "distancia_metros"
                ],
                ier=metricas_base[
                    "ier_promedio"
                ],
                clase="tarjeta-base",
            )
        )

    with columna_ier:
        render_html(
            tarjeta_ruta(
                titulo="Ruta ponderada por IER",
                distancia_metros=metricas_ier[
                    "distancia_metros"
                ],
                ier=metricas_ier[
                    "ier_promedio"
                ],
                clase="tarjeta-ier",
            )
        )

    with columna_info:
        render_html(
            """
            <div class="caja-info">
                <strong>ⓘ ¿Qué es el IER?</strong>
                <br><br>

                El Índice de Exposición al Riesgo representa
                el nivel relativo de exposición estimado para
                cada recorrido a partir de la concentración
                histórica de delitos registrados en las zonas
                atravesadas.

                <br><br>

                Un valor menor indica una menor exposición
                relativa. No representa una probabilidad exacta
                ni una garantía de seguridad.
            </div>
            """
        )

    columna_deltas, columna_escala = st.columns(
        [
            1,
            1.6,
        ],
        gap="small",
    )

    with columna_deltas:
        incremento = resultado[
            "incremento_distancia"
        ]

        reduccion = resultado[
            "reduccion_ier"
        ]

        metadata_distancia = (
            metadata_incremento_distancia(
                incremento
            )
        )

        metadata_ier = (
            metadata_reduccion_ier(
                reduccion
            )
        )

        equilibrio = metadata_equilibrio(
            incremento=incremento,
            reduccion=reduccion,
        )

        pastilla_distancia = pastilla_metrica_html(
            valor=(
                f"{formato_decimal(incremento, 1)} %"
            ),
            color=metadata_distancia[
                "color"
            ],
        )

        pastilla_ier = pastilla_metrica_html(
            valor=(
                f"{formato_decimal(reduccion, 1)} %"
            ),
            color=metadata_ier[
                "color"
            ],
        )

        pastilla_equilibrio = pastilla_metrica_html(
            valor=equilibrio[
                "texto_valor"
            ],
            color=equilibrio[
                "color"
            ],
        )

        render_html(
            f"""
            <div class="caja-comparacion">
                <div class="fila-metrica">
                    <span class="nombre-metrica">
                        Incremento de distancia
                    </span>

                    {pastilla_distancia}
                </div>

                <div class="fila-metrica">
                    <span class="nombre-metrica">
                        Reducción relativa del IER
                    </span>

                    {pastilla_ier}
                </div>

                <div class="fila-metrica">
                    <span class="nombre-metrica">
                        Eficiencia del desvío
                    </span>

                    {pastilla_equilibrio}
                </div>

                <div class="detalle-equilibrio">
                    {equilibrio["detalle"]}
                </div>
            </div>
            """
        )

    with columna_escala:
        render_html(
            """
            <div class="caja-escala">
                <strong>Escala interpretativa del IER</strong>

                <div class="escala-ier"></div>

                <div class="escala-numeros">
                    <span>0</span>
                    <span>1</span>
                </div>

                <div class="escala-extremos">
                    <span>Menor exposición relativa</span>
                    <span>Mayor exposición relativa</span>
                </div>
            </div>
            """
        )

    render_html(
        """
        <div class="aviso-final">
            Los resultados se basan en datos históricos
            y no garantizan la seguridad efectiva del trayecto.
            La elección final del recorrido permanece bajo
            responsabilidad del usuario.
        </div>
        """
    )

    with st.expander(
        "Información técnica de la consulta"
    ):
        st.write(
            {
                "Nodo de origen": resultado[
                    "nodo_origen"
                ],
                "Nodo de destino": resultado[
                    "nodo_destino"
                ],
                "Franja horaria seleccionada": resultado[
                    "franja_seleccionada"
                ],
                "Peso relativo del IER": resultado[
                    "alpha"
                ],
                "Cantidad de tramos de la ruta base": len(
                    resultado[
                        "ruta_base_aristas"
                    ]
                ),
                "Cantidad de tramos de la ruta ponderada": len(
                    resultado[
                        "ruta_ier_aristas"
                    ]
                ),
                "Segmentos IER visualizados": resultado.get(
                    "segmentos_ier_visualizados",
                    0,
                ),
            }
        )

    if estado_carga is not None:
        barra_carga.progress(
            100,
            text="Mapa y resultados actualizados.",
        )

        estado_carga.update(
            label="Consulta procesada correctamente.",
            state="complete",
            expanded=False,
        )

        st.success(
            "Rutas generadas correctamente."
        )

else:
    st.info(
        "Ingresá un punto de origen y un destino "
        "para generar y comparar recorridos."
    )
