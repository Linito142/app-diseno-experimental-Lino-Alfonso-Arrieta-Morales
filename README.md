# Aplicación de Diseño Experimental

Aplicación web educativa desarrollada con Python y Streamlit para apoyar el
análisis de diseños experimentales del curso de Diseño Experimental del
programa de Ingeniería Agrícola de la Universidad de Sucre. Los resultados
apoyan el aprendizaje y deben interpretarse junto con los supuestos del diseño
y la verificación del estudiante.

## Módulos y estado

| Módulo | Estado | Descripción |
| --- | --- | --- |
| DCA — Diseño completamente al azar | Disponible | Análisis de datos de tratamientos, ANOVA, comparaciones y diagnósticos. |
| DBCA — Diseño de bloques completos al azar | En construcción | Presentación del diseño; el análisis aún no está implementado. |
| DCL — Diseño de cuadrado latino | En construcción | Presentación del diseño; el análisis aún no está implementado. |
| DPD — Diseño de parcelas divididas | En construcción | Presentación del diseño; el análisis aún no está implementado. |
| Diseños factoriales | En construcción | Presentación del diseño; el análisis aún no está implementado. |
| RSM — Metodología de superficie de respuesta | En construcción | Presentación del diseño; el análisis aún no está implementado. |

## Estructura del proyecto

```text
.
├── app.py
├── data/
│   └── dca_secadores.csv
├── pages/
│   ├── 01_DCA.py
│   ├── 02_DBCA.py
│   ├── 03_DCL.py
│   ├── 04_DPD.py
│   ├── 05_Factoriales.py
│   └── 06_RSM.py
├── utils/
│   ├── __init__.py
│   ├── anova_utils.py
│   └── diagnostico_utils.py
├── verificacion/
│   └── verificacion_dca.R
├── requirements.txt
└── BITACORA_IA.md
```

## Instalación y ejecución local

Se requiere Python 3.10 o posterior. Desde la raíz del proyecto, crea y activa
un entorno virtual e instala las dependencias:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

En Windows, activa el entorno con `.venv\Scripts\activate` en lugar de
`source .venv/bin/activate`. Inicia la aplicación con:

```bash
streamlit run app.py
```

Streamlit mostrará en la terminal la dirección local para abrir la aplicación.

## Ejecución en GitHub Codespaces

Abre el repositorio en un Codespace y, desde la terminal integrada, instala
las dependencias e inicia Streamlit:

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

Codespaces ofrecerá abrir o reenviar el puerto 8501 para acceder a la
aplicación en el navegador.

## Verificación con R

El script `verificacion/verificacion_dca.R` calcula ANOVA, medias por secador,
coeficiente de variación y Tukey. Para ejecutarlo se necesita R y el archivo
`data/dca_mi_variante.csv` con las columnas `secador` y `humedad`; ese archivo
debe proporcionarse antes de ejecutar la verificación. Desde la carpeta
`verificacion/`, se puede correr con `Rscript verificacion_dca.R`.

## Autor y uso de inteligencia artificial

**Autor:** Lino Alfonso Arrieta Morales.

Se utilizó inteligencia artificial generativa como apoyo en el desarrollo y
la documentación del proyecto. El autor debe revisar y validar el contenido
generado; los resultados estadísticos de la aplicación se calculan a partir
de los datos suministrados y no se reemplazan por resultados simulados.
La bitácora de uso de IA se encuentra en [`BITACORA_IA.md`](./BITACORA_IA.md).
