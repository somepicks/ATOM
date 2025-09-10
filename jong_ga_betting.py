import json
import pickle
import asyncio
import datetime
import requests
import pandas as pd
import websockets
pd.set_option('display.max_columns',None) #모든 열을 보고자 할 때
pd.set_option('display.max_colwidth', None)
pd.set_option('display.width',1500)
# pd.set_option('display.max_rows', None)  # 출력 옵션 설정: 모든 열의 데이터 유형을 출력
pd.set_option("display.unicode.east_asian_width", True)
pd.set_option('mode.chained_assignment',  None)
class kiwoom_finance:
    def __init__(self, api_key: str, api_secret: str, market: str,
                 exchange: str = "서울", mock: bool = False):
        self.mock = mock
        self.market = market
        self.set_base_url(market, mock) # self.base_url 설정
        self.api_key = api_key
        self.api_secret = api_secret
        self.exchange = exchange
        self.access_token = None
        self.fetch_access = True
        if self.check_access_token(): #기존에 생성한 토큰이 있는지 확인
            print('기존 토큰 로드')
            self.load_access_token()
        else:
            print('신규 토큰 발행')
            self.issue_access_token() #없을 경우 토큰 발행

    def set_base_url(self, market: str = '주식', mock: bool = True):
        if mock:
            self.base_url = "https://mockapi.kiwoom.com"
        else:
            self.base_url = "https://api.kiwoom.com"

    def issue_access_token(self):
        if self.api_key == 'test':
            pass
        else:
            endpoint = 'oauth2/token'
            url = f"{self.base_url}/{endpoint}"
            headers = {'Content-Type': 'application/json;charset=UTF-8'}
            params = {
                'grant_type': 'client_credentials',  # grant_type
                'appkey': self.api_key,  # 앱키
                'secretkey': self.api_secret,  # 시크릿키
            }
            response = requests.post(url, headers=headers, json=params)
            data = response.json()
            try:
                self.access_token = data["token"]
            except Exception as e:
                print(f"API 오류 발생: {e}")
                print(f"{data= }")
                quit()
            data['api'] = self.api_key
            if self.mock:
                file_name = "token_mock.dat"
            else:
                file_name = "token.dat"
            with open(file_name, "wb") as f:
                pickle.dump(data, f)

    def check_access_token(self):
        if self.mock:
            file_name = "token_mock.dat"
        else:
            file_name = "token.dat"
        try:
            f = open(file_name, "rb")
            data = pickle.load(f)
            f.close()
            expire_epoch = data['expires_dt']
            if datetime.datetime.strptime(expire_epoch,"%Y%m%d%H%M%S")-datetime.datetime.now() < datetime.timedelta(hours=12):
                status = False #기존 토큰 제거
            elif not data['api'] == self.api_key:
                status = False
            else:
                status = True
            return status
        except IOError:
            return False

    def load_access_token(self):
        if self.mock:
            file_name = "token_mock.dat"
        else:
            file_name = "token.dat"
        with open(file_name, "rb") as f:
            data = pickle.load(f)
            self.access_token = data["token"]

    def fetch_asset(self) -> dict:
        endpoint = '/api/dostk/acnt'
        url = f"{self.base_url}{endpoint}"
        headers = {
            'Content-Type': 'application/json;charset=UTF-8',  # 컨텐츠타입
            'authorization': f'Bearer {self.access_token}',  # 접근토큰
            'cont-yn': "N",  # 연속조회여부
            'next-key': "",  # 연속조회키
            'api-id': 'ka01690',  # TR명
        }
        params = {
            'qry_dt': datetime.datetime.now().strftime("%Y%m%d"),  # 조회일자
        }
        res = requests.post(url, headers=headers, json=params)
        data = res.json()

        dict_data = {}
        if data['return_msg'] == "정상적으로 처리되었습니다":
            dict_data['추정자산'] = int(data['day_stk_asst'])
            dict_data['예수금'] = int(data['dbst_bal'])
            dict_data['총 매입가'] = int(data['tot_buy_amt'])
            dict_data['총 평가금액'] = int(data['tot_evlt_amt'])
            dict_data['총 평가손익'] = int(data['tot_evltv_prft'])
            dict_data['수익률'] = float(data['tot_prft_rt'])
        return dict_data

class WebSocketClient:
    def __init__(self, ACCESS_TOKEN):
        self.ACCESS_TOKEN = ACCESS_TOKEN
        self.websocket = None
        self.connected = False
        self.keep_running = True
        self.search_chennel = None
        self.df = pd.DataFrame()
    # WebSocket 서버에 연결합니다.
    async def connect(self):
        try:
            url = 'wss://api.kiwoom.com:10000/api/dostk/websocket'  # 접속 URL
            self.websocket = await websockets.connect(url, ping_interval=None)
            self.connected = True
            print("서버와 연결을 시도 중입니다.")

            # 로그인 패킷
            param = {
                'trnm': 'LOGIN',
                'token': self.ACCESS_TOKEN
            }

            print('실시간 시세 서버로 로그인 패킷을 전송합니다.')
            # 웹소켓 연결 시 로그인 정보 전달
            await self.send_message(message=param)

        except Exception as e:
            print(f'Connection error: {e}')
            self.connected = False

    # 서버에 메시지를 보냅니다. 연결이 없다면 자동으로 연결합니다.
    async def send_message(self, message):
        if not self.connected:
            await self.connect()  # 연결이 끊어졌다면 재연결
        if self.connected:
            # message가 문자열이 아니면 JSON으로 직렬화
            if not isinstance(message, str):
                message = json.dumps(message)
        await self.websocket.send(message)
        print(f'async def send_message: {message}')

    # 서버에서 오는 메시지를 수신하여 출력합니다.
    async def receive_messages(self):
        while self.keep_running:
            try:
                # 서버로부터 수신한 메시지를 JSON 형식으로 파싱
                response = json.loads(await self.websocket.recv())
                # 메시지 유형이 LOGIN일 경우 로그인 시도 결과 체크
                if response.get('trnm') == 'LOGIN':
                    if response.get('return_code') != 0:
                        print('로그인 실패하였습니다. : ', response.get('return_msg'))
                        await self.disconnect()
                    else:
                        print('로그인 성공하였습니다.')
                        print('조건검색 목록조회 패킷을 전송합니다.')
                        # 로그인 패킷
                        param = {
                            'trnm': 'CNSRLST'
                        }
                        await self.send_message(message=param)
                # 메시지 유형이 PING일 경우 수신값 그대로 송신
                elif response.get('trnm') == 'PING':
                    await self.send_message(response)
                elif response.get('trnm') == 'CNSRLST': #전체 조건 검색 시 불러오기
                    for i, li in enumerate(response['data']):
                            if title in li:
                                num_str = li[0]
                                print(f"{num_str= }")
                                self.search_chennel = num_str
                elif response.get('trnm') == 'CNSRREQ':
                    self.df = pd.DataFrame(response['data'])
                    self.df.rename(
                        columns={'9001': '종목코드', '302': '종목명', '10': '현재가', '25': '전일대비기호',
                                 '11': '전일대비', '12': '등락율', '13': '누적거래량', '16': '시가', '17': '고가', '18': '저가'}, inplace=True)
                    for col in self.df.columns:
                        try:
                            self.df[col] = pd.to_numeric(self.df[col], errors='raise')
                        except ValueError:
                            pass
                    print(self.df)
                if response.get('trnm') != 'PING':
                    print(f'실시간 시세 서버 응답 수신: {response}')

            except websockets.ConnectionClosed:
                print('Connection closed by the server')
                self.connected = False
                await self.websocket.close()

    # WebSocket 실행
    async def run(self):
        print('async def run(self):')
        # await self.connect()
        await self.receive_messages()

    # WebSocket 연결 종료
    async def disconnect(self):
        self.keep_running = False
        if self.connected and self.websocket:
            await self.websocket.close()
            self.connected = False
            print('Disconnected from WebSocket server')

    # async def fetch_tickers(self,search):
    #     # message ={
    #     #             'trnm': 'CNSRLST',  # TR명
    #     #         }
    #     # if not self.connected:
    #     #     await self.connect()  # 연결이 끊어졌다면 재연결
    #     # if self.connected:
    #     #     # message가 문자열이 아니면 JSON으로 직렬화
    #     #     if not isinstance(message, str):
    #     #         message = json.dumps(message)
    #     # await self.websocket.send(message)
    #     # while True:
    #     #     response = json.loads(await self.websocket.recv())
    #     #     print(f'조건검색 식 서버 응답 수신: {response}')
    #     #     if response['trnm'] == 'CNSRLST':
    #     #         print(f"{response['data']= }")
    #     #         print(len(response['data']))
    #     #         for i,li in enumerate(response['data']):
    #     #             if title in li:
    #     #                 num_str = li[0]
    #     #                 print(f"{num_str= }")
    #     #                 break
    #     #             print(i)
    #     message ={
    #         'trnm': 'CNSRREQ',  # 서비스명
    #         'seq': "16",  # 조건검색식 일련번호
    #         'search_type': '0',  # 조회타입
    #         'stex_tp': 'K',  # 거래소구분
    #         'cont_yn': 'N',  # 연속조회여부
    #         'next_key': '',  # 연속조회키
    #             }
        # message가 문자열이 아니면 JSON으로 직렬화
        # if not isinstance(message, str):
        #     message = json.dumps(message)
        # await self.websocket.send(message)
        # while True:
        #     response = json.loads(await self.websocket.recv())
        #     print(f'조건검색 리스트 서버 응답 수신: {response}')
        #     if response['trnm'] == 'CNSRREQ ':
        #         print(f"{response= }")
        #         break
        # return response


if __name__ == "__main__":
    mock = False
    if mock:
        api_key = "zSQr2jdgor8SPPF5DigW5Vq64xKRQcbNQY_2O4muS2o"
        secret_key = "TusEUmZ3pL6QtDIjHy3owfdsxfw8gVjJVwt1I4IeomQ"
        SOCKET_domain = 'wss://mockapi.kiwoom.com:10000'  # 모의투자 접속 URL
        SOCKET_URL = "/api/dostk/websocket"
    else:
        api_key = "P0FfJ6jrHYYv5rOroape_sHsMatIGQhdACJfA3K2TkM"
        secret_key = "TusEUmZ3pL6QtDIjHy3owfdsxfw8gVjJVwt1I4IeomQ"
        api_key = "yldEAW1zfmbEnyK0X0M_v91AqSk-b3LO5dvALqSLfRo"
        secret_key = "9BEshcgN9Rp9afF0KDmh3e8RRGxswjSkro0Df6O8cv8"
    title = '종가'
    ex = kiwoom_finance(api_key=api_key,api_secret=secret_key,market='주식',mock=mock)
    dict_res = ex.fetch_asset()

    websocket_client = WebSocketClient(ex.access_token)
    async def main():
        await websocket_client.connect()
        # await trade_stocks(access_token)


        receive_task = asyncio.create_task(websocket_client.run())


        await asyncio.sleep(1)
        if not websocket_client.search_chennel == None: #search_chennel 이 None이 아니면 메세지 전송
            await websocket_client.send_message({
                'trnm': 'CNSRREQ',  # 서비스명
                'seq': websocket_client.search_chennel,  # 조건검색식 일련번호
                'search_type': '0',  # 조회타입
                'stex_tp': 'K',  # 거래소구분
                'cont_yn': 'N',  # 연속조회여부
                'next_key': '',  # 연속조회키
            })
        print('=====')
        print(websocket_client.df)
        if not websocket_client.df.empty :
            print('*****')

            print(websocket_client.df)
        await receive_task

    # asyncio로 프로그램을 실행합니다.
    asyncio.run(main())