import os
import sys
import random
import imageio
import torch
import torch.nn as nn
from tqdm.notebook import tqdm
import torch.nn.functional as F
import torchaudio
import torchaudio.transforms as AT
import torchvision.datasets as datasets
import torchvision.transforms as transforms
import numpy as np
import matplotlib.pyplot as plt
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
#torchvision - for customized dataset creating
#librosa - for sound data pre-processing

# get curruent directory path
dirname = os.getcwd()
class SoundModel:
    
    def __init__(self):
        self.WAVE_PATH = dirname+'/input.wav'
        self.device = torch.device('cpu')
        self.CFG = {
            'EPOCHS':50,
            'LEARNING_RATE':1e-3,
            'BATCH_SIZE':64,
            'SEED':2022
        }
        self.sound = dirname+"/gunsound.png"

        self.spectrogram = nn.Sequential(
            AT.Spectrogram(n_fft=1024,
                           win_length=1024,
                           hop_length=512),
            AT.AmplitudeToDB()
        )
        
    # Fixed random seed to keep the same result when using the same variable and the same hyperparameter.
    def seed_everything(self, seed):
        random.seed(seed)
        os.environ['PYTHONHASHSEED'] = str(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)
        torch.cuda.manual_seed(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = True

    # Function to get the name and label from CSV file
    # If infer = True, it is used in the model 
    def get_data(self, df, infer=False):
        if infer:
            return df['png_name'].values
        return df['png_name'].values, df['gunsound'].values

    def setup(self):
        self.seed_everything(self.CFG['SEED']) # Seed Fix

        # filename and whether it is gunsound or not (1 if gun, 0 otherwise)
        self.test_df = pd.DataFrame([[self.sound, 1]], columns=['png_name', 'gunsound'])
        
        self.test_img_paths, self.test_labels = self.get_data(self.test_df)
        
        # data augmentation
        self.test_transform = A.Compose([ToTensorV2(p=1.0)])
        
        # A function to load the test dataset into the model
        self.test_dataset = TestCustomDataset(self.test_img_paths, self.test_labels, self.test_transform)
        self.test_loader = DataLoader(self.test_dataset, batch_size=self.CFG['BATCH_SIZE'], shuffle=False)#, num_workers=0)
            
        self.checkpoint = torch.load(dirname+'/SharpShooter-pi2/sound/model/best_model_1209_Powerspectro.pth', map_location=torch.device('cpu'))
        self.model = BaseModel().to(self.device)
        self.model.load_state_dict(self.checkpoint)
        
    # test_loader : Laod the test data
    def predict(self, model, test_loader, device):
        # evaluate the model
        model.eval()
        model_pred = []
        # no parameter update
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
        # samples, sample_rate = librosa.load(self.WAVE_PATH)
        samples, sample_rate = torchaudio.load(self.WAVE_PATH)
        fig = plt.figure(figsize=[0.72,0.72])
        ax = fig.add_subplot(111)
        ax.axes.get_xaxis().set_visible(False)
        ax.axes.get_yaxis().set_visible(False)
        ax.set_frame_on(False)
        # S = librosa.feature.melspectrogram(y=samples, sr=sample_rate)
        # librosa.display.specshow(librosa.power_to_db(S, ref=np.max))
        spec = self.spectrogram(samples)
        ax.pcolor(spec[0])
        plt.savefig(dirname+'/gunsound.png', dpi=400, bbox_inches='tight',pad_inches=0)
        plt.close('all')
        

# Model architecture 
class BaseModel(torch.nn.Module):
    def __init__(self):
        super(BaseModel, self).__init__()
        # layer 1
        self.layer1 = torch.nn.Sequential(
            nn.Conv2d(3, 8, kernel_size=2, stride=1, padding=1), #cnn layer
            nn.BatchNorm2d(8),
            nn.ELU(), #activation function
            nn.MaxPool2d(kernel_size=2, stride=2)) #pooling layer
        # layer 2
        self.layer2 = torch.nn.Sequential(
            nn.Conv2d(8, 16, kernel_size=2, stride=1, padding=1), #cnn layer
            nn.BatchNorm2d(16),
            nn.ELU(), #activation function
            nn.MaxPool2d(kernel_size=2, stride=2)) #pooling layer
        # layer 3
        self.layer3 = torch.nn.Sequential(
            nn.Conv2d(16, 32, kernel_size=2, stride=1, padding=1), #cnn layer
            nn.BatchNorm2d(32),
            nn.ELU(), #activation function
            nn.MaxPool2d(kernel_size=2, stride=2)) #pooling layer
        
        # layer 4
        self.layer4 = torch.nn.Sequential(
            nn.Conv2d(32, 16, kernel_size=2, stride=1, padding=1), #cnn layer
            nn.BatchNorm2d(16),
            nn.ELU(), #activation function
            nn.MaxPool2d(kernel_size=2, stride=2)) #pooling layer
        
        # fully connetec layer
        self.fc_layer = nn.Sequential( 
            nn.Linear(3136, 2) #fully connected layer(ouput layer)
        )    
    
    # Calculation function
    def forward(self, x):
        
        x = self.layer1(x) # layer 1

        #print(1, x.shape)
        x = self.layer2(x) # layer 2
         
        #print(2, x.shape)
        x = self.layer3(x) # layer 3
        
        #print(3, x.shape)
        x = self.layer4(x) # layer 4
        
        #print(4, x.shape)
        x = torch.flatten(x, start_dim=1) # N-demmentional array to one dementional array
        
        #print('flatten', x.shape)

        out = self.fc_layer(x)
        return out
    
# Custom dataset
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
