import csv
import itertools
import json
import warnings
from pathlib import Path
from typing import BinaryIO, TextIO

import numpy as np
import pandas as pd
from scipy.stats import studentized_range
from statsmodels.formula.api import ols
from statsmodels.regression.linear_model import RegressionResultsWrapper
from statsmodels.stats.anova import anova_lm
from statsmodels.stats.multicomp import pairwise_tukeyhsd


def cargar_datos(archivo: str | Path | BinaryIO | TextIO) -> pd.DataFrame:
    """Carga datos desde un archivo CSV o un libro Excel.

    Args:
        archivo: Ruta o archivo abierto con extensión ``.csv`` o ``.xlsx``.

    Returns:
        Los datos leídos en un DataFrame.

    Raises:
        ValueError: Si el formato no es compatible o no se detecta el separador.
    """
    # Se identifica el formato por la extensión para usar el lector apropiado.
    if isinstance(archivo, (str, Path)):
        nombre_archivo = Path(archivo).name
    else:
        nombre_archivo = Path(getattr(archivo, "name", "")).name
    extension = Path(nombre_archivo).suffix.lower()

    # Para Excel se conservan los valores y tipos que pandas detecta en el libro.
    if extension == ".xlsx":
        return pd.read_excel(archivo)
    if extension != ".csv":
        raise ValueError("El archivo debe tener extensión .csv o .xlsx.")

    # Se lee una muestra para detectar si el CSV separa sus columnas con coma o punto y coma.
    if isinstance(archivo, (str, Path)):
        with open(archivo, encoding="utf-8-sig", newline="") as entrada:
            muestra = entrada.read(4096)
    else:
        muestra_leida = archivo.read(4096)
        muestra = (
            muestra_leida.decode("utf-8-sig")
            if isinstance(muestra_leida, bytes)
            else muestra_leida
        )
        # Se rebobina el archivo para que pandas lea desde el primer carácter.
        try:
            archivo.seek(0)
        except (AttributeError, OSError) as error:
            raise ValueError("El archivo CSV debe permitir volver al inicio.") from error

    # El separador se detecta solo entre los formatos solicitados: coma y punto y coma.
    try:
        separador = csv.Sniffer().sniff(muestra, delimiters=",;").delimiter
    except csv.Error as error:
        raise ValueError("No se pudo detectar si el CSV usa coma o punto y coma.") from error
    return pd.read_csv(archivo, sep=separador, encoding="utf-8-sig")


def validar_dca(df: pd.DataFrame, col_trat: str, col_resp: str) -> list[str]:
    """Comprueba los requisitos básicos de los datos para un DCA.

    Args:
        df: Datos que contienen los tratamientos y la respuesta observada.
        col_trat: Nombre de la columna que identifica los tratamientos.
        col_resp: Nombre de la columna con la respuesta numérica.

    Returns:
        Mensajes de error en español; una lista vacía indica datos válidos.
    """
    errores: list[str] = []

    # Se verifican las columnas antes de calcular cantidad de tratamientos o réplicas.
    if col_trat not in df.columns:
        errores.append(f"No se encontró la columna de tratamiento «{col_trat}».")
    if col_resp not in df.columns:
        errores.append(f"No se encontró la columna de respuesta «{col_resp}».")
    if col_trat == col_resp:
        errores.append("Las columnas de tratamiento y respuesta deben ser distintas.")
    if col_trat not in df.columns or col_resp not in df.columns:
        return errores

    # Los tratamientos y respuestas deben estar completos para que cada observación contribuya al análisis.
    if df[col_trat].isna().any():
        errores.append("La columna de tratamiento contiene datos faltantes.")
    if df[col_resp].isna().any():
        errores.append("La columna de respuesta contiene datos faltantes.")

    # La respuesta debe ser numérica porque el ANOVA compara medias de una variable cuantitativa.
    if not pd.api.types.is_numeric_dtype(df[col_resp]):
        errores.append("La columna de respuesta no es numérica.")

    if df[col_trat].isna().any() or df[col_resp].isna().any():
        return errores

    # Se requieren al menos dos tratamientos y dos réplicas por tratamiento para comparar medias.
    if df[col_trat].nunique() < 2:
        errores.append("Se requieren al menos dos tratamientos.")
    conteos = df.groupby(col_trat, observed=True).size()
    if (conteos < 2).any():
        errores.append("Cada tratamiento debe tener al menos dos réplicas.")

    return errores


def _formula_dca(col_trat: str, col_resp: str) -> str:
    """Construye la fórmula de un DCA protegiendo nombres de columnas."""
    # La fórmula del modelo es Q("respuesta") ~ C(Q("tratamiento")).
    # Q() protege nombres con espacios, tildes, símbolos o palabras reservadas en patsy.
    respuesta = json.dumps(col_resp, ensure_ascii=False)
    tratamiento = json.dumps(col_trat, ensure_ascii=False)
    return f"Q({respuesta}) ~ C(Q({tratamiento}))"


def _exigir_datos_validos(df: pd.DataFrame, col_trat: str, col_resp: str) -> None:
    """Detiene el análisis y comunica los problemas encontrados en los datos."""
    # Se reutiliza la validación para impedir ajustes con datos incompletos o sin réplicas suficientes.
    errores = validar_dca(df, col_trat, col_resp)
    if errores:
        raise ValueError("No se puede analizar el DCA:\n- " + "\n- ".join(errores))


def _validar_alfa(alfa: float) -> None:
    """Comprueba que el nivel de significancia esté entre cero y uno."""
    # El nivel alfa debe ser una probabilidad estrictamente entre cero y uno.
    if not 0 < alfa < 1:
        raise ValueError("El nivel alfa debe ser mayor que 0 y menor que 1.")


def ajustar_dca(
    df: pd.DataFrame, col_trat: str, col_resp: str
) -> RegressionResultsWrapper:
    """Ajusta un modelo de ANOVA para un DCA de un solo factor.

    Args:
        df: Datos de los tratamientos y la respuesta.
        col_trat: Nombre de la columna que identifica los tratamientos.
        col_resp: Nombre de la columna con la respuesta numérica.

    Returns:
        El modelo lineal ajustado por mínimos cuadrados ordinarios.

    Raises:
        ValueError: Si los datos no cumplen los requisitos para un DCA.
    """
    # Se valida que existan tratamientos replicados y respuestas completas antes de estimar el modelo.
    _exigir_datos_validos(df, col_trat, col_resp)

    # El modelo usa y_ij = mu + tau_i + error_ij; Q() protege ambos nombres de columna.
    return ols(_formula_dca(col_trat, col_resp), data=df).fit()


def tabla_anova(modelo: RegressionResultsWrapper) -> pd.DataFrame:
    """Calcula la tabla ANOVA tipo II y añade la suma de cuadrados total.

    Args:
        modelo: Modelo DCA ajustado con `ajustar_dca`.

    Returns:
        Tabla con las columnas Fuente, gl, SC, CM, F y p-valor.
    """
    # El ANOVA tipo II separa la variación explicada por tratamientos del error experimental.
    resultado = anova_lm(modelo, typ=2)
    filas: list[dict[str, object]] = []
    for fuente, valores in resultado.iterrows():
        # Los grados de libertad y la suma de cuadrados provienen del modelo ajustado.
        gl = float(valores["df"])
        suma_cuadrados = float(valores["sum_sq"])
        # El cuadrado medio de cada fuente es CM = SC / gl.
        cuadrado_medio = suma_cuadrados / gl if gl else float("nan")
        filas.append(
            {
                "Fuente": "Error" if fuente == "Residual" else "Tratamientos",
                "gl": gl,
                "SC": suma_cuadrados,
                "CM": cuadrado_medio,
                "F": float(valores["F"]) if pd.notna(valores["F"]) else float("nan"),
                "p-valor": (
                    float(valores["PR(>F)"])
                    if pd.notna(valores["PR(>F)"])
                    else float("nan")
                ),
            }
        )

    # La variación total se calcula como SC_Total = suma((y_ij - media_general)^2).
    respuesta = np.asarray(modelo.model.endog, dtype=float)
    gl_total = len(respuesta) - 1
    suma_total = float(np.sum((respuesta - np.mean(respuesta)) ** 2))
    # Se aplica también a la fila total la definición solicitada CM = SC / gl.
    filas.append(
        {
            "Fuente": "Total",
            "gl": float(gl_total),
            "SC": suma_total,
            "CM": suma_total / gl_total if gl_total else float("nan"),
            "F": float("nan"),
            "p-valor": float("nan"),
        }
    )
    return pd.DataFrame(filas, columns=["Fuente", "gl", "SC", "CM", "F", "p-valor"])


def resumen_tratamientos(
    df: pd.DataFrame, col_trat: str, col_resp: str
) -> pd.DataFrame:
    """Resume las observaciones y la respuesta por tratamiento.

    Args:
        df: Datos de los tratamientos y la respuesta.
        col_trat: Nombre de la columna que identifica los tratamientos.
        col_resp: Nombre de la columna con la respuesta numérica.

    Returns:
        Tabla por tratamiento con n, total, media y desviación estándar.

    Raises:
        ValueError: Si los datos no cumplen los requisitos para un DCA.
    """
    # Se validan los grupos antes de resumirlos para que no se oculten datos incompletos.
    _exigir_datos_validos(df, col_trat, col_resp)

    # Para cada tratamiento se calculan n_i, suma(y_ij), media(y_ij) y desviación estándar muestral.
    resumen = (
        df.groupby(col_trat, observed=True)[col_resp]
        .agg(
            n="count",
            total="sum",
            media="mean",
            **{"desviación estándar": "std"},
        )
        .reset_index()
    )
    return resumen.rename(columns={col_trat: "Tratamiento"})


def coeficiente_variacion(
    modelo: RegressionResultsWrapper, df: pd.DataFrame, col_resp: str
) -> float:
    """Calcula el coeficiente de variación experimental del DCA.

    Args:
        modelo: Modelo DCA ajustado con `ajustar_dca`.
        df: Datos que contienen la respuesta.
        col_resp: Nombre de la columna con la respuesta numérica.

    Returns:
        Coeficiente de variación como porcentaje.

    Raises:
        ValueError: Si la respuesta no existe, no es numérica, está incompleta
            o su media general es cero.
    """
    # Se comprueba la variable usada como denominador antes de calcular el CV.
    if col_resp not in df.columns:
        raise ValueError(f"No se encontró la columna de respuesta «{col_resp}».")
    if not pd.api.types.is_numeric_dtype(df[col_resp]):
        raise ValueError("La columna de respuesta no es numérica.")
    if df[col_resp].isna().any():
        raise ValueError("La columna de respuesta contiene datos faltantes.")

    # La media general resume la escala de la respuesta de todos los tratamientos.
    media_general = float(df[col_resp].mean())
    if media_general == 0:
        raise ValueError("No se puede calcular el CV porque la media general es cero.")

    # El CV se calcula como CV = sqrt(CME) / media_general * 100.
    return float(np.sqrt(modelo.mse_resid) / media_general * 100)


def tukey(
    df: pd.DataFrame,
    col_trat: str,
    col_resp: str,
    alfa: float = 0.05,
) -> tuple[pd.DataFrame, float]:
    """Compara tratamientos con Tukey y calcula una diferencia mínima significativa.

    Args:
        df: Datos de los tratamientos y la respuesta.
        col_trat: Nombre de la columna que identifica los tratamientos.
        col_resp: Nombre de la columna con la respuesta numérica.
        alfa: Nivel de significancia para las comparaciones.

    Returns:
        Una tabla de comparaciones de Tukey y la DMS calculada.

    Raises:
        ValueError: Si alfa o los datos no son válidos para el análisis.
    """
    # Se comprueban alfa y los datos para que las comparaciones tengan un error experimental estimable.
    _validar_alfa(alfa)
    _exigir_datos_validos(df, col_trat, col_resp)

    # Tukey compara las medias de cada par usando el control familiar del error tipo I.
    resultado = pairwise_tukeyhsd(
        endog=df[col_resp], groups=df[col_trat], alpha=alfa
    )
    pares = list(itertools.combinations(resultado.groupsunique, 2))
    comparaciones = pd.DataFrame(
        {
            "Tratamiento 1": [grupo_1 for grupo_1, _ in pares],
            "Tratamiento 2": [grupo_2 for _, grupo_2 in pares],
            "Diferencia de medias": resultado.meandiffs,
            "p-valor ajustado": resultado.pvalues,
            "Límite inferior": resultado.confint[:, 0],
            "Límite superior": resultado.confint[:, 1],
            "Rechaza H0": resultado.reject,
        }
    )

    # El CME y glE se obtienen del ANOVA, y q usa el número de tratamientos y esos grados de libertad.
    modelo = ols(_formula_dca(col_trat, col_resp), data=df).fit()
    resultado_anova = anova_lm(modelo, typ=2)
    cme = float(resultado_anova.loc["Residual", "sum_sq"]) / float(
        resultado_anova.loc["Residual", "df"]
    )
    gl_error = float(resultado_anova.loc["Residual", "df"])
    num_tratamientos = int(df[col_trat].nunique())
    q_critico = float(studentized_range.ppf(1 - alfa, num_tratamientos, gl_error))

    # Si el número de réplicas no es igual, r es su media armónica para aproximar la DMS común.
    replicaciones = df.groupby(col_trat, observed=True).size().to_numpy(dtype=float)
    balanceado = bool(np.all(replicaciones == replicaciones[0]))
    r = (
        float(replicaciones[0])
        if balanceado
        else float(len(replicaciones) / np.sum(1 / replicaciones))
    )
    # La DMS solicitada se calcula como DMS = q(alfa; t; glE) * sqrt(CME / r).
    dms = float(q_critico * np.sqrt(cme / r))
    if not balanceado:
        # En un diseño desbalanceado una DMS única es aproximada; Tukey ajusta cada par por sus tamaños.
        warnings.warn(
            "La DMS es aproximada porque el diseño no está balanceado.",
            RuntimeWarning,
            stacklevel=2,
        )

    return comparaciones, dms


def interpretar_dca(tabla: pd.DataFrame, alfa: float = 0.05) -> str:
    """Interpreta el resultado del ANOVA de un DCA en lenguaje sencillo.

    Args:
        tabla: Tabla producida por `tabla_anova`.
        alfa: Nivel de significancia para decidir sobre la hipótesis nula.

    Returns:
        Explicación de la decisión sobre la igualdad de medias.

    Raises:
        ValueError: Si alfa es inválido o la tabla no contiene el resultado
            del efecto de tratamientos.
    """
    # Se valida alfa y se localiza el p-valor correspondiente a tratamientos.
    _validar_alfa(alfa)
    if not {"Fuente", "p-valor"}.issubset(tabla.columns):
        raise ValueError("La tabla debe incluir las columnas «Fuente» y «p-valor».")
    filas_tratamientos = tabla.loc[tabla["Fuente"] == "Tratamientos", "p-valor"]
    if filas_tratamientos.empty or pd.isna(filas_tratamientos.iloc[0]):
        raise ValueError("La tabla no contiene un p-valor válido para tratamientos.")

    # La decisión compara el p-valor del ANOVA con alfa para evaluar H0: todas las medias son iguales.
    p_valor = float(filas_tratamientos.iloc[0])
    if p_valor < alfa:
        return (
            f"Se rechaza H0 porque p-valor = {p_valor:.4g} es menor que "
            f"alfa = {alfa:g}. Hay evidencia de que al menos un tratamiento "
            "produce una media distinta; use una comparación posterior para "
            "identificar cuáles difieren."
        )
    return (
        f"No se rechaza H0 porque p-valor = {p_valor:.4g} no es menor que "
        f"alfa = {alfa:g}. No hay evidencia suficiente para concluir que las "
        "medias de los tratamientos difieren."
    )
