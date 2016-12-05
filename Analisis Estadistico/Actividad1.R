## -------------------------------------------------------------------------
## SCRIPT: Actividad1.r
## CURSO: Master en Big Data y Business Analytics
## ASIGNATURA: Analisis Estadistico
## ALUMNO: Jose Luis Gonzalez Blazquez
## FECHA: 05/12/2016
## -------------------------------------------------------------------------

## -------------------------------------------------------------------------
##       PARTE 1: 
##       ANALISIS DEL EFECTO DE LA SUPERFICIE DE LA VIVIENDA EN EL PRECIO
## -------------------------------------------------------------------------

## En este bloque se nos pide analizar cómo afecta la superficie de una vivienda
## sobre el precio final de venta de la misma.

## -------------------------------------------------------------------------

##### 1. Bloque de inicializacion de librerias y establecimiento de directorio #####

if (!require("MASS")){
  install.packages("MASS") 
  library(MASS)
}

if (!require("caTools")){
  install.packages("caTools") 
  library(caTools)
}

if (!require("glmnet")){
  install.packages("glmnet") 
  library(glmnet)
}

if (!require("ggm")){
  install.packages("ggm")
  library(ggm)
}

if(!require("igraph")){
  install.packages("igraph")
  library(igraph)
}

if (!require("ROCR")){
  install.packages("ROCR") 
  library(ROCR)
}

setwd("D:/Máster/Análisis Estadístico")

## -------------------------------------------------------------------------

##### 2. Bloque de carga de datos #####

viviendas=read.csv("Actividad1/house_train.csv")

## -------------------------------------------------------------------------

##### 3. Bloque de revision basica del dataset #####

str(viviendas)
head(viviendas)
summary(viviendas)

## -------------------------------------------------------------------------

##### 4. Explicación de los campos del dataset #####

# id: identificador de la vivienda
# date: fecha de la venta de la vivienda
# price: precio de la vivienda
# bedrooms: número de habitaciones
# bathrooms: número de baños
# sqft_living: superficie de la vivienda (en pies) 
# sqft_lot: superficie de la parcela (en pies)
# floors: número de plantas
# waterfront: indicador de estancia en primera línea al mar
# view: número de orientaciones de la vivienda
# condition: estado de la vivienda (mayor es mejor)
# grade: calidad de la construcción (mayor es mejor)
# sqft_basement: superficie de la planta baja (en pies)
# sqft_above: sqft_living - sqft_basement
# yr_built: año de construcción
# yr_renovated: año de reforma
# zipcode: codigo postal
# lat: latitud
# long: longitud
# sqft_living15: superficie media de las 15 viviendas más cercanas
# sqft_lot15: superficie media de la parcela de las 15 viviendas más cercanas

## -------------------------------------------------------------------------

##### 5. Bloque de analisis grafico del dataset #####

# Analizamos la distribución del precio de las viviendas
hist(viviendas$price)

# Los precios de las viviendas no parecen una normal. No obstante, al ser todos
# los valores del precio positivos, lo podemos aproximar a una distribución Log-Normal.
hist(log(viviendas$price))

# Vemos la relación que hay entre el precio y la superficie habitable en términos
# de elasticidad
plot(log(viviendas$price)~log(viviendas$sqft_living))
abline(rlm(log(viviendas$price)~log(viviendas$sqft_living)), col=2)

# Parece haber una relación casi lineal entre el precio y la superficie habitable.

## -------------------------------------------------------------------------

##### 6. Bloque de modelo de regresion lineal #####
## Estimación del precio en función a la superficie habitable

# Vemos la correlación entre el precio y la superficie de la vivienda
cor(viviendas$price, viviendas$sqft_living)

# Observamos que, tal y como suponíamos después del análisis gráfico, existe
# una fuerte relación entre el precio y la superficie de la vivienda.

# Modelo de regresión lineal
modelo1=lm(price~sqft_living, data=viviendas)
summary(modelo1)

# Con este modelo tenemos una variabilidad del error:
# Adjusted R-squared:  0.4941

## Analizamos los residuos
plot(modelo1$residuals)
smoothScatter(modelo1$residuals)
hist(modelo1$residuals)
qqnorm(modelo1$residuals); qqline(modelo1$residuals,col=2)
confint(modelo1, level=0.95)

# Vemos que los residuos se concentran alrededor del cero, por lo que el 
# comportamiento es bueno.
# Sin embargo, en los extremos no podemos explicar el comportamiento del precio 
# respecto a la superficie.

## -------------------------------------------------------------------------

##### 7. Bloque de modelo de regresiOn lineal #####
## Estimacion de elasticidad del precio con respecto a la superficie habitable

# Con esta transformación estimamos cuánto se mueve el precio en porcentaje
# cuando la superficie de la vivienda aumenta un 1%.
modelo2=lm(log(price)~log(sqft_living),data=viviendas)
summary(modelo2)

# Con este modelo tenemos una variabilidad del error:
# Adjusted R-squared:  0.4546

## Analizamos los residuos
plot(modelo2$residuals)
smoothScatter(modelo2$residuals)
hist(modelo2$residuals)
qqnorm(modelo2$residuals); qqline(modelo2$residuals,col=2)
confint(modelo2, level = 0.95)

# Los residuos siguen una distribución normal centrada casi en el cero.
# En los extremos sigue habiendo un comportamiento que no podemos explicar
# con la superficie. No obstante, se ajusta mejor que el anterior modelo.

## -------------------------------------------------------------------------

##### 8. Bloque de modelo de regresiOn lineal #####
## Estimacion de semielasticidad del precio con respecto a la superficie habitable

# Previamente, hemos transformado ambas variables. Ahora vamos a probar transformando
# una única variable.
# Con este modelo estimamos cuánto se mueve el precio en porcentaje con cada movimiento
# de la superficie de la vivienda.
modelo3=lm(log(price)~sqft_living,data=viviendas)
summary(modelo3)

# Con este modelo tenemos una variabilidad del error:
# Adjusted R-squared:  0.4828

## Analizamos los residuos
plot(modelo3$residuals)
smoothScatter(modelo3$residuals)
hist(modelo3$residuals)
qqnorm(modelo3$residuals); qqline(modelo3$residuals,col=2)
confint(modelo3, level = 0.95)

# Vemos que los residuos siguen de nuevo una distribución normal centrada 
# casi en el cero. Sin embargo, hay algunos valores outliers en la parte 
# negativa del histograma.
# En el qqplot vemos que en los extremos sigue habiendo un comportamiento
# del precio que no podemos explicar con la superficie. No obstante, parece que 
# los residuos se ajustan mejor a la normal que el anterior modelo.

## -------------------------------------------------------------------------

##### 8. Bloque de seleccion de estadístico robusto #####

# Vamos a utilizar un estadístico robusto para intentar suavizar los extremos.
# Para ello utilizamos la aplicación de semielasticidad que nos dio buen 
# resultado previamente.
modelo4=rlm(log(price)~sqft_living,data=viviendas)
summary(modelo4)

# Residual standard error: 0.4056 on 17382 degrees of freedom

## Analizamos los residuos
plot(modelo4$residuals)
smoothScatter(modelo4$residuals)
hist(modelo4$residuals)
qqnorm(modelo4$residuals); qqline(modelo4$residuals,col=2)

# Vemos que el comportamiento es prácticamente el mismo que con el estadístico
# simple.

## -------------------------------------------------------------------------

#### 9. Conclusión del análisis ####

##
# Vemos que el precio de la vivienda tiene una fuerte relación con la superficie 
# la misma. 
# En este sentido, con los modelos de regresión utilizados somos capaces de explicar
# la mayor parte del precio a partir de la superficie de la vivienda. No obstante, 
# hay algunos valores en los extremos que no siguen la distribución normal, por lo que 
# no seríamos capaces de explicarlos únicamente con el dato de la superficie de la
# vivienda.
#
# Si utilizamos el modelo de regresión lineal aplicando semielasticidad, podemos 
# concluir con un 95% de confianza que por cada unidad que aumenta la superficie de
# la vivienda, el precio se mueve entre un 0.03909856% y un 0.04032067%.
# Describiendo la siguiente relación:
#
#     log(price) = b0 + b1 * sqft_living
#
#         estando b0 entre 12.20601 y 12.23382
#         estando b1 entre 0.0003909856 y 0.0004032067
##

## -------------------------------------------------------------------------
##       PARTE 2: 
##       MODELO DE ESTIMACIÓN DEL PRECIO
## -------------------------------------------------------------------------

## -------------------------------------------------------------------------

##### 1. Preparamos datos de validacion #####

# Antes de nada, vamos a transformar la variable "date" a formato fecha para poder trabajar con ella
viviendas$date= as.Date(substr(viviendas$date, 0, 8), "%Y%m%d")

# A partir de los datos de entrenamiento, creamos un grupo para validar la efectividad
# de los modelos que vamos a probar antes de ejecutar el modelo seleccionado
# en el grupo de test.

sample = sample.split(viviendas$price, SplitRatio = 0.8)
viviendasTrain = subset(viviendas, sample == TRUE)
viviendasValidation = subset(viviendas, sample == FALSE)
viviendasTest = read.csv("Actividad1/house_test.csv")

viviendasTest$date= as.Date(substr(viviendasTest$date, 0, 8), "%Y%m%d")

## -------------------------------------------------------------------------

##### 2. Análisis de la relación del precio con el resto de variables #####

## Variables continuas
variables_continuas = c("price", "yr_renovated", "yr_built", "sqft_living", "sqft_lot", "sqft_above", "sqft_basement", "sqft_living15", "sqft_lot15")

# Analizamos la correlación del precio respecto al resto de variables continuas
viviendas_cor <- subset(x = viviendasTrain, select = variables_continuas)
cor(viviendas_cor)

# Observamos que las variables sqft_lot y sqft_lot15 casi no aportan información al precio.
# Así como el año de construcción de la vivienda.
# Además, las variables sqft_living y sqft_above están fuertemente correlacionadas. Esto es
# lógico puesto que sqft_living = sqft_above+sqft_basement. 
# Esto refleja una colinealidad entre estas variables.
# También tiene una fuerte relación sqft_living con sqft_living15. Es decir, la superficie de
# la vivienda está relacionada con la superficie de la vivienda de las casas más próximas.

## Variables categóricas

# Vemos que la variable "yr_renovated" tiene bastantes valores a 0. Para que sea más fácil
# trabajar con ella, vamos a crear una nueva variable categórica, que nos indique si una
# vivienda ha sido reformada o no.
viviendasTrain$is_renovated = viviendasTrain$yr_renovated>0
viviendasTrain$is_renovated = as.factor(viviendasTrain$is_renovated)

# Analizamos la relación de este tipo de variables con el precio
# Utilizando el boxplot podemos comparar el grado de solapamiento de las distribuciones.
# A más solapamiento, menos relación hay entre una variable y la otra.

boxplot(viviendasTrain$price~viviendasTrain$condition)
# Vemos que hay diferencias en los solapamientos entre las viviendas con condición 1 o 2 y el resto.

boxplot(viviendasTrain$price~viviendasTrain$view)
# La diferencia se encuentra entre las que no tienen vistas, las que tienen 1, 2 o 3 y
# un último grupo con las que tienen 4.

boxplot(viviendasTrain$price~viviendasTrain$waterfront)
# Hay bastante diferencia entre estar en primera línea de mar y no estarlo.

boxplot(viviendasTrain$price~viviendasTrain$bathrooms)
# Hay muchos valores para el número de baños, lo cual distorsiona el gráfico.
# No obstante, sí que se aprecia, en general, que cuantos más baños tiene la casa su precio es mayor.

boxplot(viviendasTrain$price~viviendasTrain$bedrooms)
# Parece que se observa una relación que a más habitaciones mayor es el precio de la casa.

boxplot(viviendasTrain$price~viviendasTrain$floors)
# Parece que el número de plantas no afecta en exceso, habiendo muchos outliers.

boxplot(viviendasTrain$price~viviendasTrain$grade)
# Parece que hay bastante relación entre el estado en el que se ha reformado la vivienda
# y el precio que tiene.

boxplot(viviendasTrain$price~viviendasTrain$is_renovated)
# Aunque las casas que han sido renovadas parece que se venden algo más caras, hay bastante
# superficie superpuesta entre ambas opciones.

## Variables temporales

# Fecha de venta
#plot(aggregate(viviendasTrain$price~viviendasTrain$date, list(viviendasTrain$date), median), type="l")

## -------------------------------------------------------------------------

##### 3. Bloque de modelo lineal con todas las variables seleccionadas #####

modelo0=lm(log(price)~.,data=viviendasTrain)
summary(modelo0)

# El ajuste de este modelo es:
# Adjusted R-squared:  0.7793

plot(modelo0$residuals)
smoothScatter(modelo0$residuals)
hist(modelo0$residuals)
qqnorm(modelo0$residuals); qqline(modelo0$residuals,col=2)

# Vemos que, aunque se ajusta bien, los extremos de los residuos se alejan bastante de
# la normal, por lo que no podemos explicarlos correctamente.

## -------------------------------------------------------------------------

##### 4. Bloque de formateo de variables #####

# Nos quedamos con las variables que aportan información al precio
variables_keep = c("price", "date", "sqft_living", "condition", "view", "waterfront", "bathrooms", "bedrooms", "grade", "zipcode", "sqft_living15")
viviendasTrain_model <- viviendasTrain[,variables_keep]

# Formateamos las variables
# Las que consideramos en el análisis gráfico que tenían más relación con el precio 
# son las siguientes, que convertimos en factores:
viviendasTrain_model$waterfront = as.factor(viviendasTrain_model$waterfront)
viviendasTrain_model$grade = as.factor(viviendasTrain_model$grade)

# Además, vamos a tener en cuenta la fecha de venta:
viviendasTrain_model$date = as.factor(format(viviendasTrain_model$date,'%Y%m')) # Considero el año y el mes en que se ha vendido la vivienda

# Volvemos a hacer una revision basica del dataset
str(viviendasTrain_model)
head(viviendasTrain_model)
summary(viviendasTrain_model)

## -------------------------------------------------------------------------

##### 5. Bloque de modelo lineal #####

## Primer modelo

# Nos quedamos con las variables que más aportan al modelo
modelo5=lm(log(price)~sqft_living+view+waterfront+grade+date+zipcode,data=viviendasTrain_model)
summary(modelo5)

# Adjusted R-squared:  0.598

plot(modelo5$residuals)
smoothScatter(modelo5$residuals)
hist(modelo5$residuals)
qqnorm(modelo5$residuals); qqline(modelo5$residuals,col=2)

# Vemos que este modelo se ajusta casi perfectamente a la curva del qqplot.

## Segundo modelo

# Consideramos el resto de variables como factores
viviendasTrain_model$condition = as.factor(viviendasTrain_model$condition)
viviendasTrain_model$view = as.factor(viviendasTrain_model$view)
viviendasTrain_model$bathrooms = as.factor(viviendasTrain_model$bathrooms)
viviendasTrain_model$bedrooms = as.factor(viviendasTrain_model$bedrooms)
viviendasTrain_model$zipcode = as.factor(viviendasTrain_model$zipcode)

#Modelo
modelo6=lm(log(price)~sqft_living+view+waterfront+grade+date+zipcode,data=viviendasTrain_model)
summary(modelo6)

# Adjusted R-squared:  0.8693

plot(modelo6$residuals)
smoothScatter(modelo6$residuals)
hist(modelo6$residuals)
qqnorm(modelo6$residuals); qqline(modelo6$residuals,col=2)

## -------------------------------------------------------------------------

##### 6. Bloque de evaluacion de los modelos #####

AIC(modelo0)
AIC(modelo5)
AIC(modelo6)

# Vemos que el modelo con menos AIC es el modelo6.
# No obstante, es el modelo donde los residuos se comportan peor, puesto que los extremos
# no siguen el qqnorm.

## -------------------------------------------------------------------------

##### 7. Validación del modelo #####

## Tenemos que hacer las mismas transformaciones a los datos de validación
viviendasValidation$waterfront = as.factor(viviendasValidation$waterfront)
viviendasValidation$grade = as.factor(viviendasValidation$grade)
viviendasValidation$date = as.factor(format(viviendasValidation$date,'%Y%m')) # Considero el año y el mes en que se ha vendido la vivienda
viviendasValidation$view = as.factor(viviendasValidation$view)
viviendasValidation$zipcode = as.factor(viviendasValidation$zipcode)

viviendasTrain$prediction=predict(modelo6,type="response")
R2_TRAIN=1-sum((viviendasTrain$price-viviendasTrain$prediction)^2)/sum((viviendasTrain$price-mean(viviendasTrain$price))^2)

viviendasValidation$prediction=predict(modelo6,newdata=viviendasValidation,type="response")
R2_TEST=1-sum((viviendasValidation$price-viviendasValidation$prediction)^2)/sum((viviendasValidation$price-mean(viviendasValidation$price))^2)

R2_TRAIN
R2_TEST

# Los errores son parecidos.

## -------------------------------------------------------------------------

##### 8. Aplicación del modelo seleccionado #####

# Realizamos las transformaciones necesarias
viviendasTest$waterfront = as.factor(viviendasTest$waterfront)
viviendasTest$grade = as.factor(viviendasTest$grade)
viviendasTest$date = as.factor(format(viviendasTest$date,'%Y%m'))
viviendasTest$view = as.factor(viviendasTest$view)
viviendasTest$zipcode = as.factor(viviendasTest$zipcode)

# Aplicamos el modelo que hemos seleccionado previamente
viviendasTest$prediction=predict(modelo6,newdata=viviendasTest,type="response")

# Al haber utilizado la transformación de semielasticidad, tenemos que convertir el precio a valores
# normales.
viviendasTest$prediction = exp(viviendasTest$prediction)

# Observamos los valores del dataset final
str(viviendasTest)
head(viviendasTest)
summary(viviendasTest)

hist(viviendasTest$prediction)
