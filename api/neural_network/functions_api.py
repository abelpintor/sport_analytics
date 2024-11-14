import pandas as pd
import numpy as np
import os



def get_data_team_for_matches(team, team2, data_season):
    d = []
    target = []
    for i in range(data_season.shape[0]):

        # este if comparara si los equpos que se pasan como parámetros son los que están jugando en el partido
        if ((data_season[i][0] == team or data_season[i][1] == team ) and (data_season[i][0] == team2 or data_season[i][1] == team2)):
            

            renglon = data_season[i][2:len(data_season[i])-1].copy()
            
            # descartamos los nombres de los equipos
            # d.append(renglon)
            value = data_season[i][len(data_season[i])-1]

            # si el equipo es visitante, invertimos el valor
            if data_season[i][1] == team:
                
                if value == 0:
                    value = 1
                elif value == 1:
                    value = 0
                target.append(value)

                new_renglon = []

                for j in range(0,len(renglon),2):
                    new_renglon.append(renglon[j+1])
                    new_renglon.append(renglon[j])

                d.append(new_renglon)
            else:
                d.append(renglon)
                target.append(value)     

    # para convertir todos los elementos a números
    d = pd.DataFrame(np.array(d))
    d = d.apply(pd.to_numeric, errors='coerce')
    d = d.to_numpy()

    return d, (np.array(target)).reshape(-1, 1)



def calculate_winner_porcentage(p_team1, p_team2):


    if p_team1 + p_team2 > 1.0:


        sobrante = 1 - (p_team1 + p_team2) # obtener el porcentaje sobrante , ejemplo ( 1 - (0.5 + 0.6) ) = 0.1

        p_team1 = p_team1 - (sobrante / 2) # restarle la mitad del sobrante al equipo 1 => 0.5 - (0.1 / 2) = 0.45
        p_team2 = p_team2 - (sobrante / 2) # restarle la mitad del sobrante al equipo 2 => 0.6 - (0.1 / 2) = 0.55

        #                                       la suma de 0.45 + 0.55 + 0.1 = 1.1, sigue siendo mayor, ahora normalizamos
        #                                       0.45 / 1.1 = 0.4090909090909091
        #                                      0.55 / 1.1 = 0.5
        #                                     0.1 / 1.1 = 0.09090909090909091
        #                       la suma nueva es 0.4090909090909091 + 0.5 + 0.09090909090909091 = 1      

        # normalizar datos

        p_team1 = p_team1 / (1 + sobrante)
        p_team2 = p_team2 / (1 + sobrante)
        empate = sobrante / (1 + sobrante)

        return ((p_team1 *100), (p_team2 * 100), (empate * 100))
    empate = 1 - (p_team1 + p_team2)
    return ((p_team1 *100), (p_team2 * 100), (empate * 100))

