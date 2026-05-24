import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
from datetime import datetime


def get_hangseng_from_naver():
    """
    네이버 증권에서 항셍지수 정보를 크롤링하는 함수
    """
    # 네이버 증권 항셍지수 페이지 URL
    url = "https://finance.naver.com/world/sise.naver?symbol=HSI@HSI"

    # User-Agent 헤더 추가 (차단 방지)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        # HTTP 요청
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # HTTP 에러 체크

        # HTML 파싱
        soup = BeautifulSoup(response.text, 'html.parser')

        # 현재가 정보 추출
        price_element = soup.select_one('.rate_info .blind')
        if price_element:
            current_price = price_element.text.strip()
        else:
            current_price = "정보 없음"

        # 전일대비 정보 추출
        change_element = soup.select_one('.rate_info .change')
        if change_element:
            change_info = change_element.get_text(strip=True)
        else:
            change_info = "정보 없음"

        # 등락률 정보 추출
        rate_element = soup.select_one('.rate_info .rate')
        if rate_element:
            change_rate = rate_element.get_text(strip=True)
        else:
            change_rate = "정보 없음"

        # 결과 반환
        result = {
            '지수명': '항셍지수 (HSI)',
            '현재가': current_price,
            '전일대비': change_info,
            '등락률': change_rate,
            '조회시간': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        return result

    except requests.RequestException as e:
        print(f"HTTP 요청 오류: {e}")
        return None
    except Exception as e:
        print(f"크롤링 오류: {e}")
        return None


def get_hangseng_alternative():
    """
    네이버 금융 메인에서 항셍지수를 가져오는 대안 방법
    """
    url = "https://finance.naver.com/world/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # 해외지수 테이블에서 항셍지수 찾기
        world_indices = soup.select('.tb_type1 tr')

        for row in world_indices:
            index_name = row.select_one('th a')
            if index_name and '항셍' in index_name.text:
                cells = row.select('td')
                if len(cells) >= 3:
                    current_price = cells[0].text.strip()
                    change = cells[1].text.strip()
                    change_rate = cells[2].text.strip()

                    return {
                        '지수명': '항셍지수',
                        '현재가': current_price,
                        '전일대비': change,
                        '등락률': change_rate,
                        '조회시간': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }

        return None

    except Exception as e:
        print(f"대안 크롤링 오류: {e}")
        return None


def continuous_monitoring(interval_minutes=5, duration_hours=1):
    """
    지속적으로 항셍지수를 모니터링하는 함수

    Args:
        interval_minutes: 조회 간격 (분)
        duration_hours: 모니터링 지속 시간 (시간)
    """
    data_list = []
    end_time = time.time() + (duration_hours * 3600)

    print(f"항셍지수 모니터링 시작 - {interval_minutes}분 간격, {duration_hours}시간 동안")

    while time.time() < end_time:
        # 데이터 수집
        data = get_hangseng_from_naver()
        if data:
            data_list.append(data)
            print(f"[{data['조회시간']}] {data['지수명']}: {data['현재가']} ({data['전일대비']}, {data['등락률']})")
        else:
            # 메인 방법 실패시 대안 시도
            data = get_hangseng_alternative()
            if data:
                data_list.append(data)
                print(f"[{data['조회시간']}] {data['지수명']}: {data['현재가']} ({data['전일대비']}, {data['등락률']})")
            else:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 데이터 수집 실패")

        # 대기
        time.sleep(interval_minutes * 60)

    # DataFrame으로 변환하여 반환
    if data_list:
        df = pd.DataFrame(data_list)
        return df
    else:
        return None


# 사용 예시
if __name__ == "__main__":
    print("=== 네이버 항셍지수 크롤링 테스트 ===")

    # 단일 조회
    result = get_hangseng_from_naver()
    if result:
        print("\n현재 항셍지수 정보:")
        for key, value in result.items():
            print(f"{key}: {value}")
    else:
        print("메인 방법 실패, 대안 시도...")
        result = get_hangseng_alternative()
        if result:
            print("\n현재 항셍지수 정보:")
            for key, value in result.items():
                print(f"{key}: {value}")
        else:
            print("데이터 수집에 실패했습니다.")

    # 지속적 모니터링 (주석 해제하여 사용)
    # df = continuous_monitoring(interval_minutes=1, duration_hours=0.1)  # 6분간 1분 간격
    # if df is not None:
    #     print("\n수집된 데이터:")
    #     print(df)
    #     df.to_csv('hangseng_data.csv', index=False, encoding='utf-8-sig')
    #     print("데이터가 hangseng_data.csv 파일로 저장되었습니다.")