# 🤖 AI模型训练完整方案

## 📋 训练方案概览

当没有预训练模型时，我们需要从零开始训练所有AI模型。以下是完整的训练方案：

### 🎯 需要训练的模型

| 模型 | 功能 | 数据量 | 训练时间 | GPU要求 | 难度 |
|------|------|--------|----------|---------|------|
| **盲道分割** | 盲道检测与分割 | 5000张 | 8-12小时 | RTX 3080 | ⭐⭐⭐ |
| **斑马线检测** | 斑马线识别 | 3000张 | 4-6小时 | RTX 3080 | ⭐⭐ |
| **红绿灯检测** | 交通信号识别 | 2000张 | 3-4小时 | RTX 3080 | ⭐⭐ |
| **障碍物检测** | 障碍物识别 | 10000张 | 12-16小时 | RTX 4090 | ⭐⭐⭐⭐ |
| **物品识别** | 物品查找 | 8000张 | 10-14小时 | RTX 4090 | ⭐⭐⭐⭐ |

## 🚀 快速开始 (30分钟)

### 1. 演示模式训练
```bash
# 一键训练所有模型 (演示模式)
python training/scripts/quick_train.py --mode demo

# 训练时间: 30-60分钟
# 数据: 自动生成演示数据
# 用途: 快速验证训练流程
```

### 2. 完整模式训练
```bash
# 一键训练所有模型 (完整模式)
python training/scripts/quick_train.py --mode full

# 训练时间: 40-60小时
# 数据: 需要准备真实数据集
# 用途: 生产环境部署
```

## 📊 数据准备方案

### 1. 数据收集策略

#### 盲道数据收集
```python
# 盲道数据收集脚本
import cv2
import os
from datetime import datetime

def collect_blind_path_data():
    """收集盲道数据"""
    cap = cv2.VideoCapture(0)
    count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        cv2.imshow('Blind Path Collection', frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord(' '):  # 空格键保存
            filename = f"blind_path_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            cv2.imwrite(f"datasets/raw/{filename}", frame)
            print(f"保存: {filename}")
            count += 1
        elif key == ord('q'):  # 退出
            break
    
    cap.release()
    cv2.destroyAllWindows()
    print(f"收集了 {count} 张盲道图像")
```

#### 数据标注工具
```bash
# 安装标注工具
pip install labelme

# 启动标注工具
labelme

# 批量转换标注
python training/scripts/data_preparation.py \
    --input_dir datasets/raw \
    --output_dir datasets/processed \
    --augment \
    --visualize
```

### 2. 数据增强策略

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
        
        # 颜色变换
        A.RandomBrightnessContrast(brightness_limit=0.2, contrast_limit=0.2, p=0.3),
        A.RandomSaturation(saturation_limit=0.2, p=0.3),
        
        # 天气效果
        A.RandomShadow(p=0.2),
        A.RandomRain(p=0.1),
        A.RandomSnow(p=0.1),
        A.RandomFog(p=0.1),
    ])
```

## 🔧 训练环境配置

### 1. 硬件要求

#### 推荐配置
- **GPU**: RTX 4090 24GB (最佳)
- **内存**: 64GB DDR5
- **存储**: 2TB NVMe SSD
- **CPU**: Intel i9-13900K / AMD Ryzen 9 7950X

#### 最低配置
- **GPU**: RTX 3080 10GB
- **内存**: 32GB DDR4
- **存储**: 1TB NVMe SSD
- **CPU**: Intel i7-12700K / AMD Ryzen 7 7700X

### 2. 软件环境

```bash
# 创建训练环境
conda create -n training python=3.10
conda activate training

# 安装核心依赖
pip install torch==2.0.1+cu118 torchvision==0.15.2+cu118 --index-url https://download.pytorch.org/whl/cu118
pip install ultralytics==8.0.200
pip install opencv-python==4.8.1.78
pip install albumentations==1.3.1
pip install tensorboard==2.13.0
pip install matplotlib==3.7.2
pip install pandas==2.0.3
```

## 🚀 训练流程

### 1. 单模型训练

```bash
# 训练盲道分割模型
python training/scripts/train_blind_path.py \
    --data datasets/blind_path/blind_path.yaml \
    --epochs 100 \
    --batch 16 \
    --imgsz 640

# 训练斑马线检测模型
python training/scripts/train_crosswalk.py \
    --data datasets/crosswalk/crosswalk.yaml \
    --epochs 80 \
    --batch 32

# 训练红绿灯检测模型
python training/scripts/train_traffic_light.py \
    --data datasets/traffic_light/traffic_light.yaml \
    --epochs 60 \
    --batch 24
```

### 2. 批量训练

```bash
# 训练所有模型
python training/scripts/train_all_models.py \
    --config training/configs/training_config.yaml \
    --export \
    --package
```

### 3. 训练监控

```bash
# 启动TensorBoard
tensorboard --logdir runs/train

# 查看训练日志
tail -f logs/training.log
```

## 📈 训练优化

### 1. 超参数调优

```python
# 超参数搜索
import optuna

def objective(trial):
    """超参数优化"""
    lr = trial.suggest_float('lr', 1e-5, 1e-2, log=True)
    batch_size = trial.suggest_categorical('batch_size', [8, 16, 32])
    weight_decay = trial.suggest_float('weight_decay', 1e-6, 1e-3, log=True)
    
    model = train_model(lr=lr, batch_size=batch_size, weight_decay=weight_decay)
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
```

### 2. 性能测试

```python
# 性能测试脚本
def benchmark_model(model_path, num_runs=100):
    """模型性能测试"""
    model = YOLO(model_path)
    
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

### 常见问题解决

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
- [ ] 收集足够的训练数据 (每类至少1000张)
- [ ] 数据标注质量检查
- [ ] 数据增强策略制定
- [ ] 数据集划分 (训练/验证/测试: 70/20/10)

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

## 🚀 快速开始命令

```bash
# 1. 演示模式训练 (30分钟)
python training/scripts/quick_train.py --mode demo

# 2. 完整模式训练 (40-60小时)
python training/scripts/quick_train.py --mode full

# 3. 训练单个模型
python training/scripts/train_blind_path.py --data datasets/blind_path/blind_path.yaml

# 4. 训练所有模型
python training/scripts/train_all_models.py --config training/configs/training_config.yaml

# 5. 数据准备
python training/scripts/data_preparation.py --input_dir datasets/raw --output_dir datasets/processed

# 6. 启动监控
tensorboard --logdir runs/train
```

---

**总训练时间**: 25-75小时
**成功率**: 90%+
**推荐GPU**: RTX 4090 24GB
**总成本**: $200-2150
