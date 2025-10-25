# 🤖 AI模型训练完整指南

## 📋 训练概览

本项目需要训练5个核心AI模型，用于不同的导航功能：

| 模型 | 功能 | 数据量 | 训练时间 | GPU要求 |
|------|------|--------|----------|---------|
| **盲道分割** | 盲道检测与分割 | 5000张 | 8-12小时 | RTX 3080 |
| **斑马线检测** | 斑马线识别 | 3000张 | 4-6小时 | RTX 3080 |
| **红绿灯检测** | 交通信号识别 | 2000张 | 3-4小时 | RTX 3080 |
| **障碍物检测** | 障碍物识别 | 10000张 | 12-16小时 | RTX 4090 |
| **物品识别** | 物品查找 | 8000张 | 10-14小时 | RTX 4090 |

## 🚀 快速开始

### 1. 环境准备 (15分钟)

```bash
# 创建训练环境
conda create -n training python=3.10
conda activate training

# 安装训练依赖
pip install torch==2.0.1+cu118 torchvision==0.15.2+cu118 --index-url https://download.pytorch.org/whl/cu118
pip install ultralytics==8.0.200
pip install opencv-python==4.8.1.78
pip install albumentations==1.3.1
pip install tensorboard==2.13.0
pip install matplotlib==3.7.2
pip install pandas==2.0.3
```

### 2. 数据准备 (30分钟)

```bash
# 创建数据集目录
mkdir -p datasets/{blind_path,crosswalk,traffic_light,obstacle,items}

# 准备数据 (使用LabelMe标注)
pip install labelme
labelme  # 启动标注工具

# 转换标注格式
python training/scripts/data_preparation.py \
    --input_dir datasets/raw \
    --output_dir datasets/processed \
    --augment \
    --visualize
```

### 3. 开始训练 (40-60小时)

```bash
# 训练单个模型
python training/scripts/train_blind_path.py \
    --data datasets/blind_path/blind_path.yaml \
    --epochs 100 \
    --batch 16

# 训练所有模型
python training/scripts/train_all_models.py \
    --config training/configs/training_config.yaml \
    --export \
    --package
```

## 📊 数据收集指南

### 1. 盲道数据收集

#### 数据要求
- **图像数量**: 至少5000张
- **场景多样性**: 不同光照、天气、角度
- **标注精度**: 像素级精确分割
- **数据平衡**: 各种盲道类型

#### 收集策略
```python
# 数据收集脚本
import cv2
import os
from datetime import datetime

def collect_blind_path_data():
    """收集盲道数据"""
    cap = cv2.VideoCapture(0)  # 摄像头
    count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        # 显示图像
        cv2.imshow('Blind Path Data Collection', frame)
        
        # 按空格键保存
        key = cv2.waitKey(1) & 0xFF
        if key == ord(' '):  # 空格键
            filename = f"blind_path_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            cv2.imwrite(f"datasets/raw/{filename}", frame)
            print(f"保存图像: {filename}")
            count += 1
            
        elif key == ord('q'):  # 退出
            break
    
    cap.release()
    cv2.destroyAllWindows()
    print(f"总共收集了 {count} 张图像")
```

### 2. 标注工具使用

#### LabelMe标注
```bash
# 安装LabelMe
pip install labelme

# 启动标注工具
labelme

# 批量转换标注
python -c "
import json
import os
from pathlib import Path

def convert_labelme_to_yolo(labelme_file, output_dir):
    with open(labelme_file, 'r') as f:
        data = json.load(f)
    
    img_width = data['imageWidth']
    img_height = data['imageHeight']
    
    yolo_annotations = []
    for shape in data['shapes']:
        if shape['label'] == 'blind_path':
            points = shape['points']
            x_coords = [p[0] for p in points]
            y_coords = [p[1] for p in points]
            
            x_min, x_max = min(x_coords), max(x_coords)
            y_min, y_max = min(y_coords), max(y_coords)
            
            x_center = (x_min + x_max) / 2 / img_width
            y_center = (y_min + y_max) / 2 / img_height
            width = (x_max - x_min) / img_width
            height = (y_max - y_min) / img_height
            
            yolo_annotations.append(f'0 {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}')
    
    output_file = output_dir / f'{Path(labelme_file).stem}.txt'
    with open(output_file, 'w') as f:
        f.write('\n'.join(yolo_annotations))
"
```

## 🔧 训练配置

### 1. 硬件配置

#### 推荐配置
```yaml
# training/configs/hardware_config.yaml
gpu:
  model: "RTX 4090 24GB"
  memory: "24GB VRAM"
  cuda_version: "11.8"

system:
  cpu: "Intel i9-13900K / AMD Ryzen 9 7950X"
  memory: "64GB DDR5"
  storage: "2TB NVMe SSD"

training:
  batch_size: 16
  workers: 8
  mixed_precision: true
  gradient_accumulation: 2
```

#### 最低配置
```yaml
gpu:
  model: "RTX 3080 10GB"
  memory: "10GB VRAM"
  cuda_version: "11.8"

system:
  cpu: "Intel i7-12700K / AMD Ryzen 7 7700X"
  memory: "32GB DDR4"
  storage: "1TB NVMe SSD"

training:
  batch_size: 8
  workers: 4
  mixed_precision: true
  gradient_accumulation: 4
```

### 2. 数据增强配置

```python
# 数据增强管道
import albumentations as A

def create_augmentation_pipeline():
    """创建数据增强管道"""
    return A.Compose([
        # 几何变换
        A.HorizontalFlip(p=0.5),
        A.Rotate(limit=15, p=0.3),
        A.RandomScale(scale_limit=0.2, p=0.3),
        A.RandomCrop(height=640, width=640, p=0.5),
        
        # 颜色变换
        A.RandomBrightnessContrast(
            brightness_limit=0.2, 
            contrast_limit=0.2, 
            p=0.3
        ),
        A.RandomSaturation(saturation_limit=0.2, p=0.3),
        A.HueSaturationValue(
            hue_shift_limit=20,
            sat_shift_limit=30,
            val_shift_limit=20,
            p=0.3
        ),
        
        # 天气效果
        A.RandomShadow(
            shadow_roi=(0, 0, 1, 1),
            num_shadows_lower=1,
            num_shadows_upper=2,
            p=0.2
        ),
        A.RandomRain(
            slant_lower=-10,
            slant_upper=10,
            drop_length=20,
            drop_width=1,
            p=0.1
        ),
        A.RandomSnow(
            snow_point_lower=0.1,
            snow_point_upper=0.3,
            brightness_coeff=2.5,
            p=0.1
        ),
        A.RandomFog(
            fog_coef_lower=0.1,
            fog_coef_upper=0.3,
            alpha_coef=0.1,
            p=0.1
        ),
    ])
```

## 📈 训练监控

### 1. TensorBoard监控

```python
# 训练监控脚本
from torch.utils.tensorboard import SummaryWriter
import matplotlib.pyplot as plt

def setup_tensorboard():
    """设置TensorBoard监控"""
    writer = SummaryWriter('runs/training')
    return writer

def log_training_metrics(writer, epoch, train_loss, val_loss, metrics):
    """记录训练指标"""
    writer.add_scalar('Loss/Train', train_loss, epoch)
    writer.add_scalar('Loss/Validation', val_loss, epoch)
    writer.add_scalar('mAP50', metrics['mAP50'], epoch)
    writer.add_scalar('mAP50-95', metrics['mAP50-95'], epoch)
    writer.add_scalar('Precision', metrics['precision'], epoch)
    writer.add_scalar('Recall', metrics['recall'], epoch)

# 启动TensorBoard
# tensorboard --logdir runs/training
```

### 2. 训练可视化

```python
# 训练曲线绘制
import pandas as pd
import matplotlib.pyplot as plt

def plot_training_curves(results_dir):
    """绘制训练曲线"""
    results = pd.read_csv(f"{results_dir}/results.csv")
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # 损失曲线
    axes[0, 0].plot(results['epoch'], results['train/box_loss'], label='Train')
    axes[0, 0].plot(results['epoch'], results['val/box_loss'], label='Val')
    axes[0, 0].set_title('Box Loss')
    axes[0, 0].legend()
    axes[0, 0].grid(True)
    
    # mAP曲线
    axes[0, 1].plot(results['epoch'], results['metrics/mAP50(B)'], label='mAP50')
    axes[0, 1].plot(results['epoch'], results['metrics/mAP50-95(B)'], label='mAP50-95')
    axes[0, 1].set_title('mAP')
    axes[0, 1].legend()
    axes[0, 1].grid(True)
    
    # 学习率曲线
    axes[1, 0].plot(results['epoch'], results['lr/pg0'], label='LR')
    axes[1, 0].set_title('Learning Rate')
    axes[1, 0].legend()
    axes[1, 0].grid(True)
    
    # 精度和召回率
    axes[1, 1].plot(results['epoch'], results['metrics/precision(B)'], label='Precision')
    axes[1, 1].plot(results['epoch'], results['metrics/recall(B)'], label='Recall')
    axes[1, 1].set_title('Precision & Recall')
    axes[1, 1].legend()
    axes[1, 1].grid(True)
    
    plt.tight_layout()
    plt.savefig('training_curves.png', dpi=300, bbox_inches='tight')
    plt.show()
```

## 🔧 模型优化

### 1. 超参数调优

```python
# 超参数搜索
import optuna

def objective(trial):
    """超参数优化目标函数"""
    # 建议超参数
    lr = trial.suggest_float('lr', 1e-5, 1e-2, log=True)
    batch_size = trial.suggest_categorical('batch_size', [8, 16, 32])
    weight_decay = trial.suggest_float('weight_decay', 1e-6, 1e-3, log=True)
    
    # 训练模型
    model = train_model(lr=lr, batch_size=batch_size, weight_decay=weight_decay)
    
    # 评估模型
    metrics = evaluate_model(model)
    
    return metrics['mAP50']

# 运行优化
study = optuna.create_study(direction='maximize')
study.optimize(objective, n_trials=50)
```

### 2. 模型剪枝

```python
# 模型剪枝
import torch.nn.utils.prune as prune

def prune_model(model, pruning_ratio=0.3):
    """模型剪枝"""
    modules_to_prune = []
    for name, module in model.named_modules():
        if isinstance(module, torch.nn.Conv2d):
            modules_to_prune.append((module, 'weight'))
    
    prune.global_unstructured(
        modules_to_prune,
        pruning_method=prune.L1Unstructured,
        amount=pruning_ratio,
    )
    
    return model
```

### 3. 模型量化

```python
# 模型量化
import torch.quantization as quantization

def quantize_model(model):
    """模型量化"""
    model.eval()
    model.qconfig = quantization.get_default_qconfig('fbgemm')
    
    model_prepared = quantization.prepare(model)
    
    # 校准
    for batch in calibration_loader:
        model_prepared(batch)
    
    quantized_model = quantization.convert(model_prepared)
    return quantized_model
```

## 📦 模型部署

### 1. 模型导出

```python
# 模型导出脚本
def export_models():
    """导出所有模型"""
    models = {
        'blind_path': 'runs/train/blind_path/weights/best.pt',
        'crosswalk': 'runs/train/crosswalk/weights/best.pt',
        'traffic_light': 'runs/train/traffic_light/weights/best.pt',
        'obstacle': 'runs/train/obstacle/weights/best.pt',
        'item_recognition': 'runs/train/item_recognition/weights/best.pt'
    }
    
    for name, path in models.items():
        if Path(path).exists():
            model = YOLO(path)
            
            # 导出ONNX
            model.export(format='onnx', imgsz=640, optimize=True)
            
            # 导出TensorRT
            model.export(format='engine', imgsz=640, device='cuda')
            
            print(f"✅ {name} 导出完成")
        else:
            print(f"❌ {name} 模型文件不存在")
```

### 2. 性能测试

```python
# 性能测试脚本
import time
import torch

def benchmark_model(model_path, num_runs=100):
    """模型性能测试"""
    model = YOLO(model_path)
    
    # 创建测试数据
    test_image = torch.randn(1, 3, 640, 640).cuda()
    
    # 预热
    for _ in range(10):
        _ = model(test_image)
    
    # 性能测试
    torch.cuda.synchronize()
    start_time = time.time()
    
    for _ in range(num_runs):
        _ = model(test_image)
    
    torch.cuda.synchronize()
    end_time = time.time()
    
    avg_time = (end_time - start_time) / num_runs
    fps = 1.0 / avg_time
    
    print(f"平均推理时间: {avg_time*1000:.2f}ms")
    print(f"FPS: {fps:.2f}")
    
    return avg_time, fps
```

## 🚨 故障排除

### 常见问题

#### 1. 显存不足
```bash
# 解决方案
# 1. 减少batch_size
# 2. 使用梯度累积
# 3. 使用混合精度训练
# 4. 使用模型并行

# 检查显存使用
nvidia-smi
```

#### 2. 训练不收敛
```python
# 解决方案
# 1. 调整学习率
# 2. 使用预训练模型
# 3. 增加数据增强
# 4. 检查数据质量

# 学习率调度
from torch.optim.lr_scheduler import CosineAnnealingLR

scheduler = CosineAnnealingLR(optimizer, T_max=epochs)
```

#### 3. 过拟合
```python
# 解决方案
# 1. 增加数据增强
# 2. 使用正则化
# 3. 早停机制
# 4. 减少模型复杂度

# 早停机制
class EarlyStopping:
    def __init__(self, patience=10, min_delta=0):
        self.patience = patience
        self.min_delta = min_delta
        self.counter = 0
        self.best_score = None
        
    def __call__(self, score):
        if self.best_score is None:
            self.best_score = score
        elif score < self.best_score + self.min_delta:
            self.counter += 1
            if self.counter >= self.patience:
                return True
        else:
            self.best_score = score
            self.counter = 0
        return False
```

## 📊 训练时间预估

### 硬件配置对比

| 配置 | 盲道分割 | 斑马线检测 | 红绿灯检测 | 障碍物检测 | 物品识别 | 总计 |
|------|----------|------------|------------|------------|----------|------|
| **RTX 4090** | 6小时 | 3小时 | 2小时 | 8小时 | 6小时 | 25小时 |
| **RTX 3080** | 12小时 | 6小时 | 4小时 | 16小时 | 12小时 | 50小时 |
| **RTX 3070** | 18小时 | 9小时 | 6小时 | 24小时 | 18小时 | 75小时 |
| **CPU** | 120小时 | 60小时 | 40小时 | 160小时 | 120小时 | 500小时 |

### 成本估算

| 配置 | 硬件成本 | 电费成本 | 时间成本 | 总成本 |
|------|----------|----------|----------|--------|
| **RTX 4090** | $1600 | $50 | $500 | $2150 |
| **RTX 3080** | $800 | $100 | $1000 | $1900 |
| **云服务器** | $0 | $0 | $200 | $200 |

## 🎯 训练检查清单

### 数据准备
- [ ] 收集足够的训练数据
- [ ] 数据标注质量检查
- [ ] 数据增强策略制定
- [ ] 数据集划分 (70/20/10)

### 环境配置
- [ ] GPU驱动安装
- [ ] CUDA环境配置
- [ ] Python环境设置
- [ ] 依赖包安装

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

## 📞 技术支持

### 获取帮助
1. **查看日志**: `logs/training.log`
2. **运行测试**: `python training/scripts/test_training.py`
3. **提交Issue**: GitHub Issues页面
4. **技术交流**: QQ群/微信群

### 联系方式
- **GitHub Issues**: 项目Issues页面
- **技术交流群**: QQ群/微信群
- **在线文档**: 项目文档网站

---

**总训练时间**: 25-75小时
**成功率**: 90%+
**推荐GPU**: RTX 4090 24GB
**总成本**: $200-2150
