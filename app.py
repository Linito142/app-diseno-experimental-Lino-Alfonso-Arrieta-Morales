AUTOR = "Escribe aquí tu nombre"

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="App de Diseño Experimental",
    page_icon="🌱",
    layout="wide",
)

st.title("App de Diseño Experimental")
st.subheader("Ingeniería Agrícola – Universidad de Sucre")
st.write(
    "El diseño experimental permite planificar ensayos de campo de manera "
    "ordenada para comparar tratamientos, controlar fuentes de variación y "
    "obtener evidencia confiable que apoye las decisiones agrícolas."
)

st.header("Módulos")
modulos = [
    {
        "Diseño": "DCA — Diseño completamente al azar",
        "Cuándo se usa": "Cuando las unidades experimentales son homogéneas.",
        "Ejemplo agrícola": "Comparar cuatro secadores asignando al azar muestras de yuca.",
        "Estado": "Disponible",
    },
    {
        "Diseño": "DBCA — Diseño de bloques completos al azar",
        "Cuándo se usa": "Cuando se puede agrupar la variación en bloques homogéneos.",
        "Ejemplo agrícola": "Comparar fertilizantes agrupando parcelas por gradiente de fertilidad.",
        "Estado": "En construcción",
    },
    {
        "Diseño": "DCL — Diseño de cuadrado latino",
        "Cuándo se usa": "Cuando se deben controlar dos fuentes de variación mediante filas y columnas.",
        "Ejemplo agrícola": "Comparar variedades controlando gradientes de suelo en dos direcciones.",
        "Estado": "En construcción",
    },
    {
        "Diseño": "DPD — Diseño de parcelas divididas",
        "Cuándo se usa": "Cuando los factores requieren distintos niveles de aleatorización.",
        "Ejemplo agrícola": "Evaluar métodos de riego en parcelas principales y dosis de abono en subparcelas.",
        "Estado": "En construcción",
    },
    {
        "Diseño": "Factoriales",
        "Cuándo se usa": "Cuando se estudian varios factores y sus posibles interacciones.",
        "Ejemplo agrícola": "Comparar combinaciones de variedades de maíz y dosis de fertilizante.",
        "Estado": "En construcción",
    },
    {
        "Diseño": "RSM — Metodología de superficie de respuesta",
        "Cuándo se usa": "Cuando se busca modelar y optimizar una respuesta según niveles de factores.",
        "Ejemplo agrícola": "Optimizar temperatura y flujo de aire para secar yuca.",
        "Estado": "En construcción",
    },
]
st.table(pd.DataFrame(modulos))

st.header("Instrucciones de uso")
st.markdown(
    "1. Elige el módulo que corresponda al diseño de tu experimento.\n"
    "2. Carga los datos con las variables y tratamientos requeridos.\n"
    "3. Revisa los resultados y su interpretación.\n"
    "4. Verifica los supuestos y compara los resultados con tu cálculo manual."
)

st.warning(
    "Esta app apoya el aprendizaje. El estudiante interpreta los resultados, "
    "verifica supuestos y compara con su cálculo manual."
)

with st.sidebar:
    st.header("Información del curso")
    st.write(f"Autor: {AUTOR}")
    st.write("Curso: Diseño Experimental")
    st.write("Semestre: 2026-2")
