
from copy import deepcopy
import random
from tabnanny import check
from matplotlib.pyplot import bar_label, flag
import numpy as np


# инициализация данных задачи


def init():
    # C = np.array([3,6,5,1,1,4,3,2,4,3,1,2]).reshape((3,4))
    # Z = np.array([[100,300,500]])
    # P = np.array([[200,400,100,200, 0]])

    '''Пример из лекции'''
    # C = np.array([3, 6, 5, 1, 1, 4, 3, 2, 4, 3, 1, 2]).reshape((3, 4))
    # Z = np.array([[100, 400, 600]])
    # P = np.array([[300, 500, 100, 200, 0]])

    '''Вариант 11'''
    # C = np.array([1, 9, 7, 2, 3, 1, 6, 6, 6, 8, 3, 4, 2, 3, 1, 3]).reshape((4, 4))
    # Z = np.array([[25, 40, 75,60]])
    # P = np.array([[30, 80, 20, 70, 0]])

    '''Вариант 21'''
    # C = np.array([2, 3, 9, 7, 3, 4, 6, 1, 5, 1, 2, 2, 4, 5, 8, 5]).reshape((4, 4))
    # Z = np.array([[20, 16, 14, 10]])
    # P = np.array([[15, 18, 12, 15, 0]])

    '''Вариант 14'''
    C = np.array([2, 6, 3, 4, 9, 1, 5, 6, 9, 7, 3, 4, 1, 6, 10]).reshape((3, 5))
    Z = np.array([[40, 30, 35]])
    P = np.array([[20, 34, 16, 10, 25, 0]])

    '''Вариант 18'''
    # C = np.array([1, 3, 3, 4, 5, 2, 7, 5, 7, 4, 8, 2, 6, 1, 5, 7]).reshape((4, 4))
    # Z = np.array([[50, 20, 30, 20]])
    # P = np.array([[40, 30, 35, 15, 0]])
    '''Вариант 22'''
    # C = np.array([16, 30, 17, 10, 16,
    #               20, 27, 26, 9, 23,
    #               13, 4, 22, 3, 1,
    #               2, 1, 5, 4, 24]).reshape((4, 5))
    # Z = np.array([[4, 6, 10, 10]])
    # P = np.array([[7, 7, 7, 7, 2, 0]])
    '''Ваиинат 30'''
    # C = np.array([2, 7, 3, 6, 9, 4, 5, 7, 5, 7, 6, 2]).reshape((3, 4))
    # Z = np.array([[30, 60, 50]])
    # P = np.array([[15, 40, 25, 60, 0]])
    '''Вариант 27'''
    # C = np.array([3, 7, 1, 5, 4, 6, 4, 8, 3, 12, 3, 1, 7, 4, 12]).reshape((3, 5))
    # Z = np.array([[20, 40, 60]])
    # P = np.array([[10, 35, 15, 25, 35, 0]])

    matrix = np.zeros(C.shape[0]*C.shape[1]).reshape((C.shape[0],C.shape[1]))
    matrix = np.concatenate((matrix, Z.T), axis=1)
    matrix = np.concatenate((matrix, P), axis=0)

    return matrix, C


# функиця определяющая минимум среди запасов и ресурсов
def getVal(stocks, needs):
    if needs > stocks:
        return stocks
    return needs

# получение значения целевой функии


def find_f():
    f = sum(C[i][j] * matrix[i][j] for i in range(C.shape[0])
            for j in range(C.shape[1]))
    return f

# метод северо-западного угла


def nw_corner(i = 0, j = 0):
    if i == needs and j == stocks:
        return
    if matrix[i][stocks] == 0:
        i += 1
    if matrix[needs][j] == 0:
        j += 1
    subtrahend = getVal(matrix[i][stocks], matrix[needs][j])
    matrix[i][stocks] -= subtrahend
    matrix[needs][j] -= subtrahend
    matrix[i][j] += subtrahend
    nw_corner(i, j)

# Функция нахождения минимальной цены перевозки в оставшейся таблице


def find_min(C, matrix):
    m = np.inf
    for i in range(C.shape[0]):
        if matrix[i][stocks] == 0:
            continue
        for j in range(C.shape[1]):
            if matrix[needs][j] == 0:
                continue
            if C[i][j] < m:
                m = C[i][j]
                indexes = (i, j)
    return indexes

# Функиция сравнивает потребность и запас


def row_or_col(stocks, needs):
    if stocks < needs:
        return 1
    return 0

# Метод минимальной стоимости


def min_cost():
    #stocksUsedUp = all(matrix[i][stocks] == 0 for i in range(matrix.shape[0]))
    # Проверяем удовлетворены ли потребности, завершаем рекурсию при истине
    needsSatisfied = all(matrix[needs][j] == 0 for j in range(matrix.shape[1]))
    if needsSatisfied:
        return
    # находим минимальную цену перевозки, возвращаем индексы элемента
    x, y = find_min(C, matrix)

    if row_or_col(matrix[x][stocks], matrix[needs][y]):  # запас меньше потребности
        # устанавливаем в найденную ячейку значение запаса
        matrix[x][y] = matrix[x][stocks]
        # обнуляем запас (израсходован)
        matrix[x][stocks] = 0
        # уменьшаем потребность
        matrix[needs][y] -= matrix[x][y]
    else:  # потребность меньше запаса
        # устанавливаем в найденную ячейку значение потребности
        matrix[x][y] = matrix[needs][y]
        # обнуляем потребность (удовлетворена)
        matrix[needs][y] = 0
        # вычитаем из запаса новое значение в ячейке
        matrix[x][stocks] -= matrix[x][y]
    # рекурсивный вызов
    min_cost()

# расчет векторов-потенциалов u и v
def count_u_v(i=0, row_counter=0):
    # выход из рекурсии, если обработаные все строки
    if row_counter == C.shape[0]:
        return
    for j in range(C.shape[1]):
        if matrix[i][j] != 0:
            if not flag_v[j]:
                v[j] = C[i][j] - u[i]
                flag_v[j] = True
            for k in range(C.shape[0]):
                if matrix[k][j] != 0:
                    if not flag_u[k]:
                        u[k] = C[k][j] - v[j]
                        flag_u[k] = True
                    # запускаем рекурсию на нужной строке таблицы
                    count_u_v(k,row_counter + 1)

# функиця расчета дельт
def count_deltas():
    deltas = {}
    for i in range(C.shape[0]):
        for j in range(C.shape[1]):
            if matrix[i][j] == 0:
                if u[i] is not None and v[j] is not None:
                    deltas[(i, j)] = C[i][j] - (u[i] + v[j])
    return deltas

# вспомогательная функция построения цикла
# ищет всех соседей текущего элемента
def find_neighbours(axis, x, y):
    neighbours = []
    if axis:
        # поиск по горизонтали
        for j in range(matrix.shape[1] - 1):
            #print(matrix[x][j], x, j)
            if j == y:
                continue
            if matrix[x][j] != 0:
                neighbours.append((x,j))
    else:
        # поиск по вертикали
        for i in range(matrix.shape[0] - 1):
            #print(matrix[i][y], i, y)
            if i == x:
                continue
            if matrix[i][y] != 0 or (i,y) == min_delta:
                neighbours.append((i,y))
    # если среди соседей есть стартовая точка цикла, то оставляем только её
    if circ[0] in neighbours:
        neighbours = []
        neighbours.append(circ[0])
    return neighbours


# основная функция построения цикла
def cycles(i, j, level = 0):
    global circ
    global solution
    global solution_flag
    # Ситуация, когда не возможно найти цикл (опорный план вырожденный)
    # В таком случае, прекращаем рекурсию и пытаемся изменить опорный план
    # в цикле mainloop
    if level > 25:
        return False

    if solution_flag:
        return True

    # ищем смежные элементы по таблице плана
    neighbours = find_neighbours((level + 1) % 2,i,j)
    # если по горизонтали нет соседей
    if len(neighbours) == 0:
        # if level > 0:
        #     circ = deepcopy(circ_hist[level - 1])
        return False
    for k in range(len(neighbours)):

        circ.append(neighbours[k])
        circ_hist[level + 1] = deepcopy(circ)
        print(level + 1, circ_hist[level+1])

        # проверка, найден ли цикл
        # начальный и конечный элемент сотсояния списка на уровне level + 1 должны совпадать
        if circ_hist[level + 1][0] == circ_hist[level + 1][-1] and len(circ_hist[level + 1]) > 1:
            solution = level + 1
            solution_flag = True
            return True

        flag = cycles(neighbours[k][0], neighbours[k][1], level + 1)
        if not flag:
            # если нет цикла, возвращаемся к состоянию на предыдущем шаге
            circ = deepcopy(circ_hist[level])

def change_u_v():
    global saved_cords
    res = None
    m = np.inf
    for i, item in enumerate(u):
        if item is None:
            for j in range(C.shape[1]):
                if C[i][j] < m:
                    m = C[i][j]
                    res = (i,j)

    for i, item in enumerate(v):
        if item is None:
            for j in range(C.shape[0]):
                if C[j][i] < m:
                    m = C[j][i]
                    res = (j, i)

    if res is not None:
        saved_cords = res
        x, y = res
        matrix[x][y] = None
        count_u_v()

if __name__ == '__main__':

    switch = int(input('0 - северо-западного угла\n1-минимальной стоимости\n'))
    results = []
    circ_hist = [None for i in range(100)]
    solution = 0
    saved_cords = None
    solution_flag = False
    degenerate = False

    matrix, C = init()
    print(matrix,'\n\n',C)
    # получаем индексы строки потребностей и столбца запасов
    needs = matrix.shape[0] - 1
    stocks = matrix.shape[1] - 1
    # nw_corner(0, 0)
    # print(matrix)
    # print(find_f())
    #results.append(find_f())
    #matrix, C = init()
    if switch:
        min_cost()
    else:
        nw_corner()
    print(matrix)
    print(find_f())
    results.append(find_f())
    

    print(C)
    z = 0

    flag_v = [False for i in range(C.shape[1])]
    flag_u = [False for i in range(C.shape[0])]

    v = [None for i in range(C.shape[1])]
    u = [None for i in range(C.shape[0])]
    u[0] = 0
    count_u_v()
    print('UV BEFORE',u, v)
    if None in u or None in v:
        degenerate = True
        change_u_v()
    print('UV AFTER', u, v)
    print(matrix)
    deltas = count_deltas()
    print(deltas)
    # пока среди значений дельты есть хотя бы одно отрицательное число
    while any(val < 0 for val in deltas.values()):

        solution_flag = False
        circ_hist = [None for i in range(100)]
        solution = 0

        min_delta = min(deltas, key=deltas.get)
        print(min_delta)
        circ = []
        circ.append(min_delta)
        circ_hist[0] = deepcopy(circ)

        fg = cycles(min_delta[0],min_delta[1])
        circ = deepcopy(circ_hist[solution])
        
        print('Current circ is: ', circ)

        if saved_cords is not None:
            x, y = saved_cords
            matrix[x][y] = 0
            saved_cords = None

            # проверка вырожденного плана
        nonBasis = list(deltas.keys())
        nonBasis.remove(min_delta)
        if len(circ) == 1:
            x, y = random.choice(nonBasis)
            matrix[x][y] = None
            print(matrix)
            #cycles(min_delta[0],min_delta[1])
            saved_cords = (x,y)
            continue

        circ = circ[1:-1]
        circ_vals = [matrix[coords[0]][coords[1]] for coords in circ]
        print(circ_vals)
        # минимум среди значений отрицательных вершин цикла
        lmbda = min(circ_vals[::2])

        if lmbda == 0:
            continue

        matrix[min_delta[0]][min_delta[1]] = lmbda
        for k in range(len(circ)):
            i,j = circ[k]
            if k % 2 == 0:
                matrix[i][j] -= lmbda
            else:
                matrix[i][j] += lmbda

        flag_v = [False for i in range(C.shape[1])]
        flag_u = [False for i in range(C.shape[0])]

        v = [None for i in range(C.shape[1])]
        u = [None for i in range(C.shape[0])]
        u[0] = 0
        
        print(find_f())
        results.append(results[0]+min(deltas.values())*lmbda)
        
        count_u_v()

        print('BEFORE U AND V',u,v)
        if degenerate:
            if None in u or None in v:
                change_u_v()

        print('AFTER U AND V',u,v)
        print(matrix)
        print(find_f())

        deltas = count_deltas()
        print(deltas)
    print(results)