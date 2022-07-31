from operator import mod
import torch
import argparse
import torch.nn as nn
import torch.optim as optim
from argparse import ArgumentParser

from models.MultiClassificationModel import MultiClassificationModel
from utils.experiment import get_loader, save_model, load_model, train_one_epoch, evaluate_one_epoch, \
    initiate_environment

from utils.metric import  draw_loss_curve

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # Meta info
    parser.add_argument("--task_name", type=str, default="baseline", help="Task name to save.")
    parser.add_argument("--mode", type=str, choices=["train", "test"], default="train", help="Mode to run.")
    parser.add_argument("--device", type=str, default="cuda:0", help="Device number.")
    parser.add_argument("--num_workers", type=int, default=4, help="Spawn how many processes to load data.")
    parser.add_argument("--rng_seed", type=int, default=114514, help='manual seed')

    # Training
    parser.add_argument("--num_epoch", type=int, default=0, help="Current epoch number.")
    parser.add_argument("--max_epoch", type=int, default=10, help="Max epoch number to run.")
    parser.add_argument("--checkpoint_path", type=str, default="", help="Checkpoint path to load.")
    parser.add_argument("--save_path", type=str, default="./save/", help="Checkpoint path to save.")
    parser.add_argument("--save_freq", type=int, default=1, help="Save model every how many epochs.")
    # TODO Start: Define `args.val_freq` and `args.print_freq` here #
    parser.add_argument("--val_freq", type=int, default=1, help="Evaluate model every how many epochs.")
    parser.add_argument("--print_freq", type=int, default=1, help="Print model every how many epochs.")
    # TODO End #
    parser.add_argument("--batch_size", type=int, default=16, help="Entry numbers every batch.")

    # Optimizer
    parser.add_argument("--optimizer", type=str, choices=["SGD", "Adam"], default="Adam", help="Optimizer type.")
    parser.add_argument("--lr", type=float, default=1e-7, help="Learning rate for SGD optimizer.")
    parser.add_argument("--weight_decay", type=float, default=0.005, help="Weight decay regularization for model.")

    args = parser.parse_args()
    initiate_environment(args)

    # Prepare dataloader
    loader, val_loader = get_loader(args)
    # print(loader["image"].to(args.device))
    # Load model & optimizer
    model = MultiClassificationModel()
    if args.optimizer == "SGD":
        optimizer = optim.SGD(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)
    elif args.optimizer == "Adam":
        optimizer = optim.Adam(model.parameters(), lr = args.lr, weight_decay=args.weight_decay)
    else:
        raise NotImplementedError("You must specify a valid optimizer type!")
    # SGD与Adam优化器都是对神经网络梯度下降算法迭代的优化

    model = model.to(args.device)
    if args.checkpoint_path:
        load_model(args, model, optimizer)

    # Define loss function
    criterion = nn.CrossEntropyLoss()
    # 交叉熵损失函数
    # Main Function
    if args.mode == "train":
        stat_dict = {"train/loss": []}
        # stat_dict记录训练的损失代价
        for epoch in range(args.num_epoch, args.max_epoch):
            train_one_epoch(epoch, loader, args, model, criterion, optimizer, stat_dict)
            if epoch % args.val_freq == 0:
                evaluate_one_epoch(val_loader, args, model, criterion="acc")
            # 评估模型并记录差距
            if epoch % args.save_freq == 0:
                save_model(args, model, optimizer, epoch)
            # 保存模型
        save_model(args, model, optimizer)
        draw_loss_curve(args, stat_dict["train/loss"])
        # 保存最终模型
        print("[Main] Model training has been completed!")

    elif args.mode == "test":
        evaluate_one_epoch(loader, args, model, criterion=None, save_name="result.txt")
        # test是为了得出结果，因此并不会进行训练运算
    else:
        raise NotImplementedError("You must specify either to train or to test!")
