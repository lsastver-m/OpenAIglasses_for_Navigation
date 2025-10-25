#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
盲道分割模型训练脚本
==================

训练用于盲道检测和分割的深度学习模型
支持YOLO系列模型的分割任务

使用方法:
python train_blind_path.py --data datasets/blind_path/blind_path.yaml --epochs 100

作者: AI智能眼镜开发团队
版本: v2.4
"""

import os
import sys
import argparse
import yaml
import torch
import numpy as np
from pathlib import Path
from ultralytics import YOLO
from torch.utils.tensorboard import SummaryWriter
import matplotlib.pyplot as plt
import pandas as pd

def setup_training_environment():
    """设置训练环境"""
    print("🔧 设置训练环境...")
    
    # 检查GPU
    if torch.cuda.is_available():
        print(f"✅ GPU可用: {torch.cuda.get_device_name(0)}")
        print(f"   显存: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f}GB")
    else:
        print("⚠️  未检测到GPU，将使用CPU训练（速度较慢）")
    
    # 创建输出目录
    os.makedirs("runs/train/blind_path", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    print("✅ 训练环境设置完成")

def load_training_config(config_path):
    """加载训练配置"""
    print(f"📋 加载训练配置: {config_path}")
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    print(f"   数据集路径: {config['path']}")
    print(f"   类别数量: {config['nc']}")
    print(f"   类别名称: {config['names']}")
    
    return config

def create_model(model_type="yolov8n-seg.pt"):
    """创建模型"""
    print(f"🤖 创建模型: {model_type}")
    
    # 加载预训练模型
    model = YOLO(model_type)
    
    # 设置模型参数
    model.model.nc = 1  # 盲道类别数量
    model.model.names = {0: 'blind_path'}  # 类别名称
    
    print("✅ 模型创建完成")
    return model

def setup_data_augmentation():
    """设置数据增强"""
    print("🔄 设置数据增强...")
    
    augmentation_config = {
        'hsv_h': 0.015,  # 色调变化
        'hsv_s': 0.7,    # 饱和度变化
        'hsv_v': 0.4,    # 明度变化
        'degrees': 0.0,  # 旋转角度
        'translate': 0.1, # 平移
        'scale': 0.5,    # 缩放
        'shear': 0.0,    # 剪切
        'perspective': 0.0, # 透视变换
        'flipud': 0.0,   # 上下翻转
        'fliplr': 0.5,   # 左右翻转
        'mosaic': 1.0,   # 马赛克增强
        'mixup': 0.0,    # 混合增强
        'copy_paste': 0.0, # 复制粘贴
    }
    
    print("✅ 数据增强设置完成")
    return augmentation_config

def train_model(model, data_config, training_args):
    """训练模型"""
    print("🚀 开始训练模型...")
    
    # 设置TensorBoard
    writer = SummaryWriter('runs/train/blind_path')
    
    try:
        # 开始训练
        results = model.train(
            data=data_config,
            epochs=training_args['epochs'],
            batch=training_args['batch_size'],
            imgsz=training_args['imgsz'],
            device=training_args['device'],
            workers=training_args['workers'],
            patience=training_args['patience'],
            save=True,
            save_period=training_args['save_period'],
            cache=True,
            project='runs/train',
            name='blind_path_seg',
            exist_ok=True,
            **training_args.get('augmentation', {})
        )
        
        print("✅ 训练完成")
        return results
        
    except Exception as e:
        print(f"❌ 训练失败: {e}")
        raise
    finally:
        writer.close()

def evaluate_model(model, data_config):
    """评估模型"""
    print("📊 评估模型性能...")
    
    try:
        # 在验证集上评估
        metrics = model.val(data=data_config)
        
        # 打印评估结果
        print("\n📈 模型评估结果:")
        print(f"   mAP50: {metrics.box.map50:.4f}")
        print(f"   mAP50-95: {metrics.box.map:.4f}")
        print(f"   精确率: {metrics.box.mp:.4f}")
        print(f"   召回率: {metrics.box.mr:.4f}")
        
        return metrics
        
    except Exception as e:
        print(f"❌ 评估失败: {e}")
        return None

def plot_training_curves(results_dir):
    """绘制训练曲线"""
    print("📊 绘制训练曲线...")
    
    try:
        # 读取训练结果
        results_file = Path(results_dir) / "results.csv"
        if not results_file.exists():
            print("⚠️  训练结果文件不存在")
            return
        
        results = pd.read_csv(results_file)
        
        # 创建图表
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # 损失曲线
        axes[0, 0].plot(results['epoch'], results['train/box_loss'], label='Train Box Loss')
        axes[0, 0].plot(results['epoch'], results['val/box_loss'], label='Val Box Loss')
        axes[0, 0].set_title('Box Loss')
        axes[0, 0].set_xlabel('Epoch')
        axes[0, 0].set_ylabel('Loss')
        axes[0, 0].legend()
        axes[0, 0].grid(True)
        
        # mAP曲线
        axes[0, 1].plot(results['epoch'], results['metrics/mAP50(B)'], label='mAP50')
        axes[0, 1].plot(results['epoch'], results['metrics/mAP50-95(B)'], label='mAP50-95')
        axes[0, 1].set_title('mAP')
        axes[0, 1].set_xlabel('Epoch')
        axes[0, 1].set_ylabel('mAP')
        axes[0, 1].legend()
        axes[0, 1].grid(True)
        
        # 学习率曲线
        axes[1, 0].plot(results['epoch'], results['lr/pg0'], label='Learning Rate')
        axes[1, 0].set_title('Learning Rate')
        axes[1, 0].set_xlabel('Epoch')
        axes[1, 0].set_ylabel('LR')
        axes[1, 0].legend()
        axes[1, 0].grid(True)
        
        # 精度和召回率
        axes[1, 1].plot(results['epoch'], results['metrics/precision(B)'], label='Precision')
        axes[1, 1].plot(results['epoch'], results['metrics/recall(B)'], label='Recall')
        axes[1, 1].set_title('Precision & Recall')
        axes[1, 1].set_xlabel('Epoch')
        axes[1, 1].set_ylabel('Score')
        axes[1, 1].legend()
        axes[1, 1].grid(True)
        
        plt.tight_layout()
        plt.savefig('runs/train/blind_path/training_curves.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print("✅ 训练曲线已保存")
        
    except Exception as e:
        print(f"❌ 绘制训练曲线失败: {e}")

def export_model(model, export_formats=['onnx', 'torchscript']):
    """导出模型"""
    print("📦 导出模型...")
    
    for format_type in export_formats:
        try:
            print(f"   导出为 {format_type} 格式...")
            model.export(format=format_type, imgsz=640, optimize=True)
            print(f"   ✅ {format_type} 格式导出完成")
        except Exception as e:
            print(f"   ❌ {format_type} 格式导出失败: {e}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='盲道分割模型训练')
    parser.add_argument('--data', type=str, default='datasets/blind_path/blind_path.yaml',
                       help='数据集配置文件路径')
    parser.add_argument('--model', type=str, default='yolov8n-seg.pt',
                       help='预训练模型路径')
    parser.add_argument('--epochs', type=int, default=100,
                       help='训练轮数')
    parser.add_argument('--batch', type=int, default=16,
                       help='批次大小')
    parser.add_argument('--imgsz', type=int, default=640,
                       help='图像尺寸')
    parser.add_argument('--device', type=str, default='cuda',
                       help='训练设备')
    parser.add_argument('--workers', type=int, default=8,
                       help='数据加载线程数')
    parser.add_argument('--patience', type=int, default=20,
                       help='早停耐心值')
    parser.add_argument('--save-period', type=int, default=10,
                       help='模型保存周期')
    
    args = parser.parse_args()
    
    print("🚀 盲道分割模型训练开始")
    print("=" * 50)
    
    # 设置训练环境
    setup_training_environment()
    
    # 加载配置
    data_config = args.data
    training_args = {
        'epochs': args.epochs,
        'batch_size': args.batch,
        'imgsz': args.imgsz,
        'device': args.device,
        'workers': args.workers,
        'patience': args.patience,
        'save_period': args.save_period,
        'augmentation': setup_data_augmentation()
    }
    
    # 创建模型
    model = create_model(args.model)
    
    # 训练模型
    results = train_model(model, data_config, training_args)
    
    # 评估模型
    metrics = evaluate_model(model, data_config)
    
    # 绘制训练曲线
    plot_training_curves('runs/train/blind_path')
    
    # 导出模型
    export_model(model)
    
    print("\n🎉 训练完成!")
    print(f"   模型保存路径: runs/train/blind_path/weights/best.pt")
    print(f"   训练日志: runs/train/blind_path/")
    print(f"   TensorBoard: tensorboard --logdir runs/train/blind_path")

if __name__ == "__main__":
    main()
