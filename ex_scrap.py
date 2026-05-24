import datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
data = requests.get('https://finance.naver.com/world/sise.naver?symbol=NII@NI225', headers=headers)

soup = BeautifulSoup(data.text, 'html.parser')

니케이 = soup.select_one("#content > div.rate_info > div.today > p.no_today > em")
니케이 = 니케이.strip
print(f"{니케이.text= }")


data = requests.get('https://finance.naver.com/world/sise.naver?symbol=HSI@HSI', headers=headers)

soup = BeautifulSoup(data.text, 'html.parser')

항셍 = soup.select_one("#content > div.rate_info > div.today > p.no_today > em")
항셍 = 항셍.strip
print(f"{항셍.text= }")



data = requests.get('https://finance.naver.com/world/sise.naver?symbol=NAS@IXIC', headers=headers)

soup = BeautifulSoup(data.text, 'html.parser')

나스닥 = soup.select_one("#content > div.rate_info > div.today > p.no_today > em")
나스닥 = 나스닥.strip
print(f"{나스닥.text= }")

data = requests.get('https://finance.naver.com/world/sise.naver?symbol=SPI@SPX', headers=headers)

soup = BeautifulSoup(data.text, 'html.parser')

SNP = soup.select_one("#content > div.rate_info > div.today > p.no_today > em")
SNP = SNP.strip
print(f"{SNP.text= }")


df = pd.DataFrame()
today =datetime.datetime.now()
df.loc[today,'니케이'] = 니케이.text
df.loc[today,'항셍'] = 항셍.text
df.loc[today,'나스닥'] = 나스닥.text
df.loc[today,'S%P'] = SNP.text

print(df)

