import time
import ntplib
import win32api
from dateutil import tz
import datetime

try:
    ntp_client = ntplib.NTPClient()
    while True:
        response = ntp_client.request('time.windows.com', version=3)
        dt = datetime.datetime.utcfromtimestamp(response.tx_time + response.delay)
        # dt = datetime.datetime.fromtimestamp(response.tx_time + response.delay, datetime.UTC)
        localtime = dt.astimezone(tz.tzlocal())
        offset = abs(response.offset)
        if offset >= 0.01:
            win32api.SetSystemTime(
                localtime.year,
                localtime.month,
                localtime.weekday(),
                localtime.day,
                localtime.hour,
                localtime.minute,
                localtime.second,
                localtime.microsecond // 1000
            )
            print(f'표준시간 동기화 중 ... 현재 표준시간과의 차이는 [{offset:.6f}]초입니다.')
        else:
            print(f'표준시간 동기화 완 ... 현재 표준시간과의 차이는 [{offset:.6f}]초입니다.')
            break
        time.sleep(1)
except:
    print('관리자 권한으로 실행하세요.')
    pass
