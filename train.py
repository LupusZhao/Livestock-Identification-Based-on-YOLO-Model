# coding:utf-8
from ultralytics import YOLO

model = YOLO("yolov8n.pt")
# Use the model
if __name__ == '__main__':
    results = model.train(data='data/data.yaml', epochs=100, batch=32)




