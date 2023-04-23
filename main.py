import asyncio
import os
import cv2

from av import VideoFrame

from imageai.Detection import VideoObjectDetection

from aiortc import MediaStreamTrack, RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaPlayer, MediaRelay, MediaBlackhole

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from bson.json_util import dumps
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates
from pymongo import MongoClient
from src.schemas import Offer

# 현재 스크립트 파일의 디렉토리 경로를 변수 ROOT에 저장합니다.
ROOT = os.path.dirname(__file__)

#FastAPI 애플리케이션을 생성합니다.
app = FastAPI()
#"/static" 경로에 정적 파일을 제공하기 위해 static 디렉토리를 마운트합니다.
app.mount("/static", StaticFiles(directory="static"), name="static")
#Jinja2 템플릿 엔진을 사용하여 "templates" 디렉토리에서 템플릿 파일을 로드합니다.
templates = Jinja2Templates(directory="templates")

#OpenCV의 CascadeClassifier를 사용하여 얼굴, 눈, 미소를 감지하는 분류기를 초기화합니다.
faces = cv2.CascadeClassifier(cv2.data.haarcascades+"haarcascade_frontalface_default.xml")
eyes = cv2.CascadeClassifier(cv2.data.haarcascades+"haarcascade_eye.xml")
smiles = cv2.CascadeClassifier(cv2.data.haarcascades+"haarcascade_smile.xml")

# MongoDB에 접속
client = MongoClient("mongodb+srv://tesless:123@cluster0.xyeyaz7.mongodb.net/test")

# 데이터베이스 선택
db = client["test"]

# 컬렉션 선택
collection = db["dw"]

#MediaStreamTrack 클래스를 상속하여 비디오 스트림을 변환하는 커스텀 비디오 스트림 트랙 클래스를 정의합니다.
class VideoTransformTrack(MediaStreamTrack):
    """
    A video stream track that transforms frames from an another track.
    """

    kind = "video"

    def __init__(self, track, transform):
        super().__init__()
        self.track = track
        self.transform = transform

    async def recv(self):
        frame = await self.track.recv()

        if self.transform == "cartoon":
            img = frame.to_ndarray(format="bgr24")

            # prepare color
            img_color = cv2.pyrDown(cv2.pyrDown(img))
            for _ in range(6):
                img_color = cv2.bilateralFilter(img_color, 9, 9, 7)
            img_color = cv2.pyrUp(cv2.pyrUp(img_color))

            # prepare edges
            img_edges = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
            img_edges = cv2.adaptiveThreshold(
                cv2.medianBlur(img_edges, 7),
                255,
                cv2.ADAPTIVE_THRESH_MEAN_C,
                cv2.THRESH_BINARY,
                9,
                2,
            )
            img_edges = cv2.cvtColor(img_edges, cv2.COLOR_GRAY2RGB)

            # combine color and edges
            img = cv2.bitwise_and(img_color, img_edges)

            # rebuild a VideoFrame, preserving timing information
            new_frame = VideoFrame.from_ndarray(img, format="bgr24")
            new_frame.pts = frame.pts
            new_frame.time_base = frame.time_base
            return new_frame
        elif self.transform == "edges":
            # perform edge detection
            img = frame.to_ndarray(format="bgr24")
            img = cv2.cvtColor(cv2.Canny(img, 100, 200), cv2.COLOR_GRAY2BGR)

            # rebuild a VideoFrame, preserving timing information
            # 변환 작업을 수행한 후, VideoFrame.from_ndarray() 메서드를 사용하여 
            # 변환된 이미지를 비디오 프레임으로 재구성하고, 타이밍 정보를 보존합니다. 이후, 재구성된 프레임을 반환합니다.
            new_frame = VideoFrame.from_ndarray(img, format="bgr24")
            new_frame.pts = frame.pts
            new_frame.time_base = frame.time_base
            return new_frame
        elif self.transform == "rotate":
            # 이미지 회전
            img = frame.to_ndarray(format="bgr24") # 현재 프레임을 ndarray 형태로 변환하여 img 변수에 저장
            rows, cols, _ = img.shape # 이미지의 행, 열, 채널 정보를 가져와서 rows, cols 변수에 저장
            M = cv2.getRotationMatrix2D((cols / 2, rows / 2), frame.time * 45, 1) # 이미지의 중심을 중심으로 회전 변환 행렬 (Rotation Matrix) 생성
            img = cv2.warpAffine(img, M, (cols, rows)) # 이미지에 회전 변환 적용

            # VideoFrame 재구성, 타이밍 정보 보존
            new_frame = VideoFrame.from_ndarray(img, format="bgr24") # 회전된 이미지를 VideoFrame 형태로 변환하여 new_frame 변수에 저장
            new_frame.pts = frame.pts # 기존 프레임의 pts (presentation timestamp) 정보를 new_frame의 pts로 복사
            new_frame.time_base = frame.time_base # 기존 프레임의 time_base 정보를 new_frame의 time_base로 복사
            return new_frame # 회전된 이미지를 반환
        elif self.transform == "cv":
            # 얼굴 및 눈 검출
            img = frame.to_ndarray(format="bgr24") # 현재 프레임을 ndarray 형태로 변환하여 img 변수에 저장
            face = faces.detectMultiScale(img, 1.1, 19) # 얼굴 검출을 위해 detectMultiScale 함수를 사용하여 얼굴의 위치와 크기를 검출하여 face 변수에 저장
            for (x, y, w, h) in face: # 검출된 얼굴의 위치와 크기를 가져와서 반복문을 통해 사각형으로 표시
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

            eye = eyes.detectMultiScale(img, 1.1, 19) # 눈 검출을 위해 detectMultiScale 함수를 사용하여 눈의 위치와 크기를 검출하여 eye 변수에 저장
            for (x, y, w, h) in eye: # 검출된 눈의 위치와 크기를 가져와서 반복문을 통해 사각형으로 표시
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # VideoFrame 재구성, 타이밍 정보 보존
            new_frame = VideoFrame.from_ndarray(img, format="bgr24") # 검출된 얼굴과 눈이 표시된 이미지를 VideoFrame 형태로 변환하여 new_frame 변수에 저장
            new_frame.pts = frame.pts # 기존 프레임의 pts (presentation timestamp) 정보를 new_frame의 pts로 복사
            new_frame.time_base = frame.time_base # 기존 프레임의 time_base 정보를

            return new_frame
        else:
            return frame


def create_local_tracks(play_from=None):
    if play_from:
        player = MediaPlayer(play_from)
        return player.audio, player.video
    else:
        options = {"framerate": "30", "video_size": "640x480"}
        webcam = MediaPlayer("/dev/video1", format="v4l2", options=options)
            # audio, video = VideoTransformTrack(webcam.video, transform="cv")
            ## 비디오 트랙에 대한 변환을 수행하는 코드
        relay = MediaRelay()
        return None, relay.subscribe(webcam.video) ## 오디오는 None으로 반환하고, 비디오에 대해 미디어 릴레이를 구독하여 반환


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request}) ## 인덱스 페이지를 반환하는 코드


@app.get("/cv", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index_cv.html", {"request": request}) # # OpenCV를 사용하는 인덱스 페이지를 반환하는 코드

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard2.html",{"request": request}) # 대시보드 페이지를 반환하는 코드

@app.get("/api/list")
async def mongodb_data():
    data = list(collection.find().limit(1).sort("_id", -1))
    mongodb_data = dumps(data)
    return {'mongodb_data': mongodb_data}

@app.post("/offer")
async def offer(params: Offer):
    offer = RTCSessionDescription(sdp=params.sdp, type=params.type)

    pc = RTCPeerConnection()
    pcs.add(pc)
    recorder = MediaBlackhole()

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        print("Connection state is %s" % pc.connectionState)
        if pc.connectionState == "failed":
            await pc.close()
            pcs.discard(pc)

    # open media source
    audio, video = create_local_tracks() # 로컬 미디어 트랙 생성

    # handle offer
    await pc.setRemoteDescription(offer) # 수신된 offer로 원격 설명 설정
    await recorder.start() # 미디어 블랙홀로 녹음 시작

    # send answer
    answer = await pc.createAnswer() # answer 생성

    await pc.setRemoteDescription(offer) # 다시 원격 설명 설정
    for t in pc.getTransceivers():
        if t.kind == "audio" and audio: # 오디오 트랙이 있을 경우 추가
            pc.addTrack(audio)
        elif t.kind == "video" and video: # 비디오 트랙이 있을 경우 추가
            pc.addTrack(video)

    await pc.setLocalDescription(answer) # 로컬 설명 설정

    return {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type} # 생성된 로컬 설명을 반환하여 answer 전송


@app.post("/offer_cv")
async def offer(params: Offer):
    offer = RTCSessionDescription(sdp=params.sdp, type=params.type)

    pc = RTCPeerConnection()
    pcs.add(pc)
    recorder = MediaBlackhole()

    relay = MediaRelay()

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        print("Connection state is %s" % pc.connectionState) # 연결 상태가 변할 때마다 출력
        if pc.connectionState == "failed":
            await pc.close()
            pcs.discard(pc)

   
    @pc.on("track")
    def on_track(track):

        if track.kind == "video":
            pc.addTrack(
                VideoTransformTrack(relay.subscribe(track), transform=params.video_transform)
            ) # 비디오 트랙이 있을 경우, 변환된 트랙을 추가
            
        @track.on("ended")
        async def on_ended():
            await recorder.stop() # 트랙이 종료될 때 녹화 중지

    # handle offer
    await pc.setRemoteDescription(offer) # 수신된 offer로 원격 설명 설정
    await recorder.start() # 미디어 블랙홀로 녹화 시작

    # send answer
    answer = await pc.createAnswer() # answer 생성
    await pc.setRemoteDescription(offer) # 다시 원격 설명 설정
    await pc.setLocalDescription(answer) # 로컬 설명 설정

    return {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}  # 생성된 로컬 설명을 반환하여 answer 전송


pcs = set() # 피어 커넥션 저장을 위한 집합
args = ''


@app.on_event("shutdown")
async def on_shutdown():
    # close peer connections
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)
    pcs.clear() # 앱 종료 시 피어 커넥션을 닫고 집합을 초기화

