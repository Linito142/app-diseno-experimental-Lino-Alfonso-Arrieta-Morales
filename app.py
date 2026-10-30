```python
import streamlit as st
import pandas as pd

AUTOR = "Escribe aquí tu nombre"

# ============================================================
# CONFIGURACIÓN DE LA APLICACIÓN
# ============================================================

st.set_page_config(
    page_title="App de Diseño Experimental",
    page_icon="🌱",
    layout="wide",
)


# ============================================================
# PORTADA
# ============================================================

st.title("App de Diseño Experimental")

st.subheader("Ingeniería Agrícola – Universidad de Sucre")

st.write(
    """
    El diseño experimental permite planear ensayos de campo para comparar
    tratamientos de forma ordenada y confiable. Esta aplicación apoya el
    aprendizaje de los diseños usados en Ingeniería Agrícola y ayuda a
    interpretar resultados para tomar decisiones sobre cultivos y procesos
    productivos.
    """
)


# ============================================================
# MÓDULOS Y ESTADO
# ============================================================

st.header("Módulos y estado")

datos_modulos = [
    {
        "Módulo": "DCA",
        "Nombre completo": "Diseño completamente al azar",
        "¿Cuándo se usa?": (
            "Cuando las unidades experimentales son homogéneas y los "
            "tratamientos pueden asignarse al azar."
        ),
        "Ejemplo agrícola": (
            "Comparar fertilizantes en camas de cultivo con condiciones "
            "uniformes."
        ),
        "Estado": "Disponible",
    },
    {
        "Módulo": "DBCA",
        "Nombre completo": "Diseño de bloques completos al azar",
        "¿Cuándo se usa?": (
            "Cuando se necesita controlar una fuente conocida de variación "
            "agrupando unidades similares en bloques."
        ),
        "Ejemplo agrícola": (
            "Comparar fertilizantes en bloques de un lote con distinto nivel "
            "de fertilidad."
        ),
        "Estado": "En construcción",
    },
    {
        "Módulo": "DCL",
        "Nombre completo": "Diseño de cuadrado latino",
        "¿Cuándo se usa?": (
            "Cuando se deben controlar dos fuentes de variación, organizadas "
            "en filas y columnas."
        ),
        "Ejemplo agrícola": (
            "Comparar variedades de maíz controlando gradientes de humedad "
            "en dos direcciones."
        ),
        "Estado": "En construcción",
    },
    {
        "Módulo": "DPD",
        "Nombre completo": "Diseño de parcelas divididas",
        "¿Cuándo se usa?": (
            "Cuando los factores requieren unidades experimentales de distinto "
            "tamaño o diferente facilidad de aplicación."
        ),
        "Ejemplo agrícola": (
            "Evaluar sistemas de riego en parcelas principales y variedades "
            "de fríjol en subparcelas."
        ),
        "Estado": "En construcción",
    },
    {
        "Módulo": "Factoriales",
        "Nombre completo": "Diseños factoriales",
        "¿Cuándo se usa?": (
            "Cuando se estudian simultáneamente varios factores y se evalúan "
            "sus posibles interacciones."
        ),
        "Ejemplo agrícola": (
            "Evaluar combinaciones de dosis de fertilizante y láminas de riego "
            "en arroz."
        ),
        "Estado": "En construcción",
    },
    {
        "Módulo": "RSM",
        "Nombre completo": "Metodología de superficie de respuesta",
        "¿Cuándo se usa?": (
            "Cuando se modela una respuesta según factores cuantitativos para "
            "explorar y optimizar sus niveles."
        ),
        "Ejemplo agrícola": (
            "Optimizar temperatura y tiempo de secado para reducir la humedad "
            "de granos."
        ),
        "Estado": "En construcción",
    },
]

df_modulos = pd.DataFrame(datos_modulos)

st.table(
    df_modulos[
        [
            "Módulo",
            "Nombre completo",
            "¿Cuándo se usa?",
            "Ejemplo agrícola",
            "Estado",
        ]
    ]
)


# ============================================================
# INSTRUCCIONES DE USO
# ============================================================

st.header("¿Cómo utilizar la aplicación?")

st.markdown(
    """
    1. **Elegir el módulo** que corresponde al diseño del experimento.
    2. **Cargar los datos** del ensayo.
    3. **Revisar los resultados** y su interpretación.
    4. **Verificar a mano** los cálculos y los supuestos.
    """
)


# ============================================================
# ADVERTENCIA ACADÉMICA
# ============================================================

st.warning(
    "Esta app apoya el aprendizaje. El estudiante interpreta los resultados, "
    "verifica supuestos y compara con su cálculo manual."
)


# ============================================================
# BARRA LATERAL
# ============================================================

st.sidebar.title("Información del proyecto")

st.sidebar.write(f"**Autor:** {AUTOR}")
st.sidebar.write("**Curso:** Diseño Experimental")
st.sidebar.write("**Programa:** Ingeniería Agrícola")
st.sidebar.write("**Universidad:** Universidad de Sucre")
st.sidebar.write("**Semestre:** 2026-2")
```
