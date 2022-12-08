import os
import sys
import random
#import glob
import imageio
import torch
import torch.nn as nn
from tqdm.notebook import tqdm
import torch.nn.functional as F
import torchvision.datasets as datasets
import torchvision.transforms as transforms
import numpy as np
import matplotlib.pyplot as plt
#import IPython.display as display
import librosa
import librosa.display
import pandas as pd
#from sklearn.model_selection import train_test_split
from torch.utils.data import Dataset, DataLoader
import cv2
import albumentations as A
from albumentations.pytorch.transforms import ToTensorV2
#from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
#import seaborn as sns

#torch.nn = torch neural network
#torchvision - customize dataset 만들기 위한 용도
#librosa - sound data 전처리용

class SoundModel:
    
    def __init__(self):
        self.WAVE_PATH = '/home/shooter/input.wav'
        self.device = torch.device('cpu')
        self.CFG = {
            'EPOCHS':50,
            'LEARNING_RATE':1e-3,
            'BATCH_SIZE':64,
            'SEED':2022
        }
        self.sound = "/home/shooter/gunsound.png"

    # 초기 시드를 미리 지정 (랜덤 시드 지정)
    # 같은 변수와 같은 하이퍼 파라미터를 썼을 때 동일한 결과를 유지시키기 위해
    def seed_everything(self, seed):
        random.seed(seed)
        os.environ['PYTHONHASHSEED'] = str(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)
        torch.cuda.manual_seed(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = True

    # 파일이름 모아놓은 csv파일이 있는데, 그곳에서 이름과 레이블을 따오기 위한 함수
    # infer = True면 테스트할 때 사용하는 것
    def get_data(self, df, infer=False):
        if infer:
            return df['png_name'].values
        return df['png_name'].values, df['gunsound'].values

    def setup(self):
        self.seed_everything(self.CFG['SEED']) # Seed 고정

        ## filename, gunsound 여부(총이면 1, 아니면 0)
        self.test_df = pd.DataFrame([[self.sound, 1]], columns=['png_name', 'gunsound'])
        
        self.test_img_paths, self.test_labels = self.get_data(self.test_df)
        
        # data augmentation 기법 중 하나
        self.test_transform = A.Compose([ToTensorV2(p=1.0)])
        
        # DataLoader : test dataset을 모델에 올리는 함수
        self.test_dataset = TestCustomDataset(self.test_img_paths, self.test_labels, self.test_transform)
        self.test_loader = DataLoader(self.test_dataset, batch_size=self.CFG['BATCH_SIZE'], shuffle=False)#, num_workers=0)
            
        self.checkpoint = torch.load('/home/shooter/PycharmProjects/receiver/sound/model/best_model_mel_1117_ELU_BN_Adagrad.pth', map_location=torch.device('cpu'))
        self.model = BaseModel().to(self.device)
        self.model.load_state_dict(self.checkpoint)
        
    # 모델 돌리는 함수
    # test_loader : test data를 로딩
    def predict(self, model, test_loader, device):
        # 모델 평가할거야
        model.eval()
        model_pred = []
        # 파라미터 업데이트 안할거야
        with torch.no_grad():
            for img, label in tqdm(iter(test_loader)):
                img, label = img.float().to(device), label.to(device)
                # print(img)
                pred_logit = model(img)
                pred_logit = pred_logit.argmax(dim=1, keepdim=True).squeeze(1)
                model_pred.extend(pred_logit.tolist())
                
        return model_pred
    
    def execute(self):
        preds = self.predict(self.model, self.test_loader, self.device)
        
        return preds[0]
    
    def processing(self):
        samples, sample_rate = librosa.load(self.WAVE_PATH)
        fig = plt.figure(figsize=[0.72,0.72])
        ax = fig.add_subplot(111)
        ax.axes.get_xaxis().set_visible(False)
        ax.axes.get_yaxis().set_visible(False)
        ax.set_frame_on(False)
        S = librosa.feature.melspectrogram(y=samples, sr=sample_rate)
        librosa.display.specshow(librosa.power_to_db(S, ref=np.max))
        plt.savefig('/home/shooter/gunsound.png', dpi=400, bbox_inches='tight',pad_inches=0)
        plt.close('all')
        

# 모델의 구조를 표현
class BaseModel(torch.nn.Module):
    def __init__(self):
        super(BaseModel, self).__init__()
        self.layer1 = torch.nn.Sequential(
            nn.Conv2d(3, 8, kernel_size=2, stride=1, padding=1), #cnn layer
            nn.BatchNorm2d(8),
            nn.ELU(), #activation function
            nn.MaxPool2d(kernel_size=2, stride=2)) #pooling layer
        
        self.layer2 = torch.nn.Sequential(
            nn.Conv2d(8, 16, kernel_size=2, stride=1, padding=1), #cnn layer
            nn.BatchNorm2d(16),
            nn.ELU(), #activation function
            nn.MaxPool2d(kernel_size=2, stride=2)) #pooling layer
        
        self.layer3 = torch.nn.Sequential(
            nn.Conv2d(16, 32, kernel_size=2, stride=1, padding=1), #cnn layer
            nn.BatchNorm2d(32),
            nn.ELU(), #activation function
            nn.MaxPool2d(kernel_size=2, stride=2)) #pooling layer
        
        self.layer4 = torch.nn.Sequential(
            nn.Conv2d(32, 16, kernel_size=2, stride=1, padding=1), #cnn layer
            nn.BatchNorm2d(16),
            nn.ELU(), #activation function
            nn.MaxPool2d(kernel_size=2, stride=2)) #pooling layer
        
        # fully connetec layer : 완전 연결된 계층
        # 앞의 layer들을 2개의 class로 분류할 수 있게 끔.
        self.fc_layer = nn.Sequential( 
            nn.Linear(3136, 2) #fully connected layer(ouput layer)
        )    
    
    # 계산함수
    def forward(self, x):
        
        x = self.layer1(x) #1층

        #print(1, x.shape)
        x = self.layer2(x) #2층
         
        #print(2, x.shape)
        x = self.layer3(x) #3층
        
        #print(3, x.shape)
        x = self.layer4(x) #4층
        
        #print(4, x.shape)
        x = torch.flatten(x, start_dim=1) # N차원 배열 -> 1차원 배열
        
        #print('flatten', x.shape)

        out = self.fc_layer(x)
        return out

class TestCustomDataset(Dataset):
    def __init__(self, img_paths, labels, transforms=None):
        self.img_paths = img_paths
        self.labels = labels
        self.transforms = transforms

    def __getitem__(self, index):
        img_path = self.img_paths[index]
        image = cv2.imread(img_path)
        #print(image.shape)
        #image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        if self.transforms is not None:
            image = self.transforms(image=image)['image']
        
        if self.labels is not None:
            label = self.labels[index]
            return image, label
        else:
            return image
    
    def __len__(self):
        return len(self.img_paths)
