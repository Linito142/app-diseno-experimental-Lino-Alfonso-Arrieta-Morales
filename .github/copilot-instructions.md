# Instrucciones permanentes del repositorio

## Contexto del proyecto

- Este proyecto es una aplicación de Diseño Experimental desarrollada en Python y Streamlit para el curso de Diseño Experimental del programa de Ingeniería Agrícola de la Universidad de Sucre.
- La estructura esperada es:
  - `app.py`: portada de la aplicación.
  - `pages/`: un archivo por cada diseño experimental.
  - `utils/`: funciones reutilizables; debe incluir `__init__.py`.
  - `data/`: archivos CSV de ejemplo.
  - `verificacion/`: scripts de R para verificación.

## Idioma y documentación del código

- Escribe todo el código, comentarios, docstrings y mensajes de la interfaz en español.
- Añade un comentario en cada paso estadístico para explicar qué se calcula y por qué, con explicaciones adecuadas para estudiantes de Ingeniería Agrícola.
- Define las funciones con anotaciones de tipos (type hints) y docstrings con el estilo Google, redactados en español.

## Dependencias permitidas

- Utiliza únicamente estas librerías: `streamlit`, `pandas`, `numpy`, `scipy`, `statsmodels`, `plotly` y `openpyxl`.
- No agregues otras dependencias sin pedir permiso.

## Análisis estadístico

- Ajusta los modelos ANOVA con `statsmodels.formula.api.ols` y calcula la tabla con `statsmodels.stats.anova.anova_lm(typ=2)`.
- Realiza las comparaciones de Tukey con `statsmodels.stats.multicomp.pairwise_tukeyhsd`.
- No inventes ni simules resultados para presentarlos como análisis: todos los números mostrados deben provenir del cálculo correspondiente.

## Verificación antes de terminar

- Antes de dar por terminada una tarea, ejecuta el código pertinente, revisa los errores que aparezcan y corrígelos.
