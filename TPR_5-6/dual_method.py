import simplex # программа реализующая симплекс метод, написанная в предыдущей практической работе
import numpy as np
import math

# Функция возвращающая матрицу коэффициентов системы ограничений
def get_limit_matrix():
    a = []
    a.extend(simplex.a1[:-1])
    a.extend(simplex.a2[:-1])
    for i in range(4):
        buf = np.zeros(4)
        buf[i] = 1
        a.extend(buf)
    a = np.reshape(a, (6, 4))
    return a


if __name__ == '__main__':

    # Получаем матрицу коэффициентов системы ограничений
    a = get_limit_matrix()
    print('Матрица коэффициентов системы ограничений:\n',a)
    # Получаем словари базисных и небазисных переменных
    d_cj = simplex.d_cj
    d_cb = simplex.d_cb
    print('Базисные перменные их коэффициенты в целевой функции прямой задачи:\n',d_cb)
    # Составляем матрицу базисных векторов (Полученных в результате решения задачи симплекс методом)
    D = []
    for item in d_cb:
        index = int(list(item.keys())[0]) - 1
        D.extend(a[index])
    D = np.reshape(D, (4, 4))
    D = D.T
    print('Матрица базисных векторов:\n',D)
    # Находим обратную матрицу Базисных векторов
    D_inv = np.linalg.inv(D)
    print('Обратная матрица:\n',D_inv)
    # Находим вектор решений двойственной задачи по формуле Cb * D^-1
    cb = simplex.cb
    y = cb @ D_inv
    print('Значения двойственных переменных:\n',y)
    # Найдем минимальное значение целевой функции двойственной задачи
    a0 = simplex.a0[:-1]
    g_min = math.ceil(y @ a0)
    print(f'Значение целевой функции двойственной задачи: {g_min}')