'''
한국투자증권 python wrapper
'''
import json
import pickle
import asyncio
import sqlite3
import time
from base64 import b64decode
from multiprocessing import Process, Queue
import datetime
import requests
import zipfile
import os
import pandas as pd
from pandas import to_numeric
# from datetime import datetime, timedelta, date
import websockets
# from Crypto.Cipher import AES
# from Crypto.Util.Padding import unpad
from pprint import pprint
import math
import numpy as np
from PyQt5 import QtTest
from PyQt5.QtTest import *
# from dateutil.relativedelta import relativedelta

import common_def

# from user_agent import generate_user_agent, generate_navigator


pd.set_option('display.max_columns',None) #모든 열을 보고자 할 때
pd.set_option('display.max_colwidth', None)
pd.set_option('display.width',1500)
# pd.set_option('display.max_rows', None)  # 출력 옵션 설정: 모든 열의 데이터 유형을 출력
pd.set_option("display.unicode.east_asian_width", True)
pd.set_option('mode.chained_assignment',  None) # SettingWithCopyWarning 경고를 끈다
EXCHANGE_CODE = {
    "홍콩": "HKS",
    "뉴욕": "NYS",
    "나스닥": "NAS",
    "아멕스": "AMS",
    "도쿄": "TSE",
    "상해": "SHS",
    "심천": "SZS",
    "상해지수": "SHI",
    "심천지수": "SZI",
    "호치민": "HSX",
    "하노이": "HNX"
}

# 해외주식 주문
# 해외주식 잔고
EXCHANGE_CODE2 = {
    "미국전체": "NASD",
    "나스닥": "NAS",
    "뉴욕": "NYSE",
    "아멕스": "AMEX",
    "홍콩": "SEHK",
    "상해": "SHAA",
    "심천": "SZAA",
    "도쿄": "TKSE",
    "하노이": "HASE",
    "호치민": "VNSE"
}

EXCHANGE_CODE3 = {
    "나스닥": "NASD",
    "뉴욕": "NYSE",
    "아멕스": "AMEX",
    "홍콩": "SEHK",
    "상해": "SHAA",
    "심천": "SZAA",
    "도쿄": "TKSE",
    "하노이": "HASE",
    "호치민": "VNSE"
}

EXCHANGE_CODE4 = {
    "나스닥": "NAS",
    "뉴욕": "NYS",
    "아멕스": "AMS",
    "홍콩": "HKS",
    "상해": "SHS",
    "심천": "SZS",
    "도쿄": "TSE",
    "하노이": "HNX",
    "호치민": "HSX",
    "상해지수": "SHI",
    "심천지수": "SZI"
}

CURRENCY_CODE = {
    "나스닥": "USD",
    "뉴욕": "USD",
    "아멕스": "USD",
    "홍콩": "HKD",
    "상해": "CNY",
    "심천": "CNY",
    "도쿄": "JPY",
    "하노이": "VND",
    "호치민": "VND"
}

execution_items = [
    "유가증권단축종목코드", "주식체결시간", "주식현재가", "전일대비부호", "전일대비",
    "전일대비율", "가중평균주식가격", "주식시가", "주식최고가", "주식최저가",
    "매도호가1", "매수호가1", "체결거래량", "누적거래량", "누적거래대금",
    "매도체결건수", "매수체결건수", "순매수체결건수", "체결강도", "총매도수량",
    "총매수수량", "체결구분", "매수비율", "전일거래량대비등락율", "시가시간",
    "시가대비구분", "시가대비", "최고가시간", "고가대비구분", "고가대비",
    "최저가시간", "저가대비구분", "저가대비", "영업일자", "신장운영구분코드",
    "거래정지여부", "매도호가잔량", "매수호가잔량", "총매도호가잔량", "총매수호가잔량",
    "거래량회전율", "전일동시간누적거래량", "전일동시간누적거래량비율", "시간구분코드",
    "임의종료구분코드", "정적VI발동기준가"
]

orderbook_items = [
    "유가증권 단축 종목코드",
    "영업시간",
    "시간구분코드",
    "매도호가01",
    "매도호가02",
    "매도호가03",
    "매도호가04",
    "매도호가05",
    "매도호가06",
    "매도호가07",
    "매도호가08",
    "매도호가09",
    "매도호가10",
    "매수호가01",
    "매수호가02",
    "매수호가03",
    "매수호가04",
    "매수호가05",
    "매수호가06",
    "매수호가07",
    "매수호가08",
    "매수호가09",
    "매수호가10",
    "매도호가잔량01",
    "매도호가잔량02",
    "매도호가잔량03",
    "매도호가잔량04",
    "매도호가잔량05",
    "매도호가잔량06",
    "매도호가잔량07",
    "매도호가잔량08",
    "매도호가잔량09",
    "매도호가잔량10",
    "매수호가잔량01",
    "매수호가잔량02",
    "매수호가잔량03",
    "매수호가잔량04",
    "매수호가잔량05",
    "매수호가잔량06",
    "매수호가잔량07",
    "매수호가잔량08",
    "매수호가잔량09",
    "매수호가잔량10",
    "총매도호가 잔량", # 43
    "총매수호가 잔량",
    "시간외 총매도호가 잔량",
    "시간외 총매수호가 증감",
    "예상 체결가",
    "예상 체결량",
    "예상 거래량",
    "예상체결 대비",
    "부호",
    "예상체결 전일대비율",
    "누적거래량",
    "총매도호가 잔량 증감",
    "총매수호가 잔량 증감",
    "시간외 총매도호가 잔량",
    "시간외 총매수호가 증감",
    "주식매매 구분코드"
]

notice_items = [
    "고객ID", "계좌번호", "주문번호", "원주문번호", "매도매수구분", "정정구분", "주문종류",
    "주문조건", "주식단축종목코드", "체결수량", "체결단가", "주식체결시간", "거부여부",
    "체결여부", "접수여부", "지점번호", "주문수량", "계좌명", "체결종목명", "신용구분",
    "신용대출일자", "체결종목명40", "주문가격"
]


class KoreaInvestmentWS(Process):
    """WebSocket
    """
    def __init__(self, api_key: str, api_secret: str, tr_id_list: list,
                 tr_key_list: list, user_id: str = None):
        """_summary_
        Args:
            api_key (str): _description_
            api_secret (str): _description_
            tr_id_list (list): _description_
            tr_key_list (list): _description_
            user_id (str, optional): _description_. Defaults to None.
        """
        super().__init__()
        self.api_key = api_key
        self.api_secret = api_secret
        self.tr_id_list = tr_id_list
        self.tr_key_list = tr_key_list
        self.user_id = user_id
        self.aes_key = None
        self.aes_iv = None
        self.queue = Queue()
        self.base_url = "https://openapi.koreainvestment.com:9443"

    def run(self):
        """_summary_
        """
        asyncio.run(self.ws_client())

    async def ws_client(self):
        """_summary_
        """
        uri = "ws://ops.koreainvestment.com:21000"

        approval_key = self.get_approval()

        async with websockets.connect(uri, ping_interval=None) as websocket:
            header = {
                "approval_key": approval_key,
                "personalseckey": "1",
                "custtype": "P",
                "tr_type": "1",
                "content-type": "utf-8"
            }
            fmt = {
                "header": header,
                "body": {
                    "input": {
                        "tr_id": None,
                        "tr_key": None,
                    }
                }
            }

            # 주식체결, 주식호가 등록
            for tr_id in self.tr_id_list:
                for tr_key in self.tr_key_list:
                    fmt["body"]["input"]["tr_id"] = tr_id
                    fmt["body"]["input"]["tr_key"] = tr_key
                    subscribe_data = json.dumps(fmt)
                    await websocket.send(subscribe_data)

            # 체결 통보 등록
            if self.user_id is not None:
                fmt["body"]["input"]["tr_id"] = "H0STCNI0"
                fmt["body"]["input"]["tr_key"] = self.user_id
                subscribe_data = json.dumps(fmt)
                await websocket.send(subscribe_data)

            while True:
                data = await websocket.recv()
                if data[0] == '0':
                    # 주식체결, 오더북
                    tokens = data.split('|')
                    if tokens[1] == "H0STCNT0":     # 주식 체결 데이터
                        self.parse_execution(tokens[2], tokens[3])
                    elif tokens[1] == "H0STASP0":  #주식 호가 데이터
                        self.parse_orderbook(tokens[3])
                elif data[0] == '1':
                    tokens = data.split('|')
                    if tokens[1] == "H0STCNI0":
                        self.parse_notice(tokens[3])
                else:
                    ctrl_data = json.loads(data)
                    tr_id = ctrl_data["header"]["tr_id"]

                    if tr_id != "PINGPONG":
                        rt_cd = ctrl_data["body"]["rt_cd"]
                        if rt_cd == '1':
                            break
                        elif rt_cd == '0':
                            if tr_id in ["H0STASP0", "K0STCNI9", "H0STCNI0", "H0STCNI9"]:
                                self.aes_key = ctrl_data["body"]["output"]["key"]
                                self.aes_iv  = ctrl_data["body"]["output"]["iv"]

                    elif tr_id == "PINGPONG":
                        await websocket.send(data)

    def get_approval(self) -> str:
        """실시간 (웹소켓) 접속키 발급

        Returns:
            str: 웹소켓 접속키
        """
        headers = {"content-type": "application/json"}
        body = {"grant_type": "client_credentials",
                "appkey": self.api_key,
                "secretkey": self.api_secret}
        PATH = "oauth2/Approval"
        URL = f"{self.base_url}/{PATH}"
        res = requests.post(URL, headers=headers, data=json.dumps(body))
        return res.json()["approval_key"]

    def aes_cbc_base64_dec(self, cipher_text: str):
        """_summary_
        Args:
            cipher_text (str): _description_
        Returns:
            _type_: _description_
        """
        # cipher = AES.new(self.aes_key.encode('utf-8'), AES.MODE_CBC, self.aes_iv.encode('utf-8'))
        # return bytes.decode(unpad(cipher.decrypt(b64decode(cipher_text)), AES.block_size))

    def parse_notice(self, notice_data: str):
        """_summary_
        Args:
            notice_data (_type_): 주식 체잔 데이터
        """
        aes_dec_str = self.aes_cbc_base64_dec(notice_data)
        tokens = aes_dec_str.split('^')
        notice_data = dict(zip(notice_items, tokens))
        self.queue.put(['체잔', notice_data])

    def parse_execution(self, count: str, execution_data: str):
        """주식현재가 실시간 주식 체결가 데이터 파싱
        Args:
            count (str): the number of data
            execution_data (str): 주식 체결 데이터
        """
        tokens = execution_data.split('^')
        for i in range(int(count)):
            parsed_data = dict(zip(execution_items, tokens[i * 46: (i + 1) * 46]))
            self.queue.put(['체결', parsed_data])

    def parse_orderbook(self, orderbook_data: str):
        """_summary_
        Args:
            orderbook_data (str): 주식 호가 데이터
        """
        recvvalue = orderbook_data.split('^')
        orderbook = dict(zip(orderbook_items, recvvalue))
        self.queue.put(['호가', orderbook])

    def get(self):
        """get data from the queue
        Returns:
            _type_: _description_
        """
        data = self.queue.get()
        return data

    def terminate(self):
        if self.is_alive():
            self.kill()


class KoreaInvestment:
    '''
    한국투자증권 REST API
    '''
    def __init__(self, api_key: str, api_secret: str, acc_no: str, market: str,
                 exchange: str = "서울", mock: bool = False):
        """생성자
        Args:
            api_key (str): 발급받은 API key
            api_secret (str): 발급받은 API secret
            acc_no (str): 계좌번호 체계의 앞 8자리-뒤 2자리
            exchange (str): "서울", "나스닥", "뉴욕", "아멕스", "홍콩", "상해", "심천",
                            "도쿄", "하노이", "호치민"
            mock (bool): True (mock trading), False (real trading)
            market (str): "주식", "선옵"
        """
        self.mock = mock
        self.market = market
        self.set_base_url(market, mock)
        self.api_key = api_key
        self.api_secret = api_secret

        # account number
        self.acc_no = acc_no
        self.acc_no_prefix = acc_no.split('-')[0]
        self.acc_no_postfix = acc_no.split('-')[1]

        if self.market == '해외선옵' or self.market == '해외주식':
            exchange = '미국'
        self.exchange = exchange

        # access token
        self.access_token = None
        if self.check_access_token():
            self.load_access_token()
        else:
            self.issue_access_token()

    def set_base_url(self, market: str = '주식', mock: bool = True):
        """테스트(모의투자) 서버 사용 설정
        Args:
            mock(bool, optional): True: 테스트서버, False: 실서버 Defaults to True.
        """
        if market == '주식':
            if mock:
                self.base_url = "https://openapivts.koreainvestment.com:29443"
                # print(f'{market}: 돌다리도 두드리자')
            else:
                self.base_url = "https://openapi.koreainvestment.com:9443"
                # print(f'{market}: 인생은 실전')
        elif market == '선옵':
            if mock:
                self.base_url = "https://openapivts.koreainvestment.com:29443"
                # print(f'{market}: 돌다리도 두드리자')
            else:
                self.base_url = "https://openapi.koreainvestment.com:9443"
                # print(f'{market}: 인생은 실전')
        else:
            raise
    def issue_access_token(self):
        if self.api_key == 'test':
            # print(' KIS 테스트모드')
            pass
        else:
            """OAuth인증/접근토큰발급
            """
            path = "oauth2/tokenP"
            url = f"{self.base_url}/{path}"
            headers = {"content-type": "application/json"}
            data = {
                "grant_type": "client_credentials",
                "appkey": self.api_key,
                "appsecret": self.api_secret
            }

            resp = requests.post(url, headers=headers, data=json.dumps(data))
            resp_data = resp.json()
            self.access_token = f'Bearer {resp_data["access_token"]}'

            # add extra information for the token verification
            now = datetime.datetime.now()
            resp_data['timestamp'] = int(now.timestamp()) + resp_data["expires_in"]
            resp_data['api_key'] = self.api_key
            resp_data['api_secret'] = self.api_secret

            # dump access token
            with open("token.dat", "wb") as f:
                pickle.dump(resp_data, f)

    def check_access_token(self):
        """check access token

        Returns:
            Bool: True: token is valid, False: token is not valid
        """
        try:
            f = open("token.dat", "rb")
            data = pickle.load(f)
            f.close()

            expire_epoch = data['timestamp']
            now_epoch = int(datetime.datetime.now().timestamp())
            status = False

            if ((now_epoch - expire_epoch > 0) or
                (data['api_key'] != self.api_key) or
                (data['api_secret'] != self.api_secret)):
                status = False
            else:
                status = True
            return status
        except IOError:
            return False

    def load_access_token(self):
        """load access token
        """
        with open("token.dat", "rb") as f:
            data = pickle.load(f)
            self.access_token = f'Bearer {data["access_token"]}'

    def check_holiday_domestic_stock(self,day:str):
        """국내주식 업종/기타/국내휴장일조회[국내주식-040] """
        path = "uapi/domestic-stock/v1/quotations/chk-holiday"
        url = f"{self.base_url}/{path}"
        headers = {
           "content-type": "application/json; charset=utf-8",
           "authorization": self.access_token,
           "appKey": self.api_key,
           "appSecret": self.api_secret,
           "tr_id": "CTCA0903R"
        }
        params = {
            "BASS_DT": day,
            "CTX_AREA_NK": '',
            "CTX_AREA_FK": ''
        }
        resp = requests.get(url, headers=headers, params=params)
        return resp.json()


    def issue_hashkey(self, data: dict):
        """해쉬키 발급
        Args:
            data (dict): POST 요청 데이터
        Returns:
            _type_: _description_
        """
        path = "uapi/hashkey"
        url = f"{self.base_url}/{path}"
        headers = {
           "content-type": "application/json",
           "appKey": self.api_key,
           "appSecret": self.api_secret,
           "User-Agent": "Mozilla/5.0"
        }
        resp = requests.post(url, headers=headers, data=json.dumps(data))
        haskkey = resp.json()["HASH"]
        return haskkey

    def fetch_price(self, symbol: str or dict) -> dict:
        if self.exchange == "서울":
            if self.market == '주식':
                return self.fetch_domestic_price("J", symbol)
            elif self.market == '선옵':
                trade_market = '선물' if symbol[:1] == '1' else '콜옵션' if symbol[:1] == '2' else '풋옵션' if symbol[:1] == '3' else '스프레드'
                if trade_market == '선물':
                    return self.fetch_domestic_price("F", symbol)
                elif trade_market[1:] == '옵션':
                    return self.fetch_domestic_price("O", symbol)
        else:
            if self.market == '주식':
                return self.fetch_oversea_price(symbol)
            elif self.market == '해외선옵':
                trade_market = '선물' if symbol[:1] == '1' else '콜옵션' if symbol[:1] == '2' else '풋옵션' if symbol[:1] == '3' else '스프레드'
                if trade_market == '선물':
                    return self.fetch_domestic_price("F", symbol)
                elif trade_market[1:] == '옵션':
                    return self.fetch_domestic_price("O", symbol)

    def fetch_domestic_price(self, market_code: str, symbol: str) -> dict:
        i = 0
        while True:
            if self.market == '주식':
                path = "uapi/domestic-stock/v1/quotations/inquire-price"
                url = f"{self.base_url}/{path}"
                headers = {
                   "content-type": "application/json",
                   "authorization": self.access_token,
                   "appKey": self.api_key,
                   "appSecret": self.api_secret,
                   "tr_id": "FHKST01010100"
                }
                params = {
                    "fid_cond_mrkt_div_code": market_code,
                    "fid_input_iscd": symbol
                }
                resp = requests.get(url, headers=headers, params=params)

            elif self.market == '선옵':
                path = "uapi/domestic-futureoption/v1/quotations/inquire-price"
                url = f"{self.base_url}/{path}"
                headers = {
                   "content-type": "application/json",
                   "authorization": self.access_token,
                   "appKey": self.api_key,
                   "appSecret": self.api_secret,
                   "tr_id": "FHMIF10000000"
                }
                params = {
                    "fid_cond_mrkt_div_code": market_code,
                    "fid_input_iscd": symbol
                }
                resp = requests.get(url, headers=headers, params=params)
            if resp.json()['msg1'] == '정상처리 되었습니다.':
                break
            elif i == 10:
                raise print(f'{symbol} : {i}번 이상 해도 조회 안됨')
            i += 1
            QTest.qWait(500)
        return resp.json()['output']

    def fetch_oversea_price(self, symbol: str) -> dict:
        """해외주식현재가/해외주식 현재체결가
        Args:
            symbol (str): 종목코드
        Returns:
            dict: API 개발 가이드 참조
        """
        path = "uapi/overseas-price/v1/quotations/price"
        url = f"{self.base_url}/{path}"

        # request header
        headers = {
           "content-type": "application/json",
           "authorization": self.access_token,
           "appKey": self.api_key,
           "appSecret": self.api_secret,
           "tr_id": "HHDFS00000300"
        }

        # query parameter
        exchange_code = EXCHANGE_CODE[self.exchange]
        params = {
            "AUTH": "",
            "EXCD": exchange_code,
            "SYMB": symbol
        }
        resp = requests.get(url, headers=headers, params=params)
        return resp.json()

    def fetch_today_1m_ohlcv(self, symbol: str, to: str=""):
        """주식당일분봉조회"""
        ohlcv = []
        now = datetime.datetime.now()
        if self.market == '주식':
            if to == "":
                to = now.strftime("%H%M%S")
                # kospi market end time
                if (90000 > int(to)) or (int(to) > 153000):
                    to = "153000"
            while True:  # 매번 전체를 조회하는 방식임 시간 단축을 위해 추 후 변경 필요
                resp = self._fetch_today_1m_ohlcv(symbol, to)  # to = 현재시간
                if resp['msg1'] != '정상처리 되었습니다.':
                    # time.sleep(0.3)
                    QTest.qWait(300)
                    # QTest.qWait(self,300)
                elif resp['msg1'] == '기간이 만료된 token 입니다.':
                    raise
                else:
                    output = resp['output2']
                    ohlcv.extend(output)
                    to = ohlcv[-1]['stck_cntg_hour']
                    dt = datetime.datetime.strptime(to, "%H%M%S").time()
                    dt = datetime.datetime.combine(datetime.date.today(), dt)
                    dt = dt - datetime.timedelta(minutes=1)
                    # if dt < early:
                    to = dt.strftime("%H%M%S")
                    # time.sleep(0.5)
                    QTest.qWait(500)
                    # QTest.qWait(self,500)

                    if to == '085900':
                        break
            ohlcv = self.make_ohlcv_1m(ohlcv)
            return ohlcv
        elif self.market == '선옵':
            trade_market = '선물' if symbol[:1]=='1' else '콜옵션' if symbol[:1]=='2' else '풋옵션' if symbol[:1]=='3' else '스프레드'
            market_mark = 'F' if trade_market == '선물' else 'O'
            if to == "":
                to = now.strftime("%H%M%S")
                if (90000 > int(to)) or (int(to) > 153000):
                    to = "153400"
            while True:  # 매번 전체를 조회하는 방식임 시간 단축을 위해 추 후 변경 필요
                output = self._fetch_futopt_today_1m_ohlcv(market_mark, symbol, to)  # to = 현재시간
                if output['msg1'] != '정상처리 되었습니다.':
                    # time.sleep(0.3)
                    QTest.qWait(300)
                else:
                    output = output['output2']
                    ohlcv.extend(output)
                    to = ohlcv[-1]['stck_cntg_hour']
                    dt = datetime.datetime.strptime(to, "%H%M%S").time()
                    dt = datetime.datetime.combine(datetime.date.today(), dt)
                    dt = dt - datetime.timedelta(minutes=1)
                    to = dt.strftime("%H%M%S")
                    # time.sleep(0.5)
                    QTest.qWait(500)
                    if to == '084400':
                        break
            ohlcv = self.make_ohlcv_1m(ohlcv)
            return ohlcv
    def fetch_futopt_1m_ohlcv(self, symbol: str, limit: int, ): #허봉을 포함하지 않은 최초 데이터 수집 (허봉 포함 시 당일만 조회됨)
        """풋옵션최초 분봉조회"""
        ohlcv = []
        to = datetime.datetime.now().strftime("%H%M") + "00"  # 마지막에 초는 00으로
        if (90000 > int(to)) or (int(to) > 153000):
            to = "153400"
        day = datetime.datetime.now().date().strftime("%Y%m%d")
        i = 0
        while True:
            i += 1
            output = self._fetch_futopt_today_1m_ohlcv(symbol=symbol,to=to, day=day, fake_tick=False)  # to = 현재시간
            if output['msg1'] == '정상처리 되었습니다.':
                output = output['output2']
                if output :  #체결이 안된 시간은 데이터를 제공하지 않기 때문에 -1분 을 to로 넣어서 조회하면 빈 리스트를 반환 하기 때문에 확인
                    ohlcv.extend(output)
                    if to == '084400': # 8시 44분은 조회가 안되기 때문에 다음날로 넘어가야됨
                        day = ohlcv[-1]['stck_bsop_date']
                        day = datetime.datetime.strptime(day, "%Y%m%d").date()
                        day = day - datetime.timedelta(days=1)
                        day = day.strftime("%Y%m%d")
                        to = "153400"
                    else:
                        day = ohlcv[-1]['stck_bsop_date']
                        to = ohlcv[-1]['stck_cntg_hour']
                        dt = datetime.datetime.strptime(to, "%H%M%S").time()
                        dt = datetime.datetime.combine(datetime.date.today(), dt)
                        dt = dt - datetime.timedelta(minutes=1)
                        to = dt.strftime("%H%M%S")

                    list_bsop_dates = [item['stck_bsop_date'] for item in ohlcv]  # 딕셔너리의 날짜를 리스트로 변환
                    if len(set(list_bsop_dates)) > limit:
                        ohlcv = ohlcv[:list_bsop_dates.index(list_bsop_dates[-1])]
                        break
                    # time.sleep(0.5)
                    QTest.qWait(500)
                else:
                    break
            else:
                # time.sleep(0.5)
                QTest.qWait(500)
                if i > 10:
                    print('fetch_futopt_1m_ohlcv 조회에러')
                    raise
        day = ''
        for i,data in enumerate(ohlcv):
            if day != data['stck_bsop_date']:
                day = data['stck_bsop_date']
            if i + 1 < len(ohlcv):
                if day == data['stck_bsop_date'] and day == ohlcv[i+1]['stck_bsop_date']:
                    t1 = datetime.datetime.strptime(day+data['stck_cntg_hour'],'%Y%m%d%H%M%S')
                    t2 = datetime.datetime.strptime(day+ohlcv[i+1]['stck_cntg_hour'],'%Y%m%d%H%M%S')
                    # t1 = data['stck_cntg_hour']
                    # t2 = ohlcv[i+1]['stck_cntg_hour']
                    # 체결이 안될경우 앞전 값으로 대체 거래량은 0으로 앞전 값으로 대체하고자 하지 않을 경우 주석처리 할 것
                    if t1-t2 != datetime.timedelta(minutes=1):
                        ohlcv.insert(i+1, {'acml_tr_pbmn': '0',
                                         'cntg_vol': '0',
                                         'futs_hgpr': ohlcv[i+1]['futs_hgpr'],
                                         'futs_lwpr': ohlcv[i+1]['futs_lwpr'],
                                         'futs_oprc': ohlcv[i+1]['futs_oprc'],
                                         'futs_prpr': ohlcv[i+1]['futs_prpr'],
                                         'stck_bsop_date': day,
                                         'stck_cntg_hour': datetime.datetime.strftime(t1-datetime.timedelta(minutes=1),'%H%M%S')})
        if not ohlcv:
            ohlcv= [{'acml_tr_pbmn': '0',
                                 'cntg_vol': '0',
                                 'futs_hgpr': '0',
                                 'futs_lwpr': '0',
                                 'futs_oprc': '0',
                                 'futs_prpr': '0',
                                 'stck_bsop_date': datetime.datetime.now().date().strftime("%Y%m%d"),
                                 'stck_cntg_hour': datetime.datetime.now().strftime("%H%M") + "00"}]

        return ohlcv
    def _fetch_today_1m_ohlcv(self, symbol: str, to: str):
        """국내주식시세/주식당일분봉조회

        Args:
            symbol (str): 6자리 종목코드
            to (str): "HH:MM:SS"
        """
        path = "/uapi/domestic-stock/v1/quotations/inquire-time-itemchartprice"
        url = f"{self.base_url}/{path}"
        headers = {
           "content-type": "application/json; charset=utf-8",
           "authorization": self.access_token,
           "appKey": self.api_key,
           "appSecret": self.api_secret,
           "tr_id": "FHKST03010200",
           "tr_cont": "",
        }

        params = {
            "fid_etc_cls_code": "",
            "fid_cond_mrkt_div_code": "J",
            "fid_input_iscd": symbol,
            "fid_input_hour_1": to,
            "fid_pw_data_incu_yn": "N"  #N : 당일데이터만 조회   Y : 이후데이터도 조회
        }
        i = 0
        while True:
            res = requests.get(url, headers=headers, params=params)
            # hrd = {'User_Agent': generate_user_agent(os='win', device_type='desktop')}
            if res.json()['msg1'] == '정상처리 되었습니다.':
                break
            elif i == 10:
                raise print(f'{symbol} : {i}번 이상 해도 조회 안됨 - _fetch_today_1m_ohlcv')
            else:
                # time.sleep(1)
                QTest.qWait(500)
            i += 1
        return res.json()


    def _fetch_futopt_today_1m_ohlcv(self, symbol: str, to: str, day:str="", fake_tick:bool=False):
        """국내선물옵션기본시세/손물옵션 분봉조회
        """
        path = "uapi/domestic-futureoption/v1/quotations/inquire-time-fuopchartprice"
        url = f"{self.base_url}/{path}"
        headers = {
           "content-type": "application/json; charset=utf-8",
           "authorization": self.access_token,
           "appKey": self.api_key,
           "appSecret": self.api_secret,
           "tr_id": "FHKIF03020200",
           "tr_cont": "",
        }
        continue_check = "N" if day == "" else "Y" # continue_day에 날짜가 들어오면 "Y"
        fake_tick = 'Y' if fake_tick == True else "N"
        trade_market = 'F' if symbol[:1] == '1' else 'O'
        params = {
            "FID_COND_MRKT_DIV_CODE": trade_market,
            "FID_INPUT_ISCD": symbol,
            "FID_HOUR_CLS_CODE": "60",
            "FID_PW_DATA_INCU_YN":continue_check, # "Y"일 경우 연속 조회
            "FID_FAKE_TICK_INCU_YN":fake_tick, #허봉 조회
            "FID_INPUT_DATE_1": day , # YYYYMMDD  ex) 20230908 입력 시, 2023년 9월 8일부터 일자 역순으로 조회
            "FID_INPUT_HOUR_1": to,
        }
        i=0

        while True:
            try:
                res = requests.get(url, headers=headers, params=params)  # 연결된 구성원으로부터 - 에러 발생
                output = res.json()
            except:
                output = {}
                output['msg1'] = 'KIS:_fetch_futopt_today_1m_ohlcv - 연결된 구성원으로부터 응답이 없어 연결하지 못했거나, 호스트로부터 응답이 없어 연결이 끊어졌습니다'
                # time.sleep(1)
                QTest.qWait(800)
            if output['msg1'] == '정상처리 되었습니다.':
                break
            elif output['msg1'] == 'KIS:_fetch_futopt_today_1m_ohlcv - 연결된 구성원으로부터 응답이 없어 연결하지 못했거나, 호스트로부터 응답이 없어 연결이 끊어졌습니다':
                print(output['msg1'])
            elif output['msg1'] == '기간이 만료된 token 입니다.':
                QTest.qWait(800)
                if i == 10:
                    print(output['msg1'])
                    print(f'{symbol} : {i}번 이상 해도 조회 안됨 - _fetch_futopt_today_1m_ohlcv')
                    QTest.qWait(800)
                    i = 0
                    raise
                    # raise print(f'{symbol} : {i}번 이상 해도 조회 안됨 - _fetch_futopt_today_1m_ohlcv')
            else:
                # time.sleep(1)
                QTest.qWait(800)
                if i == 10:
                    print(output['msg1'])
                    print(f'{symbol} : {i}번 이상 해도 조회 안됨 - _fetch_futopt_today_1m_ohlcv')
                    if output['msg1'] == '기간이 만료된 token 입니다.':
                        print('기간만료')

                    QTest.qWait(800)

                    i = 0
                    # raise print(f'{symbol} : {i}번 이상 해도 조회 안됨 - _fetch_futopt_today_1m_ohlcv')
            i += 1
            # time.sleep(1)
            QTest.qWait(500)
        return output


    def make_ohlcv_1m(self, ohlcv):
        try:
            df = pd.DataFrame(ohlcv)
        except:
            ohlcv
        dt = pd.to_datetime(df['stck_bsop_date'] + df['stck_cntg_hour'], format="%Y%m%d%H%M%S")
        df.set_index(dt, inplace=True)
        df = df.apply(to_numeric)
        if self.market == '주식':
            df = df[['stck_oprc', 'stck_hgpr', 'stck_lwpr', 'stck_prpr', 'cntg_vol', 'acml_tr_pbmn']]
            df.columns = ['시가', '고가', '저가', '종가', '거래량', '누적거래대금']
            df['거래대금'] = df['누적거래대금'] - df['누적거래대금'].shift(-1)
            # df['거래량'] = df['누적거래량'] - df['누적거래량'].shift(-1)
        elif self.market == '선옵':
            df = df[['futs_oprc', 'futs_hgpr', 'futs_lwpr', 'futs_prpr', 'cntg_vol', 'acml_tr_pbmn']]
            df.columns = ['시가', '고가', '저가', '종가', '거래량', '누적거래대금']
            df['거래대금'] = df['누적거래대금'] - df['누적거래대금'].shift(-1)
        df.index.name = "날짜"
        df = df[::-1]  # 거꾸로 뒤집기
        return df

    def display_opt(self, today): #휴일에 대한 대응이 안되어있음
        """국내선물옵션기본시세/국내옵션전광판_콜풋"""
        path = "uapi/domestic-futureoption/v1/quotations/display-board-callput"
        url = f"{self.base_url}/{path}"
        data = {
            "CANO": self.acc_no_prefix,
            "ACNT_PRDT_CD": self.acc_no_postfix,
            "OVRS_EXCG_CD": "SHAA"
        }
        hashkey = self.issue_hashkey(data)
        headers = {
           "content-type": "application/json; charset=utf-8",
           "authorization": self.access_token,
           "appKey": self.api_key,
           "appSecret": self.api_secret,
           "tr_id": "FHPIF05030100",
           "tr_cont": "",
           "custtype": "P",
           "hashkey": hashkey
            }
        expiry_date = self.nth_weekday(today,2,3) #이번달의 두번째 주, 목요일 구하기
        if today > expiry_date:
            expiry_month = today+datetime.timedelta(days=25)
            expiry_month = expiry_month.strftime("%Y%m")
        else:
            expiry_month = today.strftime("%Y%m")

        i = 0
        while True:
            params = {
                "FID_COND_MRKT_DIV_CODE": "O",
                "FID_COND_SCR_DIV_CODE": "20503",
                "FID_MRKT_CLS_CODE": 'CO',
                "FID_MTRT_CNT": expiry_month,
                "FID_COND_MRKT_CLS_CODE": "",
                "FID_MRKT_CLS_CODE1": "PO"
                }

            res = requests.get(url, headers=headers, params=params)
            if res.json()['msg1'] == '정상처리 되었습니다.':
                # pprint(res.json())
                df_call = pd.DataFrame(res.json()['output1'])
                df_put = pd.DataFrame(res.json()['output2'])
                # if df_call.empty:
                #     today = today + datetime.timedelta(days=25)
                # else:
                df_call.rename(
                    columns={'acpr': '행사가',
                             'unch_prpr': '환산현재가',
                             'optn_shrn_iscd': '종목코드',
                             'optn_prpr': '현재가',
                             'optn_prdy_vrss': '전일대비',
                             'prdy_vrss_sign': '전일대비부호',
                             'optn_prdy_ctrt': '옵션전일대비율',
                             'total_askp_rsqn': '매도호가잔량',
                             'total_bidp_rsqn': '매수호가잔량',
                             'optn_bidp': '매수호가',
                             'optn_askp': '매도호가',
                             'hts_otst_stpl_qty':'미결제약정',
                             'acml_vol': '거래량',
                             'acml_tr_pbmn': '거래대금'},inplace=True)
                df_call = df_call[['행사가','환산현재가','종목코드','현재가','전일대비','전일대비부호',
                                   '옵션전일대비율','매수호가','매도호가','매도호가잔량','매수호가잔량','미결제약정','거래량','거래대금']]
                df_call.set_index(df_call['종목코드'], inplace=True)
                df_put.rename(
                    columns={'acpr': '행사가',
                             'unch_prpr': '환산현재가',
                             'optn_shrn_iscd': '종목코드',
                             'optn_prpr': '현재가',
                             'optn_prdy_vrss': '전일대비',
                             'prdy_vrss_sign': '전일대비부호',
                             'optn_prdy_ctrt': '옵션전일대비율',
                             'total_askp_rsqn': '매도호가잔량',
                             'total_bidp_rsqn': '매수호가잔량',
                             'optn_bidp': '매수호가',
                             'optn_askp': '매도호가',
                             'acml_vol': '거래량',
                             'acml_tr_pbmn': '거래대금'},inplace=True)
                df_put = df_put[['행사가','환산현재가','종목코드','현재가','전일대비','전일대비부호',
                                 '옵션전일대비율','매수호가','매도호가','매도호가잔량','매수호가잔량','거래량','거래대금']]
                df_put.set_index(df_put['종목코드'], inplace=True)
                break
            elif res.json()['msg1'] == '초당 거래건수를 초과하였습니다.':
                print(f'display_opt   {res.json()}')
                QTest.qWait(1000)
            else:
                # time.sleep(1)
                # QTest.qWait(1000)
                # i += 1
                # if i == 10:
                pprint(res.json())
                print('display_opt 조회할 수 없음')
                df_call = pd.DataFrame()
                df_put = pd.DataFrame()
        return df_call, df_put
    def display_opt_weekly(self,today):
        """국내선물옵션기본시세/국내옵션전광판_콜풋"""
        path = "uapi/domestic-futureoption/v1/quotations/display-board-callput"
        url = f"{self.base_url}/{path}"
        data = {
            "CANO": self.acc_no_prefix,
            "ACNT_PRDT_CD": self.acc_no_postfix,
            "OVRS_EXCG_CD": "SHAA"
        }
        hashkey = self.issue_hashkey(data)
        headers = {
           "content-type": "application/json; charset=utf-8",
           "authorization": self.access_token,
           "appKey": self.api_key,
           "appSecret": self.api_secret,
           "tr_id": "FHPIF05030100",
           "tr_cont": "",
           "custtype": "P",
           "hashkey": hashkey
            }
        # 월: 0, 화: 1 ~ 일: 6
        dict_yoil = {'월':0,'화':1,'수':2,'목':3,'금':4,'토':5,'일':6}
        yoil = datetime.datetime.weekday(today)

        first_day_of_month = today.replace(day=1)
        first_day_weekday = first_day_of_month.isoweekday()  # 0 = 월요일, 6 = 일요일, 월요일 기준으로 하고싶으면 isoweekday() 대신에 weekday()로 변경

        # 이번 달 시작 주를 보정하여 몇 주차인지 계산
        adjusted_day = today.day + first_day_weekday
        number_of_week = (adjusted_day - 1) // 7
        if yoil == dict_yoil['월'] or yoil == dict_yoil['금'] or yoil == dict_yoil['토'] or yoil == dict_yoil['일']: #위클리 월요일일 경우
            COND_MRKT = "WKM" #위클리(월)
            if yoil == dict_yoil['금'] or yoil == dict_yoil['토']:
                number_of_week += 1
            expiry_date_week = datetime.datetime.strftime(today,'%Y%m')+'0'+str(number_of_week)
        else:
            # first_day_of_month = datetime.datetime.today().replace(day=1,second=0, microsecond=0)
            first_day_of_month = today.replace(day=1,second=0, microsecond=0)

            # 첫 번째 주의 목요일 찾기
            first_week_start = first_day_of_month - datetime.timedelta(days=first_day_of_month.weekday())  # 첫 주의 월요일

            second_week_start = first_week_start + datetime.timedelta(weeks=1)  # 두 번째 주의 월요일
            second_thursday = second_week_start + datetime.timedelta(days=3)  # 두 번째 주의 목요일

            # 오늘이 두 번째 주의 목요일인지 확인
            thursday_week = second_thursday.date()-datetime.timedelta(days=2)

            if thursday_week < today.date() and today.date() <= second_thursday.date() :  # 만기주 일 경우
                df_call, df_put = self.display_opt(today)
                return df_call, df_put, '만기주'
                # COND_MRKT = "" #몬슬리(목)
                # expiry_date_week = self.nth_weekday(today,2,3) #이번달의 두번째 주, 목요일 구하기

            elif yoil == dict_yoil['화'] or yoil == dict_yoil['수'] or yoil == dict_yoil['목']:
                number_of_week += 1
                expiry_date_week = datetime.datetime.strftime(today,'%Y%m')+'0'+str(number_of_week)
                COND_MRKT = "WKI" #위클리(목)
            else:
                raise


        while True:
            params = {
                "FID_COND_MRKT_DIV_CODE": "O",
                "FID_COND_SCR_DIV_CODE": "20503",
                "FID_MRKT_CLS_CODE": 'CO',
                "FID_MTRT_CNT": expiry_date_week[2:], #2024의 경우 앞에 20은 제외
                "FID_COND_MRKT_CLS_CODE": COND_MRKT,
                "FID_MRKT_CLS_CODE1": "PO"
                }
            res = requests.get(url, headers=headers, params=params)
            if res.json()['msg1'] == '정상처리 되었습니다.' and res.json()['output1'] and res.json()['output2']:
                df_call = pd.DataFrame(res.json()['output1'])
                df_put = pd.DataFrame(res.json()['output2'])
                # pprint(res.json())
                # if df_call.empty:
                #     today = today + datetime.timedelta(days=25)
                # else:
                df_call.rename(
                    columns={'acpr': '행사가',
                             'unch_prpr': '환산현재가',
                             'optn_shrn_iscd': '종목코드',
                             'optn_prpr': '현재가',
                             'optn_prdy_vrss': '전일대비',
                             'prdy_vrss_sign': '전일대비부호',
                             'optn_prdy_ctrt': '옵션전일대비율',
                             'total_askp_rsqn': '매도호가잔량',
                             'total_bidp_rsqn': '매수호가잔량',
                             'optn_bidp': '매수호가',
                             'optn_askp': '매도호가',
                             'hts_otst_stpl_qty':'미결제약정',
                             'acml_vol': '거래량',
                             'acml_tr_pbmn': '거래대금'},inplace=True)
                df_call = df_call[['행사가','환산현재가','종목코드','현재가','전일대비','전일대비부호',
                                   '옵션전일대비율','매수호가','매도호가','매도호가잔량','매수호가잔량','미결제약정','거래량','거래대금']]
                df_call.set_index(df_call['종목코드'], inplace=True)

                df_put.rename(
                    columns={'acpr': '행사가',
                             'unch_prpr': '환산현재가',
                             'optn_shrn_iscd': '종목코드',
                             'optn_prpr': '현재가',
                             'optn_prdy_vrss': '전일대비',
                             'prdy_vrss_sign': '전일대비부호',
                             'optn_prdy_ctrt': '옵션전일대비율',
                             'total_askp_rsqn': '매도호가잔량',
                             'total_bidp_rsqn': '매수호가잔량',
                             'optn_bidp': '매수호가',
                             'optn_askp': '매도호가',
                             'acml_vol': '거래량',
                             'acml_tr_pbmn': '거래대금'},inplace=True)
                df_put = df_put[['행사가','환산현재가','종목코드','현재가','전일대비','전일대비부호',
                                 '옵션전일대비율','매수호가','매도호가','매도호가잔량','매수호가잔량','거래량','거래대금']]
                df_put.set_index(df_put['종목코드'], inplace=True)
                break
            elif res.json()['msg1'] == '초당 거래건수를 초과하였습니다.':
                print(f'display_opt_weekly   {res.json()}')
                QTest.qWait(500)
            elif res.json()['msg1'] == '정상처리 되었습니다.' and not res.json()['output1'] and not res.json()['output2']:
                df_call = pd.DataFrame()
                df_put = pd.DataFrame()
                return  df_call, df_put, COND_MRKT
            else:
                pprint(res.json())
                raise
        return df_call, df_put, COND_MRKT


    def display_fut(self):
        """국내선물옵션기본시세/국내선물전광판_선물"""
        path = "uapi/domestic-futureoption/v1/quotations/display-board-futures"
        url = f"{self.base_url}/{path}"
        data = {
            "CANO": self.acc_no_prefix,
            "ACNT_PRDT_CD": self.acc_no_postfix,
            "OVRS_EXCG_CD": "SHAA"
        }

        params = {
            "FID_COND_MRKT_DIV_CODE": "F",
            "FID_COND_SCR_DIV_CODE": "20503",
            "FID_COND_MRKT_CLS_CODE": '',
            }
        hashkey = self.issue_hashkey(data)
        headers = {
           "content-type": "application/json; charset=utf-8",
           "authorization": self.access_token,
           "appKey": self.api_key,
           "appSecret": self.api_secret,
           "tr_id": "FHPIF05030200",
           "tr_cont": "",
           "custtype": "P",
           "hashkey": hashkey
            }
        i = 0
        while True:
            res = requests.get(url, headers=headers, params=params)
            if res.json()['msg1'] == '정상처리 되었습니다.':
                break
            else:
                i += 1
            if i == 10:
                pprint(res.json())
                if res.json()['msg1'] == '초당 거래건수를 초과하였습니다.':
                    QTest.qWait(1000)
        df = pd.DataFrame(res.json()['output'])
        df.rename(columns={'futs_shrn_iscd': '종목코드',
                           'hts_kor_isnm': '종목명',
                           'futs_prpr': '현재가',
                           'futs_prdy_vrss': '전일대비',
                     'futs_prdy_ctrt': '등락(%)',
                           'hts_thpr': '이론가',
                           'acml_vol': '거래량',
                           'futs_askp': '매도호가',
                     'futs_bidp': '매수호가',
                           'total_askp_rsqn':'매도호가 잔량',
                           'total_bidp_rsqn':'매수호가 잔량',

                           'hts_otst_stpl_qty': '미결제약정',
                           'futs_hgpr': '최고가',
                           'futs_lwpr': '최저가'}, inplace=True)
        df = df[['종목코드','종목명','현재가','전일대비','등락(%)','이론가','거래량','매도호가','매수호가','미결제약정','최고가','최저가']]
        df.set_index(df['종목코드'], inplace=True)

        return df

    def investor_trend(self):
        """국내주식 시세분석/국내기관_외국인 매매종목가집계[국내주식-037]"""
        path = "uapi/domestic-stock/v1/quotations/foreign-institution-total"
        url = f"{self.base_url}/{path}"
        market = "0000"
        params = {
            "FID_COND_MRKT_DIV_CODE": "V",
            "FID_COND_SCR_DIV_CODE": "16449",
            "FID_INPUT_ISCD": "0001", # 0000:전체, 0001:코스피, 1001:코스닥
            "FID_DIV_CLS_CODE": "1", # 0: 수량정열, 1: 금액정열
            "FID_RANK_SORT_CLS_CODE": "0", # 0: 순매수상위, 1: 순매도상위
            "FID_ETC_CLS_CODE": "0" # 0:전체 1:외국인 2:기관계 3:기타
        }
        headers = {
           "content-type": "application/json; charset=utf-8",
           "authorization": self.access_token,
           "appKey": self.api_key,
           "appSecret": self.api_secret,
           "tr_id": "FHPTJ04400000",
        }
        resp = requests.get(url, headers=headers, params=params)
        pprint(resp)
        return resp.json()
    def investor_trend_time(self,market) -> dict:
        """국내주식 시세분석/시장별 투자자매매동향(시세)"""
        path = "uapi/domestic-stock/v1/quotations/inquire-investor-time-by-market"
        url = f"{self.base_url}/{path}"
        # if market == '선물' or market == '콜옵션' or market == '풋옵션':
        if market in ['선물','콜옵션','풋옵션']:
            iscd = "K2I"
            iscd2 = "F001" if market == '선물' \
                else "OC01" if market == '콜옵션' \
                else 'OP01' if market=='풋옵션' else ''
        elif market == '주식선물':
            iscd = "999"
            if market == '주식선물': iscd2 = "S001"
        elif market in ['콜_위클리_월','콜_위클리_목','풋_위클리_월','풋_위클리_목']:
            if market in ['콜_위클리_월','풋_위클리_월']:
                iscd = "WKM"
                if market == '콜_위클리_월':
                    iscd2 = "OC05"
                    market = "콜_위클리"
                elif market == '풋_위클리_월':
                    iscd2 = "OP05"
                    market = "풋_위클리"
            elif market in ['콜_위클리_목','풋_위클리_목']:
                iscd = "WKI"
                if market == '콜_위클리_목':
                    iscd2 = "OC04"
                    market = "콜_위클리"
                elif market == '풋_위클리_목':
                    iscd2 = "OP04"
                    market = "풋_위클리"
        elif market == '코스피':
            iscd = "KSP"
            iscd2 = "0001"
        headers = {
           "content-type": "application/json; charset=utf-8",
           "authorization": self.access_token,
           "appKey": self.api_key,
           "appSecret": self.api_secret,
           "tr_id": "FHPTJ04030000",
           "tr_cont": "",
        }
        params = {
            'fid_input_iscd_2': iscd2,
            'fid_input_iscd': iscd,
        }
        i = 0
        while True:
            try:
                resp = requests.get(url, headers=headers, params=params)
                output = resp.json()
            except:
                output={}
            if output['msg1'] == '정상처리 되었습니다.':
                output = output['output'][0]
                외인 = int(output['frgn_ntby_tr_pbmn'])
                개인 = int(output['prsn_ntby_tr_pbmn'])
                기관 = int(output['orgn_ntby_tr_pbmn'])
                return {f"{market}_외인":외인, f"{market}_개인": 개인, f"{market}_기관":기관}
            elif i == 10:
                print(f'investor_trend_time : {i}번 이상 해도 조회 안됨 - investor_trend_time')
                resp = requests.get(url, headers=headers, params=params)
                pprint(resp.json())
                return 0, 0, 0
            i += 1
            QTest.qWait(500)



    def investor_trend_estimate(self,ticker):
        path = "uapi/domestic-stock/v1/quotations/investor-trend-estimate"
        url = f"{self.base_url}/{path}"
        params = {
            "MKSC_SHRN_ISCD": ticker,
        }
        # hashkey = self.issue_hashkey(data)
        headers = {
           "content-type": "application/json; charset=utf-8",
           "authorization": self.access_token,
           "appKey": self.api_key,
           "appSecret": self.api_secret,
           "tr_id": "HHPTJ04160200",
           "tr_cont": "",
           # "hashkey": hashkey
        }
        resp = requests.get(url, headers=headers, params=params)
        return resp.json()
    def fetch_ohlcv(self, symbol: str, timeframe: str = 'D', early_day:str="", lately_day:str="",
                    adj_price: bool = True) -> dict:
        """fetch OHLCV (day, week, month)
        Args:
            symbol (str): 종목코드
            timeframe (str): "D" (일), "W" (주), "M" (월)
            early_day (str): 조회시작일자
            lately_day (str): 조회종료일자
            adj_price (bool, optional): True: 수정주가 반영, False: 수정주가 미반영. Defaults to True.
        Returns:
            dict: _description_
        """
        if self.exchange == '서울':
            ohlcv = []
            if self.market == '주식':
                if early_day == '':
                    early_day = datetime.datetime.now().date() - datetime.timedelta(days=600) # early_day 비어있으면 600일 이전 조회
                    early_day = early_day.strftime("%Y%m%d")
                while True :
                    # print(early_day, lately_day)
                    resp = self._fetch_ohlcv_domestic(symbol, timeframe, early_day, lately_day, adj_price)
                    if [item for item in resp['output2'] if item == {}]: #output2가 빈 딕셔너리를 보내면 탈출
                        break
                    elif resp['msg1'] == '정상처리 되었습니다.':
                        ohlcv.extend(resp['output2'])

                        start_day = resp['output2'][-1]['stck_bsop_date']
                        start_day = datetime.datetime.strptime(start_day,"%Y%m%d").date()
                        lately_day = start_day - datetime.timedelta(days=1)
                        lately_day = lately_day.strftime("%Y%m%d")
                        if datetime.datetime.strptime(early_day,"%Y%m%d").date() >= start_day:
                            break
                        elif datetime.datetime.strptime(early_day,"%Y%m%d").date() >= datetime.datetime.strptime(lately_day,"%Y%m%d").date():
                            break
                        elif len(resp['output2']) < 100:
                            break
                        # time.sleep(0.5)
                        QTest.qWait(500)
                        # print(early_day, "==" ,lately_day)
                    elif resp['msg1'] == '기간이 만료된 token 입니다.':
                        raise
                    else:
                        QTest.qWait(300)
                        # if not resp:
                        #     break

            elif self.market == '선옵':
                trade_market = '선물' if symbol[:1] == '1' else '콜옵션' if symbol[:1] == '2' else '풋옵션' if symbol[:1] == '3' else '스프레드'
                if trade_market == '선물': market = 'F'
                elif trade_market == '옵션': market = 'O'
                resp = self._fetch_futopt_ohlcv_domestic(symbol, timeframe, early_day, lately_day, market)
                ohlcv = resp['output2']
            ########################
            df = pd.DataFrame(ohlcv)
            if not df.empty:
                dt = pd.to_datetime(df['stck_bsop_date'], format="%Y%m%d")
                df.set_index(dt, inplace=True)
                # print(df)
                if self.market == '주식':
                    df = df[['stck_oprc', 'stck_hgpr', 'stck_lwpr', 'stck_clpr', 'acml_vol', 'acml_tr_pbmn']]
                    df.columns = ['시가', '고가', '저가', '종가', '거래량', '거래대금']
                elif self.market == '선옵':
                    if trade_market == '선물':
                        df = df[['futs_oprc', 'futs_hgpr', 'futs_lwpr', 'futs_prpr','acml_vol', 'acml_tr_pbmn']]
                        df.columns = ['시가', '고가', '저가', '종가', '거래량', '거래대금']
                    elif trade_market == '옵션':
                        df = df[['futs_oprc', 'futs_hgpr', 'futs_lwpr', 'futs_prpr','acml_vol', 'acml_tr_pbmn']]
                        df.columns = ['시가', '고가', '저가', '종가', '거래량', '거래대금']
                df.index.name = "날짜"
                df = df.apply(to_numeric)
                df = df[::-1]  # 거꾸로 뒤집기
                return df
            else:
                return pd.DataFrame()


        else:
            while True:
                resp = self.fetch_ohlcv_overesea(symbol, timeframe, lately_day, adj_price)
                try:
                    print(resp)
                    return resp
                except:
                    pass


    def fetch_ohlcv_recent30(self, symbol: str, timeframe: str = 'D', adj_price: bool = True) -> dict:
        """국내주식시세/주식 현재가 일자별
        Args:
            symbol (str): 종목코드
            timeframe (str): "D" (일), "W" (주), "M" (월)
            adj_price (bool, optional): True: 수정주가 반영, False: 수정주가 미반영. Defaults to True.
        Returns:
            dict: _description_
        """
        path = "uapi/domestic-stock/v1/quotations/inquire-daily-price"
        url = f"{self.base_url}/{path}"
        headers = {
           "content-type": "application/json",
           "authorization": self.access_token,
           "appKey": self.api_key,
           "appSecret": self.api_secret,
           "tr_id": "FHKST01010400"
        }

        adj_param = "1" if adj_price else "0"
        params = {
            "fid_cond_mrkt_div_code": "J",
            "fid_input_iscd": symbol,
            "fid_org_adj_prc": adj_param,
            "fid_period_div_code": timeframe
        }
        res = requests.get(url, headers=headers, params=params)
        return res.json()


    def fetch_symbols(self):
        """fetch symbols from the exchange

        Returns:
            pd.DataFrame: pandas dataframe
        """
        if self.exchange == "서울":
            df = self.fetch_kospi_symbols()
            kospi_df = df[['단축코드', '한글명', '그룹코드']].copy()
            kospi_df['시장'] = '코스피'

            df = self.fetch_kosdaq_symbols()
            kosdaq_df = df[['단축코드', '한글명', '그룹코드']].copy()
            kosdaq_df['시장'] = 'KOSDAQ'

            df = pd.concat([kospi_df, kosdaq_df], axis=0)

        return df

    def download_master_file(self, base_dir: str, file_name: str, url: str):
        """download master file

        Args:
            base_dir (str): download directory
            file_name (str: filename
            url (str): url
        """
        os.chdir(base_dir)

        # delete legacy master file
        if os.path.exists(file_name):
            os.remove(file_name)

        # download master file
        resp = requests.get(url)
        with open(file_name, "wb") as f:
            f.write(resp.content)

        # unzip
        kospi_zip = zipfile.ZipFile(file_name)
        kospi_zip.extractall()
        kospi_zip.close()

    def parse_kospi_master(self, base_dir: str):
        """parse kospi master file

        Args:
            base_dir (str): directory where kospi code exists

        Returns:
            _type_: _description_
        """
        file_name = base_dir + "/kospi_code.mst"
        tmp_fil1 = base_dir + "/kospi_code_part1.tmp"
        tmp_fil2 = base_dir + "/kospi_code_part2.tmp"

        wf1 = open(tmp_fil1, mode="w", encoding="cp949")
        wf2 = open(tmp_fil2, mode="w")

        with open(file_name, mode="r", encoding="cp949") as f:
            for row in f:
                rf1 = row[0:len(row) - 228]
                rf1_1 = rf1[0:9].rstrip()
                rf1_2 = rf1[9:21].rstrip()
                rf1_3 = rf1[21:].strip()
                wf1.write(rf1_1 + ',' + rf1_2 + ',' + rf1_3 + '\n')
                rf2 = row[-228:]
                wf2.write(rf2)

        wf1.close()
        wf2.close()

        part1_columns = ['단축코드', '표준코드', '한글명']
        df1 = pd.read_csv(tmp_fil1, header=None, encoding='cp949', names=part1_columns)

        field_specs = [
            2, 1, 4, 4, 4,
            1, 1, 1, 1, 1,
            1, 1, 1, 1, 1,
            1, 1, 1, 1, 1,
            1, 1, 1, 1, 1,
            1, 1, 1, 1, 1,
            1, 9, 5, 5, 1,
            1, 1, 2, 1, 1,
            1, 2, 2, 2, 3,
            1, 3, 12, 12, 8,
            15, 21, 2, 7, 1,
            1, 1, 1, 1, 9,
            9, 9, 5, 9, 8,
            9, 3, 1, 1, 1
        ]

        part2_columns = [
            '그룹코드', '시가총액규모', '지수업종대분류', '지수업종중분류', '지수업종소분류',
            '제조업', '저유동성', '지배구조지수종목', 'KOSPI200섹터업종', 'KOSPI100',
            'KOSPI50', 'KRX', 'ETP', 'ELW발행', 'KRX100',
            'KRX자동차', 'KRX반도체', 'KRX바이오', 'KRX은행', 'SPAC',
            'KRX에너지화학', 'KRX철강', '단기과열', 'KRX미디어통신', 'KRX건설',
            'Non1', 'KRX증권', 'KRX선박', 'KRX섹터_보험', 'KRX섹터_운송',
            'SRI', '기준가', '매매수량단위', '시간외수량단위', '거래정지',
            '정리매매', '관리종목', '시장경고', '경고예고', '불성실공시',
            '우회상장', '락구분', '액면변경', '증자구분', '증거금비율',
            '신용가능', '신용기간', '전일거래량', '액면가', '상장일자',
            '상장주수', '자본금', '결산월', '공모가', '우선주',
            '공매도과열', '이상급등', 'KRX300', 'KOSPI', '매출액',
            '영업이익', '경상이익', '당기순이익', 'ROE', '기준년월',
            '시가총액', '그룹사코드', '회사신용한도초과', '담보대출가능', '대주가능'
        ]

        df2 = pd.read_fwf(tmp_fil2, widths=field_specs, names=part2_columns)
        df = pd.merge(df1, df2, how='outer', left_index=True, right_index=True)

        # clean temporary file and dataframe
        del (df1)
        del (df2)
        os.remove(tmp_fil1)
        os.remove(tmp_fil2)
        return df

    def parse_kosdaq_master(self, base_dir: str):
        """parse kosdaq master file

        Args:
            base_dir (str): directory where kosdaq code exists

        Returns:
            _type_: _description_
        """
        file_name = base_dir + "/kosdaq_code.mst"
        tmp_fil1 = base_dir +  "/kosdaq_code_part1.tmp"
        tmp_fil2 = base_dir +  "/kosdaq_code_part2.tmp"

        wf1 = open(tmp_fil1, mode="w", encoding="cp949")
        wf2 = open(tmp_fil2, mode="w")
        with open(file_name, mode="r", encoding="cp949") as f:
            for row in f:
                rf1 = row[0:len(row) - 222]
                rf1_1 = rf1[0:9].rstrip()
                rf1_2 = rf1[9:21].rstrip()
                rf1_3 = rf1[21:].strip()
                wf1.write(rf1_1 + ',' + rf1_2 + ',' + rf1_3 + '\n')

                rf2 = row[-222:]
                wf2.write(rf2)

        wf1.close()
        wf2.close()

        part1_columns = ['단축코드', '표준코드', '한글명']
        df1 = pd.read_csv(tmp_fil1, header=None, encoding="cp949", names=part1_columns)

        field_specs = [
            2, 1, 4, 4, 4,      # line 20
            1, 1, 1, 1, 1,      # line 27
            1, 1, 1, 1, 1,      # line 32
            1, 1, 1, 1, 1,      # line 38
            1, 1, 1, 1, 1,      # line 43
            1, 9, 5, 5, 1,      # line 48
            1, 1, 2, 1, 1,      # line 54
            1, 2, 2, 2, 3,      # line 64
            1, 3, 12, 12, 8,    # line 69
            15, 21, 2, 7, 1,    # line 75
            1, 1, 1, 9, 9,      # line 80
            9, 5, 9, 8, 9,      # line 85
            3, 1, 1, 1
        ]

        part2_columns = [
            '그룹코드', '시가총액규모', '지수업종대분류', '지수업종중분류', '지수업종소분류', # line 20
            '벤처기업', '저유동성', 'KRX', 'ETP', 'KRX100',  # line 27
            'KRX자동차', 'KRX반도체', 'KRX바이오', 'KRX은행', 'SPAC',   # line 32
            'KRX에너지화학', 'KRX철강', '단기과열', 'KRX미디어통신', 'KRX건설', # line 38
            '투자주의', 'KRX증권', 'KRX선박', 'KRX섹터_보험', 'KRX섹터_운송',   # line 43
            'KOSDAQ150', '기준가', '매매수량단위', '시간외수량단위', '거래정지',    # line 48
            '정리매매', '관리종목', '시장경고', '경고예고', '불성실공시',   # line 54
            '우회상장', '락구분', '액면변경', '증자구분', '증거금비율',     # line 64
            '신용가능', '신용기간', '전일거래량', '액면가', '상장일자',     # line 69
            '상장주수', '자본금', '결산월', '공모가', '우선주',     # line 75
            '공매도과열', '이상급등', 'KRX300', '매출액', '영업이익',   # line 80
            '경상이익', '당기순이익', 'ROE', '기준년월', '시가총액',    # line 85
            '그룹사코드', '회사신용한도초과', '담보대출가능', '대주가능'
        ]

        df2 = pd.read_fwf(tmp_fil2, widths=field_specs, names=part2_columns)
        df = pd.merge(df1, df2, how='outer', left_index=True, right_index=True)

        # clean temporary file and dataframe
        del (df1)
        del (df2)
        os.remove(tmp_fil1)
        os.remove(tmp_fil2)
        return df

    def fetch_kospi_symbols(self):
        """코스피 종목 코드

        Returns:
            DataFrame:
        """
        base_dir = os.getcwd()
        file_name = "kospi_code.mst.zip"
        url = "https://new.real.download.dws.co.kr/common/master/" + file_name
        self.download_master_file(base_dir, file_name, url)
        df = self.parse_kospi_master(base_dir)
        return df

    def fetch_kosdaq_symbols(self):
        """KOSDAQ 종목 코드

        Returns:
            DataFrame:
        """
        base_dir = os.getcwd()
        file_name = "kosdaq_code.mst.zip"
        url = "https://new.real.download.dws.co.kr/common/master/" + file_name
        self.download_master_file(base_dir, file_name, url)
        df = self.parse_kosdaq_master(base_dir)
        return df

    def check_buy_order(self, symbol: str, price: int, order_type: str):
        """국내주식주문/매수가능조회
        Args:
            symbol (str): symbol
            price (int): 1주당 가격
            order_type (str): "00": 지정가, "01": 시장가, ..., "80": 바스켓
        """
        if self.exchange == '서울':
            if self.market == '주식':
                path = "/uapi/domestic-stock/v1/trading/inquire-psbl-order"
                url = f"{self.base_url}/{path}"
                headers = {
                   "content-type": "application/json",
                   "authorization": self.access_token,
                   "appKey": self.api_key,
                   "appSecret": self.api_secret,
                   "tr_id": "VTTC8908R" if self.mock else "TTTC8908R"
                }
                params = {
                    'CANO': self.acc_no_prefix,
                    'ACNT_PRDT_CD': self.acc_no_postfix,
                    'PDNO': symbol,
                    'ORD_UNPR': str(price),
                    'ORD_DVSN': order_type,
                    'CMA_EVLU_AMT_ICLD_YN': '1',
                    'OVRS_ICLD_YN': '1'
                }

                res = requests.get(url, headers=headers, params=params)
                data = res.json()
                data['tr_cont'] = res.headers['tr_cont']
            elif self.market == '선옵':
                path = "/uapi/domestic-futureoption/v1/trading/inquire-psbl-order"
                url = f"{self.base_url}/{path}"
                headers = {
                    "content-type": "application/json; charset=utf-8",
                    "authorization": self.access_token,
                    "appKey": self.api_key,
                    "appSecret": self.api_secret,
                    "tr_id": "VTTO5105R" if self.mock else "TTTO5105R"
                }
                params = {
                    'CANO': self.acc_no_prefix,
                    'ACNT_PRDT_CD': self.acc_no_postfix,
                    'PDNO': symbol,
                    'SLL_BUY_DVSN_CD': str(price),
                    'UNIT_PRICE': order_type,
                    'ORD_DVSN_CD': '1',
                }

                res = requests.get(url, headers=headers, params=params)
                data = res.json()
                pprint(res.json())
        return data

    def fetch_balance(self) -> dict:
        """잔고 조회

        Args:

        Returns:
            dict: response data
        """
        if self.exchange == '서울':
            output = {}
            dict_amount = {}
            i = 0
            while True:
                data = self.fetch_balance_domestic()
                if data['msg1'] == '정상처리 되었습니다.'or data['msg1'] == '모의투자 조회가 완료되었습니다.                                                 ':
                    break
                else:
                    # time.sleep(0.5)
                    QTest.qWait(1000)
                    i += 1
                    if i > 10:
                        print('fetch_balance 조회에러')
                        pprint(data['msg1'])
                        quit()

            if self.market == '주식':
                # pprint(data)
                output['output1'] = data['output1']
                output['output2'] = data['output2']
                #
                # while data['tr_cont'] == 'M':
                #     fk100 = data['ctx_area_fk100']
                #     nk100 = data['ctx_area_nk100']
                #
                #     data = self.fetch_balance_domestic(fk100, nk100)
                #     output['output1'].extend(data['output1'])
                #     output['output2'].extend(data['output2'])
                #####################################
                dict_amount["예수금"] = int(output['output2'][0]['dnca_tot_amt'])
                dict_amount["총평가금액"] = int(output['output2'][0]['tot_evlu_amt'])
                df_instock = pd.DataFrame(output['output1'])
                if not df_instock.empty:
                    df_instock.rename(
                        columns={'prdt_name':'종목명','pdno':'종목코드','thdt_buyqty':'금일매수수량','thdt_sll_qty':'금일매도수량',
                                 'hldg_qty':'보유수량','ord_psbl_qty':'주문가능수량','pchs_amt':'매입금액','evlu_amt':'평가금액',
                                 'evlu_pfls_amt':'평가손익','evlu_pfls_rt':'평가손익율','evlu_erng_rt':'평가수익율','fltt_rt':'등락율',
                                 'bfdy_cprs_icdc':'전일대비증감'}, inplace=True)
                    df_instock = df_instock[['종목명','종목코드','금일매수수량','금일매도수량','보유수량','주문가능수량',
                                             '매입금액','평가금액','평가손익','평가손익율','평가수익율']]
                    df_instock.set_index('종목코드', inplace=True)
            elif self.market == '선옵':
                # output['output1'] = data['output1']
                # output['output2'] = data['output2']

                # while data['tr_cont'] == 'M':
                #     fk100 = data['ctx_area_fk100']
                #     nk100 = data['ctx_area_nk100']
                #
                #     data = self.fetch_balance_domestic(fk100, nk100)
                #     output['output1'].extend(data['output1'])
                #     output['output2'].extend(data['output2'])
                #####################################
                dict_amount['예수금현금'] = int(data['output2']['dnca_cash'])
                dict_amount['현금증거금'] = int(data['output2']['cash_mgna'])
                dict_amount['증거금총액'] = int(data['output2']['mgna_tota'])
                dict_amount['평가금액합계'] = int(data['output2']['evlu_amt_smtl'])
                dict_amount['주문가능현금'] = int(data['output2']['ord_psbl_cash'])
                df_instock = pd.DataFrame(data['output1'])
                if not df_instock.empty:
                    df_instock.rename(
                        columns={'cblc_qty':'잔고수량','ccld_avg_unpr1':'체결평균단가','evlu_amt':'평가금액','excc_unpr':'정산단가',
                                 'idx_clpr':'지수종가','lqd_psbl_qty':'청산가능수량','pchs_amt':'매입금액','evlu_pfls_amt':'평가손익',
                                 'pdno':'상품번호','prdt_name':'상품명','prdt_type_cd':'상품유형코드','shtn_pdno':'종목코드',
                                 'sll_buy_dvsn_name':'매도매수구분명','trad_pfls_amt':'매매손익금액'}, inplace=True)
                    df_instock = df_instock[['잔고수량','체결평균단가','평가금액','정산단가','지수종가','청산가능수량','매입금액',
                                             '평가손익','상품번호','상품명','상품유형코드','종목코드','매도매수구분명','매매손익금액']]
                    df_instock.set_index('종목코드', inplace=True)
            # return output
            return dict_amount, df_instock
        else: #해외주식, 선물, 옵션
            # 해외주식 잔고
            output = {}

            data = self.fetch_balance_oversea()
            output['output1'] = data['output1']
            output['output2'] = data['output2']

            while data['tr_cont'] == 'M':
                fk200 = data['ctx_area_fk200']
                nk200 = data['ctx_area_nk200']

                data = self.fetch_balance_oversea(fk200, nk200)
                output['output1'].extend(data['output1'])
                output['output2'].extend(data['output2'])

            return output

    def fetch_balance_domestic(self, ctx_area_fk100: str = "", ctx_area_nk100: str = "") -> dict:
        if self.market == '주식':
            """국내주식주문/주식잔고조회
            Args:
                ctx_area_fk100 (str): 연속조회검색조건100
                ctx_areak_nk100 (str): 연속조회키100
            Returns:
                dict: _description_
            """
            path = "uapi/domestic-stock/v1/trading/inquire-balance"
            url = f"{self.base_url}/{path}"
            headers = {
               "content-type": "application/json",
               "authorization": self.access_token,
               "appKey": self.api_key,
               "appSecret": self.api_secret,
               "tr_id": "VTTC8434R" if self.mock else "TTTC8434R"
            }
            params = {
                'CANO': self.acc_no_prefix,
                'ACNT_PRDT_CD': self.acc_no_postfix,
                'AFHR_FLPR_YN': 'N',
                'OFL_YN': 'N',
                'INQR_DVSN': '01',
                'UNPR_DVSN': '01',
                'FUND_STTL_ICLD_YN': 'N',
                'FNCG_AMT_AUTO_RDPT_YN': 'N',
                'PRCS_DVSN': '01',
                'CTX_AREA_FK100': ctx_area_fk100,
                'CTX_AREA_NK100': ctx_area_nk100
            }

            res = requests.get(url, headers=headers, params=params)
            data = res.json()
            # data['tr_cont'] = res.headers['tr_cont']
            return data
        elif self.market == '선옵':
            # print('선물')
            """국내선물옵션/선물옵션잔고조회 """
            path = "uapi/domestic-futureoption/v1/trading/inquire-balance"
            url = f"{self.base_url}/{path}"
            headers = {
               "content-type": "application/json",
               "authorization": self.access_token,
               "appKey": self.api_key,
               "appSecret": self.api_secret,
               "tr_id": "VTFO6118R" if self.mock else "CTFO6118R",
                "custtype": "P"
            }
            params = {
                'CANO': self.acc_no_prefix,
                'ACNT_PRDT_CD': self.acc_no_postfix,
                'MGNA_DVSN': '01',
                'EXCC_STAT_CD': '1',
                'CTX_AREA_FK200': '',
                'CTX_AREA_NK200': '',
            }

            res = requests.get(url, headers=headers, params=params)
            data = res.json()
            # pprint(data)
            # data['tr_cont'] = res.headers['tr_cont']
            return data


    def fetch_present_balance(self, foreign_currency: bool=True) -> dict:
        """해외주식주문/해외주식 체결기준현재잔고
        Args:
            foreign_currency (bool): True: 외화, False: 원화
        Returns:
            dict: _description_
        """
        path = "/uapi/overseas-stock/v1/trading/inquire-present-balance"
        url = f"{self.base_url}/{path}"

        # request header
        headers = {
           "content-type": "application/json",
           "authorization": self.access_token,
           "appKey": self.api_key,
           "appSecret": self.api_secret,
           "tr_id": "VTRP6504R" if self.mock else "CTRP6504R"
        }

        # query parameter
        nation_code = "000"
        if self.exchange in ["나스닥", "뉴욕", "아멕스"]:
            nation_code = "840"
        elif self.exchange == "홍콩":
            nation_code = "344"
        elif self.exchange in ["상해", "심천"]:
            nation_code = "156"
        elif self.exchange == "도쿄":
            nation_code = "392"
        elif self.exchange in ["하노이", "호치민"]:
            nation_code = "704"
        else:
            nation_code = "000"

        market_code = "00"
        if nation_code == "000":
            market_code = "00"
        elif nation_code == "840":
            if self.exchange == "나스닥":
                market_code = "01"
            elif self.exchange == "뉴욕":
                market_code = "02"
            elif self.exchange == "아멕스":
                market_code = "05"
            else:
                market_code = "00"
        elif nation_code == "156":
            market_code = "00"
        elif nation_code == "392":
            market_code = "01"
        elif nation_code == "704":
            if self.exchange == "하노이":
                market_code = "01"
            else:
                market_code = "02"
        else:
            market_code = "01"

        params = {
            'CANO': self.acc_no_prefix,
            'ACNT_PRDT_CD': self.acc_no_postfix,
            "WCRC_FRCR_DVSN_CD": "02" if foreign_currency else "01",
            "NATN_CD": nation_code,
            "TR_MKET_CD": market_code,
            "INQR_DVSN_CD": "00"
        }
        res = requests.get(url, headers=headers, params=params)
        return res.json()

    def fetch_balance_oversea(self, ctx_area_fk200: str = "", ctx_area_nk200: str = "") -> dict:
        """해외주식주문/해외주식 잔고
        Args:
            ctx_area_fk200 (str): 연속조회검색조건200
            ctx_area_nk200 (str): 연속조회키200
        Returns:
            dict: _description_
        """
        path = "/uapi/overseas-stock/v1/trading/inquire-balance"
        url = f"{self.base_url}/{path}"


        # 주야간원장 구분 호출
        resp = self.fetch_oversea_day_night()
        psbl = resp['output']['PSBL_YN']

        if self.mock:
            tr_id = "VTTS3012R" if psbl == 'N' else 'VTTT3012R'
        else:
            tr_id = "TTTS3012R" if psbl == 'N' else 'JTTT3012R'

        # request header
        headers = {
           "content-type": "application/json",
           "authorization": self.access_token,
           "appKey": self.api_key,
           "appSecret": self.api_secret,
           "tr_id": tr_id
        }

        # query parameter
        exchange_cd = EXCHANGE_CODE2[self.exchange]
        currency_cd = CURRENCY_CODE[self.exchange]

        params = {
            'CANO': self.acc_no_prefix,
            'ACNT_PRDT_CD': self.acc_no_postfix,
            'OVRS_EXCG_CD': exchange_cd,
            'TR_CRCY_CD': currency_cd,
            'CTX_AREA_FK200': ctx_area_fk200,
            'CTX_AREA_NK200': ctx_area_nk200
        }

        res = requests.get(url, headers=headers, params=params)
        data = res.json()
        data['tr_cont'] = res.headers['tr_cont']
        return data

    def fetch_oversea_day_night(self):
        """해외주식주문/해외주식 주야간원장구분조회
        """
        path = "/uapi/overseas-stock/v1/trading/dayornight"
        url = f"{self.base_url}/{path}"

        # request/header
        headers = {
           "content-type": "application/json",
           "authorization": self.access_token,
           "appKey": self.api_key,
           "appSecret": self.api_secret,
           "tr_id": "JTTT3010R"
        }

        res = requests.get(url, headers=headers)
        return res.json()

    def create_order(self, side: str, symbol: str, price, quantity: int, order_type: str) -> dict:
        while True:
            QTest.qWait(500)
            if self.market == '주식':
                path = "uapi/domestic-stock/v1/trading/order-cash"
                url = f"{self.base_url}/{path}"

                if self.mock:
                    tr_id = "VTTC0802U" if side == "buy" else "VTTC0801U"
                else:
                    tr_id = "TTTC0802U" if side == "buy" else "TTTC0801U"

                unpr = "0" if order_type == "시장가" else str(price)

                data = {
                    "CANO": self.acc_no_prefix,
                    "ACNT_PRDT_CD": self.acc_no_postfix,
                    "PDNO": symbol,
                    "ORD_DVSN": order_type,
                    "ORD_QTY": str(quantity),
                    "ORD_UNPR": unpr
                }
                hashkey = self.issue_hashkey(data)
                headers = {
                   "content-type": "application/json",
                   "authorization": self.access_token,
                   "appKey": self.api_key,
                   "appSecret": self.api_secret,
                   "tr_id": tr_id,
                   "custtype": "P",
                   "hashkey": hashkey
                }
                resp = requests.post(url, headers=headers, data=json.dumps(data))

            elif self.market == '선옵':
                path = "/uapi/domestic-futureoption/v1/trading/order"
                url = f"{self.base_url}/{path}"
                if self.mock:
                    tr_id = "VTTO1101U"
                else: # 실매매는 주간 야간 따로임
                    sky = '야간' if datetime.datetime.now().time() > datetime.time(18,0,0) or datetime.time(5,0,0) > datetime.datetime.now().time() else '주간'
                    tr_id = "TTTO1101U" if sky == "주간" else "JTCE1001U"
                SLL_BUY = "02" if side == "buy" else "01"
                unpr = "0" if order_type == "시장가" else str(price)
                ORD = "02" if order_type == "시장가" else "01"
                # print(f"{symbol= }, {SLL_BUY= },{unpr= },{ORD= }, {quantity= }")
                data = {
                    "ORD_PRCS_DVSN_CD": "02",
                    "CANO": self.acc_no_prefix,
                    "ACNT_PRDT_CD": self.acc_no_postfix,
                    "SLL_BUY_DVSN_CD": SLL_BUY, #01 : 매도 , 02 : 매수
                    "SHTN_PDNO": symbol,
                    "ORD_QTY": str(quantity),
                    "UNIT_PRICE": unpr, # 시장가나 최유리 지정가인 경우 0으로 입력
                    "NMPR_TYPE_CD": "",
                    "KRX_NMPR_CNDT_CD": "",
                    "ORD_DVSN_CD": ORD # 01 : 지정가, 02 : 시장가
                }
                hashkey = self.issue_hashkey(data)
                headers = {
                    "content-type": "application/json",
                    "authorization": self.access_token,
                    "appKey": self.api_key,
                    "appSecret": self.api_secret,
                    "tr_id": tr_id ,
                    "custtype": "P",
                    "hashkey": hashkey
                }
                # print(f"kis _create order : {side=}, {symbol=} {quantity=} {unpr=} {order_type=}, {tr_id=}")
                resp = requests.post(url, headers=headers, data=json.dumps(data))
                resp = resp.json()
            if resp['msg1'] == '주문 전송 완료 되었습니다.' or resp['msg1'] == '모의투자 매수주문이 완료 되었습니다.' or resp[
                'msg1'] == '모의투자 매도주문이 완료 되었습니다.':
                resp['output']['ODNO'] = int(resp['output']['ODNO'])
                id = str(resp['output']['ODNO'])  # 주문번호가 '000456' 이런식으로 오기 때문에 str → int → str 로 변환
                break
            elif resp['msg1'] == '주문가능금액을 초과 했습니다':
                raise print(f"create_order - {resp['msg1']}  주문 가능금액 초과")
            elif resp['msg1'] == '주문수량을 확인 하여 주십시요.':
                raise print(f"create_order - {resp['msg1']}  {symbol= }, {price= }, {quantity= }, {price*quantity= }")
            elif resp['msg1'] == '장운영일자가 주문일과 상이합니다':
                pprint(resp)
                raise print(resp['msg1'])
            elif resp['msg1'] == '주문 수량을 확인해주세요.':
                raise print(f"create_order - {resp['msg1']} - 주문 시간이 안맞았을 확률 또는 가격이나 수량이 float으로 되있거나 틀릴 확률")
            elif resp['msg1'] == '주식주문호가단위 오류입니다.':
                pprint(resp)
                raise print(resp['msg1'])
            elif resp['msg1'] == '모의투자 장시작전 입니다.':
                print(f"create_order - {resp['msg1']}")
                # time.sleep(1)
                QTest.qWait(1000)
            elif resp['msg1'] == '초당 거래건수를 초과하였습니다.':
                print(f"create_order - {resp['msg1']=}, {symbol=},  ")
            elif resp['msg1'] == '모의투자 장종료 입니다.':
                raise print(f"create_order - {resp['msg1']}")
            elif resp['msg1'] == '모의투자 주문처리가 안되었습니다(호가단위 오류)':
                raise print(f"{resp['msg1']} 종목코드: {symbol}, 매수가: {price}, 배팅금액: {price * quantity * 250000}, {quantity= }")
            elif resp['msg1'] == '모의투자 주문가능금액이 부족합니다.':
                dict_asset, df_x = self.fetch_balance()  # 자산, 보유종목
                print(f"{dict_asset}")
                print(f"create_order - {resp['msg1']} 에러 | {symbol=}, {price= }, {quantity= }, {price * quantity= }")
                raise
            elif resp['msg1'] == '모의투자 상/하한가 오류':
                pprint(f"create_order - 모의투자 상/하한가 오류 {symbol=}, {price=} {quantity=}, {side=}")
            else:
                print('create_order - =============== else ===============')
                pprint(f"create_order {resp}, {symbol=}, {price=} {quantity=}, {side=}")
                quit()
        return id

    def create_market_buy_order(self, symbol: str, quantity: int, side:str) -> dict:
        # print(f'create_market_buy_order {symbol= }, {quantity= }')
        if self.exchange == "서울":
            if self.market == '주식':
                id = self.create_order(side = "buy", symbol=symbol, price=00, quantity=quantity, order_type="시장가")
            elif self.market == '선옵':
                id = self.create_order(side = side, symbol=symbol, price=0, quantity=quantity, order_type="시장가")
        else: # 해외
            id = self.create_oversea_order("buy", symbol, "0", quantity, "00")
        return id

    def create_market_sell_order(self, symbol: str, quantity: int, side:str) -> dict:
        # print(f'create_market_sell_order {symbol= }, {quantity= }')
        if self.exchange == "서울":
            if self.market == '주식':
                id = self.create_order("sell", symbol, 0, quantity, "시장가")
            elif self.market == '선옵':
                id = self.create_order(side=side, symbol=symbol, price=0, quantity=quantity, order_type="시장가")
        else: # 해외
            id = self.create_oversea_order("sell", symbol, "0", quantity, "00")
        return id

    def create_limit_buy_order(self, symbol: str, price: int, quantity: int, side:str) -> dict:
        # print(f'create_limit_buy_order {symbol= }, {price= } {quantity= }')
        if self.exchange == "서울":
            if self.market == '주식':
                id = self.create_order("buy", symbol, price, quantity, "00")
            elif self.market == '선옵':
                id = self.create_order(side=side, symbol=symbol, price=price, quantity=quantity, order_type="지정가")
        else: # 해외
            id = self.create_oversea_order("buy", symbol, price, quantity, "00")
        return id

    def create_limit_sell_order(self, symbol: str, price: int, quantity: int, side:str) -> dict:
        # print(f'create_limit_sell_order {symbol= }, {price= } {quantity= }')
        if self.exchange == "서울":
            if self.market == '주식':
                id = self.create_order("sell", symbol, price, quantity, "00")
            elif self.market == '선옵':
                id = self.create_order(side=side, symbol=symbol, price=price, quantity=quantity, order_type="지정가")
        else: # 해외
            id = self.create_oversea_order("sell", symbol, price, quantity, "00")
        return id

    def cancel_order(self,symbol, order_no: str, quantity: int):
        """주문 취소
        Args:
            org_no(str): organization number
            order_no (str): order number
            quantity (int): 수량
            total (bool): True (잔량전부), False (잔량일부)
            order_type (str): 주문구분
            price (int): 가격
        Returns:
            dict :
        """
        i = 0
        while True:
            try:
                output = self.update_order(symbol, order_no, int(quantity) ,  price = 0, order_type = '시장가', is_change = '취소', total = True)
            except:
                output = {}
                output['msg1'] = 'KIS:cancel_order - 연결된 구성원으로부터 응답이 없어 연결하지 못했거나, 호스트로부터 응답이 없어 연결이 끊어졌습니다'
            if output['msg1'] == '모의투자 취소주문이 완료 되었습니다.' or output['msg1'] == '취소주문이 완료 되었습니다.':
                break
            elif output['msg1'] == '모의투자 정정/취소할 수량이 없습니다.' or output['msg1'] == '정정/취소할 수량이 없습니다.':
                break
            else:
                print(f"KIS-cancel_order - {output['msg1']}  {symbol=}, {order_no=} {quantity= }")
                i += 1
                if i > 10:
                    raise print(f'{symbol} : {i}번 이상 해도 조회 안됨 - cancel_order')
            # time.sleep(0.5)
            QTest.qWait(500)
        return output['msg1']

    def modify_order(self, org_no: str, order_no: str, order_type: str,
                     price: int, quantity: int, total: bool):
        """주문정정
        Args:
            org_no(str): organization number
            order_no (str): order number
            order_type (str): 주문구분
            price (int): 가격
            quantity (int): 수량
            total (bool): True (잔량전부), False (잔량일부)
        Returns:
            dict : _description_
        """
        i = 0
        # while True:
        output = self.update_order(org_no, order_no, order_type, price, quantity, True, total)
            # if output['msg1'] == '모의투자 취소주문이 완료 되었습니다.' or output['msg1'] == '취소주문이 완료 되었습니다.':
            #     break
            # else:
            #     i += 1
            #     if i > 10:
            #
        return output

    def update_order(self,symbol:str, order_no: str, quantity: int ,  price,
                     order_type: str = '시장가', is_change: str = '취소', total: bool = True):
        """국내주식주문/주식주문(정정취소)
        Args:
            org_no (str): organization code
            order_no (str): order number
            order_type (str): 주문구분
            price (int): 가격
            quantity (int): 수량
            is_change (bool, optional): True: 정정, False: 취소
            total (bool, optional): True (잔량전부), False (잔량일부)
        Returns:
            _type_: _description_
        """
        if self.exchange == '서울':
            if self.market == '주식':
                path = "uapi/domestic-stock/v1/trading/order-rvsecncl"
                url = f"{self.base_url}/{path}"
                order_type = '00' if order_type == '지정가' else "01"
                param = "02" if is_change == '취소' else "01"
                data = {
                    "CANO": self.acc_no_prefix,
                    "ACNT_PRDT_CD": self.acc_no_postfix,
                    "KRX_FWDG_ORD_ORGNO": "", #org_no
                    "ORGN_ODNO": order_no,
                    "ORD_DVSN": order_type, #주문구분
                    "RVSE_CNCL_DVSN_CD": param, # 정정 : 01 취소 : 02
                    "ORD_QTY": str(quantity),
                    "ORD_UNPR": str(price),
                    "QTY_ALL_ORD_YN": 'Y' if total else 'N'
                }
                hashkey = self.issue_hashkey(data)
                headers = {
                   "content-type": "application/json",
                   "authorization": self.access_token,
                   "appKey": self.api_key,
                   "appSecret": self.api_secret,
                   "tr_id": "VTTC0803U" if self.mock else "TTTC0803U",
                   "hashkey": hashkey
                }
                resp = requests.post(url, headers=headers, data=json.dumps(data))
            elif self.market == '선옵':
                path = "uapi/domestic-futureoption/v1/trading/order-rvsecncl"
                url = f"{self.base_url}/{path}"

                if self.mock:
                    tr_id = "VTTO1103U"
                else:  # 실매매는 주간 야간 따로임
                    sky = '야간' if datetime.datetime.now().time() > datetime.time(18, 0, 0) or datetime.time(5, 0,
                                                                                                            0) > datetime.datetime.now().time() else '주간'
                    tr_id = "TTTO1103U" if sky == "주간" else "JTCE1002U"

                order_type = '02' if order_type == '시장가' else "01"
                param = "02" if is_change == '취소' else "01"
                price = "0" if is_change == '취소' else price
                krx_code = "0" if is_change == '취소' else ""
                order_code = "01" if is_change == '취소' else ""
                market = '01' if symbol[:1] == '1' else '02' if symbol[:1] == '2' else '03' if symbol[:1] == '3' else '04'


                data = {
                    "ORD_PRCS_DVSN_CD":"02",
                    "CANO": self.acc_no_prefix,
                    "ACNT_PRDT_CD": self.acc_no_postfix,
                    "RVSE_CNCL_DVSN_CD": param, # 정정 : 01 취소 : 02
                    "ORGN_ODNO": order_no,
                    "ORD_QTY": str(quantity),
                    "UNIT_PRICE": str(price), # 시장가나 최유리의 경우 0으로 입력 (취소 시에도 0 입력)
                    "NMPR_TYPE_CD": order_type, # 01 : 지정가 02 : 시장가 03 : 조건부
                    "KRX_NMPR_CNDT_CD": krx_code,
                    "RMN_QTY_YN": 'Y' if total else 'N',
                    "FUOP_ITEM_DVSN_CD": market,
                    "ORD_DVSN_CD": order_code,   # 01 : 지정가 02 : 시장가 03 : 조건부
                }
                hashkey = self.issue_hashkey(data)
                headers = {
                   "content-type": "application/json",
                   "authorization": self.access_token,
                   "appKey": self.api_key,
                   "appSecret": self.api_secret,
                   "tr_id": tr_id,
                   "hashkey": hashkey
                }
                resp = requests.post(url, headers=headers, data=json.dumps(data))
        return resp.json()

    def fetch_open_order(self, side: str):
        if self.market == '주식':
            """주식 정정/취소가능 주문 조회
            Args:
                param (dict): 세부 파라미터
            Returns:
                _type_: _description_
            """
            path = "uapi/domestic-stock/v1/trading/inquire-psbl-rvsecncl"
            url = f"{self.base_url}/{path}"

            headers = {
               "content-type": "application/json; charset=utf-8",
               "authorization": self.access_token,
               "appKey": self.api_key,
               "appSecret": self.api_secret,
               "tr_id": "TTTC8036R"
            }
            side = '2' if side == 'buy' else '1'
            params = {
                "CANO": self.acc_no_prefix,
                "ACNT_PRDT_CD": self.acc_no_postfix,
                "CTX_AREA_FK100": '',
                "CTX_AREA_NK100": '',
                "INQR_DVSN_1": '1',   # 0 : 조회순서, 1 : 주문순, 2 : 종목순
                "INQR_DVSN_2": side
            }
            resp = requests.get(url, headers=headers, params=params)
        elif self.market == '선옵':
            path = "uapi/domestic-futureoption/v1/trading/order-rvsecncl"
            url = f"{self.base_url}/{path}"

        return resp.json()
    def fetch_closed_order(self, side:str='ALL',  ticker:str='',id:str=''):
        """주식일별주문체결조회
        Args:
        Returns:
            _type_: _description_
        """
        if self.market == '주식':
            path = "/uapi/domestic-stock/v1/trading/inquire-daily-ccld"
            url = f"{self.base_url}/{path}"
            tr = 'VTTC8001R' if self.mock else 'TTTC8001R'
            headers = {
               "content-type": "application/json",
               "authorization": self.access_token,
               "appKey": self.api_key,
               "appSecret": self.api_secret,
               "tr_id": tr
            }

            side = '02' if side == 'buy' else '01' if side == 'sell' else '00'
            ctx_area_fk200 = ''
            ctx_area_nk200 = ''
            while True:
                QTest.qWait(1000)
                params = {
                    "CANO": self.acc_no_prefix,
                    "ACNT_PRDT_CD": self.acc_no_postfix,
                    "INQR_STRT_DT": datetime.datetime.now().strftime("%Y%m%d"),
                    "INQR_END_DT": datetime.datetime.now().strftime("%Y%m%d"),
                    # "INQR_STRT_DT": '20240723',
                    # "INQR_END_DT": '20240723',
                    "SLL_BUY_DVSN_CD": side,
                    "INQR_DVSN": '00', #00 역순 , 01 정순
                    "PDNO": ticker,
                    "CCLD_DVSN": '01', # 00 : 전체, 01 : 체결, 02 : 미체결
                    "ORD_GNO_BRNO": "",
                    "ODNO": id,
                    "INQR_DVSN_3": "00",
                    "INQR_DVSN_1": "",
                    "CTX_AREA_FK100": ctx_area_fk200,
                    "CTX_AREA_NK100": ctx_area_nk200
                }
                try:
                    res = requests.get(url, headers=headers, params=params)
                    if i > 10:
                        pprint(res.json())
                        print('fetch_closed_order 이상 감지')
                        break
                    elif res.json()['msg1'] == '모의투자 조회할 내역(자료)이 없습니다.                                          ':
                        df_chegyeol = pd.DataFrame()
                        break
                    elif res.json()['msg1'] == '초당 거래건수를 초과하였습니다.':
                        print(f"fetch_closed_order - {res.json()['msg1']=} {i= }")
                        QTest.qWait(1000)
                    elif res.json()['msg1'] == '모의투자 조회가 완료되었습니다.                                                 ' \
                            or res.json()['msg1'] == '조회가 완료되었습니다.':
                        list_odno = [str(int(item['odno'])) for item in res.json()['output1']]  # 딕셔너리의 주문번호를 리스트로
                        if not res.json()['output1']:
                            if id in list_odno:
                                dict_chegyeol = res.json()['output1'][list_odno.index(id)]
                                break
                        else:
                            dict_chegyeol = {}
                    elif res.json()['msg1'] == '모의투자 조회가 계속 됩니다. 다음 또는 PaDn을 누르십시오.                       ':
                        list_odno = [str(int(item['odno'])) for item in res.json()['output1']]  # 딕셔너리의 주문번호를 리스트로
                        if id in list_odno:
                            dict_chegyeol = res.json()['output1'][list_odno.index(id)]
                            break
                        ctx_area_nk200 = res.json()['ctx_area_nk200']
                        ctx_area_nk200 = str(int(ctx_area_nk200))
                    else:
                        print(res.json()['msg1'], 'fetch_closed_order')
                        pprint(res.json())
                        raise
                except:
                    print('kis: fetch_closed_order - HTTPSConnectionPool')
                i += 1


        elif self.market == '선옵':
            path = "/uapi/domestic-futureoption/v1/trading/inquire-ccnl"
            url = f"{self.base_url}/{path}"
            tr = 'VTTO5201R' if self.mock else 'TTTO5201R'

            headers = {
                "content-type": "application/json",
                "authorization": self.access_token,
                "appKey": self.api_key,
                "appSecret": self.api_secret,
                "custtype": "P",
                "tr_id": tr
            }

            side = '02' if side == 'buy' else '01' if side=='sell' else '00'

            ctx_area_fk200 = ''
            ctx_area_nk200 = ''
            # output_chegyeol = []
            i = 0
            while True:
                QTest.qWait(1000)
                params = {
                    "CANO": self.acc_no_prefix,
                    "ACNT_PRDT_CD": self.acc_no_postfix,
                    "STRT_ORD_DT": datetime.datetime.now().strftime("%Y%m%d"),
                    "END_ORD_DT": datetime.datetime.now().strftime("%Y%m%d"),
                    # "STRT_ORD_DT": '20241014',
                    # "END_ORD_DT": '20241014',
                    "SLL_BUY_DVSN_CD": side,
                    "CCLD_NCCS_DVSN": '01',
                    "SORT_SQN": 'DS',
                    "STRT_ODNO": '01',
                    "PDNO": ticker,
                    "MKET_ID_CD": "",
                    "CTX_AREA_FK200": ctx_area_fk200,
                    "CTX_AREA_NK200": ctx_area_nk200
                    }
                # print(pd.DataFrame(res.json()['output1']))
                # quit()
                # list_odno = [str(int(item['odno'])) for item in res.json()['output1']]  # 딕셔너리의 주문번호를 리스트로
                try:
                    res = requests.get(url, headers=headers, params=params)
                    if i > 10:
                        pprint(res.json())
                        print('fetch_closed_order 이상 감지')
                        break
                    elif res.json()['msg1'] == '모의투자 조회할 내역(자료)이 없습니다.                                          ':
                        dict_chegyeol = {}
                        break
                    elif res.json()['msg1'] == '초당 거래건수를 초과하였습니다.':
                        print(f"fetch_closed_order - {res.json()['msg1']=} {i= }")
                    elif res.json()['msg1'] == '모의투자 조회가 완료되었습니다.                                                 '\
                            or res.json()['msg1'] == '조회가 완료되었습니다.':
                        list_odno = [str(int(item['odno'])) for item in res.json()['output1']]  # 딕셔너리의 주문번호를 리스트로
                        if id in list_odno:
                            dict_chegyeol = res.json()['output1'][list_odno.index(id)]
                            # pprint(dict_chegyeol)
                            break
                        else:
                            dict_chegyeol ={}
                            # pprint(res.json()['output1'])
                            # print('있다')
                            break
                        # output_chegyeol.extend(res.json()['output1'])
                        # df_chegyeol = pd.DataFrame(output_chegyeol)
                        # if not df_chegyeol.empty:
                        #     df_chegyeol.rename(columns={'nmpr_type_name':'호가유형명','ord_dt':'주문일자','odno':'주문번호','orgn_odno':	'원주문번호',
                        #                  'ord_idx':'주문가격','ord_qty':'주문수량','ord_tmd':'주문시간','pdno':'종목코드','prdt_name':'종목명',
                        #                  'qty':'잔량','trad_dvsn_name': '매매구분명','tot_ccld_qty':'총체결수량','avg_idx':'평균가격',
                        #                  'tot_ccld_amt':'총체결금액','rjct_qty':'거부수량' }, inplace=True)
                        #     df_chegyeol = df_chegyeol[['호가유형명','주문일자','주문번호',	'원주문번호',
                        #                  '주문가격','주문수량','주문시간','종목코드','종목명',
                        #                  '잔량', '매매구분명','총체결수량','평균가격',
                        #                  '총체결금액','거부수량']]
                        #
                        #     df_chegyeol.set_index('종목코드', inplace=True)
                        #     df_chegyeol = self.convert_column_types(df_chegyeol) #수치형으로 바꿀수 있는열은 변환
                    elif res.json()['msg1'] == '모의투자 조회가 계속 됩니다. 다음 또는 PaDn을 누르십시오.                       ':
                        list_odno = [str(int(item['odno'])) for item in res.json()['output1']]  # 딕셔너리의 주문번호를 리스트로
                        if id in list_odno:
                            dict_chegyeol = res.json()['output1'][list_odno.index(id)]
                            break
                        # output_chegyeol.extend(res.json()['output1'])
                        ctx_area_nk200 = res.json()['ctx_area_nk200']
                        ctx_area_nk200 = str(int(ctx_area_nk200))
                    else:
                        print(res.json()['msg1'], 'fetch_closed_order')
                        pprint(res.json())
                        raise
                except:
                    print('kis: fetch_closed_order - HTTPSConnectionPool')
                i += 1
        return dict_chegyeol
    def fetch_chegyeol_futopt(self):
        """[국내선물옵션]주문/계좌, 선물옵션 기준일체결내역        """
        if self.market == '선옵':
            path = "uapi/domestic-futureoption/v1/trading/inquire-ccnl-bstime"
            url = f"{self.base_url}/{path}"
            headers = {
                "content-type": "application/json; charset=utf-8",
                "authorization": self.access_token,
                "appKey": self.api_key,
                "appSecret": self.api_secret,
                "custtype": "P",
                "tr_id": "CTFO5139R",
                "tr_cont": ""
            }

            params = {
                "CANO": self.acc_no_prefix,
                "ACNT_PRDT_CD": self.acc_no_postfix,
                "ORD_DT": datetime.datetime.now().strftime("%Y%m%d"),
                "END_ORD_DT": datetime.datetime.now().strftime("%Y%m%d"),

                "FUOP_TR_STRT_TMD": '084500',
                "FUOP_TR_END_TMD": '153000',
                "CTX_AREA_FK200": '',
                "CTX_AREA_NK200": ""
                }

            res = requests.get(url, headers=headers, params=params)
            return res.json()




    def create_oversea_order(self, side: str, symbol: str, price: int,quantity: int, order_type: str) -> dict:
        while True:
            QTest.qWait(500)
            if self.market == '해외주식':
                path = "uapi/overseas-stock/v1/trading/order"
                url = f"{self.base_url}/{path}"

                tr_id = None
                if self.mock:
                    if self.exchange in ["나스닥", "뉴욕", "아멕스"]:
                        tr_id = "VTTT1002U" if side == "buy" else "VTTT1002U"
                    elif self.exchange == '도쿄':
                        tr_id = "VTTS0308U" if side == "buy" else "VTTS0307U"
                    elif self.exchange == '상해':
                        tr_id = "VTTS0202U" if side == "buy" else "VTTS1005U"
                    elif self.exchange == '홍콩':
                        tr_id = "VTTS1002U" if side == "buy" else "VTTS1001U"
                    elif self.exchange == '심천':
                        tr_id = "VTTS0305U" if side == "buy" else "VTTS0304U"
                    else:
                        tr_id = "VTTS0311U" if side == "buy" else "VTTS0310U"
                else:
                    if self.exchange in ["나스닥", "뉴욕", "아멕스"]:
                        tr_id = "JTTT1002U" if side == "buy" else "JTTT1006U"
                    elif self.exchange == '도쿄':
                        tr_id = "TTTS0308U" if side == "buy" else "TTTS0307U"
                    elif self.exchange == '상해':
                        tr_id = "TTTS0202U" if side == "buy" else "TTTS1005U"
                    elif self.exchange == '홍콩':
                        tr_id = "TTTS1002U" if side == "buy" else "TTTS1001U"
                    elif self.exchange == '심천':
                        tr_id = "TTTS0305U" if side == "buy" else "TTTS0304U"
                    else:
                        tr_id = "TTTS0311U" if side == "buy" else "TTTS0310U"

                exchange_cd = EXCHANGE_CODE3[self.exchange]

                ord_dvsn = "00"
                if tr_id == "JTTT1002U":
                    if order_type == "00":
                        ord_dvsn = "00"
                    elif order_type == "LOO":
                        ord_dvsn = "32"
                    elif order_type == "LOC":
                        ord_dvsn = "34"
                elif tr_id == "JTTT1006U":
                    if order_type == "00":
                        ord_dvsn = "00"
                    elif order_type == "MOO":
                        ord_dvsn = "31"
                    elif order_type == "LOO":
                        ord_dvsn = "32"
                    elif order_type == "MOC":
                        ord_dvsn = "33"
                    elif order_type == "LOC":
                        ord_dvsn = "34"
                else:
                    ord_dvsn = "00"

                data = {
                    "CANO": self.acc_no_prefix,
                    "ACNT_PRDT_CD": self.acc_no_postfix,
                    "OVRS_EXCG_CD": exchange_cd,
                    "PDNO": symbol,
                    "ORD_QTY": str(quantity),
                    "OVRS_ORD_UNPR": str(price),
                    "ORD_SVR_DVSN_CD": "0",
                    "ORD_DVSN": ord_dvsn
                }
                hashkey = self.issue_hashkey(data)
                headers = {
                   "content-type": "application/json",
                   "authorization": self.access_token,
                   "appKey": self.api_key,
                   "appSecret": self.api_secret,
                   "tr_id": tr_id,
                   "hashkey": hashkey
                }
                resp = requests.post(url, headers=headers, data=json.dumps(data))
            elif self.market == '해외선옵':
                tr_id = '' if self.mock else 'OTFM3001U'
                side = '02' if side == 'buy' else '01'
                data = {
                    "CANO": self.acc_no_prefix,
                    "ACNT_PRDT_CD": self.acc_no_postfix,
                    "OVRS_FUTR_FX_PDNO": symbol,
                    "SLL_BUY_DVSN_CD": side,
                    "PRIC_DVSN_CD": symbol,
                    "FM_LIMIT_ORD_PRIC": str(quantity),
                    "FM_STOP_ORD_PRIC": str(price),
                    "FM_ORD_QTY": "0",
                    "CCLD_CNDT_CD": ord_dvsn
                }
                hashkey = self.issue_hashkey(data)
                headers = {
                   "content-type": "application/json; charset=utf-8",
                   "authorization": self.access_token,
                   "appKey": self.api_key,
                   "appSecret": self.api_secret,
                   "tr_id": tr_id,
                   "hashkey": hashkey
                }
                resp = requests.post(url, headers=headers, data=json.dumps(data))



        return resp.json()

    def _fetch_ohlcv_domestic(self, symbol: str, timeframe:str='D', early_day:str="",
                             lately_day:str="", adj_price:bool=True):
        """국내주식시세/국내주식 기간별 시세(일/주/월/년)

        Args:
            symbol (str): symbol
            timeframe (str, optional): "D": 일, "W": 주, "M": 월, 'Y': 년
            early_day (str, optional): 조회시작일자(YYYYMMDD)
            lately_day (str, optional): 조회종료일자(YYYYMMDD)
            adjusted (bool, optional): False: 수정주가 미반영, True: 수정주가 반영
        """
        path = "/uapi/domestic-stock/v1/quotations/inquire-daily-itemchartprice"
        url = f"{self.base_url}/{path}"

        headers = {
           "content-type": "application/json",
           "authorization": self.access_token,
           "appKey": self.api_key,
           "appSecret": self.api_secret,
           "tr_id": "FHKST03010100"
        }

        if lately_day == "":
            now = datetime.datetime.now()
            lately_day = now.strftime("%Y%m%d")

        if early_day == "":
            early_day = "19800104"

        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": symbol,
            "FID_INPUT_DATE_1": early_day,
            "FID_INPUT_DATE_2": lately_day,
            "FID_PERIOD_DIV_CODE": timeframe,
            "FID_ORG_ADJ_PRC": 0 if adj_price else 1
        }
        i = 0
        while True:
            res = requests.get(url, headers=headers, params=params)
            # hrd = {'User_Agent': generate_user_agent(os='win', device_type='desktop')}
            if res.json()['msg1'] == '정상처리 되었습니다.':
                break
            elif i == 10:
                raise print(f'{symbol} : {i}번 이상 해도 조회 안됨 - _fetch_ohlcv_domestic')
            else:
                # time.sleep(1)
                QTest.qWait(1000)
            i += 1
        return res.json()


    def _fetch_futopt_ohlcv_domestic(self, symbol: str, timeframe:str='D', start_day:str="",
                             end_day:str="", market:str=""):
        """국내주식시세/국내주식 기간별 시세(일/주/월/년)

        Args:
            symbol (str): symbol
            timeframe (str, optional): "D": 일, "W": 주, "M": 월, 'Y': 년
            start_day (str, optional): 조회시작일자(YYYYMMDD)
            end_day (str, optional): 조회종료일자(YYYYMMDD)
            adjusted (bool, optional): False: 수정주가 미반영, True: 수정주가 반영
        """
        path = "uapi/domestic-futureoption/v1/quotations/inquire-daily-fuopchartprice"
        url = f"{self.base_url}/{path}"

        headers = {
           "content-type": "application/json; charset=utf-8",
           "authorization": self.access_token,
           "appKey": self.api_key,
           "appSecret": self.api_secret,
           "tr_id": "FHKIF03020100"
        }

        if start_day == "":
            start_day = "19800104"

        if end_day == "":
            now = datetime.datetime.now()
            end_day = now.strftime("%Y%m%d")

        params = {
            "FID_COND_MRKT_DIV_CODE": market,
            "FID_INPUT_ISCD": symbol,
            "FID_INPUT_DATE_1": start_day,
            "FID_INPUT_DATE_2": end_day,
            "FID_PERIOD_DIV_CODE": timeframe,
        }
        i = 0
        while True:
            res = requests.get(url, headers=headers, params=params)
            if res.json()['msg1'] == '정상처리 되었습니다.':
                break
            elif i == 10:
                raise print(f'{symbol} : {i}번 이상 해도 조회 안됨 - _fetch_futopt_ohlcv_domestic')
            else:
                time.sleep(1)
            i += 1
        return res.json()




    def fetch_ohlcv_overesea(self, symbol: str, timeframe:str='D',
                             end_day:str="", adj_price:bool=True):
        """해외주식현재가/해외주식 기간별시세

        Args:
            symbol (str): symbol
            timeframe (str, optional): "D": 일, "W": 주, "M": 월
            end_day (str, optional): 조회종료일자 (YYYYMMDD)
            adjusted (bool, optional): False: 수정주가 미반영, True: 수정주가 반영
        """
        path = "/uapi/overseas-price/v1/quotations/dailyprice"
        url = f"{self.base_url}/{path}"

        headers = {
           "content-type": "application/json",
           "authorization": self.access_token,
           "appKey": self.api_key,
           "appSecret": self.api_secret,
           "tr_id": "HHDFS76240000"
        }

        timeframe_lookup = {
            'D': "0",
            'W': "1",
            'M': "2"
        }

        if end_day == "":
            now = datetime.datetime.now()
            end_day = now.strftime("%Y%m%d")

        exchange_code = EXCHANGE_CODE4[self.exchange]

        params = {
            "AUTH": "",
            "EXCD": exchange_code,
            "SYMB": symbol,
            "GUBN": timeframe_lookup.get(timeframe, "0"),
            "BYMD": end_day,
            "MODP": 1 if adj_price else 0
        }
        resp = requests.get(url, headers=headers, params=params)
        return resp.json()

    def fetch_oversea_futopt_ohlcv(self):
        """해외기본시세/해외선물 분봉조회

        Args:
            symbol (str): symbol
            timeframe (str, optional): "D": 일, "W": 주, "M": 월
            end_day (str, optional): 조회종료일자 (YYYYMMDD)
            adjusted (bool, optional): False: 수정주가 미반영, True: 수정주가 반영
        """
        path = "uapi/overseas-futureoption/v1/quotations/inquire-time-futurechartprice"
        url = f"{self.base_url}/{path}"
        headers = {
           "content-type": "application/json; charset=utf-8",
           "authorization": self.access_token,
           "appKey": self.api_key,
           "appSecret": self.api_secret,
           "tr_id": "HHDFC55020400",
           "tr_cont": "",
        }

        params = {
            "SRS_CD":"GASQ25",
            "EXCH_CD":"ICE",
            "START_DATE_TIME":"",
            "CLOSE_DATE_TIME":"20231212",
            "QRY_TP":"P",
            "QRY_CNT":"500",
            "QRY_GAP":"1",
            "INDEX_KEY":"20231211128"
        }
        res = requests.get(url, headers=headers, params=params)
        return res.json()

    def common_header(self,tr_id):
        pass

    def ranking(self,content):
        if content == '등락율상위':
            tr_id = "FHPST01700000"
            ticker_id = 'stck_shrn_iscd'
            params = {
                "fid_cond_mrkt_div_code": "J",
                "fid_cond_scr_div_code": "20170",
                "fid_input_iscd": "0000",
                "fid_rank_sort_cls_code": "0",
                "fid_input_cnt_1": "0",
                "fid_prc_cls_code": "0",
                "fid_input_price_1": "",
                "fid_input_price_2": "",
                "fid_vol_cnt": "",
                "fid_trgt_cls_code": "0",
                "fid_trgt_exls_cls_code": "0",
                "fid_div_cls_code": "0",
                "fid_rsfl_rate1": "",
                "fid_rsfl_rate2": ""
            }
        elif content == '거래량상위':
            tr_id = "FHPST01710000"
            ticker_id = 'mksc_shrn_iscd'
            params = {
                "FID_COND_MRKT_DIV_CODE": "J",
                "FID_COND_SCR_DIV_CODE": "20171",
                "FID_INPUT_ISCD": "0000",
                "FID_DIV_CLS_CODE": "0",
                "FID_BLNG_CLS_CODE": "0",
                "FID_TRGT_CLS_CODE": "111111111",
                "FID_TRGT_EXLS_CLS_CODE": "000000",
                "FID_INPUT_PRICE_1": "0",
                "FID_INPUT_PRICE_2": "0",
                "FID_VOL_CNT": "0",
                "FID_INPUT_DATE_1": "0"
            }
        elif content == '시가총액상위':
            tr_id = "FHPST01740000"
            ticker_id = 'mksc_shrn_iscd'
            params = {
                "fid_cond_mrkt_div_code": "J",
                "fid_cond_scr_div_code": "20174",
                "fid_div_cls_code": "0",
                "fid_input_iscd": "0000",
                "fid_trgt_cls_code": "0",
                "fid_trgt_exls_cls_code": "0",
                "fid_input_price_1": "",
                "fid_input_price_2": "",
                "fid_vol_cnt": "",
            }
        elif content == '시간외잔량상위':
            tr_id = "FHPST01760000"
            ticker_id = 'stck_shrn_iscd'
            params = {
                "fid_cond_mrkt_div_code": "J",
                "fid_cond_scr_div_code": "20176",
                "fid_rank_sort_cls_code": "1",
                "fid_div_cls_code": "0",
                "fid_input_iscd": "0000",
                "fid_trgt_cls_code": "0",
                "fid_trgt_exls_cls_code": "0",
                "fid_input_price_1": "",
                "fid_input_price_2": "",
                "fid_vol_cnt": "",
            }
        elif content == '체결강도상위':
            tr_id = "FHPST01680000"
            ticker_id = 'stck_shrn_iscd'
            params = {
                "fid_cond_mrkt_div_code": "J",
                "fid_cond_scr_div_code": "20168",
                "fid_input_iscd": "0001",
                "fid_div_cls_code": "1",
                "fid_input_price_1": "",
                "fid_input_price_2": "",
                "fid_vol_cnt": "",
                "fid_trgt_exls_cls_code": "0",
                "fid_trgt_cls_code": "0"
            }
        elif content == '관심종목등록상위':
            tr_id = "FHPST01800000"
            ticker_id = 'stck_shrn_iscd'
            params = {
                "fid_cond_mrkt_div_code": "J",
                "fid_cond_scr_div_code": "20168",
                "fid_input_iscd": "0001",
                "fid_div_cls_code": "1",
                "fid_input_price_1": "",
                "fid_input_price_2": "",
                "fid_vol_cnt": "",
                "fid_trgt_exls_cls_code": "0",
                "fid_trgt_cls_code": "0"
            }
        ######################################################
        path = "uapi/domestic-stock/v1/ranking/fluctuation"
        url = f"{self.base_url}/{path}"
        headers = {
            "content-type": "application/json; charset=utf-8",
            "authorization": self.access_token,
            "appKey": self.api_key,
            "appSecret": self.api_secret,
            "tr_id": tr_id,
            "tr_cont": "",
            }

        while True:
            res = requests.get(url, headers=headers, params=params)
            if res.json()['msg1'] != '정상처리 되었습니다.':
                QTest.qWait(500)
            else:
                output = res.json()['output']
                list_ranking = [x[ticker_id] for x in output ]
                return list_ranking
    def ranking_fluctuation(self):
        """국내주식 순위분석/등락률 순위        """
        path = "uapi/domestic-stock/v1/ranking/fluctuation"
        url = f"{self.base_url}/{path}"
        headers = {
           "content-type": "application/json; charset=utf-8",
           "authorization": self.access_token,
           "appKey": self.api_key,
           "appSecret": self.api_secret,
           "tr_id": "FHPST01700000",
           "tr_cont": "",
        }

        params = {
            "fid_cond_mrkt_div_code": "J",
            "fid_cond_scr_div_code": "20170",
            "fid_input_iscd": "0000",
            "fid_rank_sort_cls_code": "0",
            "fid_input_cnt_1": "0",
            "fid_prc_cls_code": "0",
            "fid_input_price_1": "",
            "fid_input_price_2": "",
            "fid_vol_cnt": "",
            "fid_trgt_cls_code": "0",
            "fid_trgt_exls_cls_code": "0",
            "fid_div_cls_code": "0",
            "fid_rsfl_rate1": "",
            "fid_rsfl_rate2": ""
        }
        while True:
            res = requests.get(url, headers=headers, params=params)
            if res.json()['msg1'] != '정상처리 되었습니다.':
                QTest.qWait(500)
            else:
                output = res.json()['output']
                list_ranking = [x['stck_shrn_iscd'] for x in output ]
                # df = pd.DataFrame(output)
                # df.rename(columns={'stck_shrn_iscd':'종목코드', 'hts_kor_isnm':'종목명', 'prdy_vrss':'전일대비', 'prdy_vrss_sign':'전일대비부호',
                #                    'prdy_ctrt':'전일대비율', 'acml_vol':'누적거래량', 'stck_hgpr':'최고가', 'hgpr_hour':'최고가시간',
                #                    'acml_hgpr_date':'최고가일자', 'stck_lwpr':'최저가', 'lwpr_hour':'최저가시간',
                #                    'acml_lwpr_date':'최저가일자', 'cnnt_ascn_dynu':'연속상승일수',
                #                    'prd_rsfl':'기간등락', 'prd_rsfl_rate':'기간등락비율'},inplace=True)
                return list_ranking
    def ranking_volume(self):
        """국내주식 순위분석/거래량 순위        """
        path = "uapi/domestic-stock/v1/ranking/fluctuation"
        url = f"{self.base_url}/{path}"
        headers = {
           "content-type": "application/json; charset=utf-8",
           "authorization": self.access_token,
           "appKey": self.api_key,
           "appSecret": self.api_secret,
           "tr_id": "FHPST01710000",
           "tr_cont": "",
        }

        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_COND_SCR_DIV_CODE": "20171",
            "FID_INPUT_ISCD": "0000",
            "FID_DIV_CLS_CODE": "0",
            "FID_BLNG_CLS_CODE": "0",
            "FID_TRGT_CLS_CODE": "111111111",
            "FID_TRGT_EXLS_CLS_CODE": "000000",
            "FID_INPUT_PRICE_1": "0",
            "FID_INPUT_PRICE_2": "0",
            "FID_VOL_CNT": "0",
            "FID_INPUT_DATE_1": "0"
        }
        while True:
            res = requests.get(url, headers=headers, params=params)
            if res.json()['msg1'] != '정상처리 되었습니다.':
                QTest.qWait(500)
            else:
                output = res.json()['output']
                list_ranking = [x['mksc_shrn_iscd'] for x in output]
                # df = pd.DataFrame(output)
                # # print(df.columns)
                # df.rename(columns={'mksc_shrn_iscd':'종목코드', 'hts_kor_isnm':'종목명', 'prdy_vrss':'전일대비', 'prdy_vrss_sign':'전일대비부호',
                #                    'prdy_ctrt':'전일대비율', 'acml_vol':'누적거래량', 'stck_hgpr':'최고가', 'hgpr_hour':'최고가시간',
                #                    'acml_hgpr_date':'최고가일자', 'stck_lwpr':'최저가', 'lwpr_hour':'최저가시간',
                #                    'acml_lwpr_date':'최저가일자', 'cnnt_ascn_dynu':'연속상승일수',
                #                    'prd_rsfl':'기간등락', 'prd_rsfl_rate':'기간등락비율'},inplace=True)
                return list_ranking
    def ranking_cap(self):
        """국내주식 순위분석/시가총액 순위        """
        path = "uapi/domestic-stock/v1/ranking/fluctuation"
        url = f"{self.base_url}/{path}"
        headers = {
           "content-type": "application/json; charset=utf-8",
           "authorization": self.access_token,
           "appKey": self.api_key,
           "appSecret": self.api_secret,
           "tr_id": "FHPST01740000",
           "tr_cont": "",
        }

        params = {
            "fid_cond_mrkt_div_code": "J",
            "fid_cond_scr_div_code": "20174",
            "fid_div_cls_code": "0",
            "fid_input_iscd": "0000",
            "fid_trgt_cls_code": "0",
            "fid_trgt_exls_cls_code":"0",
            "fid_input_price_1": "",
            "fid_input_price_2": "",
            "fid_vol_cnt": "",
        }
        while True:
            res = requests.get(url, headers=headers, params=params)
            if res.json()['msg1'] != '정상처리 되었습니다.':
                QTest.qWait(500)
            else:
                output = res.json()['output']
                list_ranking = [x['mksc_shrn_iscd'] for x in output]
                # df = pd.DataFrame(output)
                # print(df.columns)
                # df.rename(columns={'mksc_shrn_iscd':'종목코드', 'hts_kor_isnm':'종목명', 'prdy_vrss':'전일대비', 'prdy_vrss_sign':'전일대비부호',
                #                    'prdy_ctrt':'전일대비율', 'acml_vol':'누적거래량', 'stck_hgpr':'최고가', 'hgpr_hour':'최고가시간',
                #                    'acml_hgpr_date':'최고가일자', 'stck_lwpr':'최저가', 'lwpr_hour':'최저가시간',
                #                    'acml_lwpr_date':'최저가일자', 'cnnt_ascn_dynu':'연속상승일수',
                #                    'prd_rsfl':'기간등락', 'prd_rsfl_rate':'기간등락비율'},inplace=True)
                return list_ranking
    def ranking_after_hour_balance(self):
        """국내주식 순위분석/시간외잔량 순위        """
        path = "uapi/domestic-stock/v1/ranking/fluctuation"
        url = f"{self.base_url}/{path}"
        headers = {
           "content-type": "application/json; charset=utf-8",
           "authorization": self.access_token,
           "appKey": self.api_key,
           "appSecret": self.api_secret,
           "tr_id": "FHPST01760000",
           "tr_cont": "",
        }

        params = {
            "fid_cond_mrkt_div_code": "J",
            "fid_cond_scr_div_code": "20176",
            "fid_rank_sort_cls_code": "1",
            "fid_div_cls_code": "0",
            "fid_input_iscd": "0000",
            "fid_trgt_cls_code": "0",
            "fid_trgt_exls_cls_code":"0",
            "fid_input_price_1": "",
            "fid_input_price_2": "",
            "fid_vol_cnt": "",
            }
        while True:
            res = requests.get(url, headers=headers, params=params)
            if res.json()['msg1'] != '정상처리 되었습니다.':
                QTest.qWait(500)
            else:
                output = res.json()['output']
                list_ranking = [x['stck_shrn_iscd'] for x in output]
                # df = pd.DataFrame(output)
                # print(df.columns)
                # df.rename(columns={'stck_shrn_iscd':'종목코드', 'hts_kor_isnm':'종목명', 'prdy_vrss':'전일대비', 'prdy_vrss_sign':'전일대비부호',
                #                    'prdy_ctrt':'전일대비율', 'acml_vol':'누적거래량', 'stck_hgpr':'최고가', 'hgpr_hour':'최고가시간',
                #                    'acml_hgpr_date':'최고가일자', 'stck_lwpr':'최저가', 'lwpr_hour':'최저가시간',
                #                    'acml_lwpr_date':'최저가일자', 'cnnt_ascn_dynu':'연속상승일수',
                #                    'prd_rsfl':'기간등락', 'prd_rsfl_rate':'기간등락비율'},inplace=True)
                return list_ranking
    def ranking_volume_power(self):
        """국내주식 순위분석/체결강도 상위        """
        path = "uapi/domestic-stock/v1/ranking/fluctuation"
        url = f"{self.base_url}/{path}"
        headers = {
           "content-type": "application/json; charset=utf-8",
           "authorization": self.access_token,
           "appKey": self.api_key,
           "appSecret": self.api_secret,
           "tr_id": "FHPST01680000",
           "tr_cont": "",
        }

        params = {
            "fid_cond_mrkt_div_code": "J",
            "fid_cond_scr_div_code": "20168",
            "fid_input_iscd": "0001",
            "fid_div_cls_code": "1",
            "fid_input_price_1": "",
            "fid_input_price_2": "",
            "fid_vol_cnt": "",
            "fid_trgt_exls_cls_code": "0",
            "fid_trgt_cls_code": "0"
            }
        while True:
            res = requests.get(url, headers=headers, params=params)
            if res.json()['msg1'] != '정상처리 되었습니다.':
                QTest.qWait(500)
            else:
                output = res.json()['output']
                list_ranking = [x['stck_shrn_iscd'] for x in output]
                # df = pd.DataFrame(output)
                # df.rename(columns={'stck_shrn_iscd':'종목코드', 'hts_kor_isnm':'종목명', 'prdy_vrss':'전일대비', 'prdy_vrss_sign':'전일대비부호',
                #                    'prdy_ctrt':'전일대비율', 'acml_vol':'누적거래량', 'stck_hgpr':'최고가', 'hgpr_hour':'최고가시간',
                #                    'acml_hgpr_date':'최고가일자', 'stck_lwpr':'최저가', 'lwpr_hour':'최저가시간',
                #                    'acml_lwpr_date':'최저가일자', 'cnnt_ascn_dynu':'연속상승일수',
                #                    'prd_rsfl':'기간등락', 'prd_rsfl_rate':'기간등락비율'},inplace=True)
                return list_ranking
    def ranking_top_interest(self):
        """국내주식 순위분석/관심종목등록 상위        """
        path = "uapi/domestic-stock/v1/ranking/fluctuation"
        url = f"{self.base_url}/{path}"
        headers = {
           "content-type": "application/json; charset=utf-8",
           "authorization": self.access_token,
           "appKey": self.api_key,
           "appSecret": self.api_secret,
           "tr_id": "FHPST01800000",
           "tr_cont": "",
        }

        params = {
            "fid_cond_mrkt_div_code": "J",
            "fid_cond_scr_div_code": "20168",
            "fid_input_iscd": "0001",
            "fid_div_cls_code": "1",
            "fid_input_price_1": "",
            "fid_input_price_2": "",
            "fid_vol_cnt": "",
            "fid_trgt_exls_cls_code": "0",
            "fid_trgt_cls_code": "0"
            }
        i = 0
        while True:
            res = requests.get(url, headers=headers, params=params)
            if res.json()['msg1'] != '정상처리 되었습니다.':
                pprint(res.json())
                QTest.qWait(500)
            else:
                output = res.json()['output']
                list_ranking = [x['stck_shrn_iscd'] for x in output]
                # df = pd.DataFrame(output)
                # df.rename(columns={'stck_shrn_iscd':'종목코드', 'hts_kor_isnm':'종목명', 'prdy_vrss':'전일대비', 'prdy_vrss_sign':'전일대비부호',
                #                    'prdy_ctrt':'전일대비율', 'acml_vol':'누적거래량', 'stck_hgpr':'최고가', 'hgpr_hour':'최고가시간',
                #                    'acml_hgpr_date':'최고가일자', 'stck_lwpr':'최저가', 'lwpr_hour':'최저가시간',
                #                    'acml_lwpr_date':'최저가일자', 'cnnt_ascn_dynu':'연속상승일수',
                #                    'prd_rsfl':'기간등락', 'prd_rsfl_rate':'기간등락비율'},inplace=True)
                return list_ranking


######################################### 이하 수정 본

    def hogaUnitCalc(self, jang,ticker, price):
        # print(list(jang.values())[0][:3])
        # hogaUnit = 1
        if price < 10 and jang == '업비트':
            return 0.01
        elif price < 100 and jang == '업비트':
            return 0.1
        elif price < 1000 and jang == '업비트':
            return 1
        elif price < 10000 and jang == '업비트':
            return 5
        elif price < 100000 and jang == "업비트":
            return 10
        elif price < 500000 and jang == "업비트":
            return 50
        elif price < 1000000 and jang == "업비트":
            return 100
        elif price < 2000000 and jang == "업비트":
            return 500
        elif price > 2000000 and jang == "업비트":
            return 1000
        elif price < 1000 and jang == 'KOSPI':
            return 1
        elif price < 5000 and jang == 'KOSPI':
            return 5
        elif price < 10000 and jang == 'KOSPI':
            return 10
        elif price < 50000 and jang == "KOSPI":
            return 50
        elif price < 100000 and jang == "KOSPI":
            return 100
        elif price < 500000 and jang == "KOSPI":
            return 500
        elif price >= 500000 and jang == "KOSPI":
            return 1000
        elif price >= 50000 and jang == "KOSDAQ":
            return 100
        elif jang == "ETF" or jang == "etf":
            return 5
        elif jang == '국내선옵':
            if ticker[:3] == '101': #코스피200선물
                return 0.05
            elif ticker[:3] == '105': #미니코스피200 선물
                return 0.02
            elif ticker[:3] == '106': #코스닥선물
                return 0.1
            elif (ticker[:3] == '201' or ticker[:3] == '301' or ticker[5:6]=='W') and price < 10: #코스피200 옵션 10포인트 미만
                return 0.01
            elif (ticker[:3] == '201' or ticker[:3] == '301' or ticker[5:6]=='W') and price >= 10: #코스피200 옵션 10포인트 이상
                return 0.05
            elif (ticker[:3] == '205' or ticker[:3] == '305') and price < 3: #미니코스피200 옵션  3포인트 미만
                return 0.01
            elif (ticker[:3] == '205' or ticker[:3] == '305') and price >= 10: #미니코스피200 옵션  10포인트 이상
                return 0.05
            elif ticker[:3] == '205' or ticker[:3] == '305': #미니코스피200 옵션  3포인트 이상 10포인트 미만
                return 0.02
            elif ticker[:3] == '205' or ticker[:3] == '305':  # 코스피100 옵션
                return 0.1
        else:
            raise '없음'

    def hogaUnitCalc_per(self, jang, hogaPrice):

        minPrice = 1
        if hogaPrice < 10:
            minPrice = 10
        elif hogaPrice < 100:
            minPrice = 100
        elif hogaPrice < 1000:
            minPrice = 1000
        elif hogaPrice < 10000:
            minPrice = 10000
        elif hogaPrice < 100000:
            minPrice = 100000
        elif (hogaPrice < 500000):
            minPrice = 500000
        elif (hogaPrice < 1000000) & (jang == "업비트"):
            minPrice = 1000000
        elif (hogaPrice < 2000000) & (jang == "업비트"):
            minPrice = 2000000
        elif (hogaPrice > 2000000) & (jang == "업비트"):
            minPrice = 100000000
        elif (hogaPrice >= 500000) & (jang == "KOSPI"):
            minPrice = 500000
        elif (hogaPrice >= 50000) & (jang == "KOSDAQ"):
            minPrice = 50000
        else:
            raise '없음'
        return minPrice
    def count_decimal_places(self,number):
        # 숫자를 문자열로 변환
        str_number = str(number)
        if '.' in str_number:
            # 소수점 이후 자릿수를 세기
            return len(str_number.split('.')[1].rstrip('0'))  # 끝의 0은 제외
        else:
            return 0  # 소수점 이하 자리가 없는 경우
    def hogaPriceReturn(self, jang,ticker, current_price, hoga_in):  # 호가로 입력
        if type(hoga_in) == str: #호가르 str로 받을 경우
            if hoga_in[:2] == '매도':
                mark = '-'
            elif hoga_in[:2] == '매수':
                mark = '+'
            else:
                raise
            idx = hoga_in[2:hoga_in.index('호가')]
            hoga = int(mark + idx)
        if jang == '국내선옵': #선물/옵셥의 경우
            if type(hoga_in) == str:
                for _ in range(abs(hoga)):
                    if hoga < 0:
                        hogaunit = self.hogaUnitCalc(jang,ticker, current_price)
                        decimal_num = self.count_decimal_places(hogaunit)
                        current_price = round(current_price-hogaunit,decimal_num)
                        if current_price == 0:
                            current_price = current_price + hogaunit
                    elif hoga > 0: #호가가 0보다 작으면 - 마이너스로 가기 때문에
                        hogaunit = self.hogaUnitCalc(jang,ticker, current_price)
                        decimal_num = self.count_decimal_places(hogaunit)
                        current_price = round(current_price+hogaunit,decimal_num)
                unit = self.hogaUnitCalc(jang,ticker,current_price)
                point = len(str(unit)[str(unit).index('.')+1:])
                current_price = round(current_price,point)
                if mark == '-':
                    return math.floor(current_price / unit) * unit #항상 나눴을 때 나머지가 0에 수렴하도록  예) (v=9.93 unit=0.02) = 9.92 , (v=9.93 unit=0.05) = 9.9
                elif mark == '+':
                    # return math.ceil(current_price / unit) * unit #항상 나눴을 때 나머지가 0에 수렴하도록  예) (v=9.93 unit=0.02) = 9.94 , (v=9.93 unit=0.05) = 9.95
                    return current_price #항상 나눴을 때 나머지가 0에 수렴하도록  예) (v=9.93 unit=0.02) = 9.94 , (v=9.93 unit=0.05) = 9.95
            elif type(hoga_in) == int or type(hoga_in) == float:
                current_price = current_price * ((hoga_in / 100) + 1)
                if hoga_in < 0:
                    hogaunit = self.hogaUnitCalc(jang,ticker, current_price)
                    decimal_num = self.count_decimal_places(hogaunit)
                    current_price = round(current_price - hogaunit, decimal_num)
                unit = self.hogaUnitCalc(jang,ticker,current_price)
                point = len(str(unit)[str(unit).index('.')+1:])
                current_price = round(current_price,point)
                if hoga_in < 0:
                    if current_price == 0: #반환값이 0일 경우
                        return hogaunit
                    return math.ceil(current_price / unit) * unit
                else:
                    return math.floor(current_price / unit) * unit
        for _ in range(abs(hoga)):
            if hoga < 0:
                minusV = (current_price - 1)
                hogaunit = self.hogaUnitCalc(jang,ticker, minusV)
                mot = minusV // hogaunit
                current_price = mot * hogaunit
            elif hoga > 0:
                hogaunit = self.hogaUnitCalc(jang,ticker, current_price)
                current_price = current_price + hogaunit
        return current_price

    def hogaPriceReturn_per(self,jang,ticker, currentPrice, per):  # 퍼센트로 반환
        hogaPrice = currentPrice * ((per / 100) + 1)
        hogaUnit = self.hogaUnitCalc(jang,ticker, hogaPrice)
        minPrice = self.hogaUnitCalc_per(jang, hogaPrice)
        while True:
            minPrice = (minPrice - hogaUnit)
            if minPrice <= hogaPrice:
                if per == 0 and jang != 'KOSPI' and jang != 'KOSDAQ' and jang != 'ETF':
                    minPrice += hogaUnit
                return round(minPrice, 2)

    def point_low(self, n, point):
        result = np.trunc(n * (math.pow(10, point))) / math.pow(10, point)
        rest = np.trunc((n - result) * (100000000)) / 100000000
        return result, rest

    def qtyReturn(self, hoga_price):
        qty = round((self.wallet / self.bet_division) / hoga_price)
        qty, rest = self.point_low(qty, self.split_point)
        return qty, rest

    def amount_to_precision(self,ticker,qty):
        if qty < 0:
            return 0
        else:
            return math.floor(qty)

    def price_to_precision(self,ticker,qty):
        if qty < 0:
            return 0
        else:
            return math.floor(qty)

    def convert_column_types(self, df):
        for col in df.columns:
            try:
                df[col] = pd.to_numeric(df[col], errors='raise')
            except ValueError:
                pass
        return df
    def nth_weekday(self,the_date, nth_week, week_day):
        temp = the_date.replace(day=1)
        adj = (week_day - temp.weekday()) % 7
        temp += datetime.timedelta(days=adj)
        temp += datetime.timedelta(weeks=nth_week-1)
        return temp
    def get_recent_due(self,mydate:datetime)->datetime:
        from dateutil.relativedelta import relativedelta
        # get 2nd thursday of the same month
        thismonth_duedate = self.nth_weekday(mydate, 2, 3)
        # in case today already passed the duedate (10/15) -> get nextmonth_duedate
        if mydate <= thismonth_duedate:
            return thismonth_duedate
        elif mydate > thismonth_duedate :
            nextmonth_duedate = self.nth_weekday(mydate+relativedelta(months=1),2, 3)
            return nextmonth_duedate
    def add_trend(self,현재시간,df_trend,COND_MRKT):
        dict_trend = {}
        dict_trend.update(ex_kis.investor_trend_time('코스피'))
        dict_trend.update(ex_kis.investor_trend_time('선물'))
        dict_trend.update(ex_kis.investor_trend_time('주식선물'))
        dict_trend.update(ex_kis.investor_trend_time('콜옵션'))
        dict_trend.update(ex_kis.investor_trend_time('풋옵션'))
        if COND_MRKT == "WKM":
            dict_trend.update(ex_kis.investor_trend_time('콜_위클리_월'))
            dict_trend.update(ex_kis.investor_trend_time('풋_위클리_월'))
        elif COND_MRKT == "WKI":
            dict_trend.update(ex_kis.investor_trend_time('콜_위클리_목'))
            dict_trend.update(ex_kis.investor_trend_time('풋_위클리_목'))
        # current_time = datetime.datetime.now().replace(second=0, microsecond=0)
        df = pd.DataFrame([dict_trend], index=[현재시간])
        if not df_trend.empty:
            df_trend = pd.concat([df_trend, df],axis=0)
        else:
            df_trend = df
        return df_trend

if __name__ == "__main__":
    def make_exchange_kis(trade_type):
        conn = sqlite3.connect('DB/setting.db')
        df = pd.read_sql(f"SELECT * FROM 'set'", conn).set_index('index')
        conn.close()
        if trade_type == '실전주식':
            key = df.loc['KIS_stock_api', 'value']
            secret = df.loc['KIS_stock_secret', 'value']
            acc_no = df.loc['KIS_stock_account', 'value']
            mock = False
            # broker = mojito.KoreaInvestment(api_key=key, api_secret=secret, acc_no=acc_no)
        elif trade_type == '모의주식':
            key = df.loc['KIS_stock_mock_api', 'value']
            secret = df.loc['KIS_stock_mock_secret', 'value']
            acc_no = df.loc['KIS_stock_mock_account', 'value']
            mock = True
        elif trade_type == '실전선옵':
            key = df.loc['KIS_futopt_api', 'value']
            secret = df.loc['KIS_futopt_secret', 'value']
            acc_no = df.loc['KIS_futopt_account', 'value']
            mock = False
        elif trade_type == '모의선옵' or trade_type == '모의해외선옵':
            key = df.loc['KIS_futopt_mock_api', 'value']
            secret = df.loc['KIS_futopt_mock_secret', 'value']
            acc_no = df.loc['KIS_futopt_mock_account', 'value']
            mock = True

        market = trade_type[2:]
        exchange = KoreaInvestment(api_key=key, api_secret=secret, acc_no=acc_no, market=market, mock=mock)
        return exchange
    def nth_weekday(the_date, nth_week, week_day):
        temp = the_date.replace(day=1)
        adj = (week_day - temp.weekday()) % 7
        temp += datetime.timedelta(days=adj)
        temp += datetime.timedelta(weeks=nth_week-1)
        return temp
    def get_recent_due(mydate:datetime)->datetime:
        from dateutil.relativedelta import relativedelta
        # get 2nd thursday of the same month
        thismonth_duedate = nth_weekday(mydate, 2, 3)
        # in case today already passed the duedate (10/15) -> get nextmonth_duedate
        if mydate <= thismonth_duedate:
            return thismonth_duedate
        elif mydate > thismonth_duedate :
            nextmonth_duedate = nth_weekday(mydate+relativedelta(months=1),2, 3)
            return nextmonth_duedate
    ex_kis = make_exchange_kis('모의선옵')
    df_trend = pd.DataFrame()

    li = [x for x in range(45, 60)]
    i=0
    today = datetime.datetime.now()
    df_c_weekly, df_p_weekly, COND_MRKT = ex_kis.display_opt_weekly(today)



    # frgn, prsn, orgn = ex_kis.investor_trend_time('선물')
    # print(f"외인: {frgn}, 개인: {prsn}, 기관: {orgn}")
    # today = datetime.datetime(2025,2,24)
    # res = ex_kis.check_holiday_domestic_stock(today.strftime("%Y%m%d"))
    # pprint(res)
    # output = res['output']
    # list_close_day = [x['bass_dt'] for x in output if x['opnd_yn']=='N'] #개장일
    # list_duple_day = [x['bass_dt'] for x in output if x['opnd_yn']=='N' and (x['wday_dvsn_cd']=='02' or x['wday_dvsn_cd']=='05') ] #옵션만기일(월,목)과 휴일이 겹치는날
    # print(list_close_day)
    # print(list_duple_day)
    # dt = datetime.datetime.now().isocalendar()
    # ex_kis.display_opt_weekly(today)

    # res = ex.create_limit_buy_order(symbol='309D5W350',price=5,quantity=5,side='buy')
    # pprint(res)
    # df1,df2 = ex.display_opt_weekly_thur()
    # print(df1)
    # res = ex.fetch_closed_order(side='buy',ticker=ticker,id='1693')

    # print(ex.display_opt_weekly_thur())
    # df = ex.create_limit_sell_order(symbol=ticker, price=int(매도가), quantity=int(수량),side='sell')
    # res = ex.fetch_open_
    # pprint(res)
    # print(ex.fetch_ohlcv('308430'))
    # pprint(ex.fetch_ohlcv(symbol='122630'))
    # call,put = ex.display_opt_weekly_mon()

    # def make_exchange_kis_WS(trade_type):
    #     conn = sqlite3.connect('DB/setting.db')
    #     df = pd.read_sql(f"SELECT * FROM 'set'", conn).set_index('index')
    #     conn.close()
    #     if trade_type == '실전주식':
    #         key = df.loc['KIS_stock_api', 'value']
    #         secret = df.loc['KIS_stock_secret', 'value']
    #         acc_no = df.loc['KIS_stock_account', 'value']
    #         mock = False
    #         # broker = mojito.KoreaInvestment(api_key=key, api_secret=secret, acc_no=acc_no)
    #     elif trade_type == '모의주식':
    #         key = df.loc['KIS_stock_mock_api', 'value']
    #         secret = df.loc['KIS_stock_mock_secret', 'value']
    #         acc_no = df.loc['KIS_stock_mock_account', 'value']
    #         mock = True
    #     elif trade_type == '실전선옵':
    #         key = df.loc['KIS_futopt_api', 'value']
    #         secret = df.loc['KIS_futopt_secret', 'value']
    #         acc_no = df.loc['KIS_futopt_account', 'value']
    #         mock = False
    #     elif trade_type == '모의선옵' or trade_type == '모의해외선옵':
    #         key = df.loc['KIS_futopt_mock_api', 'value']
    #         secret = df.loc['KIS_futopt_mock_secret', 'value']
    #         acc_no = df.loc['KIS_futopt_mock_account', 'value']
    #         mock = True
    #
    #     # 실시간주식 체결가
    #     broker_ws = KoreaInvestmentWS(api_key=key, api_secret=secret, tr_id_list=["H0STCNT0", "H0STASP0"], tr_key_list=["005930", "000660"], user_id="somepick")
    #     broker_ws.start()
    #     while True:
    #        data_ = broker_ws.get()
    #        if data_[0] == '체결':
    #            print(data_[1])
    #        elif data_[0] == '호가':
    #            print(data_[1])
    #        elif data_[0] == '체잔':
    #            print(data_[1])
    #
    #
    #     # 실시간주식호가
    #     broker_ws = KoreaInvestmentWS(api_key= key, api_secret=secret, tr_id_list=["H0STASP0"], tr_key_list=["005930"])
    #     broker_ws.start()
    #     for i in range(3):
    #        data = broker_ws.get()
    #        print(data)
    #
    #     # 실시간주식체결통보
    #     broker_ws = KoreaInvestmentWS(api_key=key, api_secret=secret, tr_id_list=["H0STCNI0"], user_id="somepick")
    #     broker_ws.start()
    #     for i in range(3):
    #        data = broker_ws.get()
    #        print(data)
    #
    # import pprint
    # broker = KoreaInvestment(key, secret, exchange="나스닥")
    # resp_ohlcv = broker.fetch_ohlcv("TSLA", '1d', to="")
    # print(len(resp_ohlcv['output2']))
    # pprint.pprint(resp_ohlcv['output2'][0])
    # pprint.pprint(resp_ohlcv['output2'][-1])
####