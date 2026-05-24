import asyncio
import datetime
import os
import pickle
import ccxt.pro as ccxtpro
import json

from threading import Thread
import requests
import time
import websocket
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot
from pprint import pprint
from queue import Queue
class KISReal(QThread):
    def __init__(self, app_key, secret_key,user_id, callback=print):

        self.app_key = app_key
        self.secret_key = secret_key
        self.user_id = user_id
        self.callback = callback

        self.ws = None
        self.running = False
        self._connect_key = None

        # 주문 체결용 복호화에 사용
        self.aes_key = None
        self.aes_iv = None
        # 구독할 종목 목록 (tr_id: [종목코드 리스트])
        self._subscriptions = {}

    # ---------------- 종목 등록 ---------------- #
    def subscribe(self, tr_id, codes):
        """예: subscribe('H0MFASP0', ['A05605', 'A01606'])"""
        self._subscriptions[tr_id] = codes
        print(f"{self._subscriptions= }")

    # ---------------- 인증 ---------------- #
    def _get_approval_key(self):
        url = "https://openapi.koreainvestment.com:9443/oauth2/Approval"
        body = {
            "grant_type": "client_credentials",
            "appkey": self.app_key,
            "secretkey": self.secret_key
        }
        res = requests.post(url, headers={"content-type": "application/json"}, data=json.dumps(body))
        return res.json()["approval_key"]

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
        raw = parts[3]
        if tr_id == 'H0IFASP0':  # 선물 호가
            self._parse_hoka('국내선물', raw)
        elif tr_id == 'H0IFCNT0':  # 선물 체결
            self._parse_contract('국내선물',raw)
        elif tr_id == 'H0MFASP0':  # 야간선물 호가
            self._parse_hoka('국내선물',raw)
        elif tr_id == 'H0MFCNT0':  # 야간선물 체결
            self._parse_contract('국내선물',raw)
        elif tr_id == 'H0STASP0':  # 국내주식 호가
            self._parse_hoka('국내주식', raw)
        elif tr_id == 'H0STCNT0':  # 국내주식 체결
            self._parse_contract('국내주식',raw)
        elif tr_id == 'H0STCNI0' or tr_id == 'H0STCNI9':  # 국내주식 체결통보
            self._parse_chegyeol(raw)
        elif tr_id == 'H0IFCNI0':  # 국내선옵 체결통보
            pprint(parts)
            self._parse_chegyeol(raw)
        else:
            print(f"[UNKNOWN TR] {tr_id}: {raw[:80]}")

    def _parse_hoka(self, market, raw):
        v = raw.split('^')
        pprint(v)
        if market == '국내주식':
            result = {
                'type': 'hoka',
                'code': v[0],
                'time': v[1],
                # 매도호가 1~5
                'ask1': v[3], 'ask2': v[4], 'ask3': v[5], 'ask4': v[6], 'ask5': v[7],
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
                'ask1': v[2], 'ask2': v[3], 'ask3': v[4], 'ask4': v[5], 'ask5': v[6],
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
        self.callback(result)

    def _decrypt(self, cipher_text):
        from Crypto.Cipher import AES
        from base64 import b64decode
        from Crypto.Util.Padding import unpad

        cipher = AES.new(self.aes_key.encode('utf-8'), AES.MODE_CBC, self.aes_iv.encode('utf-8'))
        return unpad(cipher.decrypt(b64decode(cipher_text)), AES.block_size).decode()

    def _parse_contract(self, market, raw):
        v = raw.split('^')
        if market == '국내주식':
            result = {
                'type': 'contract',
                'code': v[0],
                'time': v[1],
                'price': v[2],  # 현재가
                'sign': v[3],  # 전일대비부호
                'diff': v[4],  # 전일대비
                'rate': v[5],  # 전일대비율
                'open': v[7],  # 시가
                'high': v[8],  # 고가
                'low': v[9],  # 저가
                'ask': v[10],  # 매도호가
                'bid': v[11],  # 매수호가
                'vol': v[12],  # 체결거래량
                'acc_vol': v[13],  # 누적거래량
            }
        elif market == '국내선물':
            result = {
                'type': 'contract',
                'code': v[0],
                'time': v[1],
                'ratio': v[2],  # 선물 전일 대비
                'sign': v[3],  # 전일대비부호
                'diff': v[4],  # 전일대비
                'rate': v[5],  # 전일대비율
                'price': v[7],  # 선물 현재가
                'open': v[8],  # 선물 시가2
                'low': v[9],  # 선물 최저가
                'ask': v[10],  # 최종 거래량
                'vol': v[11],  # 누적 거래량
                'vol_price': v[12],  # 누적 거래 대금
            }
        print(result)
        self.callback(result)

    def _parse_chegyeol(self, raw):
        print(f"{self.aes_key= }")
        print(f"{self.aes_iv= }")
        if not self.aes_key or not self.aes_iv:
            print("[WARN] AES key not ready")
            return

        try:
            # 🔥 복호화
            dec = self._decrypt(raw)
            v = dec.split('^')

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
            print("[복호화 완료]")
            print(result)
            self.callback(result)

        except Exception as e:
            print("[DECRYPT ERROR]", e)

    # ---------------- 시스템 메시지 처리 ---------------- #
    def _handle_system(self, ws, data):
        print(f"_handle_system {data}")
        try:
            rdic = json.loads(data)
            tr_id = rdic['header']['tr_id']

            if tr_id == "PINGPONG":
                ws.send(data, websocket.ABNF.OPCODE_TEXT)
                return

            body = rdic.get('body')
            if body is None:
                return

            is_ok = body.get('rt_cd') == '0'
            msg = body.get('msg1', '')
            tr_key = rdic['header'].get('tr_key', '')

            if is_ok:
                print(f"[KIS] 구독 성공 ✅ tr_id={tr_id}, code={tr_key}, msg={msg}")
                if tr_id == "H0STCNI0" or tr_id == "H0STCNI9":
                    output = body.get('output', {})
                    self.aes_key = output.get('key')
                    self.aes_iv = output.get('iv')
                    print(f"[AES KEY SET] key={self.aes_key}, iv={self.aes_iv}")
            else:
                print(f"[KIS] 구독 실패 ❌ tr_id={tr_id}, msg={msg}")

        except Exception as e:
            print("system msg error:", e)


    # 밑에는 자동 재구독 보완
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
        if data[0] in ('0', '1'):
            self._parse(data)
        else:
            self._handle_system(ws, data)

    def on_error(self, ws, error):
        print(f"[KIS] error: {error}")

    def on_close(self, ws, status_code, close_msg):
        print(f"[KIS] closed: {status_code}, {close_msg}")

    # ---------------- 실행 / 종료 ---------------- #
    def start(self):
        self.running = True
        while self.running:
            try:
                self._connect_key = self._get_approval_key()
                print(f"[KIS] approval_key 발급 완료 {self._connect_key}")
                Thread(target=self.rest_fallback, daemon=True).start()

                self.ws = websocket.WebSocketApp(
                    "ws://ops.koreainvestment.com:21000",
                    on_open=self.on_open,
                    on_message=self.on_message,
                    on_error=self.on_error,
                    on_close=self.on_close
                )
                self.ws.run_forever(ping_interval=20, ping_timeout=10)
            except Exception as e:
                print("연결 에러:", e)
            if self.running:
                print("5초 후 재연결...")
                time.sleep(5)

    def stop(self):
        self.running = False
        if self.ws:
            self.ws.close()

    def rest_fallback(self):
        while self.running:
            time.sleep(30)
            print(f'rest fallback {datetime.datetime.now()}')


class Thread_coin(QThread):
    price_updated = pyqtSignal(dict)
    order_filled = pyqtSignal(dict)

    def __init__(self, dict_option, dict_orders):
        super().__init__()
        self.running = True
        self.market = dict_option['market']
        self.list_ticker = ['BTC/KRW']
        self.dict_ord = dict(dict_orders) if dict_orders else {}
        self._loop = None
        self._pending_orders = None  # 메인스레드→asyncio 전달용
        self.ex_ws = dict_option['ex_ws']

    def run(self):
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        try:
            self._loop.run_until_complete(self.run_all())
        finally:
            self._loop.close()

    async def run_all(self):
        await asyncio.gather(
            self.watch_ticker_info(),
            self.watch_chegyeol(),
            self.rest_fallback(),
            self.apply_pending_orders(),  # ← 주문 업데이트 수신 전담 코루틴
        )

    # ───────────────────────────────────────────
    # 메인스레드 → asyncio 안전 전달
    # ───────────────────────────────────────────
    @pyqtSlot(dict)
    def check_dict_orders(self, dict_orders):
        print(f'check_dict_orders  {dict_orders= }')
        """
        메인스레드 → asyncio: 새 주문 ID만 전달
        삭제는 웹소켓/_process_order/rest_fallback이 담당
        """
        if self._loop and self._loop.is_running():
            self._loop.call_soon_threadsafe(self._add_new_orders, dict_orders)

    def _add_new_orders(self, dict_orders):
        """새 주문만 추가, 기존 주문 절대 삭제 안 함"""
        for order_id, symbol in dict_orders.items():
            if order_id not in self.dict_ord:
                self.dict_ord[order_id] = symbol
                print(f'[WS] 신규 주문 추가: ticker={symbol}, id={order_id} | {self.dict_ord}')

    async def apply_pending_orders(self):
        """혹시 call_soon_threadsafe 외 큐 방식을 쓰고 싶을 때 확장용"""
        while self.running:
            await asyncio.sleep(1)

    # ───────────────────────────────────────────
    # 티커
    # ───────────────────────────────────────────
    async def watch_ticker_info(self):
        while self.running:
            try:
                # dict_ord의 심볼 + 기본 티커 합산
                symbols = list(set(self.list_ticker) | set(self.dict_ord.values()))
                # symbols = ['BTC/KRW','ETH/KRW','XRP/KRW']
                dict_tickers = await self.ex_ws.watch_tickers(symbols)
                self.price_updated.emit(dict_tickers)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"[WS] watch_ticker_info 에러: {e}")
                await asyncio.sleep(3)
        await self.ex_ws.close()

    # ───────────────────────────────────────────
    # 체결 감지 (수정 핵심)
    # ───────────────────────────────────────────
    async def watch_chegyeol(self):
        """심볼별 태스크를 동적으로 관리"""
        watching = {}  # symbol → Task

        while self.running:
            # 현재 감시해야 할 심볼 목록
            symbols_needed = set(self.dict_ord.values())

            # 필요 없어진 심볼 태스크 취소
            for sym in list(watching.keys()):
                if sym not in symbols_needed:
                    watching[sym].cancel()
                    del watching[sym]

            # 새 심볼 태스크 생성
            for sym in symbols_needed:
                if sym not in watching:
                    watching[sym] = asyncio.create_task(
                        self._watch_one_symbol(sym)
                    )

            await asyncio.sleep(1)

        # 종료 시 모든 태스크 취소
        for task in watching.values():
            task.cancel()

    async def _watch_one_symbol(self, symbol):
        """단일 심볼 체결 감시 (무한 루프)"""
        while self.running:
            try:
                list_orders = await self.ex_ws.watch_orders(symbol)
                for order in list_orders:
                    self._process_order(order)
            except asyncio.CancelledError:
                print(f"[WS] {symbol} 감시 취소")
                break
            except Exception as e:
                print(f"[WS] {symbol} 에러: {e}")
                await asyncio.sleep(3)

    def _process_order(self, order):
        order_id   = order['id']
        order_info = order['info']
        state      = order_info.get('state')
        print(f"[WS]_process_order 현재 관리중인 주문: {list(self.dict_ord.keys())} id={order_id} state={state} | {order_id in list(self.dict_ord.keys())}")

        if order_id in list(self.dict_ord.keys()):
            if state == 'wait':
                return  # 아직 미체결 — 계속 감시

            if state == 'done':
                pprint(f"order:  {order}")
                pprint(f"order_info:  {order_info}")
                dic_out = {order_id: {'state': '체결',
                                      'amount': order_info['executed_volume'],
                                      'price': order_info['price']}}
                self.dict_ord.pop(order_id, None)
                self.order_filled.emit(dic_out)
            elif state == 'trade':
                dic_out = {order_id: {'state': '거래중',
                                      'amount': order_info['executed_volume'],
                                      'price': 0}}
            elif state == 'cancel':
                dic_out = {order_id: {'state': '취소',
                                      'amount': order_info['executed_volume'],
                                      'price': 0}}
            print(f"[WS] {datetime.datetime.now().replace(microsecond=0)}   {dic_out}")
        else:
            print('다른 주문')
            pprint(order)



    # ───────────────────────────────────────────
    # REST 폴백
    # ───────────────────────────────────────────
    async def rest_fallback(self):
        while self.running:
            try:
                await asyncio.sleep(30)
                print(f'{datetime.datetime.now().replace(microsecond=0)} 30초마다 주문 확인  {self.dict_ord}')
                for order_id, symbol in list(self.dict_ord.items()):
                    order = self.ex_ws.fetch_order(order_id, symbol)
                    status = order['status']
                    if status == 'closed':
                        dic_out = {order_id: {'state': '체결',
                                              'amount': order['amount'],
                                              'price':  order['average']}}
                    elif status == 'canceled':
                        dic_out = {order_id: {'state': '취소',
                                              'amount': order['amount'],
                                              'price':  0}}
                    else:
                        continue

                    print(f"[REST] {order_id} {dic_out[order_id]['state']} 확인")
                    self.dict_ord.pop(order_id, None)
                    self.order_filled.emit(dic_out)

            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"[REST] 에러: {e}")

    def stop(self):
        self.running = False