# Se carga el archivo de datos ubicado en la carpeta data, relativa a verificacion.
datos <- read.csv("../data/dca_mi_variante.csv", stringsAsFactors = FALSE) # Se conservan las observaciones y se deja el factor para el análisis.
# Se identifica secador como factor porque sus valores representan tratamientos.
datos$secador <- factor(datos$secador) # Así, el modelo compara niveles y no interpreta sus etiquetas como cantidades.
# Se ajusta el análisis de varianza para comparar la humedad media entre secadores.
modelo <- aov(humedad ~ factor(secador), data = datos) # La respuesta es humedad y el factor experimental es secador.
# Se muestra la tabla ANOVA para evaluar si hay diferencias entre las medias de los tratamientos.
print(summary(modelo)) # El valor p se interpreta junto con el contexto y los supuestos del experimento.
# Se calcula la humedad media de cada secador para describir la respuesta observada por tratamiento.
medias <- aggregate(humedad ~ secador, data = datos, FUN = mean) # La media resume las réplicas de cada secador.
# Se imprimen las medias para facilitar su comparación descriptiva.
print(medias) # Estas medias no sustituyen la prueba estadística de comparación.
# Se obtiene la tabla ANOVA para extraer el cuadrado medio del error experimental.
tabla_anova <- summary(modelo)[[1]] # El error representa la variación entre réplicas no explicada por el tratamiento.
# Se extrae el cuadrado medio residual, estimación de la varianza experimental.
cuadrado_medio_error <- tabla_anova["Residuals", "Mean Sq"] # Se usa para expresar el error en las unidades de la respuesta.
# Se calcula la media general de humedad para usarla como referencia relativa.
media_general <- mean(datos$humedad) # La media reúne las observaciones de todos los secadores.
# Se calcula el coeficiente de variación como desviación estándar residual relativa a la media.
coeficiente_variacion <- sqrt(cuadrado_medio_error) / media_general * 100 # Un CV menor indica menor variación residual relativa.
# Se imprime el coeficiente de variación con dos cifras decimales.
cat(sprintf("Coeficiente de variación (CV): %.2f%%\n", coeficiente_variacion)) # El CV ayuda a valorar la precisión experimental.
# Se aplica Tukey para identificar qué pares de medias difieren después del ANOVA.
print(TukeyHSD(modelo)) # Las comparaciones múltiples controlan el error familiar entre pares de secadores.
