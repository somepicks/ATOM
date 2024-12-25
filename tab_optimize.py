from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtCore import *
import sys
import pandas as pd

pd.set_option('display.max_columns',None) #모든 열을 보고자 할 때
pd.set_option('display.max_colwidth', None)
pd.set_option('display.width',1500)
pd.set_option("display.unicode.east_asian_width", True)
pd.set_option('mode.chained_assignment',  None) # SettingWithCopyWarning 경고를 끈다

class Window(QMainWindow):
    def __init__(self, parent=None):
        super(Window, self).__init__()
        self.parent = parent
        self.setGeometry(0, 0, 1800, 1100)

        self.wid = QWidget()
        self.setCentralWidget(self.wid)

        self.globallayout = QVBoxLayout()
        self.split_V = QSplitter(Qt.Vertical)
        self.initUI()
        self.df_buy = pd.DataFrame()
        self.df_sell = pd.DataFrame()
        self.list_check_buy = []
        self.list_check_sell = []

    def initUI(self):
        label_stg = QLabel('전략')
        label_opt = QLabel('최적화')
        label_convert = QLabel('변환')
        label_convert.setFixedWidth(50)
        label_range = QLabel('범위')
        label_convert2 = QLabel('변환')
        label_convert2.setFixedWidth(50)
        label_result = QLabel('결과')
        label_stg.setAlignment(Qt.AlignCenter)
        label_opt.setAlignment(Qt.AlignCenter)
        label_convert.setAlignment(Qt.AlignCenter)
        label_range.setAlignment(Qt.AlignCenter)
        label_convert2.setAlignment(Qt.AlignCenter)
        label_result.setAlignment(Qt.AlignCenter)
        # StyleSheet_Qtextedit = "color: #353535; background-color: #BEBEBE; selection-background-color: #B4B4B4;" \
        #                        "border-color: black; header-color: black;font: 11pt 나눔고딕; "
        StyleSheet_Qtextedit = "color: #353535; background-color: #BEBEBE; selection-background-color: #B4B4B4;" \
                               "border-color: black; font: 11pt 나눔고딕; "
        label_stg.setStyleSheet(StyleSheet_Qtextedit)
        label_opt.setStyleSheet(StyleSheet_Qtextedit)
        label_convert.setStyleSheet(StyleSheet_Qtextedit)
        label_range.setStyleSheet(StyleSheet_Qtextedit)
        label_convert2.setStyleSheet(StyleSheet_Qtextedit)
        label_result.setStyleSheet(StyleSheet_Qtextedit)


        text_stg_buy = QTextEdit()
        text_stg_sell = QTextEdit()
        text_opt_buy = QTextEdit()
        text_opt_sell = QTextEdit()
        text_result_buy = QTextEdit()
        text_result_sell = QTextEdit()
        # StyleSheet_Qtextedit = "color: #e5e5e5; background-color: rgb(50, 50, 60); selection-background-color: #B4B4B4;" \
        #                        "border-color: black; header-color: black; font: 11pt 나눔고딕; "
        StyleSheet_Qtextedit = "color: #e5e5e5; background-color: rgb(50, 50, 60); selection-background-color: #B4B4B4;" \
                               "border-color: black; font: 11pt 나눔고딕; "
        text_stg_buy.setStyleSheet(StyleSheet_Qtextedit)
        text_stg_sell.setStyleSheet(StyleSheet_Qtextedit)
        text_opt_buy.setStyleSheet(StyleSheet_Qtextedit)
        text_opt_sell.setStyleSheet(StyleSheet_Qtextedit)
        text_result_buy.setStyleSheet(StyleSheet_Qtextedit)
        text_result_sell.setStyleSheet(StyleSheet_Qtextedit)

        self.table_buy = QTableWidget()
        self.table_buy.setSortingEnabled(True)
        self.table_sell = QTableWidget()
        self.table_sell.setSortingEnabled(True)
        # StyleSheet_Qtable = "color: #B4B4B4; background-color: rgb(50, 50, 60); selection-background-color: #B4B4B4; " \
        #                     "border-color: black; header-color: black; font: 11pt 나눔고딕;"
        StyleSheet_Qtable = "color: #B4B4B4; background-color: rgb(50, 50, 60); selection-background-color: #B4B4B4; " \
                            "border-color: black; font: 11pt 나눔고딕;"
        self.table_buy.setStyleSheet(StyleSheet_Qtable)
        self.table_sell.setStyleSheet(StyleSheet_Qtable)

        btn_buy = QPushButton('▶')
        btn_sell = QPushButton('▶')
        btn_buy_result = QPushButton('▶')
        btn_sell_result = QPushButton('▶')
        btn_buy.setFixedWidth(50)
        btn_sell.setFixedWidth(50)
        btn_buy_result.setFixedWidth(50)
        btn_sell_result.setFixedWidth(50)
        btn_buy.clicked.connect(lambda: self.configure_table(self.table_buy,text_stg_buy,text_opt_buy,text_result_buy,self.list_check_buy,'buy'))
        btn_sell.clicked.connect(lambda: self.configure_table(self.table_sell, text_stg_sell,text_opt_sell,text_result_sell,self.list_check_sell,'sell'))
        btn_buy_result.clicked.connect(lambda: self.configure_result(self.table_buy,text_result_buy,self.df_buy,self.list_check_buy))
        btn_sell_result.clicked.connect(lambda: self.configure_result(self.table_sell, text_result_sell,self.df_sell,self.list_check_sell))

        self.split_H1 = QSplitter(Qt.Horizontal)
        self.split_H1.setChildrenCollapsible(False) #splitter 이동으로 인해 창이 사라지는 것을 방지
        self.split_H1.addWidget(label_stg)
        self.split_H1.addWidget(label_opt)
        self.split_H1.addWidget(label_convert)
        self.split_H1.addWidget(label_range)
        self.split_H1.addWidget(label_convert2)
        self.split_H1.addWidget(label_result)
        self.split_H1.setSizes([400,400,50,400,50,200])
        self.split_V.addWidget(self.split_H1)

        self.split_H2 = QSplitter(Qt.Horizontal)
        self.split_H2.setChildrenCollapsible(False) #splitter 이동으로 인해 창이 사라지는 것을 방지
        self.split_H2.addWidget(text_stg_buy)
        self.split_H2.addWidget(text_opt_buy)
        self.split_H2.addWidget(btn_buy)
        self.split_H2.addWidget(self.table_buy)
        self.split_H2.addWidget(btn_buy_result)
        self.split_H2.addWidget(text_result_buy)
        self.split_H2.setSizes([400,400,50,400,50,200])

        self.split_V.addWidget(self.split_H2)

        self.split_H3 = QSplitter(Qt.Horizontal)
        self.split_H3.setChildrenCollapsible(False) #splitter 이동으로 인해 창이 사라지는 것을 방지
        self.split_H3.addWidget(text_stg_sell)
        self.split_H3.addWidget(text_opt_sell)
        self.split_H3.addWidget(btn_sell)
        self.split_H3.addWidget(self.table_sell)
        self.split_H3.addWidget(btn_sell_result)
        self.split_H3.addWidget(text_result_sell)
        self.split_H3.setSizes([400,400,50,400,50,200])

        self.split_V.addWidget(self.split_H3)

        self.globallayout.addWidget(self.split_V)

        self.wid.setLayout(self.globallayout)
        self.split_V.setSizes([20,500,500])

        self.split_H1.splitterMoved.connect(self.moveSplitter)
        self.split_H2.splitterMoved.connect(self.moveSplitter)
        self.split_H3.splitterMoved.connect(self.moveSplitter)

        QTimer.singleShot(0, lambda: self.split_H1.splitterMoved.emit(0, 0))
        # self.split_H1.splitterMoved
        # self.moveSplitter(0,self.split_H1.at )

    def moveSplitter( self, index, pos ):
        # splt = self._spltA if self.sender() == self._spltB else self._spltB
        self.split_H1.blockSignals(True)
        self.split_H2.blockSignals(True)
        self.split_H3.blockSignals(True)
        self.split_H1.moveSplitter(index, pos)
        self.split_H2.moveSplitter(index, pos)
        self.split_H3.moveSplitter(index, pos)
        self.split_H1.blockSignals(False)
        self.split_H2.blockSignals(False)
        self.split_H3.blockSignals(False)
        sizes = self.sender().sizes()
        for index in range(self.split_V.count()):
            self.split_V.widget(index).setSizes(sizes)

    def configure_table(self,table,stg,opt,text_result,list_ckbox,select_type):
        table.clear()
        text_result.clear()
        stg = stg.toPlainText() #전략 불러오기
        opt = opt.toPlainText()
        stg_lines = stg.splitlines() # str을 개행으로 나눠 리스트 저장
        opt_lines = opt.splitlines()
        list_ckbox=[]
        try:
            list_vars = []
            dict_vars = {}
            for text in stg_lines[:]: #  #들어가있지 않은 문자열 리스트로 저장
                if not text.find('#'):
                    stg_lines.remove(text)
            for text in opt_lines[:]:
                if not text.find('#'):
                    opt_lines.remove(text)
        except:
            if len(stg_lines) != len(opt_lines):
                print('라인이 같지 않음 확인 필요')
        for idx, text_opt in enumerate(opt_lines): #opt 한줄씩 불러오기
            num = text_opt.count('self.vars')  # self.vars수량 찾기
            text_opt = text_opt.replace("self.vars", '')  # self.vars를 지우기
            if num > 0: # self.vars가 있을 경우만 실행
                for n in range(num):
                    list_opt = list(text_opt) # opt 한글자씩 리스트로 만들기
                    txt_idx = list_opt.index('[')  # 대괄호 위치 찾기
                    idx_start = txt_idx  # opt 대괄호 시작 위치를 저장
                    text_stg = stg_lines[idx]  # opt랑 같은줄의 전략 불러오기
                    var_stg = ''
                    while text_stg[txt_idx].isdigit() or text_stg[txt_idx]=='-' or text_stg[txt_idx]=='_' or text_stg[txt_idx]=='.':  # stg에서 숫자, '-','_'가 아닐 때 까지 반복
                        text = text_stg[txt_idx]
                        var_stg = var_stg + text #최적값 저장
                        txt_idx += 1
                        if txt_idx == len(text_stg):  # 끝까지 가면 index out of range에러나기 때문에 강제로 탈출
                            break
                    var_num = ''
                    while list_opt[idx_start] != ']':  # 대괄호 나오기 전 까지 list_opt삭제
                        del list_opt[idx_start]
                        var_num = var_num + list_opt[idx_start]
                    if list_opt[idx_start] == ']':  # 대괄호 나오면 list_opt삭제
                        del list_opt[idx_start]
                    var_num = '[' + var_num #  1] 형태를 [1] 형태로 변환
                    list_opt.insert(idx_start, var_stg) # list opt에 변수 삽입
                    list_vars.append(var_stg) # list_vars에 변수 추가
                    text_range = text_opt
                    text_opt = ''.join(s for s in list_opt)

                    try:
                        text_idx = text_opt.index('[')
                        text_range_s = text_range[:text_idx]
                        text_range_e = stg_lines[idx][text_idx-1:]
                        text_range = text_range_s + text_range_e
                    except:
                        pass
                    dict_vars[var_num]=[var_stg,text_range] #dict_vars에 저장
        dict_vars = dict(('self.vars' + key, val) for (key, val) in dict_vars.items())
        df = pd.DataFrame(dict_vars)
        if not df.empty:
            df = df.transpose()
            df['self.vars'] = df.index
            df['시작값'] = ''
            df['종료값'] = ''
            df['간격'] = ''
            df['범위'] = ''
            df['상한조건'] = ''
            df.rename(columns={1: '전략', 0: '최적값'}, inplace=True)  # 컬럼명 변경
            df = df[['전략', 'self.vars', '시작값', '종료값', '간격', '최적값','범위','상한조건']]

            table.setSortingEnabled(False)
            table.clear()
            table.setRowCount(len(df.index))
            table.setColumnCount(len(df.columns))
            header = table.horizontalHeader()# 컬럼내용에따라 길이 자동조절
            for i in range(len(df.columns)):
                table.setHorizontalHeaderItem(i, QTableWidgetItem(df.columns[i]))
                header.setSectionResizeMode(i, QHeaderView.ResizeToContents) # 컬럼내용에따라 길이 자동조절

            table.verticalHeader().setVisible(False) #인덱스 삭제
            col_ch = df.columns.to_list().index('상한조건')
            for row in range(len(df.index)):
                for column in range(len(df.columns)):
                    val = df.iloc[row, column]
                    if type(val) != str:
                        val = val.item()  # numpy.float 을 float으로 변환
                    it = QTableWidgetItem()
                    it.setData(Qt.DisplayRole, val)  # 정렬 시 문자형이 아닌 숫자크기로 바꿈
                    table.setItem(row, column, it)
                ckbox = QCheckBox()
                list_ckbox.append(ckbox)
                table.setCellWidget(row, col_ch, list_ckbox[row])

            table.horizontalHeader().setStretchLastSection(True)
            table.setSortingEnabled(True) #소팅한 상태로 로딩 시 데이터가 이상해져 맨 앞과 뒤에 추가
            if select_type == 'buy':
                self.df_buy = df
                self.list_check_buy = list_ckbox
            elif select_type == 'sell':
                self.df_sell = df
                self.list_check_sell = list_ckbox
            return dict_vars

    def configure_result(self,table, text_result,df,list_ckbox):
        try:
            col_start = df.columns.to_list().index('시작값')
            col_end = df.columns.to_list().index('종료값')
            col_interval = df.columns.to_list().index('간격')
            col_opt = df.columns.to_list().index('최적값')
            col_range = df.columns.to_list().index('범위')
            result_vars = 'self.vars[0] = [[30, 30, 0], 30]'+'\n'+'===================='+'\n'+\
                          'self.vars[n] = [[시작값, 종료값, 간격], 최적값]'+'\n'+'============================='+'\n'
            for idx,row in enumerate(df.index.tolist()):
                val_start = table.item(idx, col_start).text()
                val_end = table.item(idx, col_end).text()
                val_interval = table.item(idx, col_interval).text()
                val_opt = table.item(idx, col_opt).text()
                val_range = table.item(idx, col_range).text()
                if val_interval and val_range:
                    val_opt = float(val_opt)
                    val_range = int(val_range)
                    val_interval = float(val_interval)
                    val_start = val_opt-(val_interval * val_range)
                    val_end = val_opt+(val_interval * val_range)
                    if list_ckbox[idx].isChecked(): #체크되어있을 경우 스왑
                        val_start,val_end = val_end,val_start
                        val_interval = val_interval*-1
                    if val_start.is_integer():
                       val_start = int(val_start)
                    if val_end.is_integer():
                       val_end = int(val_end)
                    if val_interval.is_integer():
                       val_interval = int(val_interval)
                    if val_opt.is_integer():
                       val_opt = int(val_opt)
                    result_vars += row+' = [['+str(val_start)+','
                    result_vars += str(val_end)+','
                    result_vars += str(val_interval)+'],'
                    result_vars += str(val_opt)+']'+ '\n'
                else:
                    result_vars = result_vars+row+' = [['+val_start+','
                    result_vars = result_vars+val_end+','
                    result_vars = result_vars+val_interval+'],'
                    result_vars = result_vars+val_opt+']'+ '\n'
                text_result.setText(result_vars)
        except:
            print('오류발생')
            pass
if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = Window(app)
    ex.setWindowTitle('window')
    ex.show()
    sys.exit(app.exec_( ))