```python
import streamlit as st
import pandas as pd

# ============================================================
# CONFIGURACIÓN DE LA APLICACIÓN
# ============================================================

st.set_page_config(
    page_title="App de Diseño Experimental",
    page_icon="🌱",
    layout="wide"
)

# Nombre del autor
AUTOR = "Lino Alfonso Arrieta Morales"


# ============================================================
# PORTADA
# ============================================================

st.title("Aplicación de Diseño Experimental")

st.subheader("Ingeniería Agrícola – Universidad de Sucre")

st.write(
    """
    Aplicación web educativa desarrollada con Python y Streamlit para
    apoyar el análisis de diseños experimentales del curso de Diseño
    Experimental del programa de Ingeniería Agrícola de la Universidad
    de Sucre. Los resultados apoyan el aprendizaje y deben interpretarse
    junto con los supuestos del diseño y la verificación del estudiante.
    """
)


# ============================================================
# MÓDULOS Y ESTADO
# ============================================================

st.header("Módulos y estado")

datos_modulos = [
    {
        "Módulo": "DCA — Diseño completamente al azar",
        "Estado": "Disponible",
        "Descripción": (
            "Analiza un factor en unidades experimentales homogéneas; "
            "incluye el ejemplo de humedad de yuca con cuatro secadores solares."
        )
    },
    {
        "Módulo": "DBCA — Diseño en bloques completos al azar",
        "Estado": "En construcción",
        "Descripción": (
            "Controla una fuente conocida de variación mediante bloques."
        )
    },
    {
        "Módulo": "DCL — Diseño en cuadrado latino",
        "Estado": "En construcción",
        "Descripción": (
            "Controla dos fuentes de variación mediante filas y columnas."
        )
    },
    {
        "Módulo": "DPD — Diseño de parcelas divididas",
        "Estado": "En construcción",
        "Descripción": (
            "Organiza factores en parcelas principales y subparcelas."
        )
    },
    {
        "Módulo": "Factoriales",
        "Estado": "En construcción",
        "Descripción": (
            "Estudia varios factores y sus interacciones."
        )
    },
    {
        "Módulo": "RSM — Metodología de superficie de respuesta",
        "Estado": "En construcción",
        "Descripción": (
            "Modela y explora respuestas según factores cuantitativos."
        )
    }
]

df_modulos = pd.DataFrame(datos_modulos)

st.table(df_modulos)


# ============================================================
# INSTRUCCIONES DE USO
# ============================================================

st.header("¿Cómo utilizar la aplicación?")

st.markdown(
    """
    **1. Elegir el módulo:** seleccione el diseño experimental que desea estudiar.

    **2. Cargar los datos:** ingrese o cargue los datos correspondientes al experimento.

    **3. Revisar los resultados:** consulte las tablas, gráficos y pruebas estadísticas.

    **4. Verificar e interpretar:** compare los resultados con su cálculo manual,
    revise los supuestos y formule la conclusión agrícola.
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

