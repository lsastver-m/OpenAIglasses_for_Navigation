#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
训练脚本测试
==========

测试训练脚本的功能和性能

使用方法:
python test_training.py --test all  # 测试所有功能
python test_training.py --test data  # 测试数据准备
python test_training.py --test model  # 测试模型训练

作者: AI智能眼镜开发团队
版本: v2.4
"""

import os
import sys
import argparse
import subprocess
import time
import torch
import numpy as np
from pathlib import Path
import yaml
import cv2

class TrainingTester:
    """训练测试器"""
    
    def __init__(self):
        self.setup_environment()
        self.test_results = {}
    
    def setup_environment(self):
        """设置测试环境"""
        print("🔧 设置测试环境...")
        
        # 创建测试目录
        os.makedirs("test_output", exist_ok=True)
        os.makedirs("test_datasets", exist_ok=True)
        
        print("✅ 测试环境设置完成")
    
    def test_environment(self):
        """测试环境配置"""
        print("\n🧪 测试环境配置...")
        
        results = {}
        
        # 测试Python版本
        python_version = sys.version_info
        results['python_version'] = f"{python_version.major}.{python_version.minor}.{python_version.micro}"
        print(f"   Python版本: {results['python_version']}")
        
        # 测试PyTorch
        try:
            torch_version = torch.__version__
            results['torch_version'] = torch_version
            print(f"   PyTorch版本: {torch_version}")
        except Exception as e:
            results['torch_version'] = f"错误: {e}"
            print(f"   PyTorch: ❌ {e}")
        
        # 测试CUDA
        if torch.cuda.is_available():
            cuda_version = torch.version.cuda
            gpu_count = torch.cuda.device_count()
            gpu_name = torch.cuda.get_device_name(0)
            results['cuda_version'] = cuda_version
            results['gpu_count'] = gpu_count
            results['gpu_name'] = gpu_name
            print(f"   CUDA版本: {cuda_version}")
            print(f"   GPU数量: {gpu_count}")
            print(f"   GPU名称: {gpu_name}")
        else:
            results['cuda_version'] = "不可用"
            results['gpu_count'] = 0
            results['gpu_name'] = "无GPU"
            print("   CUDA: ❌ 不可用")
        
        # 测试依赖包
        dependencies = [
            'ultralytics',
            'opencv-python',
            'albumentations',
            'tensorboard',
            'matplotlib',
            'pandas'
        ]
        
        results['dependencies'] = {}
        for dep in dependencies:
            try:
                __import__(dep.replace('-', '_'))
                results['dependencies'][dep] = "✅ 已安装"
                print(f"   {dep}: ✅ 已安装")
            except ImportError:
                results['dependencies'][dep] = "❌ 未安装"
                print(f"   {dep}: ❌ 未安装")
        
        self.test_results['environment'] = results
        return results
    
    def test_data_preparation(self):
        """测试数据准备"""
        print("\n🧪 测试数据准备...")
        
        results = {}
        
        # 创建测试数据
        test_data_dir = Path("test_datasets")
        test_data_dir.mkdir(exist_ok=True)
        
        # 创建测试图像
        for i in range(5):
            img = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
            img_path = test_data_dir / f"test_{i:03d}.jpg"
            cv2.imwrite(str(img_path), img)
            
            # 创建测试标注
            label_path = test_data_dir / f"test_{i:03d}.txt"
            with open(label_path, 'w') as f:
                f.write("0 0.5 0.5 0.2 0.2")
        
        results['test_images_created'] = 5
        print(f"   创建测试图像: {results['test_images_created']} 张")
        
        # 测试数据准备脚本
        try:
            cmd = [
                "python", "training/scripts/data_preparation.py",
                "--input_dir", "test_datasets",
                "--output_dir", "test_output/processed",
                "--augment",
                "--visualize"
            ]
            
            start_time = time.time()
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            end_time = time.time()
            
            results['data_preparation_success'] = True
            results['data_preparation_time'] = end_time - start_time
            print(f"   数据准备: ✅ 成功 (用时: {results['data_preparation_time']:.2f}秒)")
            
        except subprocess.CalledProcessError as e:
            results['data_preparation_success'] = False
            results['data_preparation_error'] = e.stderr
            print(f"   数据准备: ❌ 失败 - {e.stderr}")
        
        self.test_results['data_preparation'] = results
        return results
    
    def test_model_training(self):
        """测试模型训练"""
        print("\n🧪 测试模型训练...")
        
        results = {}
        
        # 测试快速训练脚本
        try:
            cmd = [
                "python", "training/scripts/quick_train.py",
                "--mode", "demo"
            ]
            
            start_time = time.time()
            result = subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=300)
            end_time = time.time()
            
            results['quick_train_success'] = True
            results['quick_train_time'] = end_time - start_time
            print(f"   快速训练: ✅ 成功 (用时: {results['quick_train_time']:.2f}秒)")
            
        except subprocess.CalledProcessError as e:
            results['quick_train_success'] = False
            results['quick_train_error'] = e.stderr
            print(f"   快速训练: ❌ 失败 - {e.stderr}")
        except subprocess.TimeoutExpired:
            results['quick_train_success'] = False
            results['quick_train_error'] = "超时"
            print(f"   快速训练: ❌ 超时")
        
        # 测试单模型训练
        try:
            cmd = [
                "python", "training/scripts/train_blind_path.py",
                "--data", "test_output/processed/dataset.yaml",
                "--epochs", "1",
                "--batch", "2",
                "--imgsz", "320"
            ]
            
            start_time = time.time()
            result = subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=180)
            end_time = time.time()
            
            results['single_model_success'] = True
            results['single_model_time'] = end_time - start_time
            print(f"   单模型训练: ✅ 成功 (用时: {results['single_model_time']:.2f}秒)")
            
        except subprocess.CalledProcessError as e:
            results['single_model_success'] = False
            results['single_model_error'] = e.stderr
            print(f"   单模型训练: ❌ 失败 - {e.stderr}")
        except subprocess.TimeoutExpired:
            results['single_model_success'] = False
            results['single_model_error'] = "超时"
            print(f"   单模型训练: ❌ 超时")
        
        self.test_results['model_training'] = results
        return results
    
    def test_model_export(self):
        """测试模型导出"""
        print("\n🧪 测试模型导出...")
        
        results = {}
        
        # 检查模型文件
        model_files = [
            "runs/train/blind_path/weights/best.pt",
            "runs/train/crosswalk/weights/best.pt",
            "runs/train/traffic_light/weights/best.pt"
        ]
        
        results['model_files'] = {}
        for model_file in model_files:
            if Path(model_file).exists():
                results['model_files'][model_file] = "✅ 存在"
                print(f"   模型文件 {model_file}: ✅ 存在")
            else:
                results['model_files'][model_file] = "❌ 不存在"
                print(f"   模型文件 {model_file}: ❌ 不存在")
        
        # 测试模型导出
        try:
            from ultralytics import YOLO
            
            # 创建测试模型
            model = YOLO('yolov8n.pt')
            
            # 测试ONNX导出
            model.export(format='onnx', imgsz=320, optimize=True)
            results['onnx_export'] = "✅ 成功"
            print("   ONNX导出: ✅ 成功")
            
        except Exception as e:
            results['onnx_export'] = f"❌ 失败: {e}"
            print(f"   ONNX导出: ❌ 失败 - {e}")
        
        self.test_results['model_export'] = results
        return results
    
    def test_performance(self):
        """测试性能"""
        print("\n🧪 测试性能...")
        
        results = {}
        
        # 测试GPU性能
        if torch.cuda.is_available():
            try:
                # 创建测试张量
                test_tensor = torch.randn(1, 3, 640, 640).cuda()
                
                # 测试矩阵乘法性能
                start_time = time.time()
                for _ in range(100):
                    _ = torch.mm(test_tensor.view(-1, 3*640*640), test_tensor.view(3*640*640, -1))
                torch.cuda.synchronize()
                end_time = time.time()
                
                results['gpu_performance'] = f"✅ {(end_time - start_time)/100*1000:.2f}ms/op"
                print(f"   GPU性能: {results['gpu_performance']}")
                
            except Exception as e:
                results['gpu_performance'] = f"❌ 错误: {e}"
                print(f"   GPU性能: ❌ 错误 - {e}")
        else:
            results['gpu_performance'] = "❌ 无GPU"
            print("   GPU性能: ❌ 无GPU")
        
        # 测试内存使用
        try:
            import psutil
            memory = psutil.virtual_memory()
            results['memory_usage'] = f"✅ {memory.percent:.1f}% 使用率"
            print(f"   内存使用: {results['memory_usage']}")
        except Exception as e:
            results['memory_usage'] = f"❌ 错误: {e}"
            print(f"   内存使用: ❌ 错误 - {e}")
        
        self.test_results['performance'] = results
        return results
    
    def generate_test_report(self):
        """生成测试报告"""
        print("\n📋 生成测试报告...")
        
        report = f"""
# AI智能眼镜训练脚本测试报告

## 测试时间
- 测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}
- 测试环境: {sys.platform}

## 环境配置测试
- Python版本: {self.test_results.get('environment', {}).get('python_version', '未知')}
- PyTorch版本: {self.test_results.get('environment', {}).get('torch_version', '未知')}
- CUDA版本: {self.test_results.get('environment', {}).get('cuda_version', '未知')}
- GPU数量: {self.test_results.get('environment', {}).get('gpu_count', 0)}
- GPU名称: {self.test_results.get('environment', {}).get('gpu_name', '未知')}

## 数据准备测试
- 测试图像创建: {self.test_results.get('data_preparation', {}).get('test_images_created', 0)} 张
- 数据准备成功: {self.test_results.get('data_preparation', {}).get('data_preparation_success', False)}
- 数据准备时间: {self.test_results.get('data_preparation', {}).get('data_preparation_time', 0):.2f} 秒

## 模型训练测试
- 快速训练成功: {self.test_results.get('model_training', {}).get('quick_train_success', False)}
- 快速训练时间: {self.test_results.get('model_training', {}).get('quick_train_time', 0):.2f} 秒
- 单模型训练成功: {self.test_results.get('model_training', {}).get('single_model_success', False)}
- 单模型训练时间: {self.test_results.get('model_training', {}).get('single_model_time', 0):.2f} 秒

## 模型导出测试
- ONNX导出: {self.test_results.get('model_export', {}).get('onnx_export', '未知')}

## 性能测试
- GPU性能: {self.test_results.get('performance', {}).get('gpu_performance', '未知')}
- 内存使用: {self.test_results.get('performance', {}).get('memory_usage', '未知')}

## 测试总结
"""
        
        # 计算成功率
        total_tests = 0
        passed_tests = 0
        
        for category, results in self.test_results.items():
            for test_name, result in results.items():
                if isinstance(result, bool):
                    total_tests += 1
                    if result:
                        passed_tests += 1
                elif isinstance(result, str) and result.startswith('✅'):
                    total_tests += 1
                    passed_tests += 1
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        report += f"""
- 总测试数: {total_tests}
- 通过测试: {passed_tests}
- 成功率: {success_rate:.1f}%

## 建议
"""
        
        if success_rate < 80:
            report += """
- 环境配置需要检查
- 依赖包需要安装
- 硬件配置需要升级
"""
        elif success_rate < 95:
            report += """
- 部分功能需要优化
- 性能需要提升
"""
        else:
            report += """
- 所有功能正常
- 可以开始训练
"""
        
        # 保存报告
        report_path = "test_output/test_report.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"✅ 测试报告已保存: {report_path}")
        return report_path

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='训练脚本测试')
    parser.add_argument('--test', type=str, choices=['all', 'environment', 'data', 'model', 'export', 'performance'], 
                       default='all', help='测试类型')
    
    args = parser.parse_args()
    
    print("🧪 AI智能眼镜训练脚本测试开始")
    print("=" * 50)
    
    # 创建测试器
    tester = TrainingTester()
    
    # 执行测试
    if args.test in ['all', 'environment']:
        tester.test_environment()
    
    if args.test in ['all', 'data']:
        tester.test_data_preparation()
    
    if args.test in ['all', 'model']:
        tester.test_model_training()
    
    if args.test in ['all', 'export']:
        tester.test_model_export()
    
    if args.test in ['all', 'performance']:
        tester.test_performance()
    
    # 生成测试报告
    report_path = tester.generate_test_report()
    
    print("\n🎉 测试完成!")
    print(f"   测试报告: {report_path}")
    print("   查看详细结果请打开测试报告")

if __name__ == "__main__":
    main()
