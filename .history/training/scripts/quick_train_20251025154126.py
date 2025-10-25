#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速训练脚本
==========

一键训练所有AI模型，适合快速验证和测试

使用方法:
python quick_train.py --mode demo  # 演示模式 (快速训练)
python quick_train.py --mode full  # 完整训练

作者: AI智能眼镜开发团队
版本: v2.4
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path
import yaml
import torch
import time
from datetime import datetime

class QuickTrainer:
    """快速训练器"""
    
    def __init__(self, mode='demo'):
        self.mode = mode
        self.setup_config()
        self.setup_environment()
    
    def setup_config(self):
        """设置训练配置"""
        if self.mode == 'demo':
            # 演示模式配置 (快速训练)
            self.config = {
                'blind_path': {
                    'epochs': 5,
                    'batch': 8,
                    'imgsz': 320,
                    'description': '盲道分割 (演示)'
                },
                'crosswalk': {
                    'epochs': 3,
                    'batch': 16,
                    'imgsz': 320,
                    'description': '斑马线检测 (演示)'
                },
                'traffic_light': {
                    'epochs': 3,
                    'batch': 16,
                    'imgsz': 320,
                    'description': '红绿灯检测 (演示)'
                },
                'obstacle': {
                    'epochs': 5,
                    'batch': 12,
                    'imgsz': 320,
                    'description': '障碍物检测 (演示)'
                },
                'item_recognition': {
                    'epochs': 5,
                    'batch': 12,
                    'imgsz': 320,
                    'description': '物品识别 (演示)'
                }
            }
            self.total_time = "30-60分钟"
        else:
            # 完整训练配置
            self.config = {
                'blind_path': {
                    'epochs': 100,
                    'batch': 16,
                    'imgsz': 640,
                    'description': '盲道分割 (完整)'
                },
                'crosswalk': {
                    'epochs': 80,
                    'batch': 32,
                    'imgsz': 640,
                    'description': '斑马线检测 (完整)'
                },
                'traffic_light': {
                    'epochs': 60,
                    'batch': 24,
                    'imgsz': 640,
                    'description': '红绿灯检测 (完整)'
                },
                'obstacle': {
                    'epochs': 120,
                    'batch': 20,
                    'imgsz': 640,
                    'description': '障碍物检测 (完整)'
                },
                'item_recognition': {
                    'epochs': 100,
                    'batch': 24,
                    'imgsz': 640,
                    'description': '物品识别 (完整)'
                }
            }
            self.total_time = "40-60小时"
    
    def setup_environment(self):
        """设置训练环境"""
        print("🔧 设置训练环境...")
        
        # 检查GPU
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
            print(f"✅ GPU: {gpu_name} ({gpu_memory:.1f}GB)")
        else:
            print("⚠️  未检测到GPU，将使用CPU训练")
        
        # 创建输出目录
        os.makedirs("runs/train", exist_ok=True)
        os.makedirs("logs", exist_ok=True)
        
        print("✅ 环境设置完成")
    
    def check_data_availability(self):
        """检查数据可用性"""
        print("📊 检查数据可用性...")
        
        # 检查数据集目录
        datasets = ['blind_path', 'crosswalk', 'traffic_light', 'obstacle', 'items']
        missing_datasets = []
        
        for dataset in datasets:
            dataset_path = f"datasets/{dataset}"
            if Path(dataset_path).exists():
                # 检查图像文件
                image_files = list(Path(dataset_path).glob("*.jpg")) + list(Path(dataset_path).glob("*.png"))
                if len(image_files) > 0:
                    print(f"   ✅ {dataset}: {len(image_files)} 张图像")
                else:
                    print(f"   ⚠️  {dataset}: 目录存在但无图像文件")
                    missing_datasets.append(dataset)
            else:
                print(f"   ❌ {dataset}: 目录不存在")
                missing_datasets.append(dataset)
        
        if missing_datasets:
            print(f"\n⚠️  缺少数据集: {', '.join(missing_datasets)}")
            if self.mode == 'demo':
                print("   演示模式将使用模拟数据")
                return True
            else:
                print("   请先准备数据集")
                return False
        
        return True
    
    def create_demo_data(self):
        """创建演示数据"""
        print("🎭 创建演示数据...")
        
        import cv2
        import numpy as np
        
        # 创建演示数据集
        for dataset in ['blind_path', 'crosswalk', 'traffic_light', 'obstacle', 'items']:
            dataset_dir = Path(f"datasets/{dataset}")
            dataset_dir.mkdir(parents=True, exist_ok=True)
            
            # 创建模拟图像
            for i in range(10):  # 每个数据集10张图像
                # 创建随机图像
                img = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
                
                # 添加一些简单的模式
                if dataset == 'blind_path':
                    # 添加线条模式
                    cv2.line(img, (0, 320), (640, 320), (100, 100, 100), 20)
                elif dataset == 'crosswalk':
                    # 添加斑马线模式
                    for x in range(0, 640, 40):
                        cv2.rectangle(img, (x, 300), (x+20, 340), (255, 255, 255), -1)
                elif dataset == 'traffic_light':
                    # 添加红绿灯模式
                    cv2.circle(img, (320, 200), 30, (0, 0, 255), -1)
                elif dataset == 'obstacle':
                    # 添加障碍物模式
                    cv2.rectangle(img, (200, 200), (400, 400), (0, 255, 0), -1)
                elif dataset == 'items':
                    # 添加物品模式
                    cv2.circle(img, (320, 320), 50, (255, 0, 0), -1)
                
                # 保存图像
                img_path = dataset_dir / f"{dataset}_{i:03d}.jpg"
                cv2.imwrite(str(img_path), img)
                
                # 创建对应的标注文件
                label_path = dataset_dir / f"{dataset}_{i:03d}.txt"
                with open(label_path, 'w') as f:
                    f.write("0 0.5 0.5 0.2 0.2")  # 简单的YOLO格式标注
            
            print(f"   ✅ {dataset}: 创建了10张演示图像")
        
        print("✅ 演示数据创建完成")
    
    def train_single_model(self, model_name, config):
        """训练单个模型"""
        print(f"\n🚀 训练模型: {model_name}")
        print(f"   描述: {config['description']}")
        print(f"   轮数: {config['epochs']}")
        print(f"   批次: {config['batch']}")
        print(f"   尺寸: {config['imgsz']}")
        
        # 构建训练命令
        cmd = [
            "python", "training/scripts/train_blind_path.py",
            "--data", f"datasets/{model_name}/{model_name}.yaml",
            "--model", "yolov8n.pt",
            "--epochs", str(config['epochs']),
            "--batch", str(config['batch']),
            "--imgsz", str(config['imgsz']),
            "--device", "cuda" if torch.cuda.is_available() else "cpu",
            "--workers", "4",
            "--patience", "10",
        ]
        
        print(f"   命令: {' '.join(cmd)}")
        
        try:
            # 执行训练
            start_time = time.time()
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            end_time = time.time()
            
            training_time = end_time - start_time
            print(f"   ✅ 训练完成 (用时: {training_time/60:.1f}分钟)")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"   ❌ 训练失败: {e.stderr}")
            return False
    
    def train_all_models(self):
        """训练所有模型"""
        print("🚀 开始训练所有模型")
        print("=" * 50)
        
        # 检查数据可用性
        if not self.check_data_availability():
            if self.mode == 'demo':
                self.create_demo_data()
            else:
                print("❌ 数据检查失败，请准备数据集")
                return False
        
        # 记录开始时间
        start_time = datetime.now()
        
        # 训练结果
        results = {}
        
        # 逐个训练模型
        for model_name, config in self.config.items():
            print(f"\n📋 训练模型: {model_name}")
            
            # 训练模型
            success = self.train_single_model(model_name, config)
            results[model_name] = success
            
            if success:
                print(f"✅ {model_name} 训练成功")
            else:
                print(f"❌ {model_name} 训练失败")
        
        # 计算总时间
        end_time = datetime.now()
        total_time = end_time - start_time
        
        # 输出结果
        print("\n📊 训练结果汇总")
        print("=" * 50)
        print(f"总训练时间: {total_time}")
        
        success_count = sum(results.values())
        total_count = len(results)
        
        print(f"成功训练: {success_count}/{total_count}")
        
        for model_name, success in results.items():
            status = "✅ 成功" if success else "❌ 失败"
            print(f"   {model_name}: {status}")
        
        return success_count == total_count
    
    def create_summary_report(self):
        """创建训练总结报告"""
        print("\n📋 创建训练总结报告...")
        
        report = f"""
# AI智能眼镜模型训练报告

## 训练信息
- 训练模式: {self.mode}
- 训练时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- 预估时间: {self.total_time}

## 模型配置
"""
        
        for model_name, config in self.config.items():
            report += f"""
### {model_name}
- 描述: {config['description']}
- 轮数: {config['epochs']}
- 批次: {config['batch']}
- 尺寸: {config['imgsz']}
"""
        
        report += """
## 使用说明
1. 模型文件保存在 `runs/train/` 目录
2. 训练日志保存在 `logs/` 目录
3. 使用TensorBoard查看训练过程: `tensorboard --logdir runs/train`

## 下一步
1. 评估模型性能
2. 优化模型参数
3. 部署到生产环境
"""
        
        # 保存报告
        report_path = "training_report.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"✅ 训练报告已保存: {report_path}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='快速训练脚本')
    parser.add_argument('--mode', type=str, choices=['demo', 'full'], default='demo',
                       help='训练模式: demo(演示) 或 full(完整)')
    parser.add_argument('--models', type=str, nargs='+', 
                       choices=['blind_path', 'crosswalk', 'traffic_light', 'obstacle', 'item_recognition'],
                       help='指定要训练的模型')
    
    args = parser.parse_args()
    
    print("🚀 AI智能眼镜快速训练开始")
    print("=" * 50)
    print(f"训练模式: {args.mode}")
    print(f"预估时间: {'30-60分钟' if args.mode == 'demo' else '40-60小时'}")
    
    # 创建训练器
    trainer = QuickTrainer(args.mode)
    
    # 训练所有模型
    success = trainer.train_all_models()
    
    if success:
        print("\n🎉 所有模型训练完成!")
        
        # 创建训练报告
        trainer.create_summary_report()
        
        print("\n📋 下一步操作:")
        print("1. 查看训练报告: training_report.md")
        print("2. 启动TensorBoard: tensorboard --logdir runs/train")
        print("3. 评估模型性能: python training/scripts/evaluate_models.py")
        print("4. 部署模型: python training/scripts/deploy_models.py")
    else:
        print("\n❌ 部分模型训练失败，请检查日志")
        sys.exit(1)

if __name__ == "__main__":
    main()
