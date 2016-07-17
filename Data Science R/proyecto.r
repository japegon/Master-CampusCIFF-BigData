# Cargar los datos
# Eliminar los missing values, que están codificados como -9999.00
diabetes <- read.delim("/media/japegon/Datos/Máster/Data Analysis R/diabetes.data",header=TRUE, sep="\t", na.strings = "-9999.0")
diabetes_data <- na.omit(diabetes)

# Ver el tipo de cada una de las variables
sapply(diabetes_data, class)

# Realizar un análisis estadístico de las variables: calcular la media, varianza, rangos, etc. 
summary(diabetes_data)

# ¿Tienen las distintas variables rangos muy diferentes?
sapply(diabetes_data[3:11], range)

# Hacer un gráfico de cajas (boxplot) donde se pueda ver la información anterior de forma gráfica.
library(ggplot2)
boxplot(diabetes_data[3:11])

# Calcular la media para las filas que tienen SEX=M y la media para las filas que tienen SEX=F, utilizando la función tapply
for (i in colnames(diabetes_data[3:11])){
  print(i)
  print(tapply(diabetes_data[[i]], diabetes_data$SEX, mean))
}

# Calcular la correlación de todas las variables numéricas con la variable Y
correlaciones = cor(diabetes_data[3:10], diabetes_data$Y)

# Realizar un gráfico de dispersión para las variables que tienen más y menos correlación con Y y comentar los resultados.
# Mayor correlación: BMI
p = ggplot(diabetes_data,aes(diabetes_data$BMI, diabetes_data$Y))
p + geom_point()

# Menor correlación: S2 (en valor absoluto)
p = ggplot(diabetes_data,aes(diabetes_data$S2, diabetes_data$Y))
p + geom_point()

# ¿Cómo sería el gráfico de dispersión entre dos cosas con correlación 1?
p = ggplot(diabetes_data,aes(diabetes_data$Y, diabetes_data$Y))
p + geom_point()

# Transformar la variable SEX, que es un factor, en una variable numérica utilizando, por ejemplo, la codificación M=1 y F=2
diabetes_data$SEX <- as.numeric(diabetes_data$SEX)

# Como me ha salido M=2 y F=1 lo recodifico
#install.packages("car")
library(car)
diabetes_data$SEX<-recode(diabetes_data$SEX,"2=1;1=2")

# Definimos los outliers como los elementos (filas) de los datos para los que cualquiera de las variables está por encima o por
# debajo de la mediana más/menos 3 veces el MAD (Median Absolute Deviation). Identificar estos outliers y quitarlos.
limit_outliers_max <- (sapply(diabetes_data[3:11], median) + 3*sapply(diabetes_data[3:11], mad))
limit_outliers_min <- (sapply(diabetes_data[3:11], median) - 3*sapply(diabetes_data[3:11], mad))
bool_matrix = ((diabetes_data[3:11]>limit_outliers_max) | (diabetes_data[3:11]<limit_outliers_min))
bool_vect = bool_matrix[,1]&bool_matrix[,2]&bool_matrix[,3]&bool_matrix[,4]&bool_matrix[,5]&bool_matrix[,6]&bool_matrix[,7]&bool_matrix[8]&bool_matrix[,9]
diabetes_no_outliers = diabetes_data[bool_vect]

# Todas las filas tienen algún elemento que está fuera del rango definido. Por lo que todos los elementos son outliers.

# Separar el conjunto de datos en dos, el primero (entrenamiento) conteniendo el 70% de los datos y el segundo (test) un 30%
# de forma aleatoria
pos_train<-sample(c(1:nrow(diabetes_data)), floor(nrow(diabetes_data)*(70/100)))
train<-diabetes_data[pos_train,]
test<-diabetes_data[-pos_train,]

# Escalar los datos para que tengan media 0 y varianza 1, es decir, restar a cada variable numérica su media y dividir por la
# desviación típica. Calcular la media y desviación en el conjunto train, y utilizar esa misma media y desviación para escalar 
# el conjunto de test.
train_mean<-sapply(train,mean)
train_desv<-sapply(train,sd)
test_escalado = (test - train_mean)/train_desv

# Realizar un modelo de regresión lineal de la variable de respuesta sobre el resto y ajustarlo por mínimos cuadrados usando
# únicamente los datos del conjunto de entrenamiento.
lin_reg <- lm(Y~AGE+SEX+BMI+BP+S1+S2+S3+S4+S5+S6, data=train)

# Calcular el error cuadrático medio de los datos del conjunto de entrenamiento y de los datos del conjunto de test:
train_Y <- predict(lin_reg)
err_train <- (sum((train$Y-train_Y)^2))/nrow(train)

test_Y <- predict(lin_reg, test)
err_test <- (sum((test$Y-test_Y)^2))/nrow(test)
