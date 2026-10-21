from io import BytesIO
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
from scipy.stats import f as distribucion_f

from utils.anova_utils import (
    ajustar_dca,
    cargar_datos,
    coeficiente_variacion,
    interpretar_dca,
    resumen_tratamientos,
    tabla_anova,
    tukey,
    validar_dca,
)


@st.cache_data
def cargar_datos_cacheados(
    nombre_archivo: str, contenido: bytes | None
) -> pd.DataFrame:
    """Carga y almacena en caché datos CSV o Excel para el análisis."""
    # El archivo de ejemplo se lee desde su ruta; los archivos cargados se leen desde memoria.
    if contenido is None:
        return cargar_datos(Path(__file__).resolve().parents[1] / "data" / nombre_archivo)

    archivo = BytesIO(contenido)
    archivo.name = nombre_archivo
    return cargar_datos(archivo)


st.title("DCA — Diseño completamente al azar")
st.write(
    "El diseño completamente al azar compara tratamientos asignándolos al azar "
    "a unidades experimentales homogéneas. En este ejemplo se evalúa la humedad "
    "final de yuca (% b.h.) en cuatro secadores solares, con cuatro réplicas "
    "por secador."
)

archivo_cargado = st.file_uploader(
    "Carga un archivo de datos",
    type=["csv", "xlsx"],
    help="El archivo debe incluir una columna de tratamiento y otra de respuesta.",
)

if archivo_cargado is None:
    nombre_archivo = "dca_secadores.csv"
    contenido = None
    st.caption(
        "No se cargó un archivo; se utilizarán los datos de ejemplo "
        "data/dca_secadores.csv."
    )
else:
    nombre_archivo = archivo_cargado.name
    contenido = archivo_cargado.getvalue()

try:
    datos = cargar_datos_cacheados(nombre_archivo, contenido)
except (OSError, UnicodeDecodeError, ValueError, pd.errors.ParserError) as error:
    st.error(f"No fue posible cargar los datos: {error}")
    st.stop()

if datos.empty:
    st.error("El archivo no contiene observaciones.")
    st.stop()
if len(datos.columns) < 2:
    st.error("El archivo debe contener al menos una columna de tratamiento y una de respuesta.")
    st.stop()

columnas = list(datos.columns)
columnas_numericas = [
    columna
    for columna in columnas
    if pd.api.types.is_numeric_dtype(datos[columna])
]
indice_respuesta = next(
    (
        columnas.index(columna)
        for columna in reversed(columnas_numericas)
        if columna != columnas[0]
    ),
    1,
)

columna_tratamiento = st.selectbox(
    "Columna de tratamiento",
    options=columnas,
    index=0,
)
columna_respuesta = st.selectbox(
    "Columna de respuesta",
    options=columnas,
    index=indice_respuesta,
)
alfa = st.slider(
    "Nivel de significancia (α)",
    min_value=0.01,
    max_value=0.10,
    value=0.05,
    step=0.01,
    format="%.2f",
)

errores = validar_dca(datos, columna_tratamiento, columna_respuesta)
if errores:
    for error in errores:
        st.error(error)
    st.stop()

try:
    modelo = ajustar_dca(datos, columna_tratamiento, columna_respuesta)
    resultados_anova = tabla_anova(modelo)
    resumen = resumen_tratamientos(datos, columna_tratamiento, columna_respuesta)
    cv = coeficiente_variacion(modelo, datos, columna_respuesta)
    interpretacion = interpretar_dca(resultados_anova, alfa)
except ValueError as error:
    st.error(f"No fue posible analizar estos datos: {error}")
    st.stop()

p_valor_tratamientos = float(
    resultados_anova.loc[
        resultados_anova["Fuente"] == "Tratamientos", "p-valor"
    ].iloc[0]
)
gl_tratamientos = float(
    resultados_anova.loc[resultados_anova["Fuente"] == "Tratamientos", "gl"].iloc[0]
)
gl_error = float(
    resultados_anova.loc[resultados_anova["Fuente"] == "Error", "gl"].iloc[0]
)
f_observada = float(
    resultados_anova.loc[resultados_anova["Fuente"] == "Tratamientos", "F"].iloc[0]
)

# La F crítica es el cuantil 1 - alfa de F(gl tratamientos, gl error).
f_critica = float(
    distribucion_f.ppf(1 - alfa, gl_tratamientos, gl_error)
)

pestanas = st.tabs(["Datos", "ANOVA", "Comparaciones", "Gráficos"])

with pestanas[0]:
    st.subheader("Datos del experimento")
    st.dataframe(datos, width="stretch")
    st.subheader("Resumen por tratamiento")
    st.dataframe(
        resumen.style.format(
            {
                "total": "{:.4f}",
                "media": "{:.4f}",
                "desviación estándar": "{:.4f}",
            }
        ),
        width="stretch",
    )

with pestanas[1]:
    st.subheader("Análisis de varianza")
    st.dataframe(
        resultados_anova.style.format(
            {
                "gl": "{:.4f}",
                "SC": "{:.4f}",
                "CM": "{:.4f}",
                "F": "{:.4f}",
                "p-valor": "{:.4f}",
            },
            na_rep="—",
        ),
        width="stretch",
    )

    columna_f, columna_cv = st.columns(2)
    columna_f.metric("F crítica", f"{f_critica:.4f}")
    columna_cv.metric("Coeficiente de variación", f"{cv:.4f} %")

    if f_observada > f_critica:
        st.success(interpretacion)
    else:
        st.info(interpretacion)

with pestanas[2]:
    st.subheader("Comparaciones múltiples de Tukey")
    if p_valor_tratamientos < alfa:
        try:
            comparaciones, dms = tukey(
                datos,
                columna_tratamiento,
                columna_respuesta,
                alfa,
            )
        except ValueError as error:
            st.error(f"No fue posible realizar las comparaciones: {error}")
        else:
            st.dataframe(
                comparaciones.style.format(
                    {
                        "Diferencia de medias": "{:.4f}",
                        "p-valor ajustado": "{:.4f}",
                        "Límite inferior": "{:.4f}",
                        "Límite superior": "{:.4f}",
                    }
                ),
                width="stretch",
            )
            st.metric("Diferencia mínima significativa (DMS)", f"{dms:.4f}")
    else:
        st.info(
            "No se realiza Tukey porque el ANOVA no encontró evidencia "
            "estadística suficiente de diferencias entre tratamientos "
            f"(p-valor = {p_valor_tratamientos:.4f} ≥ α = {alfa:.2f})."
        )

with pestanas[3]:
    st.subheader("Distribución de la respuesta")
    figura_cajas = px.box(
        datos,
        x=columna_tratamiento,
        y=columna_respuesta,
        points="all",
        labels={
            columna_tratamiento: "Tratamiento",
            columna_respuesta: "Respuesta",
        },
        title="Respuesta por tratamiento",
    )
    st.plotly_chart(figura_cajas, width="stretch")

    st.subheader("Media de la respuesta por tratamiento")
    figura_medias = px.bar(
        resumen,
        x="Tratamiento",
        y="media",
        labels={"Tratamiento": "Tratamiento", "media": "Media de la respuesta"},
        title="Media por tratamiento",
    )
    st.plotly_chart(figura_medias, width="stretch")
