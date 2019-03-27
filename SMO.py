import sys
from PyQt5.QtWidgets import QWidget, QLabel, QApplication, QCheckBox, QComboBox, QPushButton, QLineEdit
from PyQt5.QtCore import Qt
import queue as qq
import numpy as np
import scipy as sp

 #время моделирования входного потока
def model_time_input(lambd, Tmax):
    t = [0]
    alpha = [np.random.uniform(0,1) for i in range(1,lambd * Tmax)]
    t.extend(- 1. / lambd * np.log(alpha))
    time_input = list(filter(lambda x: x < Tmax, sp.cumsum(t)))
    mean_time_input = (np.sum(t) / len(t)) * 60.
    return time_input, mean_time_input
 #время моделирования обслуживания
def model_time_service(q_size, flag):
    #
    if flag == True:
        t_ser = 4.7 / 60. #среднее время обслуживания
    else:
        if q_size == 0:
            t_ser = 5.5/ 60.
        elif q_size == 1 or q_size == 2:
            t_ser = 5./ 60.
        elif q_size == 3 or q_size == 4 or q_size == 5:
            t_ser = 4.5/ 60.
        elif q_size == 6:
            t_ser = 4./ 60.
    nu = 1. / t_ser
    alpha = np.random.uniform(0,1)
    time_service = - 1. / nu * np.log(alpha)
    return time_service

def SMO(lambd, flag, Tmax):
    q_ser = False #обслуживается ли кто-то терминалом
    arr_time_ser = []
    qque = qq.Queue(maxsize = 6) #очередь
    time_input, mean_time_input = model_time_input(lambd, Tmax)
    #обслуживание клиентов
    tmp = 0.0
    count_ser = 0
    count_fail = 0
    for el in time_input:
        time_ser = model_time_service(qque.qsize(), flag)
        arr_time_ser.append(time_ser)
        if q_ser == False and qque.empty():
            q_ser =True 
            tmp = el + time_ser  
        else: 
            if q_ser == False and qque.qsize() !=0:
                    el1 = qque.get()
                    q_ser =True
                    tmp = tmp + time_ser
                    qque.put(el)
            else:
                if el >= tmp:
                    q_ser = False
                    count_ser += 1 
                    if qque.qsize() !=0:
                        el1 = qque.get()
                        tmp = tmp + time_ser
                        q_ser = True
                        qque.put(el)
                    else:
                        q_ser = True
                        tmp = el + time_ser
                else:
                    if q_ser == True and qque.qsize() <= 5:
                        qque.put(el)
                    else:
                        count_fail += 1

    mean_time_ser = (np.sum(arr_time_ser)/len(arr_time_ser))*60.
    koef_load = mean_time_input / mean_time_ser
    return koef_load, mean_time_ser

class Interface(QWidget):
    def __init__(self):
        super().__init__()
        self.Tmax = 1 #время, в течение которого моделируется работа системы
        self.flag = True
        self.lambd = 12 #интенсивность входного потока в час
        self.initUI()

    def initUI(self):
        self.lbl1 = QLabel("Среднее время обслуживания:", self)
        cb = QCheckBox('4,7 мин', self)
        cb.move(10, 25)
        self.lbl1.move(10, 10)
        cb.toggle()
        cb.stateChanged.connect(self.changeTitle)

        self.lbl11 = QLabel("Интенсивность входного потока:", self)
        self.lbl11.move(200, 10)
        self.le = QLineEdit("12",self)
        self.le.move(200, 25)
        self.le.textEdited[str].connect(self.onChanged)

        self.lbl2 = QLabel("Смоделировать работу системы в течение:", self)
        self.lbl2.move(10, 50)
        combo = QComboBox(self)
        combo.addItems(["1", "8", "40"])
        combo.move(10, 70) 
        combo.activated[str].connect(self.onActivated)
        btn = QPushButton('Смоделировать', self)
        btn.move(10, 100)
        btn.resize(200,30)
        self.lbl6 = QLabel("Результаты моделирования:", self)
        self.lbl6.move(10, 130)
        self.lbl3 = QLabel("Коэффициент загрузки терминала:", self)
        self.qle1 = QLabel(" ",self)
        self.qle1.move(200, 150)
        self.qle1.resize(200,15)
        self.qle2 = QLabel(" ",self)
        self.qle2.move(200, 170)
        self.qle2.resize(200,15)
        self.lbl5 = QLabel("Факт. среднее время обслуживания:", self)
        self.lbl3.move(10, 150)
        self.lbl5.move(10, 170)
        # связывает событие нажатия на кнопку с методом
        btn.clicked.connect(self.buttonClicked)
        self.setGeometry(300, 300, 400, 200)
        self.setWindowTitle('SMO')
        self.show()

    def onActivated(self, text):
        self.Tmax = int(text)

    def changeTitle(self, state):

        if state == Qt.Checked:
            self.flag = True
        else:
            self.flag = False

    def onChanged(self, text):
        if text == "":
            self.lambd = 12
            self.le.setText(str(self.lambd))
        else:
            self.lambd = int(text)
        self.setFocus()
           
    def buttonClicked(self):
        koef_load, mean_time_ser  = SMO(self.lambd, self.flag, self.Tmax)
        self.qle1.setText(str(koef_load))
        self.qle2.setText(str(mean_time_ser) + ' мин')
        
if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    ex = Interface()
    sys.exit(app.exec_())
