import subprocess

def sync_time():
    try:
        # w32tm 명령을 사용하여 시간을 동기화합니다.
        subprocess.run(["w32tm", "/resync"], check=True)
        print("시간이 성공적으로 동기화되었습니다.")
    except subprocess.CalledProcessError as e:
        print(f"시간 동기화 중 오류 발생: {e}")
sync_time()