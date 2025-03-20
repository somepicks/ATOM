import sys
from PyQt5.QtWidgets import *
import numpy as np
import tab_trade
import tab_backtest
import tab_chart_table
import tab_optimize
import tab_set
# np.set_printoptions(threshold=sys.maxsize)
import subprocess
import win32api
import time
import os

class MyApp(QWidget):

    def __init__(self):
        super().__init__()
        self.np_array = np.array([])
        # StyleSheet_Qtextedit = "color: #B4B4B4; background-color: #353535; selection-background-color: #B4B4B4;" \
        #                        "border-color: black; header-color: black;font: 11pt 나눔고딕; "
        # StyleSheet_Qtextedit = "color: #B4B4B4; background-color: #353535; selection-background-color: #B4B4B4;" \
        #                        "border-color: black; font: 11pt 나눔고딕; "

        self.chart_table = tab_chart_table.Window()
        self.backtest = tab_backtest.Window(self.chart_table)
        self.optimize = tab_optimize.Window()
        self.trade = tab_trade.Window()
        # self.set = tab_set.Window()
        self.initUI()
        self.setMinimumSize(600,400)


        # self.setStyleSheet(StyleSheet_Qtextedit)
        # opacity_effect = QGraphicsOpacityEffect(self.Mylabel)
        # opacity_effect.setOpacity(0.3)  # 투명도를 여기서 정할 수 있다.0은 완전 투명 1은 전혀 투명하지 않은 것이다.
        # self.Mylabel.setGraphicsEffect(opacity_effect)


        self.tabs.currentChanged.connect(self.on_tab_change)
        self.backtest.QCB_market.activated[str].connect(self.select_chart)
        self.backtest.QPB_start.clicked.connect(self.select_chart)


    def initUI(self):
        self.tabs = QTabWidget()
        self.tabs.addTab(self.backtest, '백테스트')
        self.tabs.addTab(self.optimize, '최적화')
        self.tabs.addTab(self.trade, '트레이딩')
        self.tabs.addTab(self.chart_table, '차트테이블')
        # self.tabs.addTab(self.set, '설정')
        vbox = QVBoxLayout()
        vbox.addWidget(self.tabs)
        self.setLayout(vbox)
        self.setWindowTitle('ATOM')
        # self.setGeometry(0, 0, 800, 500) #x,y,w,h
        self.show()

    def on_tab_change(self, index):
        # 2번 탭이 활성화되면 1번 탭에 신호를 보내거나 작업 수행
        if index == 2:  # 탭 인덱스는 0부터 시작, 1이면 두 번째 탭
            self.chart_table.QCB_market.setCurrentText('리얼차트')
            self.chart_table.select_market('리얼차트')
        if index == 0:  # 탭 인덱스는 0부터 시작, 1이면 두 번째 탭
            if self.backtest.QCB_market.currentText() != '':
                self.chart_table.select_market(self.backtest.QCB_market.currentText())
    def select_chart(self):
        self.chart_table.QCB_market.setCurrentText(self.backtest.QCB_market.currentText())
        if self.backtest.QCB_market.currentText() != '':
            self.chart_table.select_market(self.backtest.QCB_market.currentText())
    # def select_chart2(self):
    #     self.chart_table.QCB_market.setCurrentText(self.backtest.QCB_market.currentText())
    #     if self.backtest.QCB_market.currentText() != '':
    #         self.chart_table.select_market(self.backtest.QCB_market.currentText())

if __name__ == '__main__':
    import sys
    def ExceptionHook(exctype, value, traceback):
        sys.__excepthook__(exctype, value, traceback)
        sys.exit(1)
    sys.excepthook = ExceptionHook  # 예외 후크 설정 부분 (에러가 표시되지 않으면서 종료되는증상을 방지하기 위함)

    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())



'''
안녕하세요.
KIS Developers 팀입니다.

우선 현재 유량제한이 변경된 사항은 없습니다. 실전투자의 경우 REST 1초당 20건이 맞습니다.

sleep을 주었는데도 유량제한 초과로 이슈를 겪는 고객님들 중
아래 mount 옵션 추가로 REST API 호출오류 이슈를 해결한 사례가 있어 공유드립니다. 

rs = requests.session()
rs.mount('https://', requests.adapters.HTTPAdapter(pool_connections=3, pool_maxsize=10, max_retries=3))
res = rs.get(URL, headers=headers, params=params)

다만 국내휴장일조회(TCA0903R) 서비스는 당사 원장서비스와 연관되어 있어 
단시간 내 다수 호출시 당사 서비스에 영향을 줄 수 있어 "가급적 1일 1회 호출" 부탁드립니다.

감사합니다.'''