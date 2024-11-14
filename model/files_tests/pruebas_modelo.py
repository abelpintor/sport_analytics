import numpy as np
import pandas as pd
import os
from functions_model import search_team_data
from functions_model import predict
from functions_model import premier_league


# Obtener la carpeta donde se encuentra el script actual
script_dir = os.path.dirname(os.path.abspath(__file__))


############################################################################################################################3
##########################################################################################################################333

#           PRUEBAS MODELO DE RED NEURONAL IMPLEMENTADO                   

############################################################################################################################3
##########################################################################################################################333






### PRUEBA 1: Compuerta XOR


p_x = np.array([
    [0,0],
    [0,1],
    [1,0],
    [1,1]
])

p_y = np.array([
    [0],
    [1],
    [1],
    [0]
])


### DESCOMENTA PARA EJECUTAR
# predict(
#     X=p_x,
#     y = p_y, 
#     x_test=p_x, y_test=p_y, 
#     hidden_layers=1,  # 2
#     neuronas_por_capa=2, # 5
#     learning_rate=0.4, # 0.4
#     epochs=3500,
#     plot=False
# )


### PRUEBA 2: Iris dataset

from sklearn.datasets import load_iris

iris = load_iris()
X = iris.data
Y = iris.target

# Filtramos las clases 0 y 1 directamente con un índice booleano
mask = (Y == 0) | (Y == 1)  # Crea una máscara booleana para las clases 0 y 1
p_x = X[mask]  # Filtra las características correspondientes
p_y = Y[mask]  # Filtra las etiquetas correspondientes

# Aseguramos que p_y tenga la forma correcta (n_samples, 1)
p_y = p_y.reshape(-1, 1)

p_x_train = p_x[:80]
p_y_train = p_y[:80]

p_x_test = p_x[80:]
p_y_test = p_y[80:]

### DESCOMENTAR PARA EJECUTAR
# predict(
#     X=p_x_train,
#     y = p_y_train, 
#     x_test=p_x_test, 
#     y_test=p_y_test, 
#     hidden_layers=1,
#     neuronas_por_capa=3,
#     learning_rate=0.1,
#     epochs=5000,
#     plot=False
# )







## NOMBRE DE LOS EQUIPOS DE LA PREMIER LEAGUE CON LOS QUE SE ENCUENTRA EN EL DATASET
equipos = {
    "ARSENAL",
    "ASTON VILLA",
    "BRENTFORD",
    "BRIGHTON",
    "BOURNEMOUTH",
    "CHELSEA",
    "CRYSTAL PALACE",
    "EVERTON",
    "FULHAM",
    "IPSWICH",
    "LEICESTER",
    "LIVERPOOL",
    "MAN CITY",
    "MAN UTD",
    "NEWCASTLE",
    "NOTT'M FOREST",
    "SOUTHAMPTON",
    "SPURS",
    "WOLVES",
    "WEST HAM",
}



### PRUEBA simple: en este caso se quiere poner a prueba el modelo con datos del partido
# entre el MAN CITY y el Brighton del sabado 9 de noviembre de 2024, este partido fue gando
# por el Brighton 2-1, por lo que el target es 0.
# Teniendo esto en cuenta se optó por entrenar al modelo del manchester city y pasar
# las estadisticas de esta derrota, con el fin de determinar si el modelo era capaz de predecir
# esta derrota con las estadisticas del partido.
# sin embargo, el modelo no fue capaz de predecir la derrota, le dió una una probabilidad de 0.53 
# de que el manchester city ganaria, aunque se pasaron las estadisticas que de cierta forma
# se le decia al modelo "el manchester city perdió este partido", el modelo no fue capaz de predecirlo
# una de las razones por las que pudo haber fallado es que el modelo se creo en base a los partidos
# del manchester city, uno de los equipos más fuertes de la premier league, además, el 
# historial entre city y brighton es muy favorable al city, con 31 encuntros 21 a favor del city 4 empates y 6 victorias del brighton
# por lo que, como muchos analistas deportivos asi como pronosticos de casas de apuestas, 
# el modelo se inclinó por el city.
caracteristicas_equipo, target_equipo = search_team_data("MAN CITY", premier_league)
test_data = np.array([
    2,    
    1,      # goles ==> 2
    35.5,
    64.5,   # posesión ==> 4
    4,
    4,    # tiros a puerta ==> 6
    12,                             
    18,    # tiros 8  ==> 8
    514,
    781,  # toques ==> 10
    334,
    600,  # pases ==> 12
    16,
    14,   # entradas ==> 14
    36,
    8,   # despejes    ==> 16
    3,
    10,    # corners ==> 18
    2,
    0,    # fueras de juego ==> 20
    2,
    1,    # tarjetas amarillas ==> 22
    0,
    0,    # tarjetas rojas  ==> 24
    11,
    6    # faltas concedidas   ==> 26

])

test_data = test_data.reshape(1, -1)
test_data_y = np.array([0]) # 0 si perdió o empató, 1 si ganó


# ### DESCOMENTAR PARA EJECUTAR
# ## invertir datos para dejar al city que fue de local como equipo local, SOLO POR CONSISTENCIA, PERO NO AFECTA EL RESULTADO
# for i in range(0,len(test_data[0]),2):
#     test_data[0][i], test_data[0][i+1] = test_data[0][i+1], test_data[0][i]
# predict(
#     X=caracteristicas_equipo,
#     y = target_equipo, 
#     x_test=test_data, y_test=test_data_y, 
#     hidden_layers=6,  # 3
#     neuronas_por_capa=5, # 4
#     learning_rate=0.3
# )


def test_model():

    data = pd.read_csv(script_dir + '/test_data.csv')
    x_data = data.iloc[:, 1:29].values


    # limpieza de datos
    test_data = x_data[:,2::]
    test_data = pd.DataFrame(np.array(test_data))
    test_data = test_data.apply(pd.to_numeric, errors='coerce')
    test_data = test_data.to_numpy()

    test_target = data.iloc[:, 29].values
    test_target = test_target.reshape(-1, 1)
    
    # entrenamiento de la red neuronal por cada equipo

    counter = 0
    for i in range(test_target.shape[0]):

        # se buscan los datos del equipo local y sobre ese equipo se entrena la red neuronal y se hace la predicción
        x_train, y_train = search_team_data(x_data[i][0], premier_league)

        p = predict(
            X=x_train,
            y = y_train,
            x_test = test_data[i].reshape(1, -1),
            y_test= test_target[i].reshape(-1, 1),
            epochs=1000,
            hidden_layers=6,
            neuronas_por_capa=5,
            learning_rate=0.3,
            plot=False
        )

        if p.round() == test_target[i]:
            counter += 1
            print('acertó')
        else:
            print('falló')

    print(f"Porcentaje de aciertos: {counter / test_target.shape[0] * 100}%")
    

## PRUEBA DE LA RED NEURONAL CON LOS DATOS DE LOS EQUIPOS DE LA PREMIER LEAGUE
# if __name__ == '__main__':
#     test_model()




