# Síntesis metodológica

## Datos

Se integraron diez archivos de delitos correspondientes al período 2016–2025. El proceso conservó la fuente y el año de origen de cada registro, homologó los nombres de columnas y documentó las exclusiones.

Los controles principales abarcaron:

- coordenadas faltantes o fuera del rango aproximado de CABA;
- fechas y horas no interpretables;
- cantidades no numéricas;
- posibles duplicados;
- diferencias de estructura entre archivos.

## Preparación espacial

Los datos de origen se interpretaron en `EPSG:4326` y se proyectaron a `EPSG:32721` para realizar operaciones en metros.

## KDE e IER

Los hechos se rasterizaron en una grilla regular y se suavizaron mediante un filtro gaussiano. La calibración comparó tamaños de celda de 75, 100, 150 y 200 metros, junto con bandwidths de 250, 350, 500 y 750 metros.

La configuración seleccionada fue:

- celda de 100 metros;
- bandwidth de 750 metros;
- margen de 3000 metros.

Las superficies temporales se ajustaron por la cantidad de horas representadas. Todas las franjas se normalizaron mediante un máximo global común para conservar la comparabilidad.

## Franjas horarias

- Madrugada: 00:00–05:59.
- Mañana: 06:00–11:59.
- Tarde: 12:00–17:59.
- Noche: 18:00–23:59.
- General: conjunto completo de registros utilizables.

## Red peatonal

La red se obtuvo desde OpenStreetMap mediante OSMnx, se proyectó al CRS métrico y se validó su conectividad. El grafo final contó con 45.291 nodos y 139.972 segmentos dirigidos.

## IER por segmento

Cada segmento se muestreó cada 25 metros. El IER del tramo se calculó mediante la media de los valores interpolados, lo que aproxima la exposición promedio a lo largo de su geometría.

## Función de costo

La ruta base minimiza la longitud. La ruta alternativa minimiza:

```text
longitud × (1 + alpha × IER)
```

Se compararon valores de alpha entre 0 y 5. Se seleccionó `alpha = 3` por ofrecer una reducción media del IER de 10,61 % con un incremento medio de distancia de 2,48 %.

## Alcance de la interpretación

El IER es relativo a las fuentes y decisiones metodológicas utilizadas. Su objetivo es comparar recorridos, no estimar una probabilidad individual ni garantizar la seguridad.
