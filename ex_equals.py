import numpy as np
import time

# 1차원 배열 크기 설정
size = 10_000_000  # 천만 개

# 1. 파이썬 리스트 생성
python_list = list(range(size))

# 2. NumPy 배열 생성
numpy_array = np.arange(size)

print(f"배열 크기: {size:,}개 원소\n")

# ============================================
# 테스트 1: for문으로 순회하며 합계 계산
# ============================================

# 파이썬 리스트 순회
start = time.time()
sum_list = 0
for i in range(len(python_list)):
    sum_list += python_list[i]
time_list = time.time() - start

print(f"1. For문 순회 + 합계 계산")
print(f"   리스트: {time_list:.4f}초, 결과: {sum_list}")

# NumPy 배열 순회
start = time.time()
sum_numpy = 0
for i in range(len(numpy_array)):
    sum_numpy += numpy_array[i]
time_numpy = time.time() - start

print(f"   NumPy:  {time_numpy:.4f}초, 결과: {sum_numpy}")
print(f"   → 리스트가 {time_numpy/time_list:.2f}배 빠름\n")

# ============================================
# 테스트 2: NumPy 벡터화 연산
# ============================================

start = time.time()
sum_vectorized = np.sum(numpy_array)
time_vectorized = time.time() - start

print(f"2. NumPy 벡터화 연산 (np.sum)")
print(f"   시간: {time_vectorized:.6f}초, 결과: {sum_vectorized}")
print(f"   → 리스트 for문보다 {time_list/time_vectorized:.0f}배 빠름\n")

# ============================================
# 테스트 3: 각 원소에 2 곱하기
# ============================================

# 리스트 컴프리헨션
start = time.time()
doubled_list = [x * 2 for x in python_list]
time_list_double = time.time() - start

print(f"3. 각 원소에 2 곱하기")
print(f"   리스트: {time_list_double:.4f}초")

# NumPy 벡터화 연산
start = time.time()
doubled_numpy = numpy_array * 2
time_numpy_double = time.time() - start

print(f"   NumPy:  {time_numpy_double:.6f}초")
print(f"   → NumPy가 {time_list_double/time_numpy_double:.0f}배 빠름\n")

# ============================================
# 테스트 4: 조건 연산 (5,000,000보다 큰 값 개수)
# ============================================

# 리스트로 조건 검사
start = time.time()
count_list = sum(1 for x in python_list if x > 5_000_000)
time_list_cond = time.time() - start

print(f"4. 조건 연산 (5,000,000보다 큰 값 개수)")
print(f"   리스트: {time_list_cond:.4f}초, 개수: {count_list}")

# NumPy 벡터화 조건 연산
start = time.time()
count_numpy = np.sum(numpy_array > 5_000_000)
time_numpy_cond = time.time() - start

print(f"   NumPy:  {time_numpy_cond:.6f}초, 개수: {count_numpy}")
print(f"   → NumPy가 {time_list_cond/time_numpy_cond:.0f}배 빠름\n")

# ============================================
# 테스트 5: 평균 계산
# ============================================

# 리스트 평균
start = time.time()
avg_list = sum(python_list) / len(python_list)
time_list_avg = time.time() - start

print(f"5. 평균 계산")
print(f"   리스트: {time_list_avg:.4f}초, 평균: {avg_list:.2f}")

# NumPy 평균
start = time.time()
avg_numpy = np.mean(numpy_array)
time_numpy_avg = time.time() - start

print(f"   NumPy:  {time_numpy_avg:.6f}초, 평균: {avg_numpy:.2f}")
print(f"   → NumPy가 {time_list_avg/time_numpy_avg:.0f}배 빠름\n")

# ============================================
# 결론
# ============================================

print("=" * 60)
print("결론 (1차원 배열):")
print("- For문 인덱싱 순회: 리스트가 NumPy보다 2~3배 빠름")
print("- 벡터화 연산/집계: NumPy가 수십~수백 배 빠름")
print("- 1차원도 2차원과 동일한 패턴")
print("- NumPy 사용 시 반드시 벡터화 연산 활용!")
print("=" * 60)