import talib
import numpy as np
import subprocess
import pandas as pd
import sqlite3
import ccxt
import KIS
from pandas import to_numeric
import time
from pybit.unified_trading import HTTP
from PyQt5.QtWidgets import QMainWindow, QGridLayout, QLineEdit, QLabel, QPushButton, QWidget, QVBoxLayout, \
    QTableWidget, QSplitter, QApplication, QCheckBox, QTextEdit, QTableWidgetItem, QHeaderView, QComboBox, QAbstractItemView
from PyQt5.QtCore import Qt, QThread, pyqtSlot, QTimer, QRegExp
from PyQt5.QtTest import QTest
from PyQt5.QtGui import QFontMetrics, QFont, QColor, QSyntaxHighlighter, QTextCharFormat
import datetime
from pprint import pprint

def convert_df(df):
    # print(convert_df)
    df['등락율'] = round((df['종가'] - df['종가'].shift(1)) / df['종가'].shift(1) * 100, 2)
    df['변화율'] = round((df['종가'] - df['시가']) / df['시가'] * 100, 2)
    df['이평5'] = talib.MA(df['종가'], 5)
    df['이평20'] = talib.MA(df['종가'], 20)
    df['이평60'] = talib.MA(df['종가'], 60)
    df['이평120'] = talib.MA(df['종가'], 120)
    df['이평240'] = talib.MA(df['종가'], 200)
    df['거래량이평3'] = talib.MA(df['거래량'], 3)
    df['거래량이평20'] = talib.MA(df['거래량'], 20)
    df['거래량이평60'] = talib.MA(df['거래량'], 60)
    df['MACD'], df['MACD_SIGNAL'], df['MACD_HIST'] = talib.MACD(df['종가'], fastperiod=12, slowperiod=26, signalperiod=9)
    df['RSI14'] = talib.RSI(df["종가"], timeperiod=14).round(1)
    df['RSI18'] = talib.RSI(df["종가"], timeperiod=18).round(1)
    df['RSI30'] = talib.RSI(df["종가"], timeperiod=30).round(1)
    df['ATR'] = talib.ATR(df['고가'], df['저가'], df['종가'], timeperiod=10)
    df['TRANGE'] = talib.TRANGE(df['고가'], df['저가'], df['종가'])
    df['이격도20이평'] = df['종가'].shift(1) / df['이평20'].shift(1) * 100
    df['이격도60이평'] = df['종가'].shift(1) / df['이평60'].shift(1) * 100
    df['밴드상'], df['밴드중'], df['밴드하'] = talib.BBANDS(df['종가'].shift(1), 20, 2)
    df['고저평균대비등락율'] = ((df['종가'] / ((df['고가'] + df['저가']) / 2) - 1) * 100).round(2)
    df['데이터길이'] = np.arange(1, len(df.index.tolist()) + 1, 1)  # start=1, stop=len(df.index.tolist())+1, step=1
    return df

def resample_df(df, bong, rule, name):
    ohlc_dict = {
        '상세시가': 'first',
        '상세고가': 'max',
        '상세저가': 'min',
        '상세종가': 'last',
        '상세거래량': 'sum',
        # '상세거래대금': 'sum'
    }

    df = df.resample(rule).apply(ohlc_dict).dropna()

    if bong == name:  # 기준봉일 경우
        df.rename(columns={f'상세시가': f'시가', f'상세고가': f'고가', f'상세저가': f'저가', f'상세종가': f'종가',
                           f'상세거래량': f'거래량', f'상세거래대금': f'거래대금'}, inplace=True)  # 컬럼명 변경
        df = convert_df(df)
        df[f'시가_{name}'] = df['시가'].copy()
        df[f'고가_{name}'] = df['고가'].copy()
        df[f'저가_{name}'] = df['저가'].copy()
        df[f'종가_{name}'] = df['종가'].copy()
        df[f'거래량_{name}'] = df['거래량'].copy()
        # df[f'거래대금_{name}'] = df['거래대금'].copy()
        df[f'이평5_{name}'] = df['이평5'].copy()
        df[f'이평20_{name}'] = df['이평20'].copy()
        df[f'이평60_{name}'] = df['이평60'].copy()
        # print(df)
    else:
        df.rename(columns={'상세시가': f'시가_{name}', '상세고가': f'고가_{name}', '상세저가': f'저가_{name}', '상세종가': f'종가_{name}',
                     '상세거래량': f'거래량_{name}', '상세거래대금': f'거래대금_{name}'}, inplace=True)  # 컬럼명 변경
        df[f'이평5_{name}'] = talib.MA(df[f'종가_{name}'], 5)
        df[f'이평20_{name}'] = talib.MA(df[f'종가_{name}'], 20)
        df[f'이평60_{name}'] = talib.MA(df[f'종가_{name}'], 60)
        df[f'데이터길이_{name}'] = np.arange(1, len(df.index.tolist()) + 1,1)  # start=1, stop=len(df.index.tolist())+1, step=1
    return df

def get_kis_ohlcv(market, ohlcv):
    df = pd.DataFrame(ohlcv)
    dt = pd.to_datetime(df['stck_bsop_date'] + df['stck_cntg_hour'], format="%Y%m%d%H%M%S")
    df.set_index(dt, inplace=True)
    df = df.apply(to_numeric)
    if market == '국내주식':
        df = df[['stck_oprc', 'stck_hgpr', 'stck_lwpr', 'stck_prpr', 'cntg_vol', 'acml_tr_pbmn']]
        df.columns = ['시가', '고가', '저가', '종가', '거래량', '누적거래대금']
        df['거래대금'] = df['누적거래대금'] - df['누적거래대금'].shift(-1)
    elif market == '국내선옵':
        df = df[['futs_oprc', 'futs_hgpr', 'futs_lwpr', 'futs_prpr', 'cntg_vol', 'acml_tr_pbmn']]
        df.columns = ['시가', '고가', '저가', '종가', '거래량', '누적거래대금']
        df['거래대금'] = df['누적거래대금'] - df['누적거래대금'].shift(-1)
    df.index.name = "날짜"
    df = df[::-1]  # 거꾸로 뒤집기
    return df

def get_bybit_ohlcv(ex_bybit, ohlcv, stamp_date_old, ticker_full_name, ticker, bong, bong_detail):
    i = 0
    # print(f"{ohlcv= }, {stamp_date_old= }, {ticker= },{bong= }, {bong_detail= }")
    dict_bong_stamp ={'1분봉': 1*60, '3분봉': 3*60, '5분봉': 5*60, '15분봉': 15*60, '30분봉': 30*60, '60분봉': 60*60, '4시간봉': 240*60, '일봉': 1440*60,
                       '주봉': 10080*60}
    dict_bong = {'1분봉': '1m', '3분봉': '3m','5분봉': '5m', '15분봉': '15m', '30분봉': '30m', '60분봉': '1h', '4시간봉':'4h','일봉': 'd', '주봉': 'W', '월봉': 'M'}  # 국내시장의 경우 일봉을 기본으로하기 때문에 일봉은 제외

    while True:
        try:
            list_ohlcv = ex_bybit.fetch_ohlcv(symbol=ticker + 'USDT', timeframe=dict_bong[bong_detail],
                                                   limit=10000, since=int(stamp_date_old*1000)) #밀리초로 전달
            # pprint(list_ohlcv)
            ohlcv = ohlcv + list_ohlcv
            stamp_date_old = list_ohlcv[-1][0]/1000 + dict_bong_stamp[bong_detail]  # 다음봉 시간 계산

            if stamp_date_old > time.time():
                return ohlcv
        except:
            time.sleep(1)
            i += 1
            if i > 9:
                print(f' {ticker_full_name=}, {bong=}, {i}회 이상 fetch_ohlcv 조회 에러')
                raise '조회에러'


def detail_to_spread(df_min, bong,bong_detail):
    dict_bong_stamp = {'1분봉': 1, '3분봉': 3, '5분봉': 5, '15분봉': 15, '30분봉': 30, '60분봉': 60, '4시간봉': 240, '일봉': 1440,
                       '주봉': 10080}
    df_min.rename(columns={'시가': f'상세시가', '고가': f'상세고가', '저가': f'상세저가', '종가': f'상세종가',
                           '거래량': f'상세거래량', '거래대금': f'상세거래대금'}, inplace=True)  # 컬럼명 변경
    detail_unit = dict_bong_stamp[bong_detail]
    list_idx = df_min.index.tolist()
    # print(f"{dict_bong_stamp= }")
    if detail_unit == dict_bong_stamp['1분봉']:
        df_1min = resample_df(df_min, bong, '1min', '1분봉')
    if detail_unit < dict_bong_stamp['3분봉']:
        df_3min = resample_df(df_min, bong, '3min', '3분봉')
    if detail_unit < dict_bong_stamp['5분봉']:
        df_5min = resample_df(df_min, bong, '5min', '5분봉')
    if detail_unit < dict_bong_stamp['15분봉']:
        df_15min = resample_df(df_min, bong, '15min', '15분봉')
    if detail_unit < dict_bong_stamp['30분봉']:
        df_30min = resample_df(df_min, bong, '30min', '30분봉')
    if detail_unit < dict_bong_stamp['60분봉']:
        df_60min = resample_df(df_min, bong, '60min', '60분봉')
    if detail_unit < dict_bong_stamp['4시간봉']:
        df_4h = resample_df(df_min, bong, '240min', '4시간봉')
    df_daily = resample_df(df_min, bong, 'D', '일봉')
    df_weekly = resample_df(df_min, bong, 'W', '주봉')
    df_monthly = resample_df(df_min, bong, 'ME', '월봉')

    df_daily['date'] = df_daily.index.date
    df_weekly['week'] = df_weekly.index.to_period('W').astype(str)
    df_monthly['month'] = df_monthly.index.to_period('M').astype(str)
    df_min['date'] = df_min.index.date
    df_min['week'] = df_min.index.to_period('W').astype(str)
    df_min['month'] = df_min.index.to_period('M').astype(str)

    if detail_unit < dict_bong_stamp['3분봉']:
        df_min = pd.merge(df_min, df_1min, left_index=True, right_index=True, how='left')
    if detail_unit < dict_bong_stamp['3분봉']:
        df_min = pd.merge(df_min, df_3min, left_index=True, right_index=True, how='left')
    if detail_unit < dict_bong_stamp['5분봉']:
        df_min = pd.merge(df_min, df_5min, left_index=True, right_index=True, how='left')
    if detail_unit < dict_bong_stamp['15분봉']:
        df_min = pd.merge(df_min, df_15min, left_index=True, right_index=True, how='left')
    if detail_unit < dict_bong_stamp['30분봉']:
        df_min = pd.merge(df_min, df_30min, left_index=True, right_index=True, how='left')
    if detail_unit < dict_bong_stamp['60분봉']:
        df_min = pd.merge(df_min, df_60min, left_index=True, right_index=True, how='left')
    if detail_unit < dict_bong_stamp['4시간봉']:
        df_min = pd.merge(df_min, df_4h, left_index=True, right_index=True, how='left')
    df_combined = df_min.merge(df_daily, on='date',how='left', suffixes=('', '_daily'))
    df_combined = df_combined.merge(df_weekly, on='week',how='left', suffixes=('', '_weekly'))
    df_combined = df_combined.merge(df_monthly, on='month',how='left', suffixes=('', '_monthly'))

    # df_combined.fillna(method='ffill', inplace=True)
    df_combined.ffill(inplace=True)

    df_combined.index = list_idx
    df_combined.index.rename('날짜', inplace=True)  # 인덱스명 변경
    df_combined.drop('date', axis=1, inplace=True)
    df_combined.drop('week', axis=1, inplace=True)
    df_combined.drop('month', axis=1, inplace=True)
    list_col = df_combined.columns.tolist()
    # 시가 ~ 데이터프레임 열까지 갖고오기
    if bong == '1분봉':
        df = df_1min
    elif bong == '3분봉':
        df = df_3min
    elif bong == '5분봉':
        df = df_5min
    elif bong == '15분봉':
        df = df_15min
    elif bong == '30분봉':
        df = df_30min
    elif bong == '60분봉':
        df = df_60min
    elif bong == '4시간봉':
        df = df_4h
    elif bong == '일봉':
        df = df_daily
    elif bong == '주봉':
        df = df_weekly
    elif bong == '월봉':
        df = df_monthly
    else:
        df = pd.DataFrame()
    return df,df_combined
def detail_to_compare(df, bong, ticker_full_name):
    # print(ticker_full_name)
    dict_bong_rule = {'1분봉': '1min', '3분봉': '3', '5분봉': '5min', '15분봉': '15min', '30분봉': '30min', '60분봉': '60min', '4시간봉': '240min', '일봉': 'D',
                       '주봉': 'W'}
    df.rename(columns={'시가': f'상세시가', '고가': f'상세고가', '저가': f'상세저가', '종가': f'상세종가',
                           '거래량': f'상세거래량', '거래대금': f'상세거래대금'}, inplace=True)  # 컬럼명 변경
    df = resample_df(df, bong, dict_bong_rule[bong], bong)

    # 컬럼명중에 bong 이름이 들어가는 컬럼을 제거 ( '시가_일봉_BTC_일봉' 이렇게 나오기 때문에)
    df = df.drop(columns=df.filter(like='_'+bong).columns)

    df.columns = [col + '_'+ticker_full_name for col in df.columns]
    return df
def make_exchange_bybit(mock):
    conn = sqlite3.connect('DB/setting.db')
    df = pd.read_sql(f"SELECT * FROM 'set'", conn).set_index('index')
    conn.close()
    if mock == True:
        api = df.loc['BYBIT_mock_api', 'value']
        secret = df.loc['BYBIT_mock_secret', 'value']
    else:
        api = df.loc['BYBIT_api','value']
        secret = df.loc['BYBIT_secret','value']
    exchange_ccxt = ccxt.bybit(config={
        'apiKey': api,
        'secret': secret,
        'enableRateLimit': True,
        'options': {'position_mode': True,},
        })
    exchange_pybit = HTTP(
            testnet = False,
            api_key = df.loc['BYBIT_mock_api', 'value'],
            api_secret = df.loc['BYBIT_secret','value'],
        )
    if mock == True:
        exchange_ccxt.set_sandbox_mode(True)

    return exchange_ccxt, exchange_pybit


def make_exchange_kis(trade_type):
    conn = sqlite3.connect('DB/setting.db')
    df = pd.read_sql(f"SELECT * FROM 'set'", conn).set_index('index')
    conn.close()
    if trade_type == '실전주식':
        key = df.loc['KIS_stock_api','value']
        secret = df.loc['KIS_stock_secret','value']
        acc_no = df.loc['KIS_stock_account','value']
        mock = False
        # broker = mojito.KoreaInvestment(api_key=key, api_secret=secret, acc_no=acc_no)
    elif trade_type == '모의주식':
        key = df.loc['KIS_stock_mock_api','value']
        secret = df.loc['KIS_stock_mock_secret','value']
        acc_no = df.loc['KIS_stock_mock_account','value']
        mock = True
    elif trade_type == '실전선옵':
        key = df.loc['KIS_futopt_api','value']
        secret = df.loc['KIS_futopt_secret','value']
        acc_no = df.loc['KIS_futopt_account','value']
        mock = False
    elif trade_type == '모의선옵':
        key = df.loc['KIS_futopt_mock_api','value']
        secret = df.loc['KIS_futopt_mock_secret','value']
        acc_no = df.loc['KIS_futopt_mock_account','value']
        mock = True

    market = trade_type[-2:]
    exchange = KIS.KoreaInvestment(api_key=key, api_secret=secret, acc_no=acc_no, market=market, mock=mock)
    return exchange
def export_sql(df,text):
    con = sqlite3.connect('DB/bt.db')
    df.to_sql(text, con, if_exists='replace')
    con.close()
def import_sql(db_file,table_name):

    # 데이터베이스 연결
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # 테이블에 대한 인덱스 정보 가져오기
    cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type='index' AND tbl_name=?
    """, (table_name,))

    # 결과 출력
    index_names = cursor.fetchall()

    # 인덱스 이름 출력
    # for index in index_names:
    #     print(index[0])
    idx = index_names[0][0]
    # rindex = idx.rindex('_')
    idx = idx[idx.rindex('_')+1:]
    df = pd.read_sql(f"SELECT * FROM {table_name}", conn).set_index(idx)
    # 연결 종료
    conn.close()
    return df


def convert_column_types(df): #데이터프레임 중 숫자로 바꿀 수 있는데이터는 숫자로 변환
    for col in df.columns:
        try:
            df[col] = pd.to_numeric(df[col], errors='raise')
        except ValueError:
            pass
    return df
def stamp_to_int(stamp_time):
    dt = datetime.datetime.fromtimestamp(stamp_time)
    dt = dt.strftime('%Y%m%d%H%M')
    print(f"{stamp_time=},,,{dt=}")
    return int(dt)
def stamp_to_str(stamp_time):
    date_time = stamp_to_datetime(stamp_time)
    return datetime.datetime.strftime(date_time,"%Y-%m-%d %H:%M:%S")
def str_to_datetime(str):
    # print(f"{str= }")
    return datetime.datetime.strptime(str,'%Y-%m-%d %H:%M:%S')
def str_to_stamp(str):
    dt =  datetime.datetime.strptime(str,'%Y-%m-%d %H:%M:%S')
    return int(dt.timestamp())
def int_to_stamp(int_time):
    dt = datetime.datetime.strptime(str(int_time), '%Y%m%d%H%M')
    return int(dt.timestamp())
def int_to_datetime(int_time):
    return datetime.datetime.strptime(str(int_time),'%Y%m%d%H%M')
def stamp_to_datetime(stamp_time):
    int_time=stamp_to_int(stamp_time)
    return datetime.datetime.strptime(str(int_time),'%Y%m%d%H%M')
def datetime_to_stamp(date_time):
    return int(time.mktime(date_time.timetuple()))
def datetime_to_str(date_time):
    return datetime.datetime.strftime((date_time), "%Y-%m-%d %H:%M:%S")
def datetime_to_int_time(date_time):
    return int(datetime.datetime.strftime((date_time), "%H%M%S"))

class PythonHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super(PythonHighlighter, self).__init__(parent)

        self.highlightingRules = []

        # Keyword formatting
        orangeFormat = QTextCharFormat()
        orangeFormat.setForeground(QColor("orange"))
        keywords_orange = ["if", "True", "False", ":", "and", 'or', "{", "}", "not", "elif", "else", "pass"]
        for keyword in keywords_orange:
            pattern = QRegExp(f"\\b{keyword}\\b")
            self.highlightingRules.append((pattern, orangeFormat))

        # 'self' formatting
        purpleFormat = QTextCharFormat()
        purpleFormat.setForeground(QColor("purple"))
        keywords_purple = ["self", "print", "[", "]"]
        for keyword in keywords_purple:
            Pattern = QRegExp(f"\\b{keyword}\\b")
            self.highlightingRules.append((Pattern, purpleFormat))

        # Number formatting
        cyanFormat = QTextCharFormat()
        cyanFormat.setForeground(QColor("cyan"))
        keywords_purple = ["[0-9]+", "[0-9]-"]
        for keyword in keywords_purple:
            Pattern = QRegExp(f"\\b{keyword}\\b")
            self.highlightingRules.append((Pattern, cyanFormat))

        greenFormat = QTextCharFormat()
        greenFormat.setForeground(QColor("yellowgreen"))
        keywords_green = ["진입대상", "봉", "상세봉", "방향", "초기자금", "레버리지", "분할매수", "분할매도"]
        for keyword in keywords_green:
            Pattern = QRegExp(f"\\b{keyword}\\b")
            self.highlightingRules.append((Pattern, greenFormat))

        grayFormat = QTextCharFormat()
        grayFormat.setForeground(QColor("gray"))
        keywords_gray = ["#"]
        for keyword in keywords_gray:
            Pattern = QRegExp(f"\\b{keyword}\\b")
            self.highlightingRules.append((Pattern, grayFormat))

        pinkFormat = QTextCharFormat()
        pinkFormat.setForeground(QColor("pink"))
        keywords_gray = ["매수가", "매수", "매도가", "매도", "매입율", "매도전환"]
        for keyword in keywords_gray:
            Pattern = QRegExp(f"\\b{keyword}\\b")
            self.highlightingRules.append((Pattern, pinkFormat))

        darkCyanFormat = QTextCharFormat()
        darkCyanFormat.setForeground(QColor("darkCyan"))
        keywords_gray = ["매도가", "매도"]
        for keyword in keywords_gray:
            Pattern = QRegExp(f"\\b{keyword}\\b")
            self.highlightingRules.append((Pattern, darkCyanFormat))

        darkGrayFormat = QTextCharFormat()
        darkGrayFormat.setForeground(QColor("darkGray"))
        keywords_gray = ["#"]
        for keyword in keywords_gray:
            Pattern = QRegExp(f"\\b{keyword}\\b")
            self.highlightingRules.append((Pattern, darkGrayFormat))

    def highlightBlock(self, text):
        for pattern, format in self.highlightingRules:
            expression = QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)

        ################################ 괄호
        bracketStack = []
        for i, char in enumerate(text):
            if char in '({[':
                bracketStack.append((char, i))
                # color = self.bracketColors[len(bracketStack) % len(self.bracketColors)]
                format = QTextCharFormat()
                # format.setForeground(color)
                self.setFormat(i, 1, format)
            elif char in ')}]':
                if bracketStack:
                    bracket, pos = bracketStack.pop()
                    # color = self.bracketColors[len(bracketStack) % len(self.bracketColors)]
                    format = QTextCharFormat()
                    # format.setForeground(color)
                    self.setFormat(i, 1, format)
        ################################ 괄호
        self.setCurrentBlockState(0)


class CodeEditor(QTextEdit):
    def __init__(self, parent=None):
        super(CodeEditor, self).__init__(parent)
        self.setFont(QFont("Courier", 10))

    def keyPressEvent(self, event):
        # Check for the '(' key press
        if event.key() == Qt.Key_ParenLeft:
            cursor = self.textCursor()
            cursor.insertText('()')
            cursor.movePosition(cursor.Left)
            self.setTextCursor(cursor)
        # if event.key() == Qt.Key_ParenLeft:
        #     cursor = self.textCursor()
        #     cursor.insertText('{}')
        #     cursor.movePosition(cursor.Left)
        #     self.setTextCursor(cursor)
        # if event.key() == Qt.Key_ParenLeft:
        #     cursor = self.textCursor()
        #     cursor.insertText('[]')
        #     cursor.movePosition(cursor.Left)
        #     self.setTextCursor(cursor)
        else:
            super(CodeEditor, self).keyPressEvent(event)
