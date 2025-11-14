from datetime import datetime, timedelta

# 1. timedelta 객체인 경우
diff = datetime(2024, 1, 3) - datetime(2024, 1, 1)
print(diff)        # 출력: 2 days, 0:00:00
print(diff.days)   # 출력: 2

# 2. 데이터프레임 열에 적용
df['날짜차이_일수'] = (df['종료일'] - df['시작일']).dt.days

# 3. 단일 계산
date1 = datetime(2024, 1, 5)
date2 = datetime(2024, 1, 3)
days_difference = (date1 - date2).days
print(f"{days_difference}일")  # 출력: 2일

# 4. 문자열로 포맷팅
diff = datetime.now() - datetime(2024, 1, 1)
print(f"{diff.days}일")