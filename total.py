import asyncio
import json
from gpiozero import Motor, DistanceSensor
from gpiozero.pins.pigpio import PiGPIOFactory


HOST = '0.0.0.0'  # 모든 네트워크 인터페이스에서 연결 허용
PORT = 12346  # 포트 설정

# PiGPIOFactory를 사용하여 정확한 거리 측정을 할 수 있도록 설정
factory = PiGPIOFactory()

# 초음파 센서 설정 (트리거 핀: GPIO 23, 에코 핀: GPIO 24)
data_storage = DistanceSensor(echo=24, trigger=23, pin_factory=factory)

# 모터 설정
motor = Motor(forward=26, backward=19)
motor2 = Motor(forward=5, backward=6)

action = ""  # action 값 초기화
action_event = asyncio.Event() 
status = ""
status_event = asyncio.Event()

# 카운트 변수
count = 0
count1 = 0

# 거리 측정 함수 (비동기 처리 가능)
def measure_storage_distance():
    # 거리 계산 (sensor.distance는 미터 단위이므로 cm로 변환)
    distance_cm = data_storage.distance * 100
    return round(distance_cm, 2)

# 클라이언트 연결 처리 (비동기)
async def handle_client(reader, writer):
    global action, status  # 전역 변수 사용

    try:
        # 클라이언트에서 받은 데이터 처리
        await asyncio.gather(
            receive_data1(reader),  # action 받기
                 
            receive_data2(reader),    # 상태 받기
            motor_loop(writer)
        )
    except Exception as e:
        print(f"서버 오류 발생: {e}")
        await handle_client(reader, writer)
    except KeyboardInterrupt:
        print("사용자에 의해 서버가 종료되었습니다.")
# 비동기적으로 데이터를 읽을 때 Queue 사용
data_queue = asyncio.Queue()  # 데이터를 큐에 넣어서 관리

# 모터 루프 처리
async def motor_loop(writer):
    global action, count1,status

    while True:
        
        if action == "1":
            motor2.forward()
            storage_distance = measure_storage_distance()
            print(f"Storage Distance: {storage_distance} cm")

            # 두 번째 센서의 거리 기준으로 메시지 보내기
            if storage_distance < 20 and count1 == 0:
                message = "capture"
                writer.write(message.encode())
                await writer.drain()  # 메시지가 클라이언트로 전송될 때까지 대기
                count1 = count1 + 1
                print("사진 찍어 : " + message + " (전송 완료)")

            elif storage_distance >= 25:
                count1 = 0
        elif action == "2":
            motor2.stop()
            motor.stop()

        await asyncio.sleep(0.5)  # 0.5초 대기 (센서에 부하를 주지 않기 위해 조정)

# 클라이언트로부터 데이터 수신 (상태)
async def receive_data2(reader):
    global status
    while True:
        data = await data_queue.get()
        if data:
            message = data.decode()
            print(f"서버에서 받은 메시지: {message}")

            # 받은 메시지를 JSON 형식으로 파싱 (key-value 형태로 처리)
            try:
                received_data = json.loads(message)
                print(f"수신된 데이터 (key-value): {received_data}")
                status = received_data.get("status", status)  # 기본 status 값 유지
                status_event.set()
            except json.JSONDecodeError:
                print("받은 메시지가 JSON 형식이 아닙니다.")
                continue

            # 클라이언트로부터 받은 데이터에 따라 모터 제어
            if status == "1":  # 정상
                print("정상")
                print("정상")
                print("정상")
                print("정상")
                print("정상")
                motor.forward()
                await asyncio.sleep(9)
                motor.stop()  # 동작 후 멈춤

            elif status in {"2", "3", "4", "-1"}:  # 불량 조건
                print("불량 조건")
                print("불량 조건")
                print("불량 조건")
                print("불량 조건")
                print("불량 조건")
                motor.stop()
                await asyncio.sleep(0.01)
                motor.backward()
                await asyncio.sleep(9)
                motor.stop()  # 동작 후 멈춤

            else:
                print(f"잘못된 데이터: {status}")
        else:
            print("데이터가 없습니다.")

# 클라이언트로부터 데이터 수신 (action)
async def receive_data1(reader):
    global action
    while True:
        data = await reader.read(1024)  # 클라이언트로부터 데이터 읽기
        if data:
            message = data.decode()
            print(f"서버에서 받은 메시지: {message}")

            # 받은 메시지를 JSON 형식으로 파싱 (key-value 형태로 처리)
            try:
                received_data = json.loads(message)
                print(f"수신된 데이터 (key-value): {received_data}")
                action = received_data.get("action", action)  # 기본 action 값 유지
                action_event.set()
            except json.JSONDecodeError:
                print("받은 메시지가 JSON 형식이 아닙니다.")
            await data_queue.put(data)
        else:
            print("데이터가 없습니다.")
            break  # 연결이 끊어진 경우 루프 종료

# asyncio로 서버 실행
async def start_server():
    server = await asyncio.start_server(handle_client, HOST, PORT)
    addr = server.sockets[0].getsockname()
    print(f"서버가 {addr}에서 시작됨")

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    try:
        asyncio.run(start_server())
    except asyncio.CancelledError:
        print("서버가 종료되었습니다.")
