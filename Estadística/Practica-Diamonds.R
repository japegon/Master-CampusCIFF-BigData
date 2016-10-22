# Hacer uso del dataset "diamonds" que contendrá¡ el precio (entre otras variables interesantes) de unos 54.000 diamantes.
#
# Objetivo : realizar distintos tipos de análisis estadístico de sus variables para intentar
# averiguar algún tipo de comportamiento oculto aparentemente en los datos. 
#
# Para ello os marco los siguientes pasos: tipos de variables, medidas de posición central, medidas de dispersión, 
# distribución y relación entre ellas, más análisis de regresión
#
# Los diferentes indicadores presentes en el dataset "diamonds" son los siguientes:
# price: Precio en dolares americanos
# carat: peso del diamante
# cut: calidad del corte (Fair, Good, Very Good, Premium, Ideal)
# colour: color del diamante (desde D el mejor hasta J el peor)
# clarity: mide como de claro es el diamante (desde el peor I1, SI2, SI1, VS2, VS1, VVS2, VVS1, hasta el mejor IF)
# x: longitud en mm 
# y: ancho en  mm 
# z: profundidad en mm 
# depth: porcentaje total de profundidad 
# table: anchura de la parte superior de diamante con relaci?n al punto m?s ancho 

library(ggplot2)
library(sampling)
library(e1071)
library(moments)
library(prettyR)
library(plyr)
library(nortest)
library(corrplot)
library(car)
library(QuantPsyc)
library(parcor)

### 1. Muestra representativa
# Selecciona una muestra representativa para "cut"
dt<-as.data.frame(diamonds)

head(dt)
attach(dt)

# Realizamos un muestreo aleatorio con la función sample.split
set.seed(1000)
train =  sample.split(diamonds$cut, SplitRatio = 0.75)
test = sample.split(diamonds$cut, SplitRatio = 0.25)

### 2. An?lisis de las variables
# An?lisis descriptivo de las variables: Tipo de variable, distribuci?n y representaci?n
str(diamonds)

#Classes ‘tbl_df’, ‘tbl’ and 'data.frame':	53940 obs. of  10 variables:
# $ carat  : num  0.23 0.21 0.23 0.29 0.31 0.24 0.24 0.26 0.22 0.23 ...
# $ cut    : Ord.factor w/ 5 levels "Fair"<"Good"<..: 5 4 2 4 2 3 3 3 1 3 ...
# $ color  : Ord.factor w/ 7 levels "D"<"E"<"F"<"G"<..: 2 2 2 6 7 7 6 5 2 5 ...
# $ clarity: Ord.factor w/ 8 levels "I1"<"SI2"<"SI1"<..: 2 3 5 4 2 6 7 3 4 5 ...
# $ depth  : num  61.5 59.8 56.9 62.4 63.3 62.8 62.3 61.9 65.1 59.4 ...
# $ table  : num  55 61 65 58 58 57 57 55 61 61 ...
# $ price  : int  326 326 327 334 335 336 336 337 337 338 ...
# $ x      : num  3.95 3.89 4.05 4.2 4.34 3.94 3.95 4.07 3.87 4 ...
# $ y      : num  3.98 3.84 4.07 4.23 4.35 3.96 3.98 4.11 3.78 4.05 ...
# $ z      : num  2.43 2.31 2.31 2.63 2.75 2.48 2.47 2.53 2.49 2.39 ...

# carat - Variable numérica
summary(dt$carat)
# En el histograma se ve que hay mayor frecuencia al principio y ésta va decreciendo.
hist(dt$carat)
# En el boxplot se observan muchos outliers por encima de 2.
boxplot(dt$carat)

# cut - Variable categórica
summary(dt$cut)
# En el barplot vemos que la mayoría de valores son de corte 'Ideal'
barplot(table(dt$cut))

# color - Variable categórica
summary(dt$color)
# En el barplot vemos que los colores están bastante repartidos. El que menos tiene es el 'J'
barplot(table(dt$color))

# clarity - Variable categórica
summary(dt$clarity)
# En el barplot vemos que los valores están centrados en 'SI1'
barplot(table(dt$clarity))

# depth - Variable numérica
summary(dt$depth)
# El histograma se aproxima a una normal
hist(dt$depth) 
# En el boxplot se ven bastantes outliers tanto por encima como por debajo
boxplot(dt$depth)

# table - Variable numérica
summary(dt$table)
# El histograma vemos que se aproxima a una normal
hist(dt$table)
# En el boxplot hay bastantes outliers tanto por encima como por debajo
boxplot(dt$table)

# price - Variable numérica
summary(dt$price)
# En el histograma vemos que la frecuencia va decreciendo conforme aumenta el precio.
hist(dt$price)
# En el boxplot vemos que hay muchos outliers por encima de 12.500€
boxplot(dt$price) 

# x - Variable numérica
summary(dt$x)
hist(dt$x) 
# En el boxplot vemos que existen outliers en 0 y algunos outliers por encima
boxplot(dt$x)

# y - Variable numérica
summary(dt$y)
hist(dt$y)
# En el boxplot vemos que existen outliers en 0 y algunos outliers por encima.
boxplot(dt$y)

# z - Variable numérica
summary(dt$z)
hist(dt$z)
# En el boxplot vemos que existen outliers en 0 y algunos outliers por encima.
boxplot(dt$z)


### 3. Detecci?n de casos at?picos y su tratamiento
# Como hemos visto anteriormente, las variables poseen valores atípicos. 
# Calculamos el umbral por el que filtrar las variables. 
minOutlier <- function(data){
  q1 <- quantile(data, 0.25)
  q3 <- quantile(data, 0.75)
  iqr <- q3 - q1
  inferior <- q1 - (iqr * 1.5)
}

maxOutlier <- function(data){
  q1 <- quantile(data, 0.25)
  q3 <- quantile(data, 0.75)
  iqr <- q3 - q1
  superior <- (iqr * 1.5) + q3
}

dt_outliers <- diamonds

# price
dt_outliers<-dt_outliers[dt_outliers$price<maxOutlier(diamonds$price),]
dt_outliers <-dt_outliers[dt_outliers$price>minOutlier(diamonds$price),]
# carat
dt_outliers<-dt_outliers[dt_outliers$carat<maxOutlier(diamonds$carat),]
dt_outliers <-dt_outliers[dt_outliers$carat>minOutlier(diamonds$carat),]
# depth
dt_outliers<-dt_outliers[dt_outliers$depth<maxOutlier(diamonds$depth),]
dt_outliers <-dt_outliers[dt_outliers$depth>minOutlier(diamonds$depth),]
# table
dt_outliers<-dt_outliers[dt_outliers$table<maxOutlier(diamonds$table),]
dt_outliers <-dt_outliers[dt_outliers$table>minOutlier(diamonds$table),]
# x
dt_outliers<-dt_outliers[dt_outliers$x<maxOutlier(diamonds$x),]
dt_outliers <-dt_outliers[dt_outliers$x>minOutlier(diamonds$x),]
# y
dt_outliers<-dt_outliers[dt_outliers$y<maxOutlier(diamonds$y),]
dt_outliers <-dt_outliers[dt_outliers$y>minOutlier(diamonds$y),]
# z
dt_outliers<-dt_outliers[dt_outliers$z<maxOutlier(diamonds$z),]
dt_outliers <-dt_outliers[dt_outliers$z>minOutlier(diamonds$z),]

summary(dt_outliers)

# Número de outliers eliminados:
nrow(dt)-nrow(dt_outliers)

### 4. Inferencia
# Calcula un intervalo de confianza para la media de "carat" y "depth"
# La funcion t.test nos devuelve intervalo de confianza
t.test(dt_outliers$carat)

#One Sample t-test
#data:  dt_outliers$carat
#t = 417.45, df = 47482, p-value < 2.2e-16
#alternative hypothesis: true mean is not equal to 0
#95 percent confidence interval:
#  0.7042840 0.7109286
#sample estimates:
#  mean of x 
#0.7076063 

t.test(dt_outliers$depth)

#One Sample t-test
#data:  dt_outliers$depth
#t = 12179, df = 47482, p-value < 2.2e-16
#alternative hypothesis: true mean is not equal to 0
#95 percent confidence interval:
#  61.77633 61.79621
#sample estimates:
#  mean of x 
#61.78627 

# Formula un test de hip?tesis
# H0: la media de precios de 2 cortes (Very Good y Good) son iguales.
# H1: La media de precios de corte Very Good y Good es distinta
tapply(dt_outliers$price, dt_outliers$cut,mean)

#Fair      Good Very Good   Premium     Ideal 
#3677.809  3199.733  3216.381  3474.776  2794.897 

precioGood<-dt_outliers$price[dt_outliers$cut=="Good"]
precioVeryGood<-dt_outliers$price[dt_outliers$cut=="Very Good"]

# Con t.test hacemos contraste entre las 2 medias.
t.test(precioGood, precioVeryGood,  alternative='two.sided')

#Welch Two Sample t-test
#data:  precioGood and precioVeryGood
#t = -0.3381, df = 6835.1, p-value = 0.7353
#alternative hypothesis: true difference in means is not equal to 0
#95 percent confidence interval:
#  -113.1722   79.8766
#sample estimates:
#  mean of x mean of y 
#3199.733  3216.381 

# Siendo el p-value=0.7353, un valor pequeño, rechaza la hipótesis nula de que las medias de los precios son iguales.
# Aceptamos la hipótesis alternativa.

### 5. Relaciones entre las variables
# Muestra las relaciones que existen entre variables 
# (dependencia, anova, correlaci?n)

# Pasamos las variables categóricas a numéricas para poder hacer la correlación
dt_cat<-dt_outliers
dt_cat[,2]<-sapply(dt_cat[,2],switch,"Fair"=1,"Good"=2,"Very Good"=3,"Premium"=4,"Ideal"=5)
dt_cat[,3]<-sapply(dt_cat[,3],switch,"J"=1,"I"=2,"H"=3,"G"=4,"'F'"=5,"E"=6,"D"=7)
dt_cat[,4]<-sapply(dt_cat[,4],switch,"IF"=1,"VVS1"=2,"VVS2"=3,"VS1"=4,"VS2"=5,"SI1"=6,"SI2"=7,"I1"=8)

# Vemos la correlación que hay entre cada una de las variables
cor(dt_cat)

# Según vemos, hay una fuerte correlacion entre las variables
# (carat,price), (carat, x), (carat,y), (carat,z), (price, x), (price, y), (price,z), (x, y), (x,z), (y,z)

# Con ANOVA hacemos un análisis de la varianza, por el que vemos si el precio depende del color.
anov_a<-aov(dt_cat$price~dt_cat$cut)
summary(anov_a)

# Según el análisis de la varianza, existen diferencias significativas entre las medias de cada categoría.


# 6. An?lisis de regresi?n
# Formular un modelo de regresi?n y analiza los resultados
# Muestra los residuos y analiza los resultados

# Vamos a estimar el precio del diamante en funcion del resto de las variables

# Empezamos por la variable carat que hemos visto que tiene mayor correlacion: 0.922784405
attach(dt_cat)
model0 <- lm(price~carat, data=dt_cat)
summary(model0)
# Multiple R-squared:  0.8515,	Adjusted R-squared:  0.8515 
# F-statistic: 2.723e+05 on 1 and 47481 DF,  p-value: < 2.2e-16
summary(model0)$r.squared
summary(model0)$adj.r.squared
summary(model0)$coeff

# Nos fijamos en el R-squared ajustado al ser una regresión lineal.

# El 85% de los datos se ajustan al modelo, aunque el p-value es muy bajo por lo que rechazaríamos
# la hipótesis nula de que los coeficientes son iguales a cero.

# Incluimos la variable clarity (la siguiente con mayor correlación)
model1 <- lm(price~carat+clarity, data=dt_cat)
summary(model1)
# Multiple R-squared:  0.8915,	Adjusted R-squared:  0.8915 
# F-statistic: 1.95e+05 on 2 and 47480 DF,  p-value: < 2.2e-16
summary(model1)$r.squared
summary(model1)$adj.r.squared
summary(model1)$coeff

# El 89% de los datos se ajustan al modelo, aunque el p-value es muy bajo por lo que rechazaríamos
# la hipótesis nula de que los coeficientes son iguales a cero.

# Incluimos la variable color
model2 <- lm(price~carat+clarity+color, data=dt_cat)
summary(model2)
# Multiple R-squared:   0.91,	Adjusted R-squared:  0.9099 
# F-statistic: 1.599e+05 on 3 and 47479 DF,  p-value: < 2.2e-16
summary(model2)$r.squared
summary(model2)$adj.r.squared
summary(model2)$coeff

# Cerca del 91% de los datos se ajustan al modelo, aunque el p-value es muy bajo por lo que rechazaríamos
# la hipótesis nula de que los coeficientes son iguales a cero.

# Incluimos la variable x
model3 <- lm(price~carat+clarity+color+x, data=dt_cat)
summary(model3)
# Multiple R-squared:  0.9131,	Adjusted R-squared:  0.9131 
# F-statistic: 1.247e+05 on 4 and 47478 DF,  p-value: < 2.2e-16
summary(model3)$r.squared
summary(model3)$adj.r.squared
summary(model3)$coeff

# No cambia mucho respecto a la anterior variable

# Incluimos la variable cut
model4 <- lm(price~carat+clarity+color+x+cut, data=dt_cat)
summary(model4)
# Multiple R-squared:  0.9142,	Adjusted R-squared:  0.9142 
# F-statistic: 1.012e+05 on 5 and 47477 DF,  p-value: < 2.2e-16
summary(model4)$r.squared
summary(model4)$adj.r.squared
summary(model4)$coeff

# Tampoco varía demasiado respecto a las 2 anteriores variables. Sigue en un 91% de datos que se ajustan al modelo.

# Incluimos la variable depth
model5 <- lm(price~carat+clarity+color+x+cut+depth, data=dt_cat)
summary(model5)
# Multiple R-squared:  0.9145,	Adjusted R-squared:  0.9145 
# F-statistic: 8.467e+04 on 6 and 47476 DF,  p-value: < 2.2e-16
summary(model5)$r.squared
summary(model5)$adj.r.squared
summary(model5)$coeff

# Las variables x, cut y depth parece que no aportan demasiado al modelo.
# Con las anteriores variables conseguimos una fiabilidad del 91%.
# Por lo tanto nos quedamos con el model2.

plot(resid(model3))
abline(0,0,col="red")

# Vemos en la gráfica que el modelo no se ajusta a una distribución normal ya que, sobre el índice 2100, los valores
# se separan de la línea marcada y hay bastante varianza.


# Aplica una transformaci?n a la regresi?n y analiza los resultados
# Interpreta los coeficientes estandarizados de la regresi?n

# Aplicamos una transformación logarítmica a las variables
caratLog <- log(dt_cat$carat)
priceLog <- log(dt_cat$price)
clarityLog <- log(dt_cat$clarity)
colorLog <- log(dt_cat$color)

# Repetimos el modelo
modelLog<-lm(priceLog~caratLog+clarityLog+colorLog)
summary(modelLog)
# Multiple R-squared:  0.9743,	Adjusted R-squared:  0.9743 
# F-statistic: 6.001e+05 on 3 and 47479 DF,  p-value: < 2.2e-16

# Vemos que el modelo transformado se ajusta en un 97% de los datos, lo que mejora el anterior modelo.
# El p-value es pequeño por lo que se rechaza la hipótesis nula.

plot(resid(modelLog))
abline(0,0,col="red")

# Además, vemos que los valores residuales siguen la línea marcada y podemos suponer que su media es 0.
