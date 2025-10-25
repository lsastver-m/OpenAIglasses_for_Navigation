# 🤖 AI模型训练模块

## 📋 模块概览

本模块提供完整的AI模型训练解决方案，包括数据准备、模型训练、优化和部署。

## 🚀 快速开始

### 1. 演示模式 (30分钟)
```bash
# 一键训练所有模型 (演示模式)
python training/scripts/quick_train.py --mode demo
```

### 2. 完整模式 (40-60小时)
```bash
# 一键训练所有模型 (完整模式)
python training/scripts/quick_train.py --mode full
```

## 📁 目录结构

```
training/
├── scripts/                 # 训练脚本
│   ├── quick_train.py      # 快速训练脚本
│   ├── train_blind_path.py # 盲道分割训练
│   ├── train_crosswalk.py  # 斑马线检测训练
│   ├── train_traffic_light.py # 红绿灯检测训练
│   ├── train_obstacle.py   # 障碍物检测训练
│   ├── train_item_recognition.py # 物品识别训练
│   ├── train_all_models.py # 批量训练脚本
│   └── data_preparation.py # 数据准备脚本
├── configs/                # 配置文件
│   ├── training_config.yaml # 训练配置
│   ├── hardware_config.yaml # 硬件配置
│   └── augmentation_config.yaml # 数据增强配置
├── datasets/               # 数据集目录
│   ├── blind_path/         # 盲道数据集
│   ├── crosswalk/          # 斑马线数据集
│   ├── traffic_light/      # 红绿灯数据集
│   ├── obstacle/           # 障碍物数据集
│   └── items/              # 物品数据集
└── README.md               # 本文件
```

## 🔧 脚本说明

### 1. 快速训练脚本

#### `quick_train.py` - 一键训练
```bash
# 演示模式 (快速验证)
python training/scripts/quick_train.py --mode demo

# 完整模式 (生产训练)
python training/scripts/quick_train.py --mode full

# 指定模型训练
python training/scripts/quick_train.py --mode demo --models blind_path crosswalk
```

**功能特点:**
- 自动环境检测
- 演示数据生成
- 批量模型训练
- 训练结果汇总
- 自动报告生成

### 2. 单模型训练脚本

#### `train_blind_path.py` - 盲道分割训练
```bash
python training/scripts/train_blind_path.py \
    --data datasets/blind_path/blind_path.yaml \
    --epochs 100 \
    --batch 16 \
    --imgsz 640
```

**功能特点:**
- 盲道分割模型训练
- 实时训练监控
- 自动模型导出
- 训练曲线绘制

#### `train_crosswalk.py` - 斑马线检测训练
```bash
python training/scripts/train_crosswalk.py \
    --data datasets/crosswalk/crosswalk.yaml \
    --epochs 80 \
    --batch 32
```

#### `train_traffic_light.py` - 红绿灯检测训练
```bash
python training/scripts/train_traffic_light.py \
    --data datasets/traffic_light/traffic_light.yaml \
    --epochs 60 \
    --batch 24
```

#### `train_obstacle.py` - 障碍物检测训练
```bash
python training/scripts/train_obstacle.py \
    --data datasets/obstacle/obstacle.yaml \
    --epochs 120 \
    --batch 20
```

#### `train_item_recognition.py` - 物品识别训练
```bash
python training/scripts/train_item_recognition.py \
    --data datasets/items/items.yaml \
    --epochs 100 \
    --batch 24
```

### 3. 批量训练脚本

#### `train_all_models.py` - 批量训练
```bash
python training/scripts/train_all_models.py \
    --config training/configs/training_config.yaml \
    --export \
    --package
```

**功能特点:**
- 批量模型训练
- 训练进度监控
- 自动模型导出
- 部署包创建

### 4. 数据准备脚本

#### `data_preparation.py` - 数据准备
```bash
python training/scripts/data_preparation.py \
    --input_dir datasets/raw \
    --output_dir datasets/processed \
    --augment \
    --visualize
```

**功能特点:**
- 数据格式转换
- 数据增强
- 数据集划分
- 数据可视化

## ⚙️ 配置文件

### 1. 训练配置 (`training_config.yaml`)

```yaml
# 模型训练配置
models:
  blind_path:
    data: "datasets/blind_path/blind_path.yaml"
    model: "yolov8n-seg.pt"
    epochs: 100
    batch: 16
    imgsz: 640
    device: "cuda"
    workers: 8
    patience: 20
    save_period: 10
    description: "盲道检测和分割模型"
```

### 2. 硬件配置 (`hardware_config.yaml`)

```yaml
# 硬件配置
gpu:
  model: "RTX 4090 24GB"
  memory: "24GB VRAM"
  cuda_version: "11.8"

system:
  cpu: "Intel i9-13900K"
  memory: "64GB DDR5"
  storage: "2TB NVMe SSD"
```

### 3. 数据增强配置 (`augmentation_config.yaml`)

```yaml
# 数据增强配置
augmentation:
  hsv_h: 0.015
  hsv_s: 0.7
  hsv_v: 0.4
  degrees: 0.0
  translate: 0.1
  scale: 0.5
  shear: 0.0
  perspective: 0.0
  flipud: 0.0
  fliplr: 0.5
  mosaic: 1.0
  mixup: 0.0
  copy_paste: 0.0
```

## 📊 训练监控

### 1. TensorBoard监控
```bash
# 启动TensorBoard
tensorboard --logdir runs/train

# 访问地址: http://localhost:6006
```

### 2. 训练日志
```bash
# 查看训练日志
tail -f logs/training.log

# 查看特定模型日志
tail -f runs/train/blind_path/train.log
```

### 3. 训练曲线
```bash
# 训练完成后自动生成
# 位置: runs/train/{model_name}/training_curves.png
```

## 🔧 环境配置

### 1. 硬件要求

#### 推荐配置
- **GPU**: RTX 4090 24GB
- **内存**: 64GB DDR5
- **存储**: 2TB NVMe SSD
- **CPU**: Intel i9-13900K

#### 最低配置
- **GPU**: RTX 3080 10GB
- **内存**: 32GB DDR4
- **存储**: 1TB NVMe SSD
- **CPU**: Intel i7-12700K

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

## 📈 训练流程

### 1. 数据准备阶段
```bash
# 1. 收集数据
python training/scripts/data_collection.py

# 2. 标注数据
labelme

# 3. 数据预处理
python training/scripts/data_preparation.py \
    --input_dir datasets/raw \
    --output_dir datasets/processed \
    --augment \
    --visualize
```

### 2. 模型训练阶段
```bash
# 1. 演示模式 (快速验证)
python training/scripts/quick_train.py --mode demo

# 2. 完整模式 (生产训练)
python training/scripts/quick_train.py --mode full

# 3. 单模型训练
python training/scripts/train_blind_path.py \
    --data datasets/blind_path/blind_path.yaml
```

### 3. 模型优化阶段
```bash
# 1. 模型评估
python training/scripts/evaluate_models.py

# 2. 模型优化
python training/scripts/optimize_models.py

# 3. 模型导出
python training/scripts/export_models.py
```

### 4. 模型部署阶段
```bash
# 1. 创建部署包
python training/scripts/create_deployment_package.py

# 2. 性能测试
python training/scripts/benchmark_models.py

# 3. 部署到生产环境
python training/scripts/deploy_models.py
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
```

#### 3. 过拟合
```python
# 解决方案
# 1. 增加数据增强
# 2. 使用正则化
# 3. 早停机制
# 4. 减少模型复杂度
```

### 调试工具

```bash
# 1. 检查环境
python training/scripts/check_environment.py

# 2. 测试数据
python training/scripts/test_data.py

# 3. 测试模型
python training/scripts/test_model.py

# 4. 性能分析
python training/scripts/analyze_performance.py
```

## 📊 训练时间预估

| 配置 | 盲道分割 | 斑马线检测 | 红绿灯检测 | 障碍物检测 | 物品识别 | 总计 |
|------|----------|------------|------------|------------|----------|------|
| **RTX 4090** | 6小时 | 3小时 | 2小时 | 8小时 | 6小时 | 25小时 |
| **RTX 3080** | 12小时 | 6小时 | 4小时 | 16小时 | 12小时 | 50小时 |
| **RTX 3070** | 18小时 | 9小时 | 6小时 | 24小时 | 18小时 | 75小时 |
| **CPU** | 120小时 | 60小时 | 40小时 | 160小时 | 120小时 | 500小时 |

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
