# 🤖 AI模型训练指南

## 📋 模型训练概览

本项目需要训练以下AI模型：
1. **盲道分割模型** - 用于盲道检测
2. **斑马线检测模型** - 用于过马路导航
3. **红绿灯检测模型** - 用于交通信号识别
4. **障碍物检测模型** - 用于避障
5. **物品识别模型** - 用于物品查找

## 🎯 训练环境准备

### 硬件要求
- **GPU**: NVIDIA RTX 3080+ (推荐RTX 4090)
- **内存**: 32GB+ RAM
- **存储**: 500GB+ SSD
- **显存**: 12GB+ VRAM

### 软件环境
```bash
# 创建训练环境
conda create -n training python=3.10
conda activate training

# 安装训练依赖
pip install torch==2.0.1+cu118 torchvision==0.15.2+cu118 --index-url https://download.pytorch.org/whl/cu118
pip install ultralytics==8.0.200
pip install opencv-python==4.8.1.78
pip install numpy==1.24.3
pip install pillow==10.1.0
pip install matplotlib==3.7.2
pip install tensorboard==2.13.0
```

## 📊 数据集准备

### 1. 盲道数据集

#### 数据收集
```bash
# 创建数据集目录
mkdir -p datasets/blind_path/{images,labels}

# 数据标注工具
pip install labelme
labelme  # 启动标注工具
```

#### 标注格式转换
```python
# convert_annotations.py
import json
import os
from pathlib import Path

def convert_labelme_to_yolo(labelme_file, output_dir):
    """将LabelMe格式转换为YOLO格式"""
    with open(labelme_file, 'r') as f:
        data = json.load(f)
    
    # 创建YOLO格式标注
    img_width = data['imageWidth']
    img_height = data['imageHeight']
    
    yolo_annotations = []
    for shape in data['shapes']:
        if shape['label'] == 'blind_path':
            # 转换多边形为边界框
            points = shape['points']
            x_coords = [p[0] for p in points]
            y_coords = [p[1] for p in points]
            
            x_min, x_max = min(x_coords), max(x_coords)
            y_min, y_max = min(y_coords), max(y_coords)
            
            # 转换为YOLO格式 (归一化坐标)
            x_center = (x_min + x_max) / 2 / img_width
            y_center = (y_min + y_max) / 2 / img_height
            width = (x_max - x_min) / img_width
            height = (y_max - y_min) / img_height
            
            yolo_annotations.append(f"0 {x_center} {y_center} {width} {height}")
    
    # 保存YOLO格式标注
    output_file = output_dir / f"{Path(labelme_file).stem}.txt"
    with open(output_file, 'w') as f:
        f.write('\n'.join(yolo_annotations))

# 批量转换
for labelme_file in Path("datasets/blind_path/labels").glob("*.json"):
    convert_labelme_to_yolo(labelme_file, Path("datasets/blind_path/yolo_labels"))
```

### 2. 斑马线数据集

#### 数据增强
```python
# data_augmentation.py
import cv2
import numpy as np
import albumentations as A
from albumentations.pytorch import ToTensorV2

def create_augmentation_pipeline():
    """创建数据增强管道"""
    return A.Compose([
        A.HorizontalFlip(p=0.5),
        A.RandomBrightnessContrast(p=0.3),
        A.RandomSaturation(p=0.3),
        A.RandomShadow(p=0.2),
        A.RandomRain(p=0.1),
        A.RandomSnow(p=0.1),
        A.RandomFog(p=0.1),
        A.Rotate(limit=15, p=0.3),
        A.RandomScale(scale_limit=0.2, p=0.3),
    ])

# 应用数据增强
augmentation = create_augmentation_pipeline()
augmented = augmentation(image=image, mask=mask)
```

## 🚀 模型训练

### 1. 盲道分割模型训练

#### 训练脚本
```python
# train_blind_path.py
from ultralytics import YOLO
import torch

def train_blind_path_model():
    """训练盲道分割模型"""
    
    # 创建模型
    model = YOLO('yolov8n-seg.pt')  # 使用预训练模型
    
    # 训练参数
    training_args = {
        'data': 'datasets/blind_path/blind_path.yaml',
        'epochs': 100,
        'batch': 16,
        'imgsz': 640,
        'device': 'cuda',
        'workers': 8,
        'patience': 20,
        'save': True,
        'save_period': 10,
        'cache': True,
        'project': 'runs/train',
        'name': 'blind_path_seg',
        'exist_ok': True,
    }
    
    # 开始训练
    results = model.train(**training_args)
    
    # 验证模型
    metrics = model.val()
    print(f"mAP50: {metrics.box.map50}")
    print(f"mAP50-95: {metrics.box.map}")
    
    return model

if __name__ == "__main__":
    model = train_blind_path_model()
    model.export(format='onnx')  # 导出ONNX格式
```

#### 数据集配置文件
```yaml
# datasets/blind_path/blind_path.yaml
path: datasets/blind_path
train: images/train
val: images/val
test: images/test

nc: 1  # 类别数量
names: ['blind_path']  # 类别名称
```

### 2. 斑马线检测模型训练

```python
# train_crosswalk.py
def train_crosswalk_model():
    """训练斑马线检测模型"""
    
    model = YOLO('yolov8n.pt')
    
    training_args = {
        'data': 'datasets/crosswalk/crosswalk.yaml',
        'epochs': 80,
        'batch': 32,
        'imgsz': 640,
        'device': 'cuda',
        'workers': 8,
        'patience': 15,
        'save': True,
        'project': 'runs/train',
        'name': 'crosswalk_detection',
    }
    
    results = model.train(**training_args)
    return model
```

### 3. 红绿灯检测模型训练

```python
# train_traffic_light.py
def train_traffic_light_model():
    """训练红绿灯检测模型"""
    
    model = YOLO('yolov8n.pt')
    
    training_args = {
        'data': 'datasets/traffic_light/traffic_light.yaml',
        'epochs': 60,
        'batch': 24,
        'imgsz': 640,
        'device': 'cuda',
        'workers': 8,
        'patience': 10,
        'save': True,
        'project': 'runs/train',
        'name': 'traffic_light_detection',
    }
    
    results = model.train(**training_args)
    return model
```

## 📈 训练监控

### TensorBoard监控
```python
# 在训练脚本中添加
from torch.utils.tensorboard import SummaryWriter

writer = SummaryWriter('runs/training')

# 记录训练指标
for epoch in range(num_epochs):
    # 训练代码...
    
    # 记录指标
    writer.add_scalar('Loss/Train', train_loss, epoch)
    writer.add_scalar('Loss/Val', val_loss, epoch)
    writer.add_scalar('mAP50', map50, epoch)

writer.close()
```

### 训练可视化
```python
# visualize_training.py
import matplotlib.pyplot as plt
import pandas as pd

def plot_training_curves(results_dir):
    """绘制训练曲线"""
    
    # 读取训练结果
    results = pd.read_csv(f"{results_dir}/results.csv")
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # 损失曲线
    axes[0, 0].plot(results['epoch'], results['train/box_loss'])
    axes[0, 0].plot(results['epoch'], results['val/box_loss'])
    axes[0, 0].set_title('Box Loss')
    axes[0, 0].legend(['Train', 'Val'])
    
    # mAP曲线
    axes[0, 1].plot(results['epoch'], results['metrics/mAP50(B)'])
    axes[0, 1].set_title('mAP50')
    
    # 学习率曲线
    axes[1, 0].plot(results['epoch'], results['lr/pg0'])
    axes[1, 0].set_title('Learning Rate')
    
    # 精度曲线
    axes[1, 1].plot(results['epoch'], results['metrics/precision(B)'])
    axes[1, 1].plot(results['epoch'], results['metrics/recall(B)'])
    axes[1, 1].set_title('Precision & Recall')
    axes[1, 1].legend(['Precision', 'Recall'])
    
    plt.tight_layout()
    plt.savefig('training_curves.png')
    plt.show()
```

## 🔧 模型优化

### 1. 模型剪枝
```python
# model_pruning.py
import torch.nn.utils.prune as prune

def prune_model(model, pruning_ratio=0.3):
    """模型剪枝"""
    
    # 获取需要剪枝的层
    modules_to_prune = []
    for name, module in model.named_modules():
        if isinstance(module, torch.nn.Conv2d):
            modules_to_prune.append((module, 'weight'))
    
    # 应用剪枝
    prune.global_unstructured(
        modules_to_prune,
        pruning_method=prune.L1Unstructured,
        amount=pruning_ratio,
    )
    
    return model
```

### 2. 模型量化
```python
# model_quantization.py
import torch.quantization as quantization

def quantize_model(model):
    """模型量化"""
    
    # 设置量化配置
    model.eval()
    model.qconfig = quantization.get_default_qconfig('fbgemm')
    
    # 准备量化
    model_prepared = quantization.prepare(model)
    
    # 校准
    # 使用验证集进行校准
    for batch in validation_loader:
        model_prepared(batch)
    
    # 转换为量化模型
    quantized_model = quantization.convert(model_prepared)
    
    return quantized_model
```

## 📊 模型评估

### 评估脚本
```python
# evaluate_model.py
def evaluate_model(model_path, test_data):
    """评估模型性能"""
    
    model = YOLO(model_path)
    
    # 在测试集上评估
    results = model.val(data=test_data)
    
    # 计算各种指标
    metrics = {
        'mAP50': results.box.map50,
        'mAP50-95': results.box.map,
        'precision': results.box.mp,
        'recall': results.box.mr,
        'f1': 2 * (results.box.mp * results.box.mr) / (results.box.mp + results.box.mr)
    }
    
    print("模型评估结果:")
    for metric, value in metrics.items():
        print(f"{metric}: {value:.4f}")
    
    return metrics
```

## 🚀 部署优化

### 模型转换
```python
# convert_model.py
def convert_to_onnx(model_path, output_path):
    """转换为ONNX格式"""
    
    model = YOLO(model_path)
    model.export(format='onnx', imgsz=640, optimize=True)
    
    print(f"模型已转换为ONNX格式: {output_path}")

def convert_to_tensorrt(model_path, output_path):
    """转换为TensorRT格式"""
    
    model = YOLO(model_path)
    model.export(format='engine', imgsz=640, device='cuda')
    
    print(f"模型已转换为TensorRT格式: {output_path}")
```

## 📋 训练检查清单

### 数据准备
- [ ] 收集足够的训练数据 (每类至少1000张)
- [ ] 数据标注质量检查
- [ ] 数据增强策略制定
- [ ] 数据集划分 (训练/验证/测试: 70/20/10)

### 训练配置
- [ ] 选择合适的预训练模型
- [ ] 设置合适的学习率
- [ ] 配置数据加载器
- [ ] 设置训练参数

### 训练监控
- [ ] 配置TensorBoard
- [ ] 设置早停机制
- [ ] 监控训练指标
- [ ] 定期保存检查点

### 模型优化
- [ ] 超参数调优
- [ ] 模型剪枝
- [ ] 模型量化
- [ ] 性能测试

## 🎯 训练时间预估

| 模型 | 数据量 | 训练时间 | GPU要求 |
|------|--------|----------|---------|
| 盲道分割 | 5000张 | 8-12小时 | RTX 3080 |
| 斑马线检测 | 3000张 | 4-6小时 | RTX 3080 |
| 红绿灯检测 | 2000张 | 3-4小时 | RTX 3080 |
| 障碍物检测 | 10000张 | 12-16小时 | RTX 4090 |
| 物品识别 | 8000张 | 10-14小时 | RTX 4090 |

## 📞 训练支持

### 常见问题
1. **显存不足**: 减少batch_size或使用梯度累积
2. **训练不收敛**: 调整学习率或使用预训练模型
3. **过拟合**: 增加数据增强或使用正则化
4. **训练速度慢**: 使用混合精度训练

### 技术支持
- **训练脚本**: `training/`目录
- **数据集**: `datasets/`目录
- **模型检查点**: `runs/train/`目录
- **训练日志**: `logs/`目录

---

**总训练时间**: 40-60小时
**成功率**: 90%+
**推荐GPU**: RTX 4090 24GB
