from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QToolButton, QMessageBox, QLabel, QMainWindow, QMenuBar, \
    QMenu, QAction, QDialog
from PyQt5.QtWidgets import QGridLayout, QHBoxLayout, QVBoxLayout, QStyleFactory
from PyQt5.QtCore import Qt, QEvent, pyqtSignal, QSignalMapper, QSize, QTimer, QThread
from PyQt5.QtGui import QFont, QIcon, QPixmap
import PyQt5.sip
import numpy as np
import random
import sys


# 重构按钮
class MyButton(QToolButton):
    LeftClick = pyqtSignal()
    RightClick = pyqtSignal()
    DoubleClick = pyqtSignal()

    def __init__(self, *arg, **kwargs):
        super(MyButton, self).__init__(*arg, **kwargs)
        self.state = {'is_opened': False, 'is_marked': False}

    def mousePressEvent(self, event): # 重载鼠标点击事件
        if event.button() == Qt.RightButton:
            self.RightClick.emit()
        elif event.button() == Qt.LeftButton:
            self.LeftClick.emit()

    def mouseDoubleClickEvent(self, event): #重载鼠标双击事件
        if event.button() == Qt.LeftButton:
            self.DoubleClick.emit()

    def setMarked(self, b=True): # 设置标记状态
        self.state['is_marked'] = b

    def setOpened(self, b=True): # 设置翻开状态
        self.state['is_opened'] = b


class MineWidget(QWidget):
    # 定义信号
    GameOver = pyqtSignal() #游戏结束信号，控制界面关闭
    Marked = pyqtSignal(bool) #标记信号，控制标记数量
    Time = pyqtSignal(int) # 时间信号
    #定义字体
    font = QFont()
    font.setFamily('黑体')
    font.setPixelSize(20)
    font.setBold(True)

    def __init__(self, model=1):  # model为游戏难度选择0，1，2三中难度
        super(MineWidget, self).__init__()
        if model == 1:
            self.notmine_quantity = 90 # 非雷数
            self.size = (10, 10)
            self.mine_quantity = 10 # 雷数
        elif model == 2:
            self.mine_quantity = 40
            self.size = (16, 16)
            self.notmine_quantity = 16 * 16 - 40
        elif model == 3:
            self.mine_quantity = 99
            self.size = (16, 30)
            self.notmine_quantity = 16 * 30 - 99

        self.model = model
        self.__firstclick = True
        self._can_rightClicked = True

        self.buttons_dictionary = {}
        layout = QGridLayout()# 布局
        self.LeftClickedSignalMap = QSignalMapper(self)  # 建立信号管理对象
        self.RightClickedSignalMap = QSignalMapper(self)  # 建立信号管理对象
        self.DoubleClickedSignalMap = QSignalMapper(self)  # 建立信号管理对象

        # 建立按钮阵
        for i in range(self.size[0]):
            for j in range(self.size[1]):
                button = MyButton(self) #创建按钮
                # button.setText(str(self.MinesArray[i][j])) # 设置显示信息 ！！！！！！！
                button.setIcon(QIcon('0')) # 遮住数字
                button.setFont(self.font) #设置字体
                self.buttons_dictionary[(i, j)] = button #用字典把按钮跟位置信息对应

                button.LeftClick.connect(self.LeftClickedSignalMap.map)  # 将鼠标左击信号放在管理对象的信号仓库
                button.RightClick.connect(self.RightClickedSignalMap.map)
                button.DoubleClick.connect(self.DoubleClickedSignalMap.map)

                mycode = str(i) + '_' + str(j) #位置编码
                self.LeftClickedSignalMap.setMapping(button, mycode)  # 为对象建立参数联系
                self.RightClickedSignalMap.setMapping(button, mycode)
                self.DoubleClickedSignalMap.setMapping(button, mycode)


                button.setMinimumSize(50, 50)
                button.setMaximumSize(100, 100)
                button.setStyleSheet("QToolButton{background-color:rgb(99,184,255);}")
                button.setToolButtonStyle(Qt.ToolButtonIconOnly) #不显示数字
                layout.addWidget(button, i, j) #布局

        self.LeftClickedSignalMap.mappedString.connect(self.LeftClicked)  # 将信号仓库的全部信号连上槽函数
        self.RightClickedSignalMap.mappedString.connect(self.RightClicked)
        self.DoubleClickedSignalMap.mappedString.connect(self.double_clicked)

        layout.setSpacing(0)
        self.setLayout(layout)


    def double_clicked(self, index_code):
        # 将位置坐标码翻译回int
        x, y = index_code.split('_')
        x, y = int(x), int(y)
        _currentbutton = self.buttons_dictionary[(x, y)]  # 获得该按钮

        if not _currentbutton.state['is_marked']:
            # 获取上下左右位置
            up, left, right, down = x - 1, y - 1, y + 1, x + 1
            position_code = {'UL': str(x - 1) + '_' + str(y - 1),
                             'U': str(x - 1) + '_' + str(y),
                             'UR': str(x - 1) + '_' + str(y + 1),
                             'L': str(x) + '_' + str(y - 1),
                             'R': str(x) + '_' + str(y + 1),
                             'DL': str(x + 1) + '_' + str(y - 1),
                             'D': str(x + 1) + '_' + str(y),
                             'DR': str(x + 1) + '_' + str(y + 1)}

            __x = self.size[0] - 1 # 位置边界值
            __y = self.size[1] - 1 # 位置边界值

            # 处理边缘的按钮
            if up < 0:
                if left < 0: #左上角
                    for value in [position_code['R'], position_code['D'], position_code['DR']]:
                        self.LeftClicked(value)
                elif right > __y: #右上角
                    for value in [position_code['L'], position_code['D'], position_code['DL']]:
                        self.LeftClicked(value)
                else: #上边缘
                    for value in [position_code['R'], position_code['D'], position_code['DR'], position_code['L'],
                                  position_code['DL']]:
                        self.LeftClicked(value)
            elif down > __x:
                if left < 0: #左下角
                    for value in [position_code['R'], position_code['U'], position_code['UR']]:
                        self.LeftClicked(value)
                elif right > __y: # 右下角
                    for value in [position_code['L'], position_code['U'], position_code['UL']]:
                        self.LeftClicked(value)
                else: # 下边缘
                    for value in [position_code['R'], position_code['U'], position_code['UR'], position_code['L'],
                                  position_code['UL']]:
                        self.LeftClicked(value)
            elif left < 0: #左边缘
                for value in [position_code['U'], position_code['UR'], position_code['R'], position_code['DR'],
                              position_code['D']]:
                    self.LeftClicked(value)
            elif right > __y: #右边缘
                for value in [position_code['U'], position_code['UL'], position_code['L'], position_code['DL'],
                              position_code['D']]:
                    self.LeftClicked(value)
            else: # 中间的直接打开
                for value in position_code.values():
                    self.LeftClicked(value)
                    print(value)

            print('DoubleClicking-- Button!!!')

    # 判断是否是雷，翻出数字
    def LeftClicked(self, index_code):

        # 对位置解码
        x, y = index_code.split('_')
        x, y = int(x), int(y)
        _currentbutton = self.buttons_dictionary[(x, y)] #获得该按钮

        if self.__firstclick: #若是第一次点击
            # 初始化地雷位置，避免第一次点击踩雷
            self.MinesArray = self.initMinesArray(mineQuantity=self.mine_quantity, out_x=x, out_y=y, model=self.model)  # 建立雷数阵
            for i in range(self.size[0]):
                for j in range(self.size[1]):
                    self.buttons_dictionary[(i, j)].setText(str(self.MinesArray[i][j]))  # 设置显示信息

            self.timer = QTimer() # 建立计时器
            self._runtime = 0
            self.timer.start(1000)
            self.timer.timeout.connect(self.emitTime) #每一秒发射一次信号
            self.__firstclick = False  # 开关变化


        if not _currentbutton.state['is_opened'] : # 若此按钮还未被打开

            if not _currentbutton.state['is_marked']: # 没被标记，被标记不处理，不打开
                if 10 == int(_currentbutton.text()): # 此位置有雷
                    self.timer.stop() #时间停止

                    _currentbutton.setIcon(QIcon("Cosmo-Mine.ico"))
                    _currentbutton.setStyleSheet("QToolButton{background-color:white;}")
                    _currentbutton.setIconSize(QSize(30, 30))
                    self.update()
                    self.showAllMines() # 打开所有雷
                    # 弹出提示，游戏结束
                    box = QMessageBox(QMessageBox.Information, '游戏结束', '很遗憾！！！您踩到雷了！')
                    box.setWindowIcon(QIcon("Cosmo-Mine.ico"))
                    box.setModal(True)
                    box.exec()
                    self.GameOver.emit() #发出游戏结束信号
                else:
                    _currentbutton.setStyleSheet("QToolButton{background-color:white;}") #
                    _currentbutton.setOpened(True)
                    if _currentbutton.text() != '0': # 只展示非零的数字
                        _currentbutton.setToolButtonStyle(Qt.ToolButtonTextOnly)
                    else:# 若此开关周围没有雷
                        self.double_clicked(index_code)  # 打开周围按钮

                    self.notmine_quantity -= 1 # 非地雷按钮数量-1
                    if self.notmine_quantity == 0: # 若非地雷按钮数量为0，游戏胜利
                        self.timer.stop()
                        box = QMessageBox(QMessageBox.Information, '游戏完成', '恭喜大神！！!')
                        box.setWindowIcon(QIcon("Cosmo-Mine.ico"))
                        box.setModal(True)
                        box.exec()
                        self.GameOver.emit() #发出游戏结束信号

    def RightClicked(self, index_code):
        if self._can_rightClicked: #若允许右键单击
            x, y = index_code.split('_') #位置解码
            x, y = int(x), int(y)
            _currentbutton = self.buttons_dictionary[(x, y)]
            print('opened:', _currentbutton.state['is_opened'],'marked', _currentbutton.state['is_marked'])
            if  not _currentbutton.state['is_opened']:
                if _currentbutton.state['is_marked'] : #若已被标记
                    _currentbutton.setIcon(QIcon('0')) # 取消棋子图标
                    _currentbutton.setMarked(False) #取消标记
                    self.Marked.emit(False)
                else:
                    _currentbutton.setIcon(QIcon("flag_red.ico"))
                    _currentbutton.setIconSize(QSize(30, 30))
                    _currentbutton.setMarked(True)
                    self.Marked.emit(True)

        print('RightClicking- Button!!!')


    def initMinesArray(self, mineQuantity, out_x, out_y, model= 1):
        _x = self.size[0]
        _y = self.size[1]
        arr = np.zeros(self.size, dtype=np.int8)
        while arr.sum() != mineQuantity:
            a = random.randint(0, _x - 1)
            b = random.randint(0, _y - 1)
            if (out_x - model)< a <(out_x + model) and (out_y - model) < b < (out_y + model):
                pass
            else:
                arr[a][b] = 1  # 不断产生1，就是雷

        print(arr.sum())

        #  把矩阵扩大2行，2列，在周围补零，方便计算9宫格的和
        disp_arr = np.zeros(self.size, dtype=np.int8)  # 创建一个全零矩阵
        expanded_arr = np.zeros((_x + 2, _y + 2), dtype=np.int8)
        expanded_arr[1:_x + 1, 1:_y + 1] = arr  # 在中间补充原矩阵

        for i in range(_x):
            for j in range(_y):
                temp_arr = expanded_arr[i:i + 3, j:j + 3]  # 截取九宫格内
                disp_arr[i][j] = temp_arr.sum()  # 计算九宫格数和，就是雷数

        for i in range(_x):
            for j in range(_y):
                if arr[i][j] == 1:  # 对原来的雷阵判断， 如果是雷
                    disp_arr[i][j] = 10  # 把该位置改为数字10，便于区分
        print('new array !!!')
        return disp_arr

    def showAllMines(self):
        for button in self.buttons_dictionary.values():
            if button.text() == '10':
                button.setIcon(QIcon("Cosmo-Mine.ico"))
                button.setStyleSheet("QToolButton{background-color:white;}")
                button.setIconSize(QSize(30, 30))
                self.update()

    def emitTime(self): #发送时间函数
        self._runtime += 1
        self.Time.emit(self._runtime)

    def setUnRigthclicked(self): # 设置右键标记不可用
        self._can_rightClicked = False

# 主窗口类
class Mainwindow(QMainWindow):
    # 设置字体
    font = QFont()
    font.setFamily('黑体')
    font.setPixelSize(40)
    font.setBold(True)

    def __init__(self, *argu):
        super(Mainwindow, self).__init__(*argu)
        self.setWindowIcon(QIcon('./Cosmo-Mine.ico')) # 设置窗口图标
        self.setWindowTitle('扫雷') # 设置窗口标题
        self.resize(600, 600) # 设置窗口大小
        self.positionctrl = True # 控制位置变化的开关

        self.initMenu() #初始化菜单函数

    # 初始化菜单函数
    def initMenu(self):
        menubar = QMenuBar() # 创建菜单栏

        #一级菜单选项
        _difficulty = QMenu('难度', self) #创建子菜单
        _quit = QAction('退出', self)

        # 二级菜单选项
        _first = QAction('10 * 10', self)
        _second = QAction('16 * 16', self)
        _third = QAction('16 * 30', self)

        for act in [_first, _second, _third]:# 导入二级菜单
            _difficulty.addAction(act)
            _difficulty.addSeparator()

        # 建立菜单并填充内容
        setting = menubar.addMenu('开始')
        setting.addMenu(_difficulty)
        setting.addSeparator()
        setting.addAction(_quit)

        self.setMenuBar(menubar)

        # 连接菜单项点击响应函数
        _first.triggered.connect(lambda: self.initMainWidget(1))
        _second.triggered.connect(lambda: self.initMainWidget(2))
        _third.triggered.connect(lambda: self.initMainWidget(3))

        _quit.triggered.connect(app.instance().quit)

    # 初始化地雷方阵控件
    def initMainWidget(self, model=1): # 初始化地雷区控件
        self.minewidget = MineWidget(model=model)
        self.mineQuantity = self.minewidget.mine_quantity #读出地雷总个数

        # 创建下方时间、地雷数量标签
        _mineQuantityIcon = QLabel(self)
        self._mineQuantityLabel = QLabel(str(self.mineQuantity), self)
        _timeIcon = QLabel(self)
        self._timeLabel = QLabel('0', self)

        self.positionctrl = True #一个用于控制位置变化的开关
        self.handleTimeBug = False

        #为标签设置字体和图标
        self._mineQuantityLabel.setFont(self.font)
        self._timeLabel.setFont(self.font)
        _mineQuantityIcon.setPixmap(QPixmap('Cosmo-Mine.ico').scaled(50, 50))
        _timeIcon.setPixmap(QPixmap('Date-Timer.ico').scaled(50, 50))

        # 设置布局
        downLayout = QHBoxLayout()
        downLayout.addWidget(_mineQuantityIcon)
        downLayout.addWidget(self._mineQuantityLabel)
        downLayout.addWidget(_timeIcon)
        downLayout.addWidget(self._timeLabel)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.minewidget)
        mainLayout.addLayout(downLayout)
        mainLayout.setAlignment(Qt.AlignHCenter)

        self._widget = QWidget(self)
        self._widget.setLayout(mainLayout)
        self.setCentralWidget(self._widget)

        # 三个操作信号连接
        self.minewidget.GameOver.connect(self._widget.close)
        self.minewidget.Marked.connect(self.resetMineLabel)
        self.minewidget.Time.connect(self.showtime)

    # 控制地雷数量变化函数
    def resetMineLabel(self, Bool):
        if Bool == True:# True表示标记
            if self.mineQuantity == 0: #当标记数量用完
                self.minewidget.setUnRigthclicked() #设置地雷控件不能再进行右键标记
            else:
                self.mineQuantity -= 1 #标记数量-1
        else: #取消标记
            self.mineQuantity += 1  #标记数量+1
        self._mineQuantityLabel.setText(str(self.mineQuantity)) #更新标签显示数据

    # 时间展示函数，传入时间
    def showtime(self, _time):
        if _time == 1:
            self.handleTimeBug = True # 处理一个小小bug
        if self.handleTimeBug:
            if _time < 60: #60秒内时间
                self._timeLabel.setText(str(_time))
            else:
                # 大于一分钟时间，转化成'分：秒'形式
                minu = int(_time / 60)
                second = _time % 60
                self._timeLabel.setText('%d : %d' % (minu, second))


    def setDesktopGeometry(self, width, height): #一个获取显示器像素函数
        self.desktop_width = width
        self.desktop_height = height
        print(type(self.desktop_height))

    def resizeEvent(self, event): # 一个控制界面位置函数
        if self.positionctrl: #True表示是新创建一个游戏
            pos_x = (self.desktop_width - self.width()) / 2
            pos_y = (self.desktop_height - self.height()) / 2
            self.move(int(pos_x), int(pos_y))
            self.positionctrl = False


if __name__ == '__main__':
    app = QApplication(sys.argv)
    print(app.desktop().width(), app.desktop().height())
    app.setStyle(QStyleFactory.create('Windows'))
    window = Mainwindow()
    window.setDesktopGeometry(app.desktop().width(), app.desktop().height())
    window.show()

    app.exit(app.exec_())
