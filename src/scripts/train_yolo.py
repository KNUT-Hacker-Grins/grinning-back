import torch, cv2
from ultralytics import YOLO

class YoloManager:
    def __init__(self, model_path):    
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model = YOLO(model_path).to(self.device)

    def train_yolo(self, config_path, epochs=100, imgsz=640, batch=16, project='src/classifier/results', name=None, lr0=0.01, optimizer='Auto', **kwargs):
        return self.model.train(
            data=config_path,
            epochs=epochs,
            imgsz=imgsz,
            batch=batch,
            project=project,
            name=name,
            lr0=lr0,
            optimizer=optimizer,
            device=self.device,
            **kwargs
        )