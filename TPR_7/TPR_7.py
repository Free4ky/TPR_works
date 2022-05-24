import numpy as np
from tkinter import *
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
import random
from copy import deepcopy

class Counter():
    
    def __init__(self, gui):
        self.gui = gui
        self.matrix = gui.matrix
        self.C = gui.C
        self.circ = []
        self.results = []
        self.degenerate = False
        self.saved_cords = None
        
        self.circ_hist = [None for i in range(100)]
        self.solution = 0
        self.solution_flag = False
        
    # определяет что меньше: значение запаса или значение потребности
    def getVal(self, stocks, needs):
        if needs > stocks:
            return stocks
        return needs
    # находит значение функции стоимости
    def find_f(self):
        f = sum(self.C[i][j] * self.matrix[i][j] for i in range(self.C.shape[0])
                for j in range(self.C.shape[1]))
        return f
    # метод северо-западного угла
    def nw_corner(self,i=0, j=0):
        needs = self.needs
        stocks = self.stocks
        if i == needs and j == stocks:
            return
        if self.matrix[i][stocks] == 0:
            i += 1
        if self.matrix[needs][j] == 0:
            j += 1       
        subtrahend = self.getVal(self.matrix[i][stocks], self.matrix[needs][j])
        self.matrix[i][stocks] -= subtrahend
        self.matrix[needs][j] -= subtrahend
        self.matrix[i][j] += subtrahend
        self.nw_corner(i, j)
        
    # ищет минимальное значение среди оставшихся клеток (используется в методе минимальной стоимости)
    def find_min(self, C, matrix):
        needs = self.needs
        stocks = self.stocks
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
    
    # определяет что меньше: значение запаса или значение потребности
    def row_or_col(self,stocks, needs):
        if stocks < needs:
            return 1
        return 0
    
    # метод минимальной стоимости
    def min_cost(self):
        #stocksUsedUp = all(matrix[i][stocks] == 0 for i in range(matrix.shape[0]))
        # Проверяем удовлетворены ли потребности, завершаем рекурсию при истине
        needs = self.needs
        stocks = self.stocks
        needsSatisfied = all(self.matrix[needs][j] == 0 for j in range(self.matrix.shape[1]))
        if needsSatisfied:
            return
        # находим минимальную цену перевозки, возвращаем индексы элемента
        x, y = self.find_min(self.C, self.matrix)

        if self.row_or_col(self.matrix[x][stocks], self.matrix[needs][y]):  # запас меньше потребности
            # устанавливаем в найденную ячейку значение запаса
            self.matrix[x][y] = self.matrix[x][stocks]
            # обнуляем запас (израсходован)
            self.matrix[x][stocks] = 0
            # уменьшаем потребность
            self.matrix[needs][y] -= self.matrix[x][y]
        else:  # потребность меньше запаса
            # устанавливаем в найденную ячейку значение потребности
            self.matrix[x][y] = self.matrix[needs][y]
            # обнуляем потребность (удовлетворена)
            self.matrix[needs][y] = 0
            # вычитаем из запаса новое значение в ячейке
            self.matrix[x][stocks] -= self.matrix[x][y]
        # рекурсивный вызов
        self.min_cost()
        
    # вычисление потенциалов
    def count_u_v(self, i = 0, row_counter = 0):
        # выход из рекурсии, если обработаные все строки
        if row_counter == self.C.shape[0]:
            return
        for j in range(self.C.shape[1]):
            if self.matrix[i][j] != 0:
                self.v[j] = self.C[i][j] - self.u[i]
                for k in range(1, self.C.shape[0]):
                    if self.matrix[k][j] != 0:
                        self.u[k] = self.C[k][j] - self.v[j]
                        # запускаем рекурсию на нужной строке таблицы
                        self.count_u_v(k, row_counter + 1)
                        
    # вычисление отночительных оценок (дельт)
    def count_deltas(self):
        deltas = {}
        for i in range(self.C.shape[0]):
            for j in range(self.C.shape[1]):
                if self.matrix[i][j] == 0:
                    if self.u[i] is not None and self.v[j] is not None:
                        deltas[(i, j)] = self.C[i][j] - (self.u[i] + self.v[j])
        return deltas
    
    # нахождение смежных элементов
    def find_neighbours(self,axis, x, y):
        neighbours = []
        if axis:
            # поиск по горизонтали
            for j in range(self.matrix.shape[1] - 1):
                #print(matrix[x][j], x, j)
                if j == y:
                    continue
                if self.matrix[x][j] != 0:
                    neighbours.append((x,j))
        else:
            # поиск по вертикали
            for i in range(self.matrix.shape[0] - 1):
                #print(matrix[i][y], i, y)
                if i == x:
                    continue
                if self.matrix[i][y] != 0 or (i,y) == self.min_delta:
                    neighbours.append((i,y))
                    
        # если среди соседей есть стартовая точка цикла, то оставляем только её
        if self.circ[0] in neighbours:
            neighbours = []
            neighbours.append(self.circ[0])
        return neighbours

    # основная функция построения цикла
    # метод обхода в глубину
    def cycles(self, i, j, level = 0):
        # Ситуация, когда не возможно найти цикл (опорный план вырожденный)
        # В таком случае, прекращаем рекурсию и пытаемся изменить опорный план в методе mainloop
        if level > 25:
            return False
        if self.solution_flag:
            return True
        # ищем смежные элементы по таблице плана
        neighbours = self.find_neighbours((level + 1) % 2,i,j)
        # если нет смежных элементов
        if len(neighbours) == 0:
            if level > 0:
                self.circ = deepcopy(self.circ_hist[level - 1])
            return False
        for k in range(len(neighbours)):
            self.circ.append(neighbours[k])
            self.circ_hist[level + 1] = deepcopy(self.circ)
            #print(level + 1, self.circ_hist[level+1])
            
            # проверка, найден ли цикл
            # начальный и конечный элемент сотсояния списка на уровне level + 1 должны совпадать
            if self.circ_hist[level + 1][0] == self.circ_hist[level + 1][-1] and len(self.circ_hist[level + 1]) > 1:
                self.solution = level + 1
                self.solution_flag = True
                return True
            
            flag = self.cycles(neighbours[k][0], neighbours[k][1], level + 1)
            if not flag:
                # если нет цикла, возвращаемся к состоянию на предыдущем шаге
                self.circ = deepcopy(self.circ_hist[level])
                
    def change_u_v(self):
        res = None
        m = np.inf
        for i, item in enumerate(self.u):
            if item is None:
                for j in range(self.C.shape[1]):
                    if self.C[i][j] < m:
                        m = self.C[i][j]
                        res = (i,j)

        for i, item in enumerate(self.v):
            if item is None:
                for j in range(self.C.shape[0]):
                    if self.C[j][i] < m:
                        m = self.C[j][i]
                        res = (j, i)

        if res is not None:
            self.saved_cords = res
            x, y = res
            self.matrix[x][y] = None
            self.count_u_v()
    
    def mainloop(self):
        self.needs = self.matrix.shape[0] - 1
        self.stocks = self.matrix.shape[1] - 1
        if self.gui.switch:
            self.min_cost()
        else:
            self.nw_corner()
        print('Матрица опорного плана:\n',self.matrix)
        print('Стоимость перевозок: ',self.find_f())
        self.results.append(self.find_f())
        
        self.v = [None for i in range(self.C.shape[1])]
        self.u = [None for i in range(self.C.shape[0])]
        self.u[0] = 0
        
        self.count_u_v()
        if None in self.u or None in self.v:
            self.degenerate = True
            self.change_u_v()
        print('Потенциалы:\n',self.u, self.v)
        deltas = self.count_deltas()
        print('Относительные оценки:\n',deltas)
        # пока среди значений дельты есть хотя бы одно отрицательное число
        while any(val < 0 for val in deltas.values()):
              
            self.circ_hist = [None for i in range(100)]
            self.solution = 0
            self.solution_flag = False
            
            self.min_delta = min(deltas, key=deltas.get)
            print('Минимальная относительная оценка:\n',self.min_delta)
            self.circ = []
            self.circ.append(self.min_delta)
            self.circ_hist[0] = deepcopy(self.circ)
            
            self.cycles(self.min_delta[0],self.min_delta[1])
            
            self.circ = deepcopy(self.circ_hist[self.solution])
            
            if self.saved_cords is not None:
                x, y = self.saved_cords
                self.matrix[x][y] = 0
                self.saved_cords = None
                
            # проверка вырожденного плана
            nonBasis = list(deltas.keys())
            nonBasis.remove(self.min_delta)
            if len(self.circ) == 1:
                self.degenerate = True
                x, y = random.choice(nonBasis)
                self.matrix[x][y] = None
                #self.cycles(self.min_delta[0],self.min_delta[1])
                self.saved_cords = (x,y)
                continue
                
            print(f'Цикл: {self.circ}')
            self.circ = self.circ[1:-1]
            circ_vals = [self.matrix[coords[0]][coords[1]] for coords in self.circ]
            #print(circ_vals)
            # минимум среди значений отрицательных вершин цикла
            lmbda = min(circ_vals[::2])
            
            if lmbda == 0:
                continue
            
            self.matrix[self.min_delta[0]][self.min_delta[1]] = lmbda
            for k in range(len(self.circ)):
                i,j = self.circ[k]
                if k % 2 == 0:
                    self.matrix[i][j] -= lmbda
                else:
                    self.matrix[i][j] += lmbda
                    
            self.v = [None for i in range(self.C.shape[1])]
            self.u = [None for i in range(self.C.shape[0])]
            self.u[0] = 0
            # добавление результата в массив для графика
            self.results.append(self.find_f())
            self.count_u_v()
            print(f'Потенциалы\nu: {self.u}\nv: {self.v}')
            # проверка на вырожденность системы потенциалов
            if self.degenerate and (None in self.u or None in self.v):
                # если система вырождена, меняем план
                self.change_u_v()
            
            #print(deltas)
            print('Матрица базисного решения:\n',self.matrix)
            print('Стоимость перевозок: ',self.find_f())
            deltas = self.count_deltas()
            print('Относительные оценки:\n', deltas)

# вспомогательная функция построения цикла
# ищет всех соседей текущего элемента

class Gui():
    
    def __init__(self):
        self.window = Tk()
        self.window.geometry('800x800')
        # создаем фрейм для ввода данных
        self.input_frame = Frame(self.window)
        self.input_frame.pack()
        
        self.matrix_frame = None
        self.results_frame = None
        self.graphic_frame = None
        
        # добавляем метки полей ввода
        self.stocks_l = Label(self.input_frame,text="Количество поставщиков:")
        self.needs_l = Label(self.input_frame,text="Количество потребителей:")
        self.stocks_l.grid(row=0,column=1)
        self.needs_l.grid(row=1,column=1)
        # добавляем поля ввода
        self.stocks_e = Entry(self.input_frame)
        self.stocks_e.insert(END,'0')
        self.needs_e = Entry(self.input_frame)
        self.needs_e.insert(END,'0')
        self.stocks_e.grid(row=0,column=2)
        self.needs_e.grid(row=1,column=2)
        
        self.button_frame = Frame(master=self.window)
        self.button_frame.pack()
        
        self.build_matrix_entry = Button(master = self.button_frame,
                           command= self.add_grid,
                           height=2,
                           width=12,
                           text="Создать")
        self.build_matrix_entry.grid(row=2,column=0)
        
        self.switch = True
        self.methods = ['Метод северо-западного угла', 'Метод минимальной стоимости']
        self.current_method = StringVar()
        self.current_method.set(self.methods[self.switch])
        
        self.method_frame = Frame(master=self.window)
        self.method_frame.pack()
        self.current_method_label = Label(master=self.method_frame,textvariable=self.current_method)
        self.current_method_label.grid(row=0,column=0,)
        self.method_switch = Button(master=self.method_frame,
                                    command=self.change_method,
                                    height=2,
                                    width=12,
                                    text="Сменить метод")
        self.method_switch.grid(row=0,column=1)
        
        
    def change_method(self):
        self.switch = not self.switch
        self.current_method.set(self.methods[self.switch])

        
    def add_grid(self):
        # пересоздаем матрицу транспортной задачи по нажатию на кнопку
        if self.matrix_frame is not None:
            self.matrix_frame.pack_forget()
        
        if self.results_frame is not None:
            self.results_frame.pack_forget()
            
        if self.graphic_frame is not None:
            self.graphic_frame.pack_forget()
        
        # создаем фрейм для матрицы транспортной задачи
        self.matrix_frame = Frame(self.window)
        self.matrix_frame.pack()
        self.num_stocks = int(self.stocks_e.get())
        self.num_needs = int(self.needs_e.get())
        if self.num_needs == 0 or self.num_stocks == 0:
            return
        self.cells = []
        self.row_names = [Label(master=self.matrix_frame, text='Пункты')]
        self.row_names[0].grid(row=0,column=0)
        self.col_names = []
        for i in range(self.num_stocks):
            self.row_names.append(Label(master=self.matrix_frame,text=f'A{i+1}'))
            self.row_names[i+1].grid(row=i+1,column=0)
            for j in range(self.num_needs):
                cell = Entry(self.matrix_frame,width=10)
                cell.insert(END,'0')
                cell.grid(row=i+1,column=j+1)
                self.cells.append(cell)
                
                self.col_names.append(Label(master=self.matrix_frame,text=f'B{j+1}'))
                self.col_names[j].grid(row=0,column=j+1)
        self.row_names.append(Label(master=self.matrix_frame,text="Потребности"))
        self.row_names[-1].grid(row=self.num_stocks + 1,column=0)
        self.row_needs = []
        for j in range(self.num_needs):
            e = Entry(master=self.matrix_frame,width=10)
            e.insert(END,'0')
            e.grid(row=self.num_stocks+1,column=j+1)
            self.row_needs.append(e)
        
        self.col_names.append(Label(master=self.matrix_frame,text="Запасы"))
        self.col_names[-1].grid(row=0,column=self.num_needs + 1)
        self.col_stocks = []
        for i in range(self.num_stocks):
            e = Entry(master=self.matrix_frame,width=10)
            e.insert(END,'0')
            e.grid(row=i+1,column=self.num_needs+1)
            self.col_stocks.append(e)
            
            
        self.count_button = Button(master=self.button_frame,
                                   command=self.count,
                                   height=2,
                                   width=12,
                                   text="Рассчитать")
        self.count_button.grid(row=3,column=0)
        
    def init(self):
        self.matrix = np.zeros(self.num_stocks*self.num_needs).reshape((self.num_stocks,self.num_needs))
        self.C = []
        for i in range(len(self.cells)):
            self.C.append(float(self.cells[i].get()))
        self.C = np.array(self.C).reshape(self.num_stocks,self.num_needs)
        
        Z = [[]]
        for i in range(self.num_stocks):
            Z[0].append(float(self.col_stocks[i].get()))
            
        P = [[]]
        for i in range(self.num_needs):
            P[0].append(float(self.row_needs[i].get()))
        P[0].append(0)
        
        Z = np.array(Z)
        P = np.array(P)
        
        self.matrix = np.concatenate((self.matrix, Z.T), axis=1)
        self.matrix = np.concatenate((self.matrix, P), axis=0)
        self.counter = Counter(self)
        
    def count(self):
        self.init()
        self.counter.mainloop()
        if self.results_frame is not None:
            self.results_frame.pack_forget()
        
        if self.graphic_frame is not None:
            self.graphic_frame.pack_forget()
        
        self.graphic_frame = Frame(master=self.window)        
        self.graphic_frame.pack()
        
        # создание графика
        
        iterations = [i for i in range(len(self.counter.results))]
        print(self.counter.results)
        print(iterations)
        fig = Figure(figsize = (6,4),dpi=100)
        graphic = fig.add_subplot(111)
        graphic.set_xlabel('Iterations')
        graphic.set_ylabel('Cost function')
        graphic.plot(iterations,self.counter.results,color="red",label='Затраты на перевозку')
        
        # добавляем точки и их значения на график
        for i in range(len(self.counter.results)):
            graphic.annotate(
                self.counter.results[i],
                xy=(iterations[i],self.counter.results[i]),
                xytext=(5,5),
                textcoords='offset points',
                color='blue',
                size=7)
            graphic.scatter(iterations[i],self.counter.results[i], color="blue")
        # добавляем легенду к графику
        graphic.legend()
        
        canvas = FigureCanvasTkAgg(fig, master = self.graphic_frame)
        canvas.draw()
        canvas.get_tk_widget().pack()
        
        # добавление навигационной панели matplotlib
        toolbar = NavigationToolbar2Tk(canvas,self.graphic_frame)
        toolbar.update()
        canvas.get_tk_widget().pack()
        
        self.results_frame = Frame(self.window)
        self.results_frame.pack()

        t_res = Label(master=self.results_frame,text="Минимальные затраты на перевозку:")
        t_res.grid(row=0,column=0)
        
        self.result = StringVar()
        self.result.set(str(self.counter.results[-1]))
        self.res_label = Label(master=self.results_frame,textvariable=self.result)
        self.res_label.grid(row=0,column=1)

    def start(self):
        self.window.mainloop()

if __name__ == '__main__':
    gui = Gui()
    gui.start()