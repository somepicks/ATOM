import datetime
import time

from pykrx import stock
from pprint import pprint
import pandas as pd
import sqlite3
import numpy as np
import KIS
import schedule
import subprocess
import talib
import os
class strategy():
    def __init__(self,kis,stock_easy_txt):
        self.kis = kis
        self.list_stock_easy = stock_easy_txt
        self.init_file()
        self.get_signal_kodex_leverage()
        self.get_stock_easy_list()

    def init_file(self):
        db_file = 'DB/stock_easy.db'
        if not os.path.isfile(db_file): #파일이 없으면
            self.df_wallet = pd.DataFrame(columns=['매수금액','잔고','평가금액','수익률'],index=['STOCK_EASY','KODEX_레버리지'])
            self.df_wallet.loc['STOCK_EASY','매수금액'] = 0
            self.df_wallet.loc['STOCK_EASY','잔고'] = 8_000_000
            self.df_wallet.loc['STOCK_EASY','평가금액'] = 0
            self.df_wallet.loc['STOCK_EASY','수익률'] = 0
            self.df_wallet.loc['KODEX_레버리지','매수금액'] = 0
            self.df_wallet.loc['KODEX_레버리지','잔고'] = 2_000_000
            self.df_wallet.loc['KODEX_레버리지','평가금액'] = 0
            self.df_wallet.loc['KODEX_레버리지','수익률'] = 0
            self.df_stock_easy = pd.DataFrame(columns=['ticker','종목명','평단가', '매수수량','주문수량','주문금액', '수익률', '매수금액','매도금액','id','상태','진입일','청산일' ])
            self.df_kodex_leverage = pd.DataFrame(columns=['ticker','종목명','평단가', '매수수량','주문수량','주문금액', '수익률', '매수금액','매도금액','id','상태','진입일' ,'청산일'],index=['KODEX 레버리지'])
            self.df_kodex_leverage.loc['KODEX 레버리지', 'ticker'] = '122630'
            self.df_kodex_leverage.loc['KODEX 레버리지', '종목명'] = 'KODEX 레버리지'
            self.df_kodex_leverage.loc['KODEX 레버리지','상태'] = '매도'
            self.conn = sqlite3.connect('DB/stock_easy.db')
            self.df_wallet.to_sql('wallet', self.conn, if_exists='replace')
            self.df_stock_easy.to_sql('stock_easy', self.conn, if_exists='replace')
            self.df_kodex_leverage.to_sql('KODEX 레버리지', self.conn, if_exists='replace')

            self.df_history_stock = pd.DataFrame(columns=['ticker','종목명','진입가', '청산가','보유수량','진입금액', '청산금액', '수익률','수익금','진입일','청산일' ],index=['KODEX 레버리지'])
            self.df_history_stock.to_sql('종목거래내역', self.conn, if_exists='replace')
            self.df_history_wallet = pd.DataFrame(columns=['총평가금액','예수금'],index=['KODEX 레버리지'])
            self.df_history_wallet.to_sql('자산변화', self.conn, if_exists='replace')
        else:
            self.conn = sqlite3.connect('DB/stock_easy.db')
            # cursor = self.conn.cursor()
            # cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            self.df_wallet = pd.read_sql(f"SELECT * FROM 'wallet'", self.conn).set_index('index')
            self.df_stock_easy = pd.read_sql(f"SELECT * FROM 'stock_easy'", self.conn).set_index('index')
            self.df_kodex_leverage = pd.read_sql(f"SELECT * FROM 'KODEX 레버리지'", self.conn).set_index('index')
            self.df_history_stock = pd.read_sql(f"SELECT * FROM '종목거래내역'", self.conn).set_index('index')
            self.df_history_wallet = pd.read_sql(f"SELECT * FROM '자산변화'", self.conn).set_index('index')
        # self.df_wallet.loc['STOCK_EASY','매수가능잔고'] = self.df_wallet.loc['STOCK_EASY','잔고']
        # self.df_wallet.loc['KODEX_레버리지','매수가능잔고'] = self.df_wallet.loc['KODEX_레버리지','잔고']
    def get_stock_easy_list(self):
        stock_list = \
        pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13', header=0)[0]

        stock_list.종목코드 = stock_list.종목코드.map('{:06}'.format)  # 종목코드가 6자리이기 때문에 6자리를 맞춰주기 위해 설정해줌
        self.df_stock_info = stock_list[['회사명', '종목코드', '업종', '주요제품', '상장일']]  # 우리가 필요한 것은 회사명과 종목코드이기 때문에 필요없는 column들은 제외해준다.
        # list_tickers = stock_list['종목코드'].tolist()
        self.df_stock_info.set_index('회사명', inplace=True)
        list_company = self.df_stock_info.index.tolist()
        self.list_se_tickers = []
        for ticker in list_company:
            for stock_easy_line in self.list_stock_easy:
                if ticker in stock_easy_line:
                    self.list_se_tickers.append(ticker)
        self.list_se_tickers = list(set(self.list_se_tickers))

        real_ticker = []
        for stock_easy_line in self.list_stock_easy:
            max_font = 0
            for ticker in self.list_se_tickers:
                if ticker in stock_easy_line:
                    if max_font < len(ticker):
                        max_font = len(ticker)
                        true_ticker = ticker
            try:
                real_ticker.append(true_ticker)
            except:
                pass
        real_ticker = [x for x in real_ticker if not x == '']
        self.list_stock_easy = list(set(real_ticker))
        print(f"스탁이지 종목= {self.list_stock_easy}")
        list_hold = self.df_stock_easy.loc[self.df_stock_easy['상태'] == '매수', '종목명'].tolist()

        print(f"보유종목= {list_hold}")
        self.list_buy_company_name = list(set(self.list_stock_easy)-set(list_hold))
        self.list_sell_company_name = list(set(list_hold)-set(self.list_stock_easy))
        print(f"스탁이지 신규매수 종목= {self.list_buy_company_name}")
        print(f"스탁이지 이탈 종목= {self.list_sell_company_name}")
    def stg_stock_easy(self,):
        종목당투자금액 = self.df_wallet.loc['STOCK_EASY','잔고']/50-len(self.df_stock_easy)

        for i,company in enumerate(self.list_buy_company_name):
            ticker = self.df_stock_info.loc[company, '종목코드']
            out = self.kis.fetch_price(symbol=ticker)
            price = int(out['현재가'])
            price = self.kis.hogaPriceReturn(jang='KOSPI', ticker=ticker, current_price=price, hoga_in='매도4호가')
            qty = int(종목당투자금액/price)
            if qty < 1 and price < 500000:
                qty = 1
            if qty > 0:
                print(f"스탁이지 매수 - {company}   {qty=}   {price=}  주문금액= {qty*price}")
                id = self.kis.create_order('buy', ticker, price, qty, '지정가')
                self.df_stock_easy.loc[company, '상태'] = '매수주문'
                self.df_stock_easy.loc[company, '주문수량'] = qty
                self.df_stock_easy.loc[company, 'ticker'] = ticker
                self.df_stock_easy.loc[company, '종목명'] = company
                self.df_stock_easy.loc[company, 'id'] = id
                self.df_stock_easy.loc[company, '주문일자'] = datetime.datetime.now().date().strftime("%Y%m%d")

        for company in self.list_sell_company_name:
            # print(self.df_stock)
            ticker = self.df_stock_info.loc[company, '종목코드']
            out = self.kis.fetch_price(symbol=ticker)
            price = int(out['현재가'])

            qty = self.df_stock_easy.loc[company, '매수수량']
            if qty > 0:
                # print(price)
                print(f"스탁이지 매도 - {company}   {qty=}   {price=}  주문금액= {qty*price}")
                id = self.kis.create_order('sell', ticker, price, qty, '지정가')
                self.df_stock_easy.loc[company, '상태'] = '매도주문'
                self.df_stock_easy.loc[company, '주문수량'] = self.df_stock_easy.loc[company, '매수수량']
                self.df_stock_easy.loc[company, 'id'] = id
        self.df_stock_easy.to_sql('stock_easy', self.conn, if_exists='replace')

    def stg_kodex_leverage(self):
        if self.signal_ksp == True: #매수주문
            if '매도' == self.df_kodex_leverage.loc['KODEX 레버리지','상태']: #신규 진입
                print('매수주문')
                df = self.kis.fetch_ohlcv(symbol='122630')
                today = datetime.datetime.now().date()
                wallet = self.df_wallet.loc['KODEX_레버리지', '잔고']
                if today == df.index[-1].date():
                    price_o = df.loc[df.index[-1],'시가']
                    price = self.kis.hogaPriceReturn(jang='ETF',ticker='122630',current_price=price_o,hoga_in='매도4호가')
                    qty = int(wallet/price)
                    id = self.kis.create_order('buy','122630',price,qty,'지정가')
                    self.df_kodex_leverage.loc['KODEX 레버리지','상태'] = '매수주문'
                    self.df_kodex_leverage.loc['KODEX 레버리지','주문수량'] = qty
                    self.df_kodex_leverage.loc['KODEX 레버리지','id'] = id
                    # self.df_wallet.loc['KODEX_레버리지','잔고'] = self.df_wallet.loc['KODEX_레버리지','잔고']-(qty*price)
                    self.df_kodex_leverage.to_sql('KODEX 레버리지', self.conn, if_exists='replace')
            elif '매수' == self.df_kodex_leverage.loc['KODEX 레버리지','상태']:
                print("KODEX 레버리지 기존 수량 보유")
            elif '매수주문' == self.df_kodex_leverage.loc['KODEX 레버리지','상태']:
                print("KODEX 레버리지 체결 확인 중")
        else:
            print('else')
            if '매수' == self.df_kodex_leverage.loc['KODEX 레버리지','상태']: #매도 진입
                print('매도주문')
                df = self.kis.fetch_ohlcv(symbol='122630')
                price_o = df.loc[df.index[-1], '시가']
                price = self.kis.hogaPriceReturn(jang='ETF', ticker='122630', current_price=price_o, hoga_in='매수4호가')
                qty = self.df_kodex_leverage.loc['KODEX 레버리지','매수수량']
                id = self.kis.create_order('sell', '122630', price, qty, '지정가')
                self.df_kodex_leverage.loc['KODEX 레버리지','상태'] = '매도주문'
                self.df_kodex_leverage.loc['KODEX 레버리지','주문수량'] = self.df_kodex_leverage.loc['KODEX 레버리지','매수수량']
                self.df_kodex_leverage.loc['KODEX 레버리지','id'] = id
                self.df_kodex_leverage.to_sql('KODEX 레버리지', self.conn, if_exists='replace')

    def get_signal_kodex_leverage(self):
        df_kodex_200 = self.kis.fetch_ohlcv(symbol='122630')
        df_kodex_200['이평20'] = talib.MA(df_kodex_200['종가'], 20)
        df_kodex_200['이격도20이평'] = df_kodex_200['종가'].shift(1) / df_kodex_200['이평20'].shift(1) * 100
        df_kodex_200['거래량이평3'] = talib.MA(df_kodex_200['거래량'], 3)
        today = datetime.datetime.now()
        tday = today.date()
        print(df_kodex_200)
        if tday == df_kodex_200.index[-1].date():
            if today.time() < datetime.time(15,50,0):
                df_kodex_200.drop(index=tday, inplace=True)
        print(df_kodex_200)

        signal1 = False
        signal2 = False

        if (df_kodex_200.loc[df_kodex_200.index[-1], '저가'] > df_kodex_200.loc[df_kodex_200.index[-2], '저가']) or (
                df_kodex_200.loc[df_kodex_200.index[-1], '거래량'] < df_kodex_200.loc[df_kodex_200.index[-1], '거래량이평3']):
            signal1 = True
        if (df_kodex_200.loc[df_kodex_200.index[-1], '이격도20이평'] < 98) or (df_kodex_200.loc[df_kodex_200.index[-1], '이격도20이평'] > 106):
            signal2 = True
        if signal1 and signal2:
            self.signal_ksp = True
            print(f"KODEX 레버리지 매수신호")
        else:
            self.signal_ksp = False
            print(f"KODEX 레버리지 매도신호")

    def check_chegyeol(self):
        if self.df_kodex_leverage.loc['KODEX 레버리지','상태'] == '매수주문':
            df_chegyeol = self.kis.fetch_closed_order()
            signal = True
        elif self.df_kodex_leverage.loc['KODEX 레버리지','상태'] == '매도주문':
            df_chegyeol = self.kis.fetch_closed_order()
            signal = True
        elif '매수주문' in self.df_stock_easy['상태'].tolist():
            df_chegyeol = self.kis.fetch_closed_order()
            signal = True
        elif '매도주문' in self.df_stock_easy['상태'].tolist():
            df_chegyeol = self.kis.fetch_closed_order()
            signal = True
        else:
            df_chegyeol = pd.DataFrame()
            signal = False
        ##########################################################################
        if signal:
            if not df_chegyeol.empty:
                list_chegyeol_id = df_chegyeol.index.tolist()
                if self.df_kodex_leverage.loc['KODEX 레버리지','상태'] == '매수주문':
                    self.df_kodex_leverage = self.chegyeol(self.df_kodex_leverage,df_chegyeol,list_chegyeol_id,'KODEX 레버리지','buy')
                    if self.df_kodex_leverage.loc['KODEX 레버리지','상태'] == '매수' or self.df_kodex_leverage.loc['KODEX 레버리지','상태'] == '부분매수':
                        if self.df_kodex_leverage.loc['KODEX 레버리지', '상태'] == '매수':
                            self.df_wallet.loc['KODEX_레버리지','잔고'] = self.df_wallet.loc['KODEX_레버리지','잔고']-self.df_kodex_leverage.loc['KODEX 레버리지','매수금액']
                            self.df_wallet.loc['KODEX_레버리지','매수금액'] = self.df_kodex_leverage.loc['KODEX 레버리지','매수금액']
                            self.df_wallet.loc['KODEX_레버리지','평가금액'] = self.df_kodex_leverage.loc['KODEX 레버리지','매수금액']
                            self.df_kodex_leverage.to_sql('KODEX 레버리지', self.conn, if_exists='replace')
                            self.df_wallet.to_sql('wallet', self.conn, if_exists='replace')
                elif self.df_kodex_leverage.loc['KODEX 레버리지','상태'] == '매도주문':
                    self.df_kodex_leverage = self.chegyeol(self.df_kodex_leverage,df_chegyeol,list_chegyeol_id,'KODEX 레버리지','sell')
                    if self.df_kodex_leverage.loc['KODEX 레버리지','상태'] == '매도' or self.df_kodex_leverage.loc['KODEX 레버리지','상태'] == '부분매도':
                        if self.df_kodex_leverage.loc['KODEX 레버리지', '상태'] == '매도':
                            self.df_wallet.loc['KODEX_레버리지','매수금액'] = 0
                            self.df_wallet.loc['KODEX_레버리지','잔고'] = self.df_wallet.loc['KODEX_레버리지','잔고']+self.df_kodex_leverage.loc['KODEX 레버리지','매도금액']
                            self.df_kodex_leverage.to_sql('KODEX 레버리지', self.conn, if_exists='replace')
                            self.df_wallet.to_sql('wallet', self.conn, if_exists='replace')
                            print(f"KODEX 레버리지 매도 {self.df_kodex_leverage.loc['KODEX 레버리지', '상태']}")
                            print(self.df_kodex_leverage)
                            print(self.df_wallet)
                if '매수주문' in self.df_stock_easy['상태'].tolist():
                    for company in self.df_stock_easy.index.tolist():
                        if self.df_stock_easy.loc[company,'상태'] == '매수주문':
                            self.df_stock_easy = self.chegyeol(self.df_stock_easy,df_chegyeol,list_chegyeol_id,company,'buy')
                            if self.df_stock_easy.loc[company, '상태'] == '매수' or self.df_stock_easy.loc[company, '상태'] == '부분매수':
                                if self.df_stock_easy.loc[company, '상태'] == '매수':
                                    self.df_stock_easy.loc[company, '진입일'] = datetime.datetime.now().date().strftime('%Y-%m-%d')
                                    self.df_wallet.loc['STOCK_EASY', '잔고'] = self.df_wallet.loc['STOCK_EASY', '잔고'] - \
                                                                             self.df_stock_easy.loc[company, '매수금액']
                                    self.df_wallet.loc['STOCK_EASY', '매수금액'] = self.df_wallet.loc['STOCK_EASY', '매수금액']+self.df_stock_easy.loc[company, '매수금액']

                                    self.df_stock_easy.to_sql('stock_easy', self.conn, if_exists='replace')
                                    self.df_wallet.to_sql('wallet', self.conn, if_exists='replace')
                                    print(f"STOCK_EASY {company} : {self.df_stock_easy.loc[company, '상태']}")
                                    print(self.df_kodex_leverage)
                                    print(self.df_wallet)
                if '매도주문' in self.df_stock_easy['상태'].tolist():
                    for company in self.df_stock_easy.index.tolist():
                        if self.df_stock_easy.loc[company,'상태'] == '매도주문':
                            self.df_stock_easy = self.chegyeol(self.df_stock_easy, df_chegyeol,list_chegyeol_id, company, 'sell')
                            if self.df_stock_easy.loc[company, '상태'] == '매도' or self.df_stock_easy.loc[company, '상태'] == '부분매도':
                                if self.df_stock_easy.loc[company, '상태'] == '매도':
                                    self.df_wallet.loc['STOCK_EASY', '잔고'] = self.df_wallet.loc['STOCK_EASY', '잔고']+self.df_stock_easy.loc[company, '매도금액']
                                    self.df_wallet.loc['STOCK_EASY', '매수금액'] = self.df_wallet.loc['STOCK_EASY', '매수금액']-self.df_stock_easy.loc[company, '매도금액']
                                    # self.df_stock_easy = self.chegyeol(self.df_stock_easy,df_chegyeol,company,'sell')
                                    self.df_stock_easy.drop(company,inplace=True)
                                    self.df_stock_easy.to_sql('stock_easy', self.conn, if_exists='replace')
                                    self.df_wallet.to_sql('wallet', self.conn, if_exists='replace')
                                    print(f"STOCK_EASY {company} : {self.df_stock_easy.loc[company, '상태']}")
                                    print(self.df_kodex_leverage)
                                    print(self.df_wallet)

    def check_finish(self):
        if self.df_kodex_leverage.loc['KODEX 레버리지','상태'] == '매수주문':
            self.df_kodex_leverage.loc['KODEX 레버리지','상태'] = '매도'
            self.df_kodex_leverage.to_sql('KODEX 레버리지', self.conn, if_exists='replace')
        elif self.df_kodex_leverage.loc['KODEX 레버리지','상태'] == '매도주문':
            self.df_kodex_leverage.loc['KODEX 레버리지','상태'] = '매수'
            self.df_kodex_leverage.to_sql('KODEX 레버리지', self.conn, if_exists='replace')
        if '매수주문' in self.df_stock_easy['상태'].tolist():
            self.df_stock_easy.loc[self.df_stock_easy['상태'] == '매수주문', '상태'] = '매도'
            # 주문 취소
            df_buy = self.df_stock_easy[self.df_stock_easy['상태']=='매수주문']
            for company in df_buy.index.tolist():
                ticker = self.df_stock_info.loc[company, '종목코드']
                id = self.df_stock_easy.loc[company,'id']
                qty = self.df_stock_easy.loc[company,'주문수량']
                self.kis.cancel_order(symbol=ticker, order_no=id,quantity=qty)
                self.df_stock_easy.drop(company,inplace=True)
        if '매도주문' in self.df_stock_easy['상태'].tolist():
            self.df_stock_easy.loc[self.df_stock_easy['상태'] == '매도주문', '상태'] = '매도'
            # 주문 취소
            df_sell = self.df_stock_easy[self.df_stock_easy['상태']=='매도주문']
            for company in df_sell.index.tolist():
                ticker = self.df_stock_info.loc[company, '종목코드']
                id = self.df_stock_easy.loc[company,'id']
                qty = self.df_stock_easy.loc[company,'주문수량']
                self.kis.cancel_order(symbol=ticker, order_no=id,quantity=qty)
        dict_amount, df_stock = kis.fetch_balance()
        if dict_amount:
            self.df_history_wallet.loc[datetime.datetime.now().date().strftime('%Y-%m-%d'),'예수금'] = dict_amount['예수금']
            self.df_history_wallet.loc[datetime.datetime.now().date().strftime('%Y-%m-%d'),'총평가금액'] = dict_amount['총평가금액']
            self.df_history_wallet.to_sql('자산변화', self.conn, if_exists='replace')
    def chegyeol(self,df,df_chegyeol,list_chegyeol_id,company,side):
        ticker = df.loc[company, 'ticker']
        id = df.loc[company, 'id']
        # 주문수량 = df.loc[company, '주문수량']
        # 종목명 = df.loc[company, '종목명']
        if id in list_chegyeol_id:
            총체결수량 = int(df_chegyeol.loc[id,'총체결수량'])
            잔여수량 = int(df_chegyeol.loc[id,'잔여수량'])
            총체결금액 = int(df_chegyeol.loc[id,'총체결금액'])
            평균가 = float(df_chegyeol.loc[id,'평균가'])
            주문수량 = int(df_chegyeol.loc[id,'주문수량'])

            if 총체결수량 > 0:
                if side == 'buy':
                    수수료 = 총체결금액 * (0.1 // 100)
                    보유수량 = 총체결수량
                    if 주문수량 == 총체결수량:
                        print(f"chegyeol - {company= }, {ticker= }, {총체결수량= }, {총체결금액= }, {평균가 }, {수수료= }")
                        상태 = '매수'
                    elif 주문수량 > 총체결수량:
                        상태 = '부분매수'
                    else:
                        상태 = '매수주문'
                    df.loc[company, '매수금액'] = 총체결금액
                elif side == 'sell':
                    보유수량 = 주문수량-총체결수량
                    if 주문수량 == 총체결수량:
                        print(f"chegyeol - {company= }, {ticker= }, {총체결수량= }, {총체결금액= }, {평균가 }")
                        상태 = '매도'
                    elif 주문수량 > 총체결수량:
                        상태 = '부분매도'
                    else:
                        상태 = '매도주문'
                    df.loc[company, '매도금액'] = 총체결금액
                df.loc[company, '평단가'] = 평균가
                df.loc[company, '매수수량'] = 보유수량
                df.loc[company, '상태'] = 상태
        return df
    def cal_ror(self):
        pass
if __name__ == "__main__":
    # subprocess.Popen('python timesync.py')
    filename = 'DB/stock_easy.txt'
    # with open(filename, "r", encoding="utf-8") as f:
    #     text = f.read()
    with open(filename, "r", encoding="utf-8") as f:
        text_lines = [line.strip() for line in f.readlines()] # str 가장 끝에 개행을 표시하는 \n를 빼고 갖고오기



    api = text_lines[len(text_lines)-3]
    secret = text_lines[len(text_lines)-2]
    acc_no = text_lines[len(text_lines)-1]
    now_day = datetime.datetime.now().date()
    kis = KIS.KoreaInvestment(market='국내주식',api_key=api,secret_key=secret,acc_no=acc_no,mock=False)
    dict_amount,df_stock=kis.fetch_balance()
    if dict_amount:
        print('예수금')
        print(dict_amount)
    if not df_stock.empty:
        print('보유종목')
        print(df_stock)
    df_holiday = kis.check_holiday_domestic_stock(now_day)
    holiday = df_holiday.loc[now_day.strftime("%Y%m%d"),'개장일']
    initial_signal = True
    if holiday == 'Y':
        print('오늘은 휴장일이 아닙니다.')
    else:
        print('오늘은 휴장일 입니다.')
    stg = strategy(kis,text_lines)
    stg.check_chegyeol()
    while holiday == 'Y':
        now_time = datetime.datetime.now().time()
        if initial_signal == True:
            print(f"{now_time.strftime('%H:%M:%S')} 매매 대기 중...")
            if now_time > datetime.time(9,0,2):
                stg.stg_kodex_leverage()
                stg.stg_stock_easy()
                initial_signal = False
        elif now_time > datetime.time(15,45,0):
            stg.check_finish()
            import os
            os.system("shutdown /s /t 0")
            break
        if initial_signal == False:
            stg.check_chegyeol()
            stg.cal_ror()
        time.sleep(1)
    print('종료')


