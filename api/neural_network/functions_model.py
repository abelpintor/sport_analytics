
import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt

# Obtener la carpeta donde se encuentra el script actual
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construir las rutas relativas
path_csv= 'datos_api_full'
data_2021 = pd.read_csv(os.path.join(script_dir, path_csv, '2021-22', 'matches.csv'))
data_2022 = pd.read_csv(os.path.join(script_dir, path_csv, '2022-23', 'matches.csv'))
data_2023 = pd.read_csv(os.path.join(script_dir, path_csv, '2023-24', 'matches.csv'))
data_2024 = pd.read_csv(os.path.join(script_dir, path_csv, '2024-25', 'matches.csv'))

data_21 = data_2021.iloc[:, 1:30].values

data_22 = data_2022.iloc[:, 1:30].values

data_23 = data_2023.iloc[:, 1:30].values

data_24 = data_2024.iloc[:, 1:30].values


# concatenar los datos de las temporadas para tener un solo dataset y poder buscar los datos de los equipos
premier_league = np.concatenate((data_21, data_22, data_23, data_24), axis=0)


def search_team_data(team, data_season):
    d = []
    target = []
    for i in range(data_season.shape[0]):
        if (data_season[i][0] == team or data_season[i][1] == team):
            

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

    return d, (np.array(target)).reshape(-1, 1) # el reshape es para que sea un vector columna y no sea un simple arreglo (n,) y si (n, 1)



def sigmoide(x):
    return 1 / (1 + np.exp(-x))

def derivada_sigmoide(x):
    return x * (1 - x)

def forward_pass(X, weights, biases):
    x_entrada = [X] # se guarda X porque es la entrada de la red neuronal y se ocupa para la primera capa

    # zip enpaqueta los elementos en una tupla
    # en este caso weights y biases son listas de matrices, cada elemento de weight es de la forma (n, m) donde n es el número
    # de neuronas de la capa anterior y m el número de neuronas de la capa actual
    # en el caso de biases, cada elemento es de la forma (1, m) donde m es el número de neuronas de la capa actual

    # ejemplo, en una matriz de una capa oculta con 5 entradas y 4 neuronas en la capa oculta
    # el w seria de (5, 4) y el b de (1, 4), X sería de (1, 5) donde 1 es la fila y 5 las columnas (en el caso de que fuera un solo dato)
    # la multiplicacion quedaria (1x5)X(5x4) = 1x4, el resultado es 1x4 porque es un solo dato y son 4 neuronas en la capa oculta, osea 4 salidas
    # despues se le suma B que es de (1,4), entonces cada elemento de la salida se le suma el bias correspondiente
    # en caso de que la X no fuera un solo datos sino varios, la multiplicación sería (nx5)X(5x4) = nx4, donde n es el número de datos
    # para la suma aunque b sigue siendo vector de 1x4, cada fila del rsultado de (nx4) se le suma el bias correspondiente
    # esto con ayuda de python y numpy con el broadcasting
    for w, b in zip(weights, biases):

        z = np.dot(x_entrada[-1], w) + b
        a = sigmoide(z)
        x_entrada.append(a)
    return x_entrada

def backpropagation(X, y, x_entrada, weights, biases, lr=0.5, errores=[]):
    output = x_entrada[-1]
    output_error = y - output

    # error cuadrático medio, para posteriormente graficar el error por época
    squeare_error = np.square(output_error)
    errores.append(squeare_error.mean())

    # Calcular delta para la capa de salida
    output_delta = output_error * derivada_sigmoide(output) # se multiplcan elemento a elemento con broadcasting [5x1][5x1] = [5x1]

    deltas = [output_delta] # el primer delta es el de la capa de salida

    # Calcular deltas para capas ocultas
    for i in range(len(weights) - 1, 0, -1): # desde la última capa oculta hasta la primera
        hidden_error = deltas[-1].dot(weights[i].T) # (w_siguiente * delta_siguiente)
        hidden_delta = hidden_error * derivada_sigmoide(x_entrada[i]) # sigmoide_derivada(de la salida de la capa)
        deltas.append(hidden_delta)

    # se invierte la lista de deltas para que vaya de la primera capa hasta la última
    deltas.reverse()

    # Actualización de pesos y biases
    for i in range(len(weights)):
        weights[i] += x_entrada[i].T.dot(deltas[i]) * lr
        biases[i] += np.sum(deltas[i], axis=0, keepdims=True) * lr

    return weights, biases


def predict(X, y, x_test, y_test, hidden_layers=3, neuronas_por_capa=4, learning_rate=0.1, epochs=10000, plot=True):
    
    # Inicialización de parámetros
    input_size = X.shape[1]  # Número de características de entrada
    output_size = y.shape[1]  # Número de características de salida

    # Inicialización de pesos y sesgos
    weights = []
    biases = []

    np.random.seed(42)
    # Pesos de la capa de entrada a la primera capa oculta
    weights.append(np.random.rand(input_size, neuronas_por_capa))
    biases.append(np.random.rand(1, neuronas_por_capa))

    # Pesos y sesgos de las capas ocultas
    for i in range(hidden_layers - 1):
        weights.append(np.random.rand(neuronas_por_capa, neuronas_por_capa))
        biases.append(np.random.rand(1, neuronas_por_capa))

    # Pesos de la última capa oculta a la capa de salida
    weights.append(np.random.rand(neuronas_por_capa, output_size))
    biases.append(np.random.rand(1, output_size))



    #### Entrenamiento
    # lista de erroes por epoca
    errores = []
    for epoch in range(epochs):
        # Forward pass
        x_entrada = forward_pass(X, weights, biases)
        
        # Backward pass y actualización de pesos y SESGO
        weights, biases = backpropagation(X, y, x_entrada, weights, biases, learning_rate, errores)

    
    if plot:
        plt.plot(np.linspace(1,epochs, len(errores)), errores)
        # plt.plot(errores)
        plt.xlabel('Epochs')
        plt.ylabel('Error')
        plt.title('Error por época de entrenamiento (Escala Logarítmica)')
        plt.xscale('log')  # Cambia el eje X a escala logarítmica
        plt.grid(True)
        plt.show()

        plt.plot(np.linspace(1, epochs, len(errores)), errores)
        plt.xlabel('Epochs')
        plt.ylabel('Error')
        plt.title('Error por época de entrenamiento (Escala Lineal)')
        plt.grid(True)
        plt.show()


    # Prueba de la red neuronal
    counter = 0
    for i in range(len(x_test)): # por cada dato de prueba/fila

        # el reshape es para que sea un vector fila y no un simple arreglo (n,) y si (1, n)
        x_entrada = forward_pass(x_test[i].reshape(1, -1), weights, biases)
        output = x_entrada[-1]

        if (output.round() == y_test[i]):
            counter += 1
        print(output)
    
    print(f"Porcentaje de aciertos: {counter / len(x_test) * 100}%")
    return output


