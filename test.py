from geometry_msgs.msg import Twist
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Union
from fastapi import FastAPI
import io
import json
from PIL import Image
from fastapi import File, FastAPI, Response, Form
import torch
import cv2
from fastapi import Request
from fastapi.responses import StreamingResponse
import json
import telegram
import webbrowser
from datetime import datetime
import rospy
import numpy as np
from cv_bridge import CvBridge, CvBridgeError
from sensor_msgs.msg import Image
import threading
from pymongo import MongoClient
from bson.json_util import dumps
import asyncio
import manual
from time import sleep
import sys
import select
import tty
import termios
import smach_ros
import os
from smach import State, StateMachine
import actionlib
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
import subprocess
import pymongo
import manual


app = FastAPI()  # Fastapi 실행 app 으로 변수 지정
templates = Jinja2Templates(directory="templates")  # 템플릿 디렉토리 지정
app.mount("/static", StaticFiles(directory="static"),
          name="static")  # 파일 저장공간 지정
# bridge = CvBridge() # ?
cv2_img = np.zeros((480, 640, 3), np.uint8)  # cv2_img 화면 크기?

twist = Twist()
pub = rospy.Publisher('cmd_vel', Twist, queue_size=10)
# MongoDB에 접속
client = MongoClient(
    "mongodb+srv://tesless:123@cluster0.xyeyaz7.mongodb.net/test")

# 데이터베이스 선택
db = client["slamdunk"]

# 컬렉션 선택
collection = db["status"]
collection2 = db["data"]

# 학습시킨 모델 불러오기 및 경로(yolov5, best.pt(학습데이터))
model = torch.hub.load('/home/tesless/slamdunk/yolov5/', 'custom', '/home/tesless/slamdunk/0403_custom/exp/weights/best.pt',
                       source='local', device='cpu', force_reload=True)


def isData():
    # 문자열을 읽을 수 있는 함수
    return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])


# original
# waypoints = [
#         ['one', (1.1, 0.5), (0.0, 0.0, 0.0, 1.0)],
#         ['two', (2.1, 4.43), (0.0, 0.0, -0.984047240305, 0.177907360295)],
#         ['three', (-1.3, 4.4), (0.0, 0.0, 0.0, 1.0)],
#         ['four', (-1.3, 0.1), (0.0, 0.0, 0.0, 1.0)]
#     ]

# second
waypoints = [
    ['one', (2.64499974251, 0.509999752045),
     (0.0, 0.0, 0.707106796641, 0.707106765732)],
    ['two', (2.47258925438, 4.40223407745),
     (0.0, 0.0, 0.999878011069, -0.0156193143396)],
    ['three', (-1.40137755871, 4.37288618088),
     (0.0, 0.0, -0.703452686599, 0.71074208945)],
    ['four', (-1.32800757885, 0.0733705535531),
     (0.0, 0.0, 0.0142813322057, 0.999898016575)]
]

roslaunch_process = None


async def send_msg(text):  # 혜진 텔레그램 정보
    # bot = telegram.Bot(token='6007372301:AAEZWipCHU_oaQV7a1Kh_0Ig-ZARlPHjHjs')
    # chat_id =6102779631
    # 창민 텔레그램 정보
    bot = telegram.Bot(token='6058917202:AAFcgLcUziqHIvwAQ0htUqdun-TrJMFHXpU')
    chat_id = 1794821594
    await bot.sendMessage(chat_id, text)

# def telegram_alarm():
#     pre_num_persons = 0 # 이전 비디오에서 발견된 사람 수를 저장할 변수 초기화
#     pre_num_smoke = 0   # 이전 비디오에서 발견된 연기 수를 저장할 변수 초기화
#     pre_num_fire = 0    # 이전 비디오에서 발견된 불 수를 저장할 변수 초기화
#     frame_num = 0       # 이전 비디오 개수 저장할 변수 초기화
#     print("SLAMDUNK 경비 순찰 시작합니다")
#     asyncio.run(send_msg(text="SLAMDUNK 경비 순찰 시작합니다\n"))

# def print_message(last_data[0]["num_persons"],num_smoke,num_fire):
#     global pre_num_fire, pre_num_persons,pre_num_smoke
#     message =""
#     # nonlocal pre_num_persons, pre_num_fire, pre_num_smoke
#     # if frame_num == 0: # 프레임 번호가 0일때만 "SLAMDUNK 경비 순찰 시작합니다" 메시지 전송
#     #     asyncio.run(send_msg(text="SLAMDUNK 경비 순찰 시작합니다"))
#     # if frame_num % 3000 == 0: # 대략적으로 5분에 한번 문자오는듯 ,현재 프레임 번호가 3000 배수일때 문자전송
#     #     message = "SLAMDUNK 경비 순찰 중 입니다.\n"
#     # 이전 프레임 ,객체의 개수가 바뀌어야만 문자알림 전송, 안그러면 많은 문자가 중복되어 쌓이게 됨,
#     # 같은 객체를 인식하고 반복적으로 문자를 보내는것을 막기위함
#     if num_persons != pre_num_persons or num_smoke != pre_num_smoke or num_fire != pre_num_fire:
#         if num_persons > 0 and num_persons != pre_num_persons == 0:
#             message += f"사람이 {num_persons}명 확인 되었습니다.\n"
#             # webbrowser.open("https://webqr.com/index.html")
#             pre_num_persons = num_persons
#             print(pre_num_persons)
#         if num_smoke > 0 and num_smoke != pre_num_smoke:
#             message += f"연기가 {num_smoke}곳 에서 발견 되었습니다.\n지금 바로 확인 바랍니다\n"
#             pre_num_smoke = num_smoke
#         if num_fire > 0 and num_fire != pre_num_fire:
#             message += f"화재가 {num_fire}곳 에서 발견 되었습니다.\n지금 바로 확인 바랍니다\n"
#             pre_num_fire = num_fire

#     if message:
#         asyncio.run(send_msg(text=message))


def gen_frames():
    def callback(msg):
        global cv2_img
        try:
            # msg = rospy.wait_for_message("/usb_cam/image_raw", Image)
            # cv2_img = bridge.imgmsg_to_cv2(msg, "bgr8")
            cv2_img1 = np.frombuffer(msg.data, dtype=np.uint8).reshape(
                msg.height, msg.width, -1)
            cv2_img = cv2.cvtColor(cv2_img1, cv2.COLOR_RGB2BGR)

        except CvBridgeError as e:
            print(e)
    image_topic = "/usb_cam/image_raw"

    threading.Thread(target=lambda: rospy.init_node(
        'image_listener', disable_signals=True)).start()

    rospy.Subscriber(image_topic, Image, callback)
    while True:
        global cv2_img
        global results
        frame = cv2_img
        # frame_num += 1
        if frame is None:
            break
        else:
            results = model(frame)
            annotated_frame = results.render()
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            image_detect(results, client, db, collection2)
            print_message()

            #     print_message(frame_num)
            # print(len([d for d in resulting_json if d["confidence"] >= 0.50 and d["name"] == "person"]))
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        # print(results.pandas().xyxy[0].to_json(orient="records"))
server_status = "Start"


def image_detect(results, client, db, collection2):
    global server_status
    if results and results.pandas().xyxy[0] is not None:

        resulting_json = json.loads(
            results.pandas().xyxy[0].to_json(orient="records"))
        num_persons = len([d for d in resulting_json if d["confidence"]
                          >= 0.50 and d["name"] == "person"])  # 사람은 기준점 75%를 넘어야 문자
        # 연기는 기준점없이 문자 알람
        num_smoke = len([d for d in resulting_json if d["name"] == "smoke"])
        # 불 도 기준점 없이 문자 알람
        num_fire = len([d for d in resulting_json if d["name"] == "fire"])
        mydict = {"TimeStamp": (datetime.now()),
                  "Persons": num_persons,
                  "Smoke": num_smoke,
                  "Fire": num_fire,
                  "Server_status": server_status
                  }
        collection2.insert_one(mydict)

    if server_status == "Start":
        print("SLAMDUNK 경비 순찰 서버 시작합니다")
        asyncio.run(send_msg("SLAMDUNK 경비 서버 시작합니다\n"))
        server_status = "On"


def print_message():
    last_data = list(collection2.find().limit(2).sort("_id", -1))

    num_persons = last_data[0]["Persons"]
    pre_num_persons = last_data[1]["Persons"]
    num_smoke = last_data[0]["Smoke"]
    pre_num_smoke = last_data[1]["Smoke"]
    fire = last_data[0]["Fire"]
    pre_fire = last_data[1]["Fire"]
    message = ''
    if num_persons != pre_num_persons or num_smoke != pre_num_smoke or fire != pre_fire:
        if num_persons > 0 and num_persons != pre_num_persons == 0:
            message += f"사람이 {num_persons}명 확인 되었습니다.\n"
            # webbrowser.open("https://webqr.com/index.html")
        if num_smoke > 0 and num_smoke != pre_num_smoke:
            message += f"연기가 {num_smoke}곳 에서 발견 되었습니다.\n지금 바로 확인 바랍니다\n"
        if fire > 0 and fire != pre_fire:
            message += f"화재가 {fire}곳 에서 발견 되었습니다.\n지금 바로 확인 바랍니다\n"

    if message:
        asyncio.run(send_msg(message))


@app.get('/', response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard2.html", {"request": request})


@app.post("/stop")
async def stop():
    twist.linear.x = 0.0
    twist.angular.z = 0.0
    pub.publish(twist)
    manual.db_save("stop")
    return print("stop")


@app.post("/up")
async def up():
    twist.linear.x = 0.2
    twist.angular.z = 0.0
    pub.publish(twist)
    return print("up")


@app.post("/down")
async def down():
    twist.linear.x = -0.2
    twist.angular.z = 0.0
    pub.publish(twist)
    return print("down")


@app.post("/left")
async def left():
    twist.linear.x = 0.0
    twist.angular.z = 1.0
    pub.publish(twist)
    return print("left")


@app.post("/right")
async def right():
    twist.linear.x = 0.0
    twist.angular.z = -1.0
    pub.publish(twist)
    return print("right")


@app.post("/one")
async def one():
    twist.linear.x = 0.0
    twist.angular.z = 0.0
    pub.publish(twist)
    manual.db_save("one")
    return print("one")


@app.post("/two")
async def two():
    twist.linear.x = 0.0
    twist.angular.z = 0.0
    pub.publish(twist)
    manual.db_save("two")
    return print("two")


@app.post("/three")
async def three():
    twist.linear.x = 0.0
    twist.angular.z = 0.0
    pub.publish(twist)
    manual.db_save("three")
    return print("three")


@app.post("/four")
async def four():
    twist.linear.x = 0.0
    twist.angular.z = 0.0
    pub.publish(twist)
    manual.db_save("four")
    return print("four")


@app.get("/api/list")
async def mongodb_data():
    data = list(collection.find().limit(10).sort("_id", -1))

    return {"TimeStamp": str(data[0]["TimeStamp"])[11:19], "linear_velocity": data[0]["linear_velocity"],
            "angular_velocity": data[0]["angular_velocity"], "motor_states_temperature": data[0]["motor_states_temperature"],
            "motor_states_rpm": data[0]["motor_states_rpm"]}

# 비디오 스트리밍 페이지?


@app.get('/video')
def video():
    return StreamingResponse(gen_frames(), media_type="multipart/x-mixed-replace; boundary=frame")


if __name__ == '__main__':
    FastAPI.run(app)
