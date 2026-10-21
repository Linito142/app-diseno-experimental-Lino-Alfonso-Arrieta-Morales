import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy.stats import levene, probplot, shapiro
from statsmodels.regression.linear_model import RegressionResultsWrapper

from utils.anova_utils import validar_dca


def residuos_y_ajustados(modelo: RegressionResultsWrapper) -> pd.DataFrame:
    """Obtiene los residuos y valores ajustados del modelo.

    Args:
        modelo: Modelo DCA ajustado con mínimos cuadrados ordinarios.

    Returns:
        DataFrame con las columnas ``Ajustados`` y ``Residuos``.
    """
    # Los residuos e_ij = y_ij - y_estimado_ij permiten revisar el comportamiento del error.
    return pd.DataFrame(
        {
            "Ajustados": np.asarray(modelo.fittedvalues, dtype=float),
            "Residuos": np.asarray(modelo.resid, dtype=float),
        }
    )


def prueba_shapiro(
    residuos: pd.Series | np.ndarray | list[float], alfa: float = 0.05
) -> tuple[float, float, str]:
    """Evalúa la normalidad de los residuos con Shapiro-Wilk.

    Args:
        residuos: Valores residuales del modelo ajustado.
        alfa: Nivel de significancia para interpretar la prueba.

    Returns:
        Estadístico W, p-valor y conclusión en español.

    Raises:
        ValueError: Si hay menos de tres residuos o alfa no es válido.
    """
    # Se comprueba alfa para usar el mismo umbral de decisión que en el ANOVA.
    if not 0 < alfa < 1:
        raise ValueError("El nivel alfa debe ser mayor que 0 y menor que 1.")

    # Shapiro-Wilk necesita al menos tres observaciones para evaluar si los residuos son normales.
    valores = np.asarray(residuos, dtype=float)
    if valores.size < 3:
        raise ValueError("Shapiro-Wilk requiere al menos tres residuos.")
    if not np.isfinite(valores).all():
        raise ValueError("Los residuos deben ser numéricos y no contener valores faltantes.")

    # La hipótesis nula de Shapiro-Wilk establece que los residuos provienen de una distribución normal.
    resultado = shapiro(valores)
    estadistico = float(resultado.statistic)
    p_valor = float(resultado.pvalue)
    if p_valor < alfa:
        conclusion = (
            f"Se rechaza la normalidad de los residuos (p-valor = {p_valor:.4g} "
            f"< α = {alfa:g})."
        )
    else:
        conclusion = (
            f"No se rechaza la normalidad de los residuos (p-valor = {p_valor:.4g} "
            f"≥ α = {alfa:g})."
        )
    return estadistico, p_valor, conclusion


def prueba_levene(
    df: pd.DataFrame,
    col_trat: str,
    col_resp: str,
    alfa: float = 0.05,
) -> tuple[float, float, str]:
    """Evalúa la igualdad de varianzas entre tratamientos con Levene.

    Args:
        df: Datos con los tratamientos y la respuesta.
        col_trat: Nombre de la columna que identifica los tratamientos.
        col_resp: Nombre de la columna con la respuesta numérica.
        alfa: Nivel de significancia para interpretar la prueba.

    Returns:
        Estadístico de Levene, p-valor y conclusión en español.

    Raises:
        ValueError: Si los datos no cumplen los requisitos del DCA o alfa no es válido.
    """
    # Se comprueba alfa y se reutilizan las validaciones del DCA para evitar grupos incompletos.
    if not 0 < alfa < 1:
        raise ValueError("El nivel alfa debe ser mayor que 0 y menor que 1.")
    errores = validar_dca(df, col_trat, col_resp)
    if errores:
        raise ValueError("No se puede evaluar Levene:\n- " + "\n- ".join(errores))

    # La prueba de Levene compara la dispersión entre tratamientos y usa medianas para ser más robusta.
    grupos = [
        grupo[col_resp].to_numpy(dtype=float)
        for _, grupo in df.groupby(col_trat, observed=True, sort=False)
    ]
    resultado = levene(*grupos, center="median")
    estadistico = float(resultado.statistic)
    p_valor = float(resultado.pvalue)
    if p_valor < alfa:
        conclusion = (
            f"Se rechaza la igualdad de varianzas entre tratamientos "
            f"(p-valor = {p_valor:.4g} < α = {alfa:g})."
        )
    else:
        conclusion = (
            f"No se rechaza la igualdad de varianzas entre tratamientos "
            f"(p-valor = {p_valor:.4g} ≥ α = {alfa:g})."
        )
    return estadistico, p_valor, conclusion


def grafico_residuos_vs_ajustados(modelo: RegressionResultsWrapper) -> go.Figure:
    """Crea un gráfico de residuos frente a valores ajustados.

    Args:
        modelo: Modelo DCA ajustado con mínimos cuadrados ordinarios.

    Returns:
        Figura Plotly para revisar patrones y dispersión de los residuos.
    """
    # Se grafican residuos e_ij = y_ij - y_estimado_ij frente a y_estimado_ij para buscar patrones.
    datos_grafico = residuos_y_ajustados(modelo)
    figura = go.Figure()
    figura.add_trace(
        go.Scatter(
            x=datos_grafico["Ajustados"],
            y=datos_grafico["Residuos"],
            mode="markers",
            name="Observaciones",
        )
    )
    figura.add_hline(y=0, line_dash="dash", line_color="red")
    figura.update_layout(
        title="Residuos frente a valores ajustados",
        xaxis_title="Valores ajustados",
        yaxis_title="Residuos",
    )
    return figura


def grafico_qq(residuos: pd.Series | np.ndarray | list[float]) -> go.Figure:
    """Crea un gráfico Q-Q normal para los residuos del modelo.

    Args:
        residuos: Valores residuales del modelo ajustado.

    Returns:
        Figura Plotly para comparar cuantiles observados y normales teóricos.

    Raises:
        ValueError: Si hay menos de tres residuos o contienen valores no finitos.
    """
    # Se requieren suficientes residuos y valores finitos para comparar cuantiles.
    valores = np.asarray(residuos, dtype=float)
    if valores.size < 3:
        raise ValueError("El gráfico Q-Q requiere al menos tres residuos.")
    if not np.isfinite(valores).all():
        raise ValueError("Los residuos deben ser numéricos y no contener valores faltantes.")

    # Los cuantiles de probplot comparan los residuos observados con cuantiles de una distribución normal.
    cuantiles_teoricos, cuantiles_observados = probplot(
        valores, dist="norm", fit=False
    )
    pendiente, intercepto = np.polyfit(cuantiles_teoricos, cuantiles_observados, 1)
    figura = go.Figure()
    figura.add_trace(
        go.Scatter(
            x=cuantiles_teoricos,
            y=cuantiles_observados,
            mode="markers",
            name="Residuos",
        )
    )
    figura.add_trace(
        go.Scatter(
            x=cuantiles_teoricos,
            y=pendiente * cuantiles_teoricos + intercepto,
            mode="lines",
            name="Línea de referencia",
        )
    )
    figura.update_layout(
        title="Gráfico Q-Q de los residuos",
        xaxis_title="Cuantiles teóricos normales",
        yaxis_title="Cuantiles observados de los residuos",
    )
    return figura
