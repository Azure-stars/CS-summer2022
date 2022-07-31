import os
import numpy as np
from PIL import Image
from tqdm import tqdm
from pathlib import Path
from argparse import ArgumentParser


def calc_label(label: np.ndarray, threshold: float):
    """
    计算label中各像素对应的标签,然后返回该图片的标签分类
    Calc label category statistics.
    For all label_ids in `label` array, calculate the total number of mountains (namely how many label_ids is in [0,7]),
    if this number is greater than threshold * sizeof label, then mark the `mountain` field in return dictionary as
    True, else as False.
    :param label: A numpy array, shaped (H, W).
    :param threshold: float number.
    :return: {"mountain": bool, "sky": bool, "water": bool}
    """

    label2id = {
        "mountain": [0, 7],
        "sky": [1],
        "water": [2, 3, 8, 16, 20],
    }

    answer = {}
    
    for key,val in label2id.items():
        num = 0
        for val_num in val:
            num += np.sum(label == val_num)
        if num > label.size * threshold:
            answer[key] = True
        else:
            answer[key] = False
    return answer


def process_data(mode: str, threshold: float):
    """
    Pre-process data.
    :param mode: Either in `train`, `val` or `test`
    :param threshold: threshold to determine a category.
    :return: None. Write a file to the corresponding path.
    """
    working_dir = (Path(__file__) / ".." / ".." / "data" / mode).resolve()
    # 得到数据集所在目录
    # path.resolve总是返回一个以相对于当前的工作目录（working directory）的绝对路径。
    image_dir = working_dir / 'imgs'
    label_dir = working_dir / 'labels'
    
    print(f"[Data] Now in {working_dir}...")

    out_str = "img_path,mountain,sky,water\n"

    assert os.path.exists(image_dir), "No directory called `imgs` found in working directory!"
    assert os.path.exists(label_dir), "No directory called `labels` found in working " \
                                                                "directory!"
    filename_list = []
    for file in os.listdir(image_dir):
        filename_list.append(os.path.splitext(file)[0])
    # 去除文件的后缀名，存储在filename_list中

    for idx, file_name in tqdm(enumerate(filename_list), total=len(filename_list)):
        label_path = str(label_dir / f"{file_name}.png")
        label = Image.open(label_path)
        label_array = np.array(label)
        # 读入图片并转化为像素array张量
        statistics = calc_label(label_array, threshold)
        out_str += f"{file_name}.jpg,{statistics['mountain']},{statistics['sky']},{statistics['water']}\n"

        if idx == 5000:
            break

    outfile = open(working_dir/'file.txt', 'w')
    outfile.write(out_str)
    # 输出格式与val/file.txt格式相同
    outfile.close()

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--threshold", type=float, default=0.2, help="Threshold for determining if a label exists in "
                                                                   "the image.")
    parser.add_argument("--mode", type=str, choices=["train", "val", "test"], default="train")
    args = parser.parse_args()

    process_data(args.mode, args.threshold)
