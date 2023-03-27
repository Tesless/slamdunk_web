from typing import Union

from fastapi import FastAPI
import io
import json
from PIL import Image
from fastapi import File,FastAPI, Response
import torch
import cv2
from fastapi import Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

cap = cv2.VideoCapture(0)

# Model
# model = torch.hub.load('ultralytics/yolov5', 'yolov5s', device='cpu', force_reload=True)
model = torch.hub.load('/home/khj/fastapi_test/slamdunk/yolov5/', 'custom','/home/khj/fastapi_test/slamdunk/0322_custom_weights/exp/weights/best.pt', source='local', device='cpu', force_reload=True)

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def video_show(request: Request):
    return templates.TemplateResponse("simple_gui.html",{"request": request})

def gen_frames():
    while True:
        _, frame = cap.read()
        if not _:
            break
        else:
            results = model(frame)
            annotated_frame = results.render()
            
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        print(results.pandas().xyxy[0].to_json(orient="records"))

@app.get('/video')
def video():
    return StreamingResponse(gen_frames(), media_type="multipart/x-mixed-replace; boundary=frame")
    # return StreamingResponse(video_streaming(), media_type="multipart/x-mixed-replace; boundary=frame")
    
# if __name__ == "__main__":
#     app.run(debug=True)


# def gen_frames():
    # while(True):
    #     ret, frame = cam.read()
    #     results= model(frame)
    #     annotation = results.render()
    #     print(results.pandas().xyxy[0].to_json(orient="records"))
    #     cv2.imshow("test", frame)
    #     cv2.waitKey(1)
        
# def read_root():
#     return {"Hello": "World"}


# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: Union[str, None] = None):
#     return {"item_id": item_id, "q": q}