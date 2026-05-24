from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot
import os
import pickle
import ccxt.pro as ccxtpro
import asyncio
from pprint import pprint

class WebSocketThread(QThread):
    price_updated = pyqtSignal(dict)
    order_filled = pyqtSignal(dict)

    def __init__(self, dict_option, dict_orders):
        super().__init__()
        self.running = True
        self.market = dict_option['market']
        self.list_ticker = ['BTC/KRW']
        self.dict_ord = dict(dict_orders) if dict_orders else {}

        if self.market == "업비트":
            # token_name = "DB/token.dat"
            # if os.path.isfile(token_name):
            #     with open(token_name, "rb") as f:
            #         data = pickle.load(f)
            # # else:
            # #     data = {}
            # api = data.get("업비트", {}).get('api', '')
            # secret = data.get("업비트", {}).get('secret', '')
            self.ex_ws = dict_option['ex_ws']

    def run(self):
        asyncio.run(self.run_all())

    async def run_all(self):
        task1 = asyncio.create_task(self.watch_ticker_info())
        task2 = asyncio.create_task(self.watch_chegyeol())
        task3 = asyncio.create_task(self.rest_fallback())
        await asyncio.gather(task1, task2, task3)

    async def watch_ticker_info(self):
        while self.running:
            try:
                dict_tickers = await self.ex_ws.watch_tickers(self.list_ticker)
                self.price_updated.emit(dict_tickers)
            except asyncio.CancelledError:
                print("[WS] watch_ticker_info  watch_ticker 종료")
                break
            except Exception as e:
                print(f"[WS] watch_ticker_info  ticker 에러: {e}")
                break
        await self.ex_ws.close()

    async def watch_chegyeol(self):
        """심볼별 주문 체결 감지"""
        while self.running:
            try:
                for symbol in list(set(self.dict_ord.values())):
                    list_orders = await self.ex_ws.watch_orders(symbol)
                    print(f"watch_chegyeol: {list_orders= }")
                    for order in list_orders:
                        order_info = order['info']
                        print(f"{order_info['uuid']} watch_chegyeol : {order_info= }")
                        if order_info['state'] == 'done':
                            dic_out = {order['id']:{'state':'체결','amount':order_info['executed_volume'],'price':order_info['average']}}
                        elif order_info['state'] == 'trade':
                            dic_out = {order['id']:{'state':'거래중','amount':order_info['executed_volume'],'price':0}}
                        elif order_info['state'] == 'cancel':
                            dic_out = {order['id']:{'state':'취소','amount':order_info['executed_volume'],'price':0}}
                        elif order_info['state'] == 'wait':
                            continue
                        if order_info['uuid'] in list(set(self.dict_ord.keys())):
                            self.dict_ord.pop(order['id'], None)
                            self.order_filled.emit(dic_out)
                        else:
                            print(f"ATOM_WS [watch_chegyeol] not in uuids {order_info}")
            except asyncio.CancelledError:
                print("[WS] watch_chegyeol 종료")
                break  # 정상 종료로 처리
            except Exception as e:
                print(f"[WS] 에러: {e}")
                break

    async def rest_fallback(self):
        """30초마다 REST로 누락 확인"""
        while self.running:
            try:
                await asyncio.sleep(30)
                if self.dict_ord:
                    print(f"self.dict_ord : {self.dict_ord}")
                else:
                    print(f"self.dict_ord : ---------------")
                for order_id, symbol in list(self.dict_ord.items()):
                    order = await self.ex_ws.fetch_order(order_id, symbol)
                    # pprint(order)
                    if order['status'] in ('closed', 'canceled'):
                        pprint(order)
                        if order['status'] == 'closed':
                            dic_out = {order_id: {'state': '체결', 'amount': order['amount'], 'price': order['average']}}
                        elif order['status'] == 'canceled':
                            dic_out = {order_id: {'state': '취소', 'amount': order['amount'], 'price': 0}}
                        else:
                            dic_out = {order_id: {'state': '몰라', 'amount': order['amount'], 'price': 0}}
                        print(f"[REST] rest_fallback ✅ {order_id} {dic_out[order_id]['state']} 완료 {dic_out}")
                        self.dict_ord.pop(order_id, None)
                        self.order_filled.emit(dic_out)
                    else:
                        # print(f"[REST] rest_fallback ✅ {order_id} 업비트 미체결")
                        pass
            except asyncio.CancelledError:
                print("[REST] rest_fallback 종료")
                break
            except Exception as e:
                print(f"[REST] 에러: {e}")

    @pyqtSlot(dict)
    def check_dict_orders(self,dict_orders):
        self.dict_ord = dict_orders
        print(f'check_dict_orders {self.dict_ord}')

    def stop(self):
        self.running = False