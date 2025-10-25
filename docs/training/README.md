# 🤖 AI模型训练文档

## 📋 文档概览

本目录包含AI智能眼镜导航系统的所有模型训练相关文档。

## 📁 文档结构

### 核心训练文档
- **[MODEL_TRAINING.md](./MODEL_TRAINING.md)** - 完整的AI模型训练指南
- **[MODEL_TRAINING_SUMMARY.md](./MODEL_TRAINING_SUMMARY.md)** - 模型训练方案总结
- **[TRAINING_GUIDE.md](./TRAINING_GUIDE.md)** - 详细的训练流程指南
- **[README.md](./README.md)** - 训练模块说明

## 🚀 快速开始

### 1. 演示模式训练 (30分钟)
```bash
# 一键训练所有模型 (演示模式)
python training/scripts/quick_train.py --mode demo
```

### 2. 完整模式训练 (40-60小时)
```bash
# 一键训练所有模型 (完整模式)
python training/scripts/quick_train.py --mode full
```

## 📊 需要训练的模型

| 模型 | 功能 | 数据量 | 训练时间 | GPU要求 | 难度 |
|------|------|--------|----------|---------|------|
| **盲道分割** | 盲道检测与分割 | 5000张 | 8-12小时 | RTX 3080 | ⭐⭐⭐ |
| **斑马线检测** | 斑马线识别 | 3000张 | 4-6小时 | RTX 3080 | ⭐⭐ |
| **红绿灯检测** | 交通信号识别 | 2000张 | 3-4小时 | RTX 3080 | ⭐⭐ |
| **障碍物检测** | 障碍物识别 | 10000张 | 12-16小时 | RTX 4090 | ⭐⭐⭐⭐ |
| **物品识别** | 物品查找 | 8000张 | 10-14小时 | RTX 4090 | ⭐⭐⭐⭐ |

## 🔧 训练脚本

### 快速训练
- `quick_train.py` - 一键训练所有模型
- `train_all_models.py` - 批量训练脚本
- `test_training.py` - 训练测试脚本

### 单模型训练
- `train_blind_path.py` - 盲道分割训练
- `train_crosswalk.py` - 斑马线检测训练
- `train_traffic_light.py` - 红绿灯检测训练
- `train_obstacle.py` - 障碍物检测训练
- `train_item_recognition.py` - 物品识别训练

### 数据准备
- `data_preparation.py` - 数据准备和增强脚本

## 📈 训练时间预估

| 配置 | 盲道分割 | 斑马线检测 | 红绿灯检测 | 障碍物检测 | 物品识别 | 总计 |
|------|----------|------------|------------|------------|----------|------|
| **RTX 4090** | 6小时 | 3小时 | 2小时 | 8小时 | 6小时 | 25小时 |
| **RTX 3080** | 12小时 | 6小时 | 4小时 | 16小时 | 12小时 | 50小时 |
| **RTX 3070** | 18小时 | 9小时 | 6小时 | 24小时 | 18小时 | 75小时 |
| **CPU** | 120小时 | 60小时 | 40小时 | 160小时 | 120小时 | 500小时 |

## 🎯 训练流程

1. **环境准备** (15分钟)
   - 安装依赖包
   - 配置GPU环境
   - 检查硬件配置

2. **数据准备** (30分钟)
   - 收集训练数据
   - 数据标注
   - 数据增强
   - 数据集划分

3. **模型训练** (40-60小时)
   - 演示模式：30分钟
   - 完整模式：40-60小时
   - 训练监控
   - 模型优化

4. **模型部署** (30分钟)
   - 模型导出
   - 性能测试
   - 部署到生产环境

## 🚨 故障排除

### 常见问题
1. **显存不足**: 减少batch_size，使用梯度累积
2. **训练不收敛**: 调整学习率，使用预训练模型
3. **过拟合**: 增加数据增强，使用正则化
4. **训练速度慢**: 使用混合精度训练，优化数据加载

### 调试工具
```bash
# 检查环境
python training/scripts/test_training.py --test environment

# 测试数据
python training/scripts/test_training.py --test data

# 测试模型
python training/scripts/test_training.py --test model
```

## 📞 技术支持

- **查看日志**: `logs/training.log`
- **运行测试**: `python training/scripts/test_training.py`
- **提交Issue**: GitHub Issues页面
- **技术交流**: QQ群/微信群

---

**总训练时间**: 25-75小时
**成功率**: 90%+
**推荐GPU**: RTX 4090 24GB
**总成本**: $200-2150