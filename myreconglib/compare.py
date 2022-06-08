# -*- coding = utf-8 -*-
# @Time : 2022/6/7 22:21
# @Author : SBP
# @File : compare.py
# @Software : PyCharm

import torchvision.transforms as ttf
import torch
from PIL import Image
from facenet_pytorch import InceptionResnetV1

resnet = InceptionResnetV1(pretrained='vggface2').eval()

img2tensor = ttf.Compose([
    # ttf.Grayscale(),
    ttf.Resize((128, 128)),
    ttf.ToTensor(),
    ttf.Normalize(mean=[0.5], std=[0.5]),
])


def compare(img1, img2, thread=0.85):
    img1 = img1.resize((256, 256))
    img2 = img2.resize((256, 256))
    t1 = img2tensor(img1)
    t2 = img2tensor(img2)
    img_embedding1 = resnet(t1.unsqueeze(0))
    img_embedding2 = resnet(t2.unsqueeze(0))
    error = torch.norm(img_embedding1 - img_embedding2).item()
    if error < thread:
        return True, error
    else:
        return False, error
