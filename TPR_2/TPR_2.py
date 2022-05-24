from cmath import inf
import pandas as pd
import numpy as np
import graphviz as gv
from collections import Counter
#import os


#os.environ["PATH"] += os.pathsep + 'C:\\Users\\Den Ka\\AppData\\Local\\Programs\\Python\\Python310\\Graphviz\\bin'

MONEY = 2
CAREER = 3
RATING = 4
LENGTH = 5
INTEREST = 6
FRIEND = 7
NUM_CRITERIA = 6
WEIGHT_ROW = 10

def code_table(data):
    #перекодировка таблицы
    for col in range(2, data.shape[1]):
        for row in range(data.shape[0]):
            value = float(data.iloc[row][col])
            if col == MONEY:
                if 80 <= value < 90:
                    data.at[row,'Зарплата,  тыс. руб.(+)'] = 5
                elif 90 <= value < 100:
                    data.at[row,'Зарплата,  тыс. руб.(+)'] = 10
                elif 100 <= value < 110:
                    data.at[row,'Зарплата,  тыс. руб.(+)'] = 15
                else:
                    data.at[row,'Зарплата,  тыс. руб.(+)'] = 20         
            elif col == CAREER:
                if 4.6 <= value <= 5:
                    data.at[row,'Карьерный рост(+)'] = 15     
                elif 4.3 <= value < 4.6:
                    data.at[row,'Карьерный рост(+)'] = 10
                elif 4 <= value < 4.3:
                    data.at[row,'Карьерный рост(+)'] = 5
                elif value < 4:
                    data.at[row,'Карьерный рост(+)'] = 1
            elif col == RATING:
                if 4.6 <= value <= 5:
                    data.at[row,'Рейтинг фирмы (+)'] = 15     
                elif 4.3 <= value < 4.6:
                    data.at[row,'Рейтинг фирмы (+)'] = 10
                elif 4 <= value < 4.3:
                    data.at[row,'Рейтинг фирмы (+)'] = 5
                elif value < 4:
                    data.at[row,'Рейтинг фирмы (+)'] = 1
            elif col == LENGTH:
                if value >= 20:
                    data.at[row,'Удаленность от дома, км (-)'] = 5
                elif 10 <= value < 20:
                    data.at[row,'Удаленность от дома, км (-)'] = 3
                elif value < 10:
                    data.at[row,'Удаленность от дома, км (-)'] = 1
            elif col == INTEREST:
                if 4.6 <= value <= 5:
                    data.at[row,'Интересность задач (+)'] = 15     
                elif 4.3 <= value < 4.6:
                    data.at[row,'Интересность задач (+)'] = 10
                elif 4 <= value < 4.3:
                    data.at[row,'Интересность задач (+)'] = 5
                elif value < 4.1:
                    data.at[row,'Интересность задач (+)'] = 1
            elif col == FRIEND:
                if value >= 0.6:
                    data.at[row,'Не дружелюбность коллектива (-)'] = 8
                elif 0.3 <= value < 0.6:
                    data.at[row,'Не дружелюбность коллектива (-)'] = 4
                elif value < 0.3:
                    data.at[row,'Не дружелюбность коллектива (-)'] = 2
    # считывание весов и добавление их к перекодированной таблице
    weight = pd.read_csv("C:\Study\ТПР\Практика2\weight.csv")
    data = pd.concat([data,weight],ignore_index=True)
    return data

def electra_matrix(data):
    # создаем пустой датафрейм для итоговой матрицы
    matrix = pd.DataFrame(np.zeros((10,10)),columns=[i for i in range(10)])
    # перебор элементов, подсчет значений (Pij, Nij, Dij), (Pji, Nji, Dji)
    for i in range(data.shape[0] - 1):
        for j in range(i+1, data.shape[0] - 1):
            Pij = Nij = 0
            for col in range(2,data.shape[1]):
                if (j != i):
                    if (col == MONEY or col == CAREER or col == RATING or col == INTEREST):
                        if (data.iloc[i][col] > data.iloc[j][col]): 
                            Pij += data.iloc[WEIGHT_ROW][col]
                            #Nji += data.iloc[WEIGHT_ROW][col]
                        elif(data.iloc[i][col] < data.iloc[j][col]):
                            Nij += data.iloc[WEIGHT_ROW][col]
                            #Pji += data.iloc[WEIGHT_ROW][col]
                    if (col == LENGTH or col == FRIEND):
                        if (data.iloc[i][col] < data.iloc[j][col]):
                            Pij += data.iloc[WEIGHT_ROW][col]
                            #Nji += data.iloc[WEIGHT_ROW][col]
                        elif(data.iloc[i][col] > data.iloc[j][col]):
                            Nij += data.iloc[WEIGHT_ROW][col]
                            #Pji += data.iloc[WEIGHT_ROW][col]
                # подсчет значений Dij и Dji и запись их в итоговую матрицу
            if (Pij > 0 and Nij == 0): # деление на 0 дает бесконечность
                matrix.iloc[i][j] = inf
            elif(Nij != 0 and Pij/Nij > 1):
                matrix.iloc[i][j] = Pij/Nij  
            elif(Pij == 0 and Nij > 0):
                matrix.iloc[j][i] = inf
            elif(Pij != 0 and Nij/Pij > 1):
                matrix.iloc[j][i] = Nij/Pij
    return matrix
 
# функция установки порога значений в матрице электро, для устранения цикличности 
def set_bounds(matrix,bound_value):
    for row in range(matrix.shape[0]):
        for col in range(matrix.shape[1]):
            if matrix.iloc[row][col] <= bound_value:
                matrix.iloc[row][col] = 0
    return matrix

# построение графа по матрице электра 2   
def build_graph(matrix):
    matrix = set_bounds(matrix,4.74)
    dot = gv.Digraph(comment='Graph from matrix')
    nodes = []
    for row in range(matrix.shape[0]):
        if row not in nodes:
            nodes.append(row)
            dot.node(str(row),str(row))
        for col in range(matrix.shape[1]):
            if matrix.iloc[row][col] != 0 and row != col:
                if col in nodes:
                    dot.edge(str(row),str(col))
                else:
                    dot.node(str(col),str(col))
                    dot.edge(str(row),str(col))
    return dot
    
# вывод уровней
def count_entry(matrix):
    levels = []        
    for i in range(matrix.shape[0]):
        num_in_row = 0
        row = matrix.iloc[i]
        for j in range(len(row)):
            if row[j] > 0:
                num_in_row += 1
        levels.append((i,num_in_row))
        
    sorted_levels = sorted(levels,key=lambda tup: tup[1], reverse=True)
    result = []
    result.append('0: ' + str(sorted_levels[0][0]) + ', ')
    cnt = 0
    for i in range(1,len(sorted_levels)):
        if sorted_levels[i][1] == sorted_levels[i - 1][1]:
            result[cnt] += str(sorted_levels[i][0]) + ', '
        else:
            cnt += 1
            result.append(str(cnt) + ': ' + str(sorted_levels[i][0]) + ', ')
    
    for i in range(len(result)):
        result[i] = result[i][:-2]
            
    return result

if __name__ == '__main__':
    #считываем таблицу предметной области в dataframe
    data = pd.read_csv("TPR_2\Paretto1.csv")
    data = code_table(data)
    print(data)
    #вычисляем матрице электра
    matrix = electra_matrix(data)
    print('\n',matrix)
     
    #построение графа по матрице электра
    dot = build_graph(matrix)
    print('\n',matrix)
    dot.view()
    
    levels = count_entry(matrix)
    print('\nLevels:')
    for level in levels:
        print(level)