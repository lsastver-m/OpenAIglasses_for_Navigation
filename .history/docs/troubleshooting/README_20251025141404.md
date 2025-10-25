# 🔧 故障排除指南

## 🚨 常见问题诊断

### 系统启动问题

#### 问题1: 服务无法启动
**症状**: 运行 `python app_main.py` 后立即退出
**可能原因**:
- Python环境问题
- 依赖包缺失
- 端口被占用
- 配置文件错误

**解决步骤**:
```bash
# 1. 检查Python环境
python --version
pip list

# 2. 安装缺失依赖
pip install -r requirements.txt

# 3. 检查端口占用
netstat -tlnp | grep 8081
lsof -i :8081

# 4. 检查配置文件
cat .env
```

#### 问题2: 模型加载失败
**症状**: 启动时显示模型加载错误
**可能原因**:
- 模型文件缺失
- 模型文件损坏
- 内存不足
- CUDA环境问题

**解决步骤**:
```bash
# 1. 检查模型文件
ls -la model/
file model/*.pt

# 2. 检查内存使用
free -h
top

# 3. 检查CUDA环境
nvidia-smi
python -c "import torch; print(torch.cuda.is_available())"

# 4. 重新下载模型
wget https://github.com/ultralytics/yolov5/releases/download/v7.0/yolov5s.pt
```

### 硬件连接问题

#### 问题3: ESP32无法连接
**症状**: 设备连接失败，WebSocket连接断开
**可能原因**:
- WiFi连接问题
- 服务器地址错误
- 防火墙阻挡
- 设备故障

**解决步骤**:
```bash
# 1. 检查WiFi连接
ping 192.168.1.1
iwconfig

# 2. 检查服务器状态
netstat -tlnp | grep 8081
curl http://localhost:8081/api/status

# 3. 检查防火墙
sudo ufw status
sudo iptables -L

# 4. 重启网络服务
sudo systemctl restart networking
```

#### 问题4: 摄像头无图像
**症状**: 视频流显示黑屏或无法显示
**可能原因**:
- 摄像头硬件故障
- 驱动程序问题
- 引脚连接错误
- 固件问题

**解决步骤**:
```cpp
// 1. 检查摄像头初始化
if (!esp_camera_init(&config)) {
    Serial.println("摄像头初始化失败");
    return;
}

// 2. 检查引脚配置
#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM     0
// ... 检查所有引脚定义

// 3. 测试摄像头功能
camera_fb_t * fb = esp_camera_fb_get();
if (!fb) {
    Serial.println("摄像头获取帧失败");
    return;
}
```

### 音频问题

#### 问题5: 麦克风无声音
**症状**: 语音识别不工作，无法接收音频
**可能原因**:
- 麦克风硬件故障
- 音频驱动问题
- 采样率不匹配
- 权限问题

**解决步骤**:
```bash
# 1. 检查音频设备
arecord -l
aplay -l

# 2. 测试麦克风
arecord -f cd -d 5 test.wav
aplay test.wav

# 3. 检查音频权限
sudo usermod -a -G audio $USER

# 4. 检查PyAudio
python -c "import pyaudio; print('PyAudio正常')"
```

#### 问题6: 扬声器无声音
**症状**: TTS语音无输出，听不到提示音
**可能原因**:
- 扬声器硬件故障
- 音频输出配置错误
- 音量设置问题
- 音频格式不匹配

**解决步骤**:
```python
# 1. 检查音频输出
import pygame
pygame.mixer.init()
pygame.mixer.music.load("test.wav")
pygame.mixer.music.play()

# 2. 检查音量设置
import os
os.system("amixer set Master 50%")

# 3. 检查音频格式
import wave
with wave.open("test.wav", "rb") as wav_file:
    print(f"采样率: {wav_file.getframerate()}")
    print(f"声道数: {wav_file.getnchannels()}")
    print(f"位深: {wav_file.getsampwidth() * 8}")
```

### AI模型问题

#### 问题7: 模型推理错误
**症状**: AI检测结果异常，识别准确率低
**可能原因**:
- 模型文件损坏
- 输入数据格式错误
- 内存不足
- 模型版本不匹配

**解决步骤**:
```python
# 1. 检查模型加载
import torch
model = torch.load("model.pt")
print(f"模型设备: {next(model.parameters()).device}")

# 2. 检查输入数据
import cv2
import numpy as np
frame = cv2.imread("test.jpg")
print(f"图像形状: {frame.shape}")
print(f"数据类型: {frame.dtype}")

# 3. 测试模型推理
with torch.no_grad():
    result = model(frame)
    print(f"推理结果: {result}")

# 4. 检查内存使用
import psutil
print(f"内存使用: {psutil.virtual_memory().percent}%")
```

#### 问题8: 检测结果不准确
**症状**: 目标检测错误，分割结果异常
**可能原因**:
- 模型训练数据不足
- 输入图像质量差
- 检测参数设置错误
- 环境光照影响

**解决步骤**:
```python
# 1. 调整检测参数
results = model(
    frame,
    conf=0.5,  # 提高置信度阈值
    iou=0.45,  # 调整IoU阈值
    imgsz=640  # 调整输入尺寸
)

# 2. 图像预处理
frame = cv2.resize(frame, (640, 640))
frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
frame = frame.astype(np.float32) / 255.0

# 3. 后处理优化
def post_process(results):
    for result in results:
        if result.conf > 0.5:  # 过滤低置信度结果
            # 应用非极大值抑制
            boxes = result.boxes.xyxy
            scores = result.boxes.conf
            indices = cv2.dnn.NMSBoxes(boxes, scores, 0.5, 0.4)
            return boxes[indices]
```

## 🔍 系统诊断工具

### 性能监控脚本
```bash
#!/bin/bash
# system_monitor.sh - 系统性能监控

echo "=== 系统性能监控 ==="
echo "时间: $(date)"
echo "---"

# CPU使用率
echo "CPU使用率:"
top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1

# 内存使用率
echo "内存使用率:"
free | grep Mem | awk '{printf("%.2f%%", $3/$2 * 100.0)}'

# 磁盘使用率
echo "磁盘使用率:"
df -h / | awk 'NR==2{printf "%s", $5}'

# 网络连接数
echo "网络连接数:"
netstat -an | grep :8081 | wc -l

# 进程状态
echo "进程状态:"
ps aux | grep python | grep app_main

# 服务状态
echo "服务状态:"
systemctl is-active aiglass
```

### 网络诊断脚本
```bash
#!/bin/bash
# network_diagnosis.sh - 网络诊断

echo "=== 网络诊断 ==="
echo "时间: $(date)"
echo "---"

# 检查网络接口
echo "网络接口:"
ip addr show

# 检查路由表
echo "路由表:"
ip route show

# 检查DNS解析
echo "DNS解析:"
nslookup google.com

# 检查端口监听
echo "端口监听:"
netstat -tlnp | grep :8081

# 检查防火墙
echo "防火墙状态:"
sudo ufw status

# 测试网络连接
echo "网络连接测试:"
ping -c 3 8.8.8.8
```

### 硬件诊断脚本
```bash
#!/bin/bash
# hardware_diagnosis.sh - 硬件诊断

echo "=== 硬件诊断 ==="
echo "时间: $(date)"
echo "---"

# 检查USB设备
echo "USB设备:"
lsusb

# 检查串口设备
echo "串口设备:"
ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null

# 检查摄像头
echo "摄像头设备:"
ls /dev/video* 2>/dev/null

# 检查音频设备
echo "音频设备:"
arecord -l
aplay -l

# 检查GPU
echo "GPU信息:"
nvidia-smi 2>/dev/null || echo "NVIDIA GPU未检测到"

# 检查温度
echo "系统温度:"
sensors 2>/dev/null || echo "温度传感器未检测到"
```

## 🛠️ 修复工具

### 自动修复脚本
```bash
#!/bin/bash
# auto_fix.sh - 自动修复脚本

echo "=== 自动修复开始 ==="

# 1. 检查并安装依赖
echo "检查Python依赖..."
pip install -r requirements.txt

# 2. 检查并修复权限
echo "修复文件权限..."
sudo chown -R $USER:$USER .
chmod +x *.sh

# 3. 检查并修复配置
echo "检查配置文件..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "已创建.env文件，请编辑配置"
fi

# 4. 检查并修复模型文件
echo "检查模型文件..."
if [ ! -d model ]; then
    mkdir -p model
    echo "已创建model目录"
fi

# 5. 重启服务
echo "重启服务..."
sudo systemctl restart aiglass

echo "=== 自动修复完成 ==="
```

### 日志分析工具
```bash
#!/bin/bash
# log_analyzer.sh - 日志分析工具

echo "=== 日志分析 ==="
echo "时间: $(date)"
echo "---"

# 分析系统日志
echo "系统日志分析:"
journalctl -u aiglass --since "1 hour ago" | grep -E "(ERROR|WARN|CRITICAL)"

# 分析应用日志
echo "应用日志分析:"
tail -n 100 /opt/aiglass/logs/app.log | grep -E "(ERROR|WARN|CRITICAL)"

# 分析网络日志
echo "网络日志分析:"
tail -n 100 /var/log/nginx/error.log | grep -E "(ERROR|WARN|CRITICAL)"

# 分析性能日志
echo "性能日志分析:"
tail -n 100 /opt/aiglass/logs/performance.log | grep -E "(high|low|critical)"
```

## 📞 技术支持

### 问题报告模板
```
问题标题: [简要描述问题]
问题描述: [详细描述问题现象]
环境信息:
- 操作系统: [Ubuntu 20.04 / Windows 10 / macOS 12]
- Python版本: [3.9 / 3.10 / 3.11]
- 硬件配置: [CPU/内存/显卡]
- 软件版本: [具体版本号]

重现步骤:
1. [步骤1]
2. [步骤2]
3. [步骤3]

预期结果: [期望的结果]
实际结果: [实际的结果]
错误日志: [粘贴错误日志]
```

### 联系方式
- **技术支持邮箱**: support@aiglass.com
- **技术交流群**: [加入QQ群/微信群]
- **GitHub Issues**: [项目Issues页面]
- **在线文档**: [项目文档网站]

### 紧急联系
- **紧急问题**: 400-123-4567
- **在线客服**: [官网在线客服]
- **远程支持**: [远程协助工具]

---

**提示**: 如果问题仍然无法解决，请提供详细的错误日志和系统信息，以便技术支持团队快速定位问题。
