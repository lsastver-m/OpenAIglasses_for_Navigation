# 🚀 快速开始文档

## 📋 文档概览

本目录包含AI智能眼镜导航系统的快速开始相关文档。

## 📁 文档结构

### 快速开始文档
- **[QUICK_START.md](./QUICK_START.md)** - 系统快速部署指南
- **[README_QUICK.md](./README_QUICK.md)** - 快速开始详细说明

## 🎯 快速开始流程

### 1. 环境准备 (5分钟)
```bash
# 克隆项目
git clone https://github.com/lsastver-m/OpenAIglasses_for_Navigation.git
cd OpenAIglasses_for_Navigation

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置设置 (5分钟)
```bash
# 复制配置文件
cp .env.example .env

# 编辑配置文件
nano .env
```

### 3. 启动系统 (5分钟)
```bash
# 启动后端服务
python app_main.py

# 启动前端界面
# 访问 http://localhost:8000
```

## 🔧 部署方式

### 方式一：一键安装脚本
```bash
# 运行一键安装脚本
chmod +x install.sh
./install.sh
```

### 方式二：Docker部署
```bash
# 使用Docker Compose
docker-compose -f docker-quick-start.yml up -d
```

### 方式三：手动安装
```bash
# 手动安装依赖
pip install -r requirements.txt

# 配置环境变量
export DASHSCOPE_API_KEY="your-api-key"

# 启动服务
python app_main.py
```

## 📊 系统要求

### 硬件要求
- **CPU**: Intel i5-8400 / AMD Ryzen 5 2600 或更高
- **内存**: 8GB RAM (推荐16GB)
- **存储**: 10GB 可用空间
- **网络**: 稳定的互联网连接

### 软件要求
- **操作系统**: Windows 10/11, macOS 10.15+, Ubuntu 18.04+
- **Python**: 3.8+ (推荐3.10)
- **Node.js**: 16+ (前端开发)
- **Git**: 2.0+

## 🚀 功能特性

### 核心功能
- **盲道导航**: 实时盲道检测和路径规划
- **过马路辅助**: 斑马线检测和安全过马路指导
- **障碍物避让**: 实时障碍物检测和避让建议
- **物品查找**: 基于语音描述的物品搜索
- **语音交互**: 自然语言语音指令处理

### 技术特性
- **实时处理**: 低延迟视频流处理
- **AI驱动**: 深度学习模型支持
- **多模态**: 视觉、听觉、触觉反馈
- **可扩展**: 模块化架构设计
- **跨平台**: 支持多种操作系统

## 📱 使用指南

### 基本操作
1. **启动系统**: 运行 `python app_main.py`
2. **连接设备**: 通过WebSocket连接ESP32设备
3. **开始导航**: 语音指令启动导航功能
4. **实时反馈**: 接收语音和触觉反馈

### 语音指令
- "开始导航" - 启动盲道导航
- "过马路" - 启动过马路辅助
- "找物品" - 启动物品搜索
- "停止导航" - 停止当前导航

## 🔧 故障排除

### 常见问题
1. **连接失败**: 检查网络连接和端口配置
2. **模型加载失败**: 检查模型文件路径和权限
3. **音频问题**: 检查音频设备配置
4. **性能问题**: 检查硬件配置和系统资源

### 调试工具
```bash
# 检查系统状态
python -c "import sys; print(sys.version)"

# 检查依赖包
pip list | grep -E "(torch|opencv|ultralytics)"

# 检查GPU
python -c "import torch; print(torch.cuda.is_available())"
```

## 📞 技术支持

### 获取帮助
- **查看日志**: `logs/app.log`
- **运行测试**: `python test_system.py`
- **提交Issue**: GitHub Issues页面
- **技术交流**: QQ群/微信群

### 联系方式
- **GitHub Issues**: 项目Issues页面
- **技术交流群**: QQ群/微信群
- **在线文档**: 项目文档网站

## 🎯 下一步

### 开发环境
1. 阅读 [开发环境搭建](../development/README.md)
2. 查看 [API接口文档](../api/README.md)
3. 参考 [扩展开发指南](../extensions/README.md)

### 生产部署
1. 阅读 [部署指南](../deployment/README.md)
2. 查看 [性能优化](../performance/README.md)
3. 参考 [安全设计](../security/README.md)

---

**部署时间**: 15-30分钟
**成功率**: 95%+
**推荐配置**: 16GB RAM + RTX 3060
**总成本**: $500-2000
