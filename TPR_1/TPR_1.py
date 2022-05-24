import numpy as np
import pandas as pd

MONEY = 2
CAREER = 3
RATING = 4
LENGTH = 5
INTEREST = 6
FRIEND = 7
NUM_CRITERIA = 6

def check_optimal(data, i, j):
    counter = 0
    for col in range(2, data.shape[1]):
        if (col == MONEY or col == CAREER or col == RATING or col == INTEREST):
            if (data.iloc[i][col] >= data.iloc[j][col]):
                counter += 1
            else:
                return 0
        if (col == LENGTH or col == FRIEND):
            if (data.iloc[i][col] <= data.iloc[j][col]):
                counter += 1
            else:
                return 0
    return counter

# СУЖЕНИЯ

# BOUNDARIES

def check_boundaries(data):
    index = []
    data.index = range(data.shape[0]) # reset indexes in dataframe
    print("Выберете количество критериев для ограничения: ")
    num_reduce = input()
    print("Выберете критерий для установки границ и в ведите его значение\nЗарплата - 1\nКарьерный рост - 2\nРейтинг - 3\nУдаленность от дома - 4\nИнтересность задач - 5\nНе дружелюбность коллектива - 6")

    reds = dict(input().split() for i in range(int(num_reduce))) # read dictionary from input
    #print(reds)
    for key,value in reds.items():
        key = int(key)
        if (key == MONEY - 1 or key == CAREER - 1 or
            key == RATING - 1 or key == INTEREST - 1):
            for i in range(data.shape[0]):
                if (data.iloc[i][key+1] <= float(value)):
                    index.append(i)
        if(key == LENGTH - 1 or key == FRIEND - 1):
            for i in range(data.shape[0]):
                if (data.iloc[i][key+1] >= float(value)):
                    index.append(i)
    return index

#субоптимизация
def suboptimization(data):
    if (data.shape[0] < 2): 
        return
    data.index = range(data.shape[0])
    index = []
    print("Введите номер критерия, который будет максимизирован:\nЗарплата - 1\nКарьерный рост - 2\nРейтинг - 3\nУдаленность от дома - 4\nИнтересность задач - 5\nНе дружелюбность коллектива - 6")
    max_criteria = input()
    print("Введите нижние границы для остальных критериев в формате номер-значение")
    reds = dict(input().split() for i in range(int(NUM_CRITERIA-1)))
    # убираем строки, которые не подходят по нижним границам
    for key,value in reds.items():
        key = int(key)
        if (key == MONEY - 1 or key == CAREER - 1 or
            key == RATING - 1 or key == INTEREST - 1):
            for i in range(data.shape[0]):
                if (data.iloc[i][key+1] < float(value)):
                    index.append(i)
        if(key == LENGTH - 1 or key == FRIEND - 1):
            for i in range(data.shape[0]):
                if (data.iloc[i][key+1] > float(value)):
                    index.append(i)
                    
    index = np.unique(index)
    for i in range(data.shape[0]):
        if (np.isin(i,index)):
            data = data.drop(i)
            
    # выбираем строку с максимальным значением в выбраном столбце критерия
    data.index = range(data.shape[0]) # reset index in dataframe
    max_in_column = []
    if (data.shape[0] > 1):
        if (int(max_criteria) == MONEY - 1):
            max_in_column.append(data['Зарплата,  тыс. руб.(+)'].idxmax())
            
        elif (int(max_criteria) == CAREER - 1):
            max_in_column.append(data['Карьерный рост(+)'].idxmax())
            
        elif (int(max_criteria) == RATING - 1):
            max_in_column.append(data['Рейтинг фирмы (+)'].idxmax())
            
        elif (int(max_criteria) == LENGTH - 1):
            max_in_column.append(data['Удаленность от дома, км (-)'].idxmin())
            
        elif (int(max_criteria) == INTEREST - 1):
            max_in_column.append(data['Интересность задач (+)'].idxmax())
            
        elif (int(max_criteria) == FRIEND - 1):
            max_in_column.append(data['Не дружелюбность коллектива (-)'].idxmin())
            
        for i in range(data.shape[0]):
            if not np.isin(i,max_in_column):
                data = data.drop(i)
    return data
    
def choose_max(data,p,num_max):
    data1 = data
    max_in_column = []
    for i in range(num_max):
        if (int(p) == MONEY - 1):
            idx = data1['Зарплата,  тыс. руб.(+)'].idxmax()
            max_in_column.append(idx)
            data1 = data1.drop(idx)
            
        elif (int(p) == CAREER - 1):
            idx = data1['Карьерный рост(+)'].idxmax()
            max_in_column.append(idx)
            data1 = data1.drop(idx)
     
        elif (int(p) == RATING - 1):
            idx = data1['Рейтинг фирмы (+)'].idxmax()
            max_in_column.append(idx)
            data1 = data1.drop(idx)

        elif (int(p) == LENGTH - 1):
            idx = data1['Удаленность от дома, км (-)'].idxmin()
            max_in_column.append(idx)
            data1 = data1.drop(idx)

        elif (int(p) == INTEREST - 1):
            idx = data1['Интересность задач (+)'].idxmax()
            max_in_column.append(idx)
            data1 = data1.drop(idx)
            
        elif (int(p) == FRIEND - 1):
            idx = data1['Не дружелюбность коллектива (-)'].idxmin()
            max_in_column.append(idx)
            data1 = data1.drop(idx)
            
    return max_in_column
            
      
def lexicographique(data):
    data.index = range(data.shape[0])
    print("Выберите приоритетность критериев в порядке убывания:\nЗарплата - 1\nКарьерный рост - 2\nРейтинг - 3\nУдаленность от дома - 4\nИнтересность задач - 5\nНе дружелюбность коллектива - 6")
    prior = [input() for i in range(NUM_CRITERIA)]
    for p in prior:
        if (data.shape[0] == 1):
            return data
        if (data.shape[0] <= 3):
            res = choose_max(data,p,1)
            print(res)
            print(data.index)
            for i in data.index:
                if not np.isin(i,res):
                    data = data.drop(i)
        else:
            res = choose_max(data,p,3)
            print(res)
            for i in data.index:
                if not np.isin(i,res):
                    data = data.drop(i)
    return data

if __name__ == "__main__":
    data = pd.read_csv("TPR_1\Paretto1.csv")
    #print(data.keys)
    #print(data['Зарплата,  тыс. руб.(+)'].idxmax())
    # нахождение парето-опртимального множества
    index = []
    for i in range(data.shape[0]):
        for j in range(data.shape[0]):
            if (i != j):
                result = check_optimal(data, i, j)
                if (result == NUM_CRITERIA):
                    index.append(i)

    index = np.unique(index)

    data1 = data

    for i in range(data.shape[0]):
        if(not(np.isin(i,index))):
            data1 = data1.drop(i)
        
    print(data1)

    #выбор метода сужения

    print("Выберете метод сужения:\nГраницы - 1\nСубоптимизация - 2\nЛексикографический -3")
    var = input()
    if int(var) == 1:
        result = check_boundaries(data1)
        data2 = data1
        #print(data2.shape)
        for i in range(data2.shape[0]):
            if(np.isin(i,result)):
                data2 = data2.drop(i)
        print(data2)
    elif int(var) == 2:
        data2 = data1
        data2 = suboptimization(data2)
        print(data2)
    elif int(var) == 3:
        data2 = data1
        data2 = lexicographique(data2)
        print(data2)

#Входные данные
#Границы
'''
4 12
6 0.3
'''
#Субоптимизация     
'''
2 4.4
3 4.5
4 12
5 4.6
6 0.3
'''
#Лексикографический
'''
1
4
5
3
6
2
'''