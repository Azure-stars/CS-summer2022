import torch
import torch.nn as nn
from typing import List


class MultiClassificationModel(nn.Module):
    def __init__(self, num_categories=3):
        """
        We use a typical VGG16 network architecture, which could serve as a backbone for extracting global features
        from the input image.
        Then we declare `three` classification head, each is a binary classifier that output True or False
        with the input of features extracted by VGG19.
        """
        super(MultiClassificationModel, self).__init__()
        self.backbone = VGG16()
        # 选取VGG16作为神经网络骨架
        self.cls_head = nn.ModuleList()
        self.flatten = nn.Flatten()
        # self.flatten是张量展平函数
        for i in range(num_categories):
            self.cls_head.append(ClassificationHead())

    def forward(self, train_input):
        features = self.backbone(train_input)
        features = self.flatten(features)
        return torch.stack([head(features) for head in self.cls_head], dim=1)  # From three (8, 2) to (8, 3, 2)
        # torch.stack函数堆叠张量增加一维

def make_layers(cfg: List, batch_norm=True):
    layers = []
    in_channels = 3
    for v in cfg:
        if v == 'M':
            layers += [nn.MaxPool2d(kernel_size=2, stride=2)]
            # 最大池，窗口2*2，步长为2
        else:
            conv2d = nn.Conv2d(in_channels, v, kernel_size=3, padding=1)
            # 卷积核
            if batch_norm:
                layers += [conv2d, nn.BatchNorm2d(v), nn.ReLU(inplace=True)]
            # nn.BatchNorm2d:批量标准化处理
            # nn.ReLU:取0和x的最大值
            else:
                layers += [conv2d, nn.ReLU(inplace=True)]
            in_channels = v
    return nn.Sequential(*layers)
    # nn.Sequential是一个有序的容器，神经网络模块将按照在传入构造器的顺序依次被添加到计算图中进行计算。

class VGG16(nn.Module):
    """
    Typical VGG16 Deep convolutional model.
    Copied from https://github.com/aaron-xichen/pytorch-playground/blob/master/imagenet/vgg.py.
    """
    def __init__(self):
        super(VGG16, self).__init__()
        self.model = make_layers([64, 64, 'M',
                                  128, 128, 'M',
                                  256, 256, 256, 'M',
                                  512, 512, 512, 'M',
                                  512, 512, 512, 'M'])

    def forward(self, data):
        return self.model(data)


class ClassificationHead(nn.Module):
    # 感觉是每一层的模型
    def __init__(self):
        super(ClassificationHead, self).__init__()
        self.linear = nn.ModuleList([
            nn.Linear(512 * (1024 // 4 // 32) * (768 // 4 // 32), 64),
            nn.Linear(64, 16),
            nn.Linear(16, 2),
        ])
        # ModuleList是特殊的list，其包含的模块会被自动注册，而包含在list中的模块无法被展示出来
        self.relu = nn.ReLU()
        self.softmax = nn.Softmax(dim=-1)
        # nn.Softmax是对n维张量进行操作，以便n维张量的元素位于[0,1]之内，总和为1.
        # Softmax(x_i) = (exp(x_i))/(sum(exp(x_j)))
        self.dropout = nn.Dropout()
        # 在训练期间，使用伯努利分布中的样本，以概率随机将输入张量的某些元素归零。每个通道将在每次转接呼叫时独立归零。
        # 已被证明是正则化和防止神经元共同适应的有效技术
    def forward(self, features):
        f1 = self.dropout(self.relu(self.linear[0](features)))
        f2 = self.dropout(self.relu(self.linear[1](f1)))
        return self.softmax(self.linear[2](f2))
