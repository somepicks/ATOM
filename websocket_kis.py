import websocket
import requests
import json
import time
import pickle
from threading import Thread
from pprint import pprint
import datetime
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from base64 import b64decode
from PyQt5.QtWidgets import QMainWindow, QGridLayout, QLineEdit, QLabel, QPushButton, QWidget, QVBoxLayout, \
    QTableWidget, QSplitter, QApplication, QCheckBox, QTextEdit, QTableWidgetItem, QHeaderView, QComboBox, \
    QAbstractItemView, QHBoxLayout, QTimeEdit,QDialog, QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot
from setuptools.command.dist_info import dist_info
from queue import Queue
from pathlib import Path

class KISReal(QThread):
    price_updated = pyqtSignal(dict)
    order_filled = pyqtSignal(dict)
    def __init__(self, dict_info,dict_orders):
        super().__init__()
        self.queue = Queue(maxsize=10000)
        self.dict_info = dict_info
        self.app_key = dict_info["key"]
        self.secret_key = dict_info["secret"]
        self.market = dict_info["market"]
        self.mock = dict_info["mock"]
        self.dict_orders = dict_orders
        self.dict_tickers = {}
        self.ws = None
        self.running = False
        self._connect_key = None

        # 주문 체결용 복호화에 사용
        self.aes_key = None
        self.aes_iv = None
        # 구독할 종목 목록 (tr_id: [종목코드 리스트])
        BASE_DIR = Path(__file__).resolve().parent
        self.token_file = BASE_DIR.parent / "DB" / "token.dat"
        # self.token_file = "DB/token.dat"
        # if self.check_access_token():  # 기존에 생성한 토큰이 있는지 확인
        #     self.load_access_token()
        # else:
        self._connect_key = self.issue_access_token()
        self._subscriptions = {}
        if self.dict_info['market'] == '국내주식':
            if self.dict_info['mock'] == True:
                self.chegyeol = 'H0STCNI9' #체결 모의
                self.contract_stock = 'H0STCNT0' #체결가
                self.hoka_stock = 'H0STASP0' # 호가
            else:
                self.chegyeol = 'H0STCNI0' #체결
                self.contract_stock = 'H0STCNT0' #체결가
                self.hoka_stock = 'H0STASP0' # 호가
        elif self.dict_info['market'] == '국내선옵':
            if self.dict_info['mock'] == True:
                self.chegyeol = 'H0IFCNI9'
            else:
                self.chegyeol = 'H0IFCNI0'
            self.contract_fut = 'H0IFCNT0'
            self.hoka_fut = 'H0IFASP0'
            self.contract_opt = 'H0IOCNT0'
            self.hoka_opt = 'H0IOASP0'
        elif self.dict_info['market'] == '야간선옵':
            self.chegyeol = 'H0MFCNI0'
            self.contract_fut = 'H0MFCNT0'
            self.hoka_fut = 'H0MFASP0'
            self.contract_opt = 'H0EUCNT0'
            self.hoka_opt = 'H0EUASP0'
        else:
            print('오늘은 휴장')
            return
        self.subscribe(self.chegyeol,[self.dict_info["user_id"]])
    def run(self):   # ✅ 이게 진짜 스레드 entry
        self.running = True
        Thread(target=self._ws_loop, daemon=True).start()
        Thread(target=self._parser_loop, daemon=True).start()
        Thread(target=self.rest_fallback, daemon=True).start()
        while self.running:
            time.sleep(1)
    def update_order(self,dict_orders):
        if not list(set(dict_orders.values())) == list(set(self.dict_orders.values())):
            self.dict_info = dict_orders
            for tr in [self.dict_info['체결'],self.dict_info['호가']]:
            # for tr in [self.contract_stock,self.hoka_stock]:
            # for tr in [self.contract_stock]:
                self.subscribe(tr,list(set(self.dict_info)))

    def fetch_tickers(self, dict_tickers):
        # for tr in ['H0STASP0', 'H0STCNT0']:
        if not list(set(dict_tickers.keys())) == list(set(self.dict_tickers.keys())):

            if self.dict_info['market'] == '국내선옵':
                for symbol,trade_market in self.dict_tickers:
                    if trade_market.endswith('선물'):
                        self._subscriptions.setdefault(self.contract_fut, []).append(symbol)
                    elif trade_market.endswith('옵션'):
                        self._subscriptions.setdefault(self.contract_opt, []).append(symbol)
                    # 중복구독 위험 때문에 아래로
                    # if code not in self._subscriptions.setdefault(tr, []):
                    #     self._subscriptions[tr].append(code)
                    # msg = self._build_message(tr, code)
                    # self.ws.send(msg)

    def remove_symbol(self, code):
        for tr, codes in self._subscriptions.items():
            if code in codes:
                codes.remove(code)
                msg = self._build_message(tr, code, tr_type='2')  # 🔥 unsubscribe
                self.ws.send(msg)
    # ---------------- 종목 등록 ---------------- #
    @pyqtSlot(str,list)
    def subscribe(self, tr_id, list_codes):
        """예: subscribe('H0MFASP0', ['A05605', 'A01606'])"""
        '''d = {'a': 1}
        x = d.setdefault('b', 100)
        print(x)  # 100
        print(d)  # {'a': 1, 'b': 100}'''
        self._subscriptions.setdefault(tr_id, [])

        for code in list_codes:
            if code not in self._subscriptions[tr_id]:
                self._subscriptions[tr_id].append(code)

        print(f"{self._subscriptions= }")
    def check_access_token(self):
        try:
            f = open(self.token_file, "rb")
            data = pickle.load(f)
            pprint(data)
            f.close()
            if self.mock:
                dic_txt = f"한투_웹소켓_{self.market}_모의"
            else:
                dic_txt = f"한투_웹소켓_{self.market}_실전"
            if dic_txt in data.keys():
                data = data[dic_txt]
                expire_epoch = data.get('access_token_token_expired')
                if expire_epoch == None:
                    return False
                # 토큰이 12시간동안 유효한지 확인
                elif datetime.datetime.strptime(expire_epoch,"%Y-%m-%d %H:%M:%S")-datetime.datetime.now() < datetime.timedelta(hours=12):
                    status = False  # 토큰 신규 발급
                    self.api_key = data['api']
                    self.secret_key = data['secret']
                    self.acc_no_prefix = data['acc_no']
                    self.user_id = data['id']
                else:
                    status = True
            else:
                status = False
            return status
        except IOError as e:
            print(f"check_access_token: {e}")
            return False
    def load_access_token(self):
        print('토큰 조회')
        with open(self.token_file, "rb") as f:
            dic_txt = f"한투_웹소켓_{self.market}_모의" if self.mock else f"한투_웹소켓_{self.market}_실전"
            data = pickle.load(f)
            data = data[dic_txt]
            self._connect_key = f'Bearer {data["approval_key"]}'
            self.api_key = data['api']
            self.secret_key = data['secret']
            self.acc_no_prefix = data['acc_no']
            self.user_id = data['user_id']
    # ---------------- 인증 ---------------- #
    def issue_access_token(self):
        print(f"[issue_access_token] approval_key 발급 {self._connect_key}")
        dic_txt = f"한투_웹소켓_{self.market}_모의" if self.mock else f"한투_웹소켓_{self.market}_실전"
        f = open(self.token_file, "rb")
        data = pickle.load(f)
        api_data = data.get(dic_txt)

        # 추 후 아래부분 수정
        if api_data == None:
            api_data = data.get('한국투자증권_국내_주식_실전')
        api_data = data['한국투자증권_국내_주식_실전']

        self.app_key = api_data['api']
        self.secret_key = api_data['secret']
        self.acc_no = api_data['acc_no']
        self.user_id = api_data['user_id']

        if self.mock:
            self.base_url = "https://openapivts.koreainvestment.com:29443/oauth2/Approval"
        else:
            self.base_url = "https://openapi.koreainvestment.com:9443/oauth2/Approval"
        body = {
            "grant_type": "client_credentials",
            "appkey": self.app_key,
            "secretkey": self.secret_key
        }
        res = requests.post(self.base_url, headers={"content-type": "application/json"}, data=json.dumps(body))
        output = res.json()
        output['access_token_token_expired'] = (datetime.datetime.now()+datetime.timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
        if output.get('error_description'):
            print(f"[issue_access_token]  {output= }")

        with open(self.token_file, "wb") as f:
            output['api'] = self.app_key
            output['secret'] = self.secret_key
            output['acc_no'] = self.acc_no
            output['user_id'] = self.user_id
            data[dic_txt] = output
            pickle.dump(data, f)
        return output["approval_key"]

    # ---------------- 구독 메시지 빌드 ---------------- #
    def _build_message(self, tr_id, tr_key, tr_type='1'):
        return json.dumps({
            "header": {
                "approval_key": self._connect_key,
                "custtype": "P",
                "tr_type": tr_type,
                "content-type": "utf-8"
            },
            "body": {
                "input": {
                    "tr_id": tr_id,
                    "tr_key": tr_key
                }
            }
        })

    # ---------------- 데이터 파싱 ---------------- #
    def _parse(self, data):
        parts = data.split('|')
        if len(parts) < 4:
            return

        tr_id = parts[1]
        raw   = parts[3]
        print('============')
        print(f"_parse: {self.dict_info['market']}")
        if self.dict_info['market'] == '국내선옵':
            if tr_id == self.chegyeol:  # 국내선옵 체결통보
                self._parse_chegyeol('국내선옵',raw)
            # elif tr_id == self.hoka_fut:   # 선물 호가
            #     self._parse_hoka('국내선물',raw)
            elif tr_id == self.contract_fut:   # 선물 체결가
                self._parse_contract('국내선물',raw)
            # elif tr_id == self.hoka_opt:  # 옵션 체결가
            #     self._parse_hoka('국내옵션', raw)
            elif tr_id == self.contract_opt:  # 옵션 체결가
                self._parse_contract('국내옵션', raw)
        elif self.dict_info['market'] == '야간선옵':
            if tr_id == self.chegyeol:  # 체결통보
                self._parse_chegyeol('야간선옵',raw)
            elif tr_id == self.contract_fut: #  체결가
                self._parse_contract('야간선물',raw)
            elif tr_id == self.contract_opt: #  체결가
                self._parse_contract('야간옵션', raw)
        elif self.dict_info['market'] == '국내주식':
            if tr_id == self.chegyeol:  # 국내주식 체결통보 실전|모의
                self._parse_chegyeol('국내주식',raw)
            # if tr_id == self.hoka_stock: # 국내주식 호가
            #     self._parse_hoka('국내주식',raw)
            elif tr_id == self.contract_stock: # 국내주식 체결가
                self._parse_contract('국내주식', raw)
        else:
            print(f"[UNKNOWN TR] {tr_id}: {raw[:80]}")


    # ---------------- 시스템 메시지 처리 ---------------- #
    def _handle_system(self, ws, data):
        # print(f"[_handle_system] {data=}")
        try:
            rdic = json.loads(data)
            tr_id = rdic['header']['tr_id']
            if tr_id == "PINGPONG":
                ws.send(data, websocket.ABNF.OPCODE_TEXT)
                return
            body = rdic.get('body')
            if body is None:
                return
            elif body["msg1"].startswith("ALREADY IN"):
                print(f'_handle_system 기존 연결된게 있음 끊어야 됨 {body}')
            else:
                print(f'_handle_system {body= }')

            is_ok = body.get('rt_cd') == '0'
            msg   = body.get('msg1', '')
            tr_key = rdic['header'].get('tr_key', '')
            if is_ok:
                print(f"[KIS] 구독 성공 ✅ tr_id={tr_id}, code={tr_key}, msg={msg}")
                # if tr_id in ("H0STCNI0", "H0STCNI9", "H0IFCNI0", "H0MFCNI0"):
                output = body.get('output', {})
                self.aes_key = output.get('key')
                self.aes_iv = output.get('iv')
                print(f"[AES KEY SET] key={self.aes_key}, iv={self.aes_iv}")
            else:
                print(f"[KIS] 구독 실패 ❌ tr_id={tr_id}, msg={msg}")
        except Exception as e:
            print("[_handle_system] msg error:", e)
    def on_open(self, ws):
        # print("[WS OPEN] 재구독 시작")
        # 🔥 체결통보 대비 초기화
        self.aes_key = None
        self.aes_iv = None

        def _do_subscribe():
            time.sleep(0.5)  # 서버 준비 대기

            for tr_id, codes in self._subscriptions.items():
                for code in codes:
                    msg = self._build_message(tr_id, code)
                    ws.send(msg, websocket.ABNF.OPCODE_TEXT)
                    print(f"[재구독] {tr_id} / {code}")
                    time.sleep(0.2)

        Thread(target=_do_subscribe, daemon=True).start()
    def on_message(self, ws, data):
        # if data[0] in ('0', '1'):
        #     self._parse(data)
        # else:
        #     self._handle_system(ws, data)

        self.queue.put(data) #바로 던지고 끝
    def on_error(self, ws, error):
        print(f"*** on_error ***: {error}")
    def on_close(self, ws, status_code, close_msg):
        print(f"*** on_close ***: {status_code}, {close_msg}")

    def _parse_hoka(self,market, raw):
        v = raw.split('^')
        if market == '국내주식':
            result = {
                'type': 'hoka',
                'code': v[0],
                'time': v[1],
                # 매도호가 1~5
                'ask1': v[3],  'ask2': v[4],  'ask3': v[5],  'ask4': v[6],  'ask5': v[7],
                # 매수호가 1~5
                'bid1': v[13], 'bid2': v[14], 'bid3': v[15], 'bid4': v[16], 'bid5': v[17],
                # 매도잔량 1~5
                'ask_qty1': v[23], 'ask_qty2': v[24], 'ask_qty3': v[25], 'ask_qty4': v[26], 'ask_qty5': v[27],
                # 매수잔량 1~5
                'bid_qty1': v[33], 'bid_qty2': v[34], 'bid_qty3': v[35], 'bid_qty4': v[36], 'bid_qty5': v[37],
                # 총잔량
                'total_ask_qty': v[43],
                'total_bid_qty': v[44],
            }
        elif market == '국내선물':
            result = {
                'type': 'hoka',
                'code': v[0],
                'time': v[1],
                # 매도호가 1~5
                'ask1': v[2],  'ask2': v[3],  'ask3': v[4],  'ask4': v[5],  'ask5': v[6],
                # 매수호가 1~5
                'bid1': v[7], 'bid2': v[8], 'bid3': v[9], 'bid4': v[10], 'bid5': v[11],
                # 매도잔량 1~5
                'ask_qty1': v[22], 'ask_qty2': v[23], 'ask_qty3': v[24], 'ask_qty4': v[25], 'ask_qty5': v[26],
                # 매수잔량 1~5
                'bid_qty1': v[27], 'bid_qty2': v[28], 'bid_qty3': v[29], 'bid_qty4': v[30], 'bid_qty5': v[31],
                # 총잔량
                'total_ask_qty': v[34],
                'total_bid_qty': v[35],
                '총매도호가잔량증감': v[36],
                '총매수호가잔량증감': v[37],
            }
        self.price_updated.emit(result)
    def _decrypt(self, cipher_text):
        cipher = AES.new(self.aes_key.encode('utf-8'), AES.MODE_CBC, self.aes_iv.encode('utf-8'))
        return unpad(cipher.decrypt(b64decode(cipher_text)), AES.block_size).decode()
    def _parse_contract(self,market, raw):
        v = raw.split('^')
        if market == '국내주식':
            result = {
                'type':    'contract',
                'code':    v[0],
                'time':    v[1],
                'price':   v[2],   # 현재가
                'sign':    v[3],   # 전일대비부호
                'diff':    v[4],   # 전일대비
                'rate':    v[5],   # 전일대비율
                'open':    v[7],   # 시가
                'high':    v[8],   # 고가
                'low':     v[9],   # 저가
                'ask':     v[10],  # 매도호가
                'bid':     v[11],  # 매수호가
                'vol':     v[12],  # 체결거래량
                'acc_vol': v[13],  # 누적거래량
            }
        elif market == '국내선물':
            result = {
                'type':    'contract',
                'code':    v[0],
                'time':    v[1],
                'price':   v[2],   # 현재가
                'sign':    v[3],   # 전일대비부호
                'diff':    v[4],   # 전일대비
                'rate':    v[5],   # 전일대비율
                'open':    v[7],   # 시가
                'high':    v[8],   # 고가
                'low':     v[9],   # 저가
                'ask':     v[10],  # 매도호가
                'bid':     v[11],  # 매수호가
                'vol':     v[12],  # 체결거래량
                'acc_vol': v[13],  # 누적거래량
            }
        elif market == '국내옵션':
            result = {
                'type':    'contract',
                'code':    v[0],
                'time':    v[1],
                'price':   v[2],   # 현재가
                'sign':    v[3],   # 전일대비부호
                'diff':    v[4],   # 전일대비
                'rate':    v[5],   # 전일대비율
                'open':    v[7],   # 시가
                'high':    v[8],   # 고가
                'low':     v[9],   # 저가
                'ask':     v[10],  # 매도호가
                'bid':     v[11],  # 매수호가
                'vol':     v[12],  # 체결거래량
                'acc_vol': v[13],  # 누적거래량
            }
        self.price_updated.emit(result)
    def _parse_chegyeol(self,market , raw):
        if not self.aes_key or not self.aes_iv:
            print("[WARN] AES key not ready")
            return
        try:
            # 🔥 복호화
            dec = self._decrypt(raw)
            v = dec.split('^')
            pprint(v)
            print(f"{market}")
            if market == '국내주식':
                result = {
                    'type': 'chegyeol',
                    'id': v[0],
                    'acc': v[1],
                    'uuid': v[2],
                    'won_uuid': v[3],
                    '매수매도': v[4],
                    '정정': v[5],
                    '주문종류': v[6],
                    'ticker': v[8],
                    '체결수량': v[9],
                    'price': v[10],
                    'time': v[11],
                    '체결여부': v[13],
                    '주문수량': v[16],
                    '거래소': v[16],
                    '실시간체결창 표시여부': v[20],
                    '체결종목명': v[24],
                    '주문가격': v[25],
                }
            elif market == '국내선옵':
                result = {
                    'type': 'chegyeol',
                    'id': v[0],
                    'acc': v[1],
                    'uuid': v[2],
                    'won_uuid': v[3],
                    '매수매도': v[4],
                    '정정': v[5],
                    '주문종류': v[6],
                    'ticker': v[8],
                    '체결수량': v[9],
                    'price': v[10],
                    'time': v[11],
                    '체결여부': v[13],
                    '주문수량': v[16],
                    '거래소': v[16],
                    '실시간체결창 표시여부': v[20],
                    '체결종목명': v[24],
                    '주문가격': v[25],
                }
            elif market == '야간선옵' :
                result = {
                    'type': 'chegyeol',
                    'id': v[0],
                    'acc': v[1],
                    'uuid': v[2],
                    'won_uuid': v[3],
                    '매수매도': v[4],
                    '정정': v[5],
                    '주문종류': v[6],
                    'ticker': v[7],
                    '체결수량': v[8],
                    'price': v[9],
                    'time': v[10],
                    '거부여부': v[11],
                    '체결여부': v[12],
                    '주문수량': v[15],
                    '계좌명': v[16],
                    '체결종목명': v[17],
                    '주문조건': v[18],
                }
            print("[복호화 완료]")
            self.order_filled.emit(result)
        except Exception as e:
            print("[DECRYPT ERROR]", e)

    def _ws_loop(self):
        while self.running:
            try:
                if not self._connect_key:
                    self._connect_key = self.issue_access_token()
                # self._connect_key = self._get_approval_key()
                if self.mock == True:
                    url = "ws://ops.koreainvestment.com:31000"
                else:
                    url = "ws://ops.koreainvestment.com:21000"
                # print(f"{url= }")
                self.ws = websocket.WebSocketApp(
                    url,
                    on_open=self.on_open,
                    on_message=self.on_message,
                    on_error=self.on_error,
                    on_close=self.on_close
                )
                self.ws.run_forever(ping_interval=15, ping_timeout=10)
            except Exception as e:
                print("WS error:", e)
            time.sleep(3)

    def _parser_loop(self):
        while self.running:
            # print('self.running')
            try:
                data = self.queue.get()
                # print('====================')
                # pprint(f"[_parser_loop] {data=}")
                # print('====================')
                if data[0] in ('0', '1'):
                    self._parse(data)
                else:
                    self._handle_system(self.ws, data)
            except Exception as e:
                print("parse error:", e)

    def stop(self):
        self.running = False
        if self.ws:
            self.ws.close()
    def rest_fallback(self):
        while self.running:
            time.sleep(30)
            print(f'rest fallback {datetime.datetime.now()}')


class Window(QMainWindow): #별도로 실행하고자 할 때
    send_orders = pyqtSignal(dict)
    send_tickers = pyqtSignal(dict)
    def __init__(self):
        super().__init__()
        self.QPB_start_stock = QPushButton('웹소켓 연결(주식)')
        self.QPB_start_futopt = QPushButton('웹소켓 연결(선옵)')
        self.QPB_start_futopt_night = QPushButton('웹소켓 연결(야간선옵)')
        self.QPB_chegyeol = QPushButton('체결연결')
        self.QPB_stop = QPushButton('웹소켓 중지')
        self.QPB_add = QPushButton('종목추가')
        self.QPB_del = QPushButton('종목삭제')
        self.QLE = QLineEdit()
        self.QTE = QTextEdit()

        QVB_main = QVBoxLayout()
        QVB_main.addWidget(self.QPB_start_stock)
        QVB_main.addWidget(self.QPB_start_futopt)
        QVB_main.addWidget(self.QPB_start_futopt_night)
        QVB_main.addWidget(self.QPB_chegyeol)
        QVB_main.addWidget(self.QPB_add)
        QVB_main.addWidget(self.QPB_del)
        QVB_main.addWidget(self.QLE)
        QVB_main.addWidget(self.QTE)

        QW_main = QWidget()
        QW_main.setLayout(QVB_main)
        self.setCentralWidget(QW_main)
        self.QPB_start_stock.clicked.connect(lambda:self.connect_ws('국내주식'))
        self.QPB_start_futopt.clicked.connect(lambda:self.connect_ws('국내선옵'))
        self.QPB_start_futopt_night.clicked.connect(lambda:self.connect_ws('야간선옵'))
        self.QPB_chegyeol.clicked.connect(lambda:self.connect_ws('야간선옵'))
        self.QPB_add.clicked.connect(lambda: self.add_order(self.QLE.text()))
        self.QPB_del.clicked.connect(lambda: self.del_order(self.QLE.text()))
        self.dict_info = {}
    def connect_ws(self,market):
        if market == '국내주식':
            key = "PSnRbdaAPoj86qrw73q25rCnIzc8zBqBs02J"
            secret = "68UdwXxybY6j19I/QW86VLXe676PUsJnCmIq99oq2tjazDn+gDoY6IcwLOZMuMRY0wuy5Mzjd1C5AvXrNknEtZiaazSDcdxg4+1BiYdlSEs7drk2d8xVMqSdASB79QN6g8TUOf/8VsLOWIx3IQeVhn0gFkQTlHNQxfEZwG4rnvF9FA1Ndmc="
            night = False
            tr_key = 'somepick'
        elif market == '국내선옵' or market == '야간선옵':
            # key = "PSCLO2WTCrnbFTVJLqZcRGZwYVAll8BHU34I"
            # secret = "l/12Smyub2n5MSDGwxiLde3vK6FWsRWq6HcU8RPfKYgw31qnDiQLhyaj1y2cpyOromd9nZOkeIBIug7PWu+RQShovpzMGB5uf59xKFnOAIbkmTGFGdNhr9ULEWR4OiK2SDdUuZ9PST94RZfy5IDpewS2vUi0q6wcO2t1C/pJ1QZFxsPNvvk="
            key = "PSnRbdaAPoj86qrw73q25rCnIzc8zBqBs02J"
            secret = "68UdwXxybY6j19I/QW86VLXe676PUsJnCmIq99oq2tjazDn+gDoY6IcwLOZMuMRY0wuy5Mzjd1C5AvXrNknEtZiaazSDcdxg4+1BiYdlSEs7drk2d8xVMqSdASB79QN6g8TUOf/8VsLOWIx3IQeVhn0gFkQTlHNQxfEZwG4rnvF9FA1Ndmc="
            tr_key = 'somepick'
            if market == '국내선옵':
                night = False
            elif market == '야간선옵':
                night = True
        mock = False
        # self.dict_info = {"key":key,'secret':secret,"ID":'somepick','호가':hoka,'체결가':contract,'체결':chegyeol}
        self.dict_info = {"key":key,'secret':secret,"user_id":tr_key,'market':market,'night':night,'mock':mock}
        self.dict_orders = {}
        self.thread_ws = KISReal(dict_info=self.dict_info,dict_orders=self.dict_orders)
        self.thread_ws.price_updated.connect(self.price_data)
        self.thread_ws.order_filled.connect(self.chegyeol_closed)
        self.send_orders.connect(self.thread_ws.update_order)
        self.send_tickers.connect(self.thread_ws.fetch_tickers)
        # self.thread_ws.subscribe('H0STCNI9','somepick')
        self.thread_ws.start()
    @pyqtSlot(dict)
    def price_data(self,data):
        print(data)
    @pyqtSlot(dict)
    def chegyeol_closed(self,data):
        print(f"체결:    {data}")
    def add_order(self,code):

        print(code)
        if not code in list(set(self.dict_orders.values())):
            self.thread_ws.add_symbol(code)
        self.send_orders.emit(code)

        # id = datetime.datetime.now().replace(microsecond=0).strftime("%Y%m%d%H%M%S")
        # self.dict_orders[id] = code
        # self.QTE.clear()
        # formatted_text = json.dumps(self.dict_orders, indent=4, ensure_ascii=False)
        # self.QTE.setText(formatted_text)
        # print(self.dict_orders)
    def add_tickers(self):
        code = {'A01606': '선물', 'A05606': '미니선물', 'B09F1WB38': '위클리콜옵션', 'B09F1WB34': '위클리콜옵션', 'B09F1WB32': '위클리콜옵션',
         'B09F1WB30': '위클리콜옵션', 'B09F1WB28': '위클리콜옵션', 'B09F1WB26': '위클리콜옵션', 'B09F1WB25': '위클리콜옵션',
         'B09F1WB24': '위클리콜옵션', 'B09F1WB23': '위클리콜옵션', 'B09F1WB22': '위클리콜옵션', 'B09F1WB21': '위클리콜옵션',
         'B09F1WB20': '위클리콜옵션', 'B09F1WB18': '위클리콜옵션', 'B09F1WB17': '위클리콜옵션', 'B09F1WB16': '위클리콜옵션',
         'B09F1WB15': '위클리콜옵션', 'B09F1WB14': '위클리콜옵션', 'B09F1WB12': '위클리콜옵션', 'B09F1WB10': '위클리콜옵션',
         'C09F1WB18': '위클리풋옵션', 'C09F1WB14': '위클리풋옵션', 'C09F1WB12': '위클리풋옵션', 'C09F1WB11': '위클리풋옵션',
         'C09F1WB10': '위클리풋옵션', 'C09F1WB09': '위클리풋옵션', 'C09F1WB08': '위클리풋옵션', 'C09F1WB07': '위클리풋옵션',
         'C09F1WB06': '위클리풋옵션', 'C09F1WB05': '위클리풋옵션', 'C09F1WB04': '위클리풋옵션', 'C09F1WB02': '위클리풋옵션',
         'C09F1WA99': '위클리풋옵션', 'C09F1WA97': '위클리풋옵션', 'C09F1WA95': '위클리풋옵션', 'C09F1WA93': '위클리풋옵션',
         'C09F1WA89': '위클리풋옵션', 'C09F1WA85': '위클리풋옵션', 'C09F1WA81': '위클리풋옵션'}
        self.send_tickers.emit(code)

    def del_order(self,uuid):
        try:
            dict_ord_old = self.dict_orders.copy()
            self.dict_orders.pop(uuid)

            if not list(set(dict_ord_old.values())) == list(set(self.dict_orders.values())):
                code = self.dict_orders[uuid]  # 🔥 핵심
                # 동일 종목이 더 있는지 확인
                if code not in self.dict_orders.values():
                    self.thread_ws.remove_symbol(code)
                # self.send_orders.emit(self.dict_orders)
            self.QTE.clear()
            formatted_text = json.dumps(self.dict_orders, indent=4, ensure_ascii=False)
            self.QTE.setText(formatted_text)
            print(self.dict_orders)
        except:
            print(f"uuid 확인 필요 {uuid}")


if __name__ == "__main__":
    # 텔레그램 봇 설정
    # market = '국내선옵'
    import sys
    def ExceptionHook(exctype, value, traceback):
        sys.__excepthook__(exctype, value, traceback)
        sys.exit(1)
    sys.excepthook = ExceptionHook  # 예외 후크 설정 부분 (에러가 표시되지 않으면서 종료되는증상을 방지하기 위함)
    app = QApplication([])
    main_table = Window()
    main_table.setMinimumSize(600, 400)
    main_table.show()
    app.exec()
