import asyncio 
import websockets
import json
import requests
# socket 정보
# SOCKET_URL = 'wss://mockapi.kiwoom.com:10000/api/dostk/websocket'  # 모의투자 접속 URL
SOCKET_URL = 'wss://api.kiwoom.com:10000/api/dostk/websocket'  # 접속 URL

api_key = "yldEAW1zfmbEnyK0X0M_v91AqSk-b3LO5dvALqSLfRo"
secret_key = "9BEshcgN9Rp9afF0KDmh3e8RRGxswjSkro0Df6O8cv8"

base_url = "https://api.kiwoom.com"
endpoint = 'oauth2/token'
url = f"{base_url}/{endpoint}"
headers = {'Content-Type': 'application/json;charset=UTF-8'}
params = {
    'grant_type': 'client_credentials',  # grant_type
    'appkey': api_key,  # 앱키
    'secretkey': secret_key,  # 시크릿키
}
response = requests.post(url, headers=headers, json=params)
data = response.json()
ACCESS_TOKEN = data["token"]  # 고객 Access Token

class WebSocketClient:
	def __init__(self, uri):
		self.uri = uri
		self.websocket = None
		self.connected = False
		self.keep_running = True

	# WebSocket 서버에 연결합니다.
	async def connect(self):
		try:
			self.websocket = await websockets.connect(self.uri)
			self.connected = True
			print("서버와 연결을 시도 중입니다.")

			# 로그인 패킷
			param = {
				'trnm': 'LOGIN',
				'token': ACCESS_TOKEN
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
		print(f'Message sent: {message}')

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

				if response.get('trnm') != 'PING':
					print(f'실시간 시세 서버 응답 수신: {response}')

			except websockets.ConnectionClosed:
				print('Connection closed by the server')
				self.connected = False
				await self.websocket.close()

	# WebSocket 실행
	async def run(self):
		await self.connect()
		await self.receive_messages()

	# WebSocket 연결 종료
	async def disconnect(self):
		self.keep_running = False
		if self.connected and self.websocket:
			await self.websocket.close()
			self.connected = False
			print('Disconnected from WebSocket server')

async def main():
	# WebSocketClient 전역 변수 선언
	websocket_client = WebSocketClient(SOCKET_URL)

	# WebSocket 클라이언트를 백그라운드에서 실행합니다.
	receive_task = asyncio.create_task(websocket_client.run())

	# 실시간 항목 등록
	await asyncio.sleep(1)
	await websocket_client.send_message({
		'trnm': 'CNSRREQ', # 서비스명
		'seq': '16', # 조건검색식 일련번호
		'search_type': '0', # 조회타입
		'stex_tp': 'K', # 거래소구분
		'cont_yn': 'N', # 연속조회여부
		'next_key': '', # 연속조회키
	})

	# 수신 작업이 종료될 때까지 대기
	await receive_task

# asyncio로 프로그램을 실행합니다.
if __name__ == '__main__':
	asyncio.run(main())