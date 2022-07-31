import torch
import numpy as np
from PIL import Image
from torch.utils.data import Dataset
from IPython import embed

class LandScapeDataset(Dataset):
# 继承torch.utils.data.Dataset类，是数据集的类型
    def __init__(self, mode="train"):
        self.mode = mode
        # mode:训练类型
        if mode == "train" or mode == "val":
            with open(f"./data/{mode}/file.txt", 'r') as file:
                try:
                    # entries:读入的txt按照行进行分割
                    entries = file.read().strip().split('\n')[1:]
                    # table:读入的txt按照逗号划分为表格
                    table = [entry.split(",") for entry in entries]
                    # self.images:数据集中图像的名称
                    self.images = [row[0] for row in table]
                    # self.gt:数据集中所有图像的分类标签
                    self.gt = [(eval(row[1]), eval(row[2]), eval(row[3])) for row in table]
                except Exception as e:
                    embed()
        elif mode == "test":
            with open(f"./data/{mode}/file.txt", 'r') as file:
                self.images = file.read().strip().split('\n')[1:]

    def __len__(self):

        # TODO Start: Return length of current dataset #
        return len(self.images)
        # TODO End #

    def __getitem__(self, idx):
        """
        :param idx: index to get.
        :return: ret_dict: {"image": torch.Tensor (3, 192, 256), "label": torch.Tensor (3, )}
        """

        file_name = self.images[idx]

        image = Image.open(f"./data/{self.mode}/imgs/{file_name}")
        image = image.resize((image.width // 4, image.height // 4))  
        # 压缩图片大小为原来的宽度为1/4，长度为1/4

        array = np.array(image)
        array = array.transpose((2, 0, 1))  # From (192, 256, 3) to (3, 192, 256)
        # 转置改变张量维度

        ret_dict = {
            "image": torch.tensor(array),
        }

        if self.mode != "test":
            ret_dict["label"] = torch.tensor(np.array(self.gt[idx]))

        # Normalize ret_dict["image"] from [0, 255] to [-1, 1]
        ret_dict["image"] = (ret_dict["image"] / 255) * 2 - 1
        # 标准化使其范围为[-1,1]
        return ret_dict
