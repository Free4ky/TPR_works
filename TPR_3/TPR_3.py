from ast import Return
from math import fsum
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

DIM = 5
SI = 1.12
# считывание матриц
# def input_preference():
#     x = input().split()
#     matrix = np.array([x[i] for i in range(DIM**2)])
#     matrix = matrix.reshape(DIM,DIM)
#     return matrix


def read_data():
    # считывание обратно симметричной матрицы для парного сравнения критериев
    purpose = pd.read_csv('TPR_3\Data\PURPOSE.csv')
    purpose = purpose.to_numpy()

    k1 = pd.read_csv('TPR_3\Data\K1.csv')
    k1 = k1.to_numpy()

    k2 = pd.read_csv('TPR_3\Data\K2.csv')
    k2 = k2.to_numpy()

    k3 = pd.read_csv('TPR_3\Data\K3.csv')
    k3 = k3.to_numpy()

    k4 = pd.read_csv('TPR_3\Data\K4.csv')
    k4 = k4.to_numpy()

    k5 = pd.read_csv('TPR_3\Data\K5.csv')
    k5 = k5.to_numpy()

    return purpose, k1, k2, k3, k4, k5

# нахождение векторов предпочтений


def get_preference_vector(matrix):
    vector = []
    for row in range(matrix.shape[0]):
        vector.append(np.prod(matrix[row]) ** 0.2)

    s = fsum(vector)
    vector = map(lambda x: x/s, vector)
    return np.fromiter(vector, dtype=float)


def check_consistency(matrix, W):
    matrix_t = matrix.T
    col_sums = []
    for col in range(matrix_t.shape[0]):
        col_sums.append(fsum(matrix_t[col]))
    col_sums = np.array(col_sums)
    proportionality_of_preferences = col_sums @ W.T
    return (proportionality_of_preferences - DIM)/((DIM - 1) * SI)

# получение приоритета альтернатив


def count_alternatives_priority(KjY, W2i):
    return W2i @ KjY


def build_circle_diagram(vector):
    labels = [
        'Luxoft',
        'МТС',
        'Яндекс',
        'EPAM',
        'Совкомбанк Технологии'
    ]
    fix, ax = plt.subplots()
    ax.pie(vector, labels=labels, autopct='%.3f%%')
    plt.show()


if __name__ == '__main__':

    purpose, k1, k2, k3, k4, k5 = read_data()

    W2i = get_preference_vector(purpose)

    KjY = []
    KjY.append(get_preference_vector(k1))
    KjY.append(get_preference_vector(k2))
    KjY.append(get_preference_vector(k3))
    KjY.append(get_preference_vector(k4))
    KjY.append(get_preference_vector(k5))

    KjY = np.array(KjY)

    all_OS = []
    all_OS.append(check_consistency(purpose, W2i))
    all_OS.append(check_consistency(k1, KjY[0]))
    all_OS.append(check_consistency(k2, KjY[1]))
    all_OS.append(check_consistency(k3, KjY[2]))
    all_OS.append(check_consistency(k4, KjY[3]))
    all_OS.append(check_consistency(k5, KjY[4]))
    all_OS = np.array(all_OS)
    #np.set_printoptions(precision=2, floatmode='fixed')
    print(all_OS)

    priority = count_alternatives_priority(KjY, W2i)

    print(priority)

    build_circle_diagram(priority)
