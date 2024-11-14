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