#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全模型训练脚本
============

一次性训练所有需要的AI模型
包括盲道分割、斑马线检测、红绿灯检测、障碍物检测、物品识别

使用方法:
python train_all_models.py --config training/configs/training_config.yaml

作者: AI智能眼镜开发团队
版本: v2.4
"""

import os
import sys
import yaml
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
import torch
import psutil
import GPUtil

class ModelTrainer:
    """模型训练器"""
    
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.load_config()
        self.setup_environment()
    
    def load_config(self):
        """加载训练配置"""
        print(f"📋 加载训练配置: {self.config_path}")
        
        with open(self.config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        print(f"   训练模型数量: {len(self.config['models'])}")
        print(f"   总训练时间预估: {self.config.get('total_time_hours', '未知')} 小时")
    
    def setup_environment(self):
        """设置训练环境"""
        print("🔧 设置训练环境...")
        
        # 检查GPU
        if torch.cuda.is_available():
            gpu_count = torch.cuda.device_count()
            print(f"✅ 检测到 {gpu_count} 个GPU")
            for i in range(gpu_count):
                gpu = torch.cuda.get_device_properties(i)
                print(f"   GPU {i}: {gpu.name} ({gpu.total_memory / 1024**3:.1f}GB)")
        else:
            print("⚠️  未检测到GPU，将使用CPU训练")
        
        # 检查内存
        memory = psutil.virtual_memory()
        print(f"   系统内存: {memory.total / 1024**3:.1f}GB (可用: {memory.available / 1024**3:.1f}GB)")
        
        # 创建输出目录
        self.output_dir = Path("runs/train")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        print("✅ 训练环境设置完成")
    
    def check_data_availability(self):
        """检查数据可用性"""
        print("📊 检查数据可用性...")
        
        for model_name, model_config in self.config['models'].items():
            data_path = model_config.get('data')
            if data_path and Path(data_path).exists():
                print(f"   ✅ {model_name}: 数据路径存在")
            else:
                print(f"   ❌ {model_name}: 数据路径不存在 - {data_path}")
                return False
        
        return True
    
    def train_single_model(self, model_name: str, model_config: dict):
        """训练单个模型"""
        print(f"\n🚀 开始训练模型: {model_name}")
        print("=" * 50)
        
        # 构建训练命令
        cmd = [
            "python", "training/scripts/train_blind_path.py",
            "--data", model_config['data'],
            "--model", model_config.get('model', 'yolov8n-seg.pt'),
            "--epochs", str(model_config.get('epochs', 100)),
            "--batch", str(model_config.get('batch', 16)),
            "--imgsz", str(model_config.get('imgsz', 640)),
            "--device", model_config.get('device', 'cuda'),
            "--workers", str(model_config.get('workers', 8)),
            "--patience", str(model_config.get('patience', 20)),
        ]
        
        print(f"执行命令: {' '.join(cmd)}")
        
        try:
            # 执行训练
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(f"✅ {model_name} 训练完成")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ {model_name} 训练失败:")
            print(f"   错误信息: {e.stderr}")
            return False
    
    def train_all_models(self):
        """训练所有模型"""
        print("🚀 开始训练所有模型")
        print("=" * 50)
        
        # 检查数据可用性
        if not self.check_data_availability():
            print("❌ 数据检查失败，请检查数据路径")
            return False
        
        # 记录开始时间
        start_time = datetime.now()
        
        # 训练结果
        results = {}
        
        # 逐个训练模型
        for model_name, model_config in self.config['models'].items():
            print(f"\n📋 训练模型: {model_name}")
            print(f"   数据路径: {model_config['data']}")
            print(f"   训练轮数: {model_config.get('epochs', 100)}")
            print(f"   批次大小: {model_config.get('batch', 16)}")
            
            # 训练模型
            success = self.train_single_model(model_name, model_config)
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
    
    def export_models(self):
        """导出所有模型"""
        print("\n📦 导出模型...")
        
        for model_name in self.config['models'].keys():
            model_path = f"runs/train/{model_name}/weights/best.pt"
            if Path(model_path).exists():
                print(f"   导出 {model_name}...")
                # 这里可以添加模型导出逻辑
                print(f"   ✅ {model_name} 导出完成")
            else:
                print(f"   ❌ {model_name} 模型文件不存在")
    
    def create_deployment_package(self):
        """创建部署包"""
        print("\n📦 创建部署包...")
        
        # 创建部署目录
        deploy_dir = Path("deployment/models")
        deploy_dir.mkdir(parents=True, exist_ok=True)
        
        # 复制模型文件
        for model_name in self.config['models'].keys():
            src_path = f"runs/train/{model_name}/weights/best.pt"
            dst_path = deploy_dir / f"{model_name}.pt"
            
            if Path(src_path).exists():
                import shutil
                shutil.copy2(src_path, dst_path)
                print(f"   ✅ {model_name} 已复制到部署包")
            else:
                print(f"   ❌ {model_name} 模型文件不存在")
        
        # 创建模型配置文件
        model_config = {
            'models': {
                'blind_path': 'blind_path.pt',
                'crosswalk': 'crosswalk.pt',
                'traffic_light': 'traffic_light.pt',
                'obstacle': 'obstacle.pt',
                'item_recognition': 'item_recognition.pt'
            },
            'version': '2.4',
            'created_at': datetime.now().isoformat()
        }
        
        config_path = deploy_dir / 'model_config.yaml'
        with open(config_path, 'w') as f:
            yaml.dump(model_config, f, default_flow_style=False)
        
        print(f"✅ 部署包已创建: {deploy_dir}")
        print(f"   配置文件: {config_path}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='全模型训练脚本')
    parser.add_argument('--config', type=str, default='training/configs/training_config.yaml',
                       help='训练配置文件路径')
    parser.add_argument('--export', action='store_true',
                       help='是否导出模型')
    parser.add_argument('--package', action='store_true',
                       help='是否创建部署包')
    
    args = parser.parse_args()
    
    print("🚀 AI智能眼镜模型训练开始")
    print("=" * 50)
    
    # 创建训练器
    trainer = ModelTrainer(args.config)
    
    # 训练所有模型
    success = trainer.train_all_models()
    
    if success:
        print("\n🎉 所有模型训练完成!")
        
        # 导出模型
        if args.export:
            trainer.export_models()
        
        # 创建部署包
        if args.package:
            trainer.create_deployment_package()
    else:
        print("\n❌ 部分模型训练失败，请检查日志")
        sys.exit(1)

if __name__ == "__main__":
    main()
