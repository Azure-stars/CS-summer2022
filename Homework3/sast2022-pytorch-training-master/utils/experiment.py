import os
import time
import torch
import random
import numpy as np
from tqdm import tqdm
from torch.utils.data import DataLoader

from utils.metric import calc_accuracy
from datasets.dataset_landscape import LandScapeDataset


def initiate_environment(args):
    """
    初始化随机数种子
    initiate randomness.
    :param args: Runtime arguments.
    :return:
    """
    torch.manual_seed(args.rng_seed)
    torch.cuda.manual_seed_all(args.rng_seed)
    np.random.seed(args.rng_seed)
    random.seed(args.rng_seed)
    # 更加增加随机性

def get_loader(args):
    num_workers = args.num_workers
    # num_workers代表了使用多进程时加载的进程数
    val_dataset = LandScapeDataset("val")
    # LandScapeDataset代表了数据集的类，里面实现了一系列的成员函数
    val_dataloader = DataLoader(val_dataset, shuffle=False, num_workers=num_workers, batch_size=args.batch_size)
    # DataLoader 负责对数据的抽象，是对dataset的数据按照batch的规模进行操作，同时可以对数据进行shuffle和并行加速（即num_workers）
    if args.mode == "train":
        dataset = LandScapeDataset(args.mode)
        dataloader = DataLoader(dataset, shuffle=True, num_workers=num_workers, batch_size=args.batch_size)
    elif args.mode == "test":
        dataset = LandScapeDataset(args.mode)
        dataloader = DataLoader(dataset, shuffle=False, num_workers=num_workers, batch_size=args.batch_size)
    else:
        raise NotImplementedError("You must specify either to train or to test!")

    return dataloader, val_dataloader


def save_model(args, model, optimizer, epoch="last"):
    os.makedirs(args.save_path, exist_ok=True)
    checkpoint = {
        'config': args,
        'model': model.state_dict(),
        'optimizer': optimizer.state_dict(),
        # state_dict是在定义了model或optimizer之后pytorch自动生成的
        # 是一个简单的python的字典对象,将每一层与它的对应参数建立映射关系(如model的每一层的weights及偏置等等)
    }
    torch.save(checkpoint, os.path.join(args.save_path, args.task_name, f'ckpt_epoch_{epoch}.pth'))
    # torch.save 对象是字典加上存储路径

def load_model(args, model, optimizer):
    # 加载模型
    checkpoint = torch.load(args.checkpoint_path)
    # torch.load 对象是路径
    model.load_state_dict(checkpoint['model'])
    optimizer.load_state_dict(checkpoint['optimizer'])
    # load_state_dict:解序列化，把存储好的模型从字典对象中加载到model与optimizer之中


def train_one_epoch(epoch, train_loader, args, model, criterion, optimizer, stat_dict):
    """
    :param epoch: Epoch number.
    :param train_loader: Train loader.
    :param args: Runtime arguments.
    :param model: Network.
    :param criterion: Loss function.
    :param optimizer: SGD or Adam.
    :param stat_dict: {"train/loss": []}
    """
    model.train()
    start_time = time.time()

    print(f"==> [Epoch {epoch + 1}] Starting Training...")
    for train_idx, train_data in tqdm(enumerate(train_loader), total=len(train_loader)):
        train_input, train_label = train_data["image"].to(args.device), train_data["label"].to(args.device)
        pred_label = model(train_input)
        optimizer.zero_grad()
        # 将梯度清零
        loss = criterion(pred_label.reshape(-1, 2), train_label.reshape(-1).long())
        # 交叉熵损失函数
        loss.backward()
        # 计算反向梯度
        optimizer.step()
        # 根据计算好的梯度更新参数，学习率已配置完毕或者有默认值
        if train_idx % args.print_freq == 0:
            stat_dict["train/loss"].append(loss.detach().item())
            # stat_dict记录训练的损失代价
            # tqdm.write(f"[Epoch {epoch + 1} / {args.max_epoch}] [Batch {train_idx + 1} / {len(train_loader)}] " +
            #            f"Loss {loss:.4f}")
            # draw_loss_curve(args, stat_dict["train/loss"])
    print(f"==> [Epoch {epoch + 1}] Finished in {((time.time() - start_time) / 60):.2f} minutes.")


def evaluate_one_epoch(loader, args, model, criterion=None, save_name=None):
    """
    :param loader: val or test loader.
    :param args: Runtime arguments.
    :param model: Network.
    :param criterion: Loss function.
    :param save_name: if exists, save current predicted results to `{args.save_path} / {args.task_name} /
            {save_name}.txt` for further testing.
    :return: None
    """
    model.eval()
    results, ground_truths = [], []
    print(f"==> [Eval] Start evaluating model...")
    with torch.no_grad():
        # torch.no_grad() 一般用于神经网络的推理阶段, 表示张量的计算过程中无需计算梯度
        for data_idx, data in tqdm(enumerate(loader), total=len(loader)):
            pred = model(data['image'].to(args.device))
            results.append(pred.cpu().numpy())
            if 'label' in data:
                ground_truths.append(data['label'].cpu().numpy())

        results = [result.argmax(axis=-1) for result in results]
        if criterion == "acc":
            acc = calc_accuracy(results, ground_truths)
            print(f"==> [Eval] Current accuracy: {(acc * 100):.2f}%")

        if save_name is not None:
            out_str = ""
            for x in results:
                out_str += ''.join([f"{y[0]},{y[1]},{y[2]}\n" for y in x])
            with open(f"{args.save_path}/{args.task_name}/{save_name}", 'w+') as file:
                file.write(out_str)
