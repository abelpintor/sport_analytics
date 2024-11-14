from functions_model import search_team_data
from functions_model import predict
from functions_model import premier_league
import numpy as np
import pandas as pd
import os
from functions_api import get_data_team_for_matches

# Obtener la carpeta donde se encuentra el script actual
script_dir = os.path.dirname(os.path.abspath(__file__))
# Construir las rutas relativas
data_2021 = pd.read_csv(os.path.join(script_dir, 'datos_api_full/', '2021-22', 'matches.csv'))
data_2022 = pd.read_csv(os.path.join(script_dir, 'datos_api_full/', '2022-23', 'matches.csv'))
data_2023 = pd.read_csv(os.path.join(script_dir, 'datos_api_full/', '2023-24', 'matches.csv'))
data_2024 = pd.read_csv(os.path.join(script_dir, 'datos_api_full/', '2024-25', 'matches.csv'))

data_21 = data_2021.iloc[:, 1:30].values

data_22 = data_2022.iloc[:, 1:30].values

data_23 = data_2023.iloc[:, 1:30].values

data_24 = data_2024.iloc[:, 1:30].values

# concatenar los datos de las temporadas para tener un solo dataset y poder buscar los datos de los equipos

## NOTA: A diferencia del archivo final.py, en este caso data_2024 (y data_24) contienen 110 registros
## y no solo los 70 que se usan en final.py para realizar el modelo y hacer pruebas con los 35 partidos de test
## aqui se usan 110 regsitros (hasta la jornada 110 que es la ultima jugada hasta el dia de hoy 11/11/2024)
## para tener un dataset mas completo y crear un mejor modelo, ya que este archivo proveerá de resultados a la API
premier_league = np.concatenate((data_21, data_22, data_23, data_24), axis=0)


last_three_seasons = np.concatenate((data_21, data_22, data_23), axis=0)


## agregar al documento sobre la estrategia para generar los datos para las predicciones, PROMEDIO PONDERADO
## , el promedio ponderado es una técnica que se utiliza para calcular el promedio de un conjunto de datos en el que
## cada uno de los datos tiene un peso diferente. El promedio ponderado se calcula multiplicando cada uno de los
## datos por su peso y sumando los resultados de la multiplicación. Luego, se divide la suma de los productos por la
## suma de los pesos. El promedio ponderado es útil cuando se desea dar más importancia a algunos datos que a otros
## en un conjunto de datos. Por ejemplo, si se desea calcular el promedio de las calificaciones de un estudiante en
## un curso, se puede utilizar un promedio ponderado si se desea dar más importancia a las calificaciones de los
## exámenes que a las calificaciones de las tareas. En este caso, se puede asignar un peso mayor a las calificaciones
## de los exámenes que a las calificaciones de las tareas. El promedio ponderado se calcula de la siguiente manera:
## Promedio ponderado = (D1 * W1 + D2 * W2 + ... + Dn * Wn) / (W1 + W2 + ... + Wn)
## Donde D1, D2, ..., Dn son los datos y W1, W2, ..., Wn son los pesos de los datos
##

def result_match(team1:str, team2:str) -> np.ndarray:

    # obtiene los datos de entrenamiento de como le ha ido al equipo a predecir
    x_train, y_train = search_team_data(team1, premier_league)

    w1 = 0.5
    w2 = 0.25
    w3 = 0.25

    stats_currently_season, currently_season_target = search_team_data(team1, data_24)
    stats_three_last_seasons, three_last_seasons_target = search_team_data(team1, last_three_seasons)
    stats_matches_between_teams, metches_between_target = get_data_team_for_matches(team1, team2, premier_league)

    curr_season = (np.mean(stats_currently_season, axis=0) * w1).reshape(1, -1)
    last_three = (np.mean(stats_three_last_seasons, axis=0) * w2).reshape(1, -1)
    matches_between = (np.mean(stats_matches_between_teams, axis=0) * w3).reshape(1, -1)


    curr_season_target_avg = np.mean(currently_season_target)
    last_three_seasons_target_avg = np.mean(three_last_seasons_target)
    matches_between_target_avg = np.mean(metches_between_target)

    # por ejemplo, el city con 8 partidos ganados de 11, es un porcentaje de 0.72 (que redondearia de cierta manera a 1)
    # ahora bien, al multiplicarlo por .5 se pone en escala de 0.5, osea: multiplicar 0.72 * 0.5 = 0.36
    # se ve bajo ese 0.36 pero si hacemos la division de 0.36 / 0.5 = 0.72, que es el porcentaje real, solo "cambio de escala"
    curr_season_target_avg_mult = curr_season_target_avg * w1 
    last_three_seasons_target_avg_mult = last_three_seasons_target_avg * w2 # este se pone a escala de 0.25
    matches_between_target_avg_mult = matches_between_target_avg * w3 # este se pone a escala de 0.25



    # print(curr_season_target_avg_mult)
    # print(last_three_seasons_target_avg_mult)
    # print(matches_between_target_avg_mult)

    x_predict = (curr_season + last_three + matches_between) / (w1 + w2 + w3)
    y_predict = (((curr_season_target_avg_mult + last_three_seasons_target_avg_mult + matches_between_target_avg_mult) / (w1 + w2 + w3)).round()).reshape(-1, 1)

    
    p =predict(
        X=x_train,
        y = y_train,
        x_test = x_predict, 
        y_test= y_predict, 
        epochs=1000,
        hidden_layers=6,
        neuronas_por_capa=5,
        learning_rate=0.3,
        plot=False
    )
    
    print(p.round())

    return (p, x_predict)


# result_match('LIVERPOOL', 'SOUTHAMPTON') ## 0.6896   -
# result_match('SOUTHAMPTON', 'LIVERPOOL') ##  0.2758     |_> sumados dan 0.9654


# result_match('MAN CITY', 'SOUTHAMPTON')  ## 0.512886
# result_match('SOUTHAMPTON', 'MAN CITY')  ## 0.2758     |_> sumados dan 0.788686   | que representa el restante 0.211314 ???

# result_match('MAN CITY', 'LIVERPOOL')  ## 0.512886
# result_match('LIVERPOOL', 'MAN CITY')  ## 0.6896      |_> sumados dan 1.202486   | que representa el exceso 0.202486 ???
#               -> posible solucion, normalizar los valores de los pesos para que sumen 1
#               esto se hace dividiendo cada probabilidad por la suma de las probabilidades
#               de los dos equipos, de esta manera se tiene una probabilidad que suma 1
#               
#               -> otra solucion, distribuir el exceso para que sea tomado como empate, por ejemplo, sabiendo que la suma da 1.202486
#               ese resto (0.202486) se puede distribuir en partes iguales para que sea tomado como empate, es decir, 0.101243 para cada equipo
#               se tendria que restar ese 0.101243 a cada equipo, y el empate es de 0.202486
#               ahora bien, la suma es (0.512886 - 0.101243) + (0.6896 - 0.101243) + 0.202486 = 0.411 + 0.588 + 0.202 = 1.201
#               esto dá la suma original, ahora solo habria que normalizar cada procentaje dividiendolo por esa suma
#               osea 0.411 / 1.201 = 0.342, 0.588 / 1.201 = 0.489, 0.202 / 1.201 = 0.168
#               ahora la suma de esos valores es 1, y cada uno representa la probabilidad de cada equipo y el empate
#           CITY LIVERPOOL  EMPATE
#           0.342  0.489    0.168


result_match('ARSENAL', 'SPURS')
result_match('SPURS', 'ARSENAL')
