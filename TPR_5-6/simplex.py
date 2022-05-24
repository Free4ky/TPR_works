import numpy as np
import math
from copy import copy
import sys


cj = np.array([260, 300], dtype=float)
cb = np.zeros(4)

d_cj = [{'1': 260}, {'2': 300}]
d_cb = [{'3':0},{'4':0},{'5':0},{'6':0}]

a1 = np.array([16, 0.2, 6, 3])
a1 = np.append(a1, -cj[0])

a2 = np.array([12, 0.4, 5, 4])
a2 = np.append(a2, -cj[1])

a0 = np.array([1200, 30, 600, 300])
a0 = np.append(a0, 0)
matrix = np.concatenate((a1, a2, a0))
matrix = np.reshape(matrix, (3, 5)).T

#относительные оценки, характеризующие прирост целевой функции
deltas = matrix.shape[0] - 1

print('Симплекс-таблица опорного плана:\n', matrix)
print('Вектор коэффициентов свободных переменных:\n', cj)
print('Вектор коэффициентов базисных переменных:\n', cb, '\n')


# функция, проверяющая есть ли отрицательный элемент в массиве
def hasNegative(deltas):
    return any(flag < 0 for flag in deltas)

# функция, отвечающая за поиск разрешающего столбца


def findColumn(deltas):
    max_index = 0
    max_value = 0
    for i, delta in enumerate(deltas):
        if i == len(deltas)-1:
            break
        if delta < 0 and math.fabs(delta) > max_value:
            max_value = math.fabs(delta)
            max_index = i
    return max_index

# функция, отвечающая за поиск разрешающей строки


def findRow(matrix, PremissionColumn):
    index_min = math.inf
    value_min = math.inf
    for i, row in enumerate(matrix):
        if i == matrix.shape[0] - 1:
            break
        # Элементы разрешающего столбца
        ai = matrix[i][PremissionColumn]
        # Элементы столбца A0
        bi = matrix[i][matrix.shape[1] - 1]
        if bi >= 0 and ai > 0 and bi/ai < value_min:
            value_min = bi/ai
            index_min = i
    return index_min

# функция, отвечающая за построение новой симпликс-таблицы


def buildNewMatrix(matrix1, premissionColumn, premissionRow):
    # сохранение симпликс-таблицы для подсчета элементов новой симпликс-таблицы методом прямоугольника
    old_matrix = copy(matrix1)
    matrix = copy(matrix1)
    premissionElement = matrix[premissionRow][premissionColumn]
    # изменяем разрешающий эдемент на обратный себе 1/ar
    matrix[premissionRow][premissionColumn] = 1/premissionElement
    # изменение элементов разрешающего столбца: делятся на разрешающий элемент и берутся с противоположным знаком
    for i, row in enumerate(matrix):
        if i == premissionRow:
            continue
        else:
            row[premissionColumn] = -row[premissionColumn]/premissionElement
    # изменение элементов разрешаюшей строки: делятся на разрешающий элемент
    for i, row_element in enumerate(matrix[premissionRow]):
        if i == premissionColumn:
            continue
        else:
            matrix[premissionRow][i] = matrix[premissionRow][i] / \
                premissionElement
    # подсчет элементов новой матрицы методом прямоугольника
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            if i == premissionRow or j == premissionColumn:
                continue
            else:
                matrix[i][j] = (old_matrix[i][j] * premissionElement - old_matrix[i]
                                [premissionColumn]*old_matrix[premissionRow][j])/premissionElement
    return matrix

# основная фунция алгоритма симплекс-метода, содержит основную последовательность действий


def simplex(matrix):
    print('Начало расчетов:\n')
    counter = 0
    while hasNegative(matrix[deltas]):
        premissionColumn = findColumn(matrix[deltas])
        premissionRow = findRow(matrix, premissionColumn)
        '''
        cb - вектор коэффициентов целевой функции при базисных переменных
        сj - вектор коэффициентов свободных переменных
        После нахождения очередного разрешающего элемента в базис включается новыя переменная
        и убирается старая, поэтому меняются вектора коэффициентов
        '''
        cb[premissionRow], cj[premissionColumn] = cj[premissionColumn], cb[premissionRow]
        
        d_cb[premissionRow], d_cj[premissionColumn] = d_cj[premissionColumn], d_cb[premissionRow]

        matrix = buildNewMatrix(matrix, premissionColumn, premissionRow)
        print(f'Iteration {counter}:\n', matrix, '\n')
        counter += 1
    # получение вектора-оптимального плана из итоговой симпликс-таблицы (крайний правый столбец)
    A0 = np.array([row[matrix.shape[1]-1]
                  for row in matrix][:matrix.shape[0]-1]).T
    optimal_result = cb @ A0
    print(f'Optimal solution is: {optimal_result}')


simplex(matrix)