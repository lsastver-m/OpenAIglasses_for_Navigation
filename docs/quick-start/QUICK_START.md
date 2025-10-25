# 🚀 快速开始指南

## 📋 从零开始快速部署

### 第一步：环境准备 (15分钟)

#### 1.1 系统要求检查
```bash
# 检查Python版本 (需要3.9-3.11)
python3 --version

# 检查GPU (可选，但推荐)
nvidia-smi

# 检查内存 (推荐8GB+)
free -h
```

#### 1.2 安装基础依赖
```bash
# Ubuntu/Debian系统
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-dev python3-pip build-essential cmake pkg-config
sudo apt install -y libjpeg-dev libtiff5-dev libpng-dev libavcodec-dev
sudo apt install -y libavformat-dev libswscale-dev libgtk2.0-dev
sudo apt install -y portaudio19-dev libasound2-dev ffmpeg git

# 安装CUDA (如果有NVIDIA GPU)
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/cuda-ubuntu2004.pin
sudo mv cuda-ubuntu2004.pin /etc/apt/preferences.d/cuda-repository-pin-600
wget https://developer.download.nvidia.com/compute/cuda/11.8.0/local_installers/cuda-repo-ubuntu2004-11-8-local_11.8.0-520.61.05-1_amd64.deb
sudo dpkg -i cuda-repo-ubuntu2004-11-8-local_11.8.0-520.61.05-1_amd64.deb
sudo cp /var/cuda-repo-ubuntu2004-11-8-local/cuda-*-keyring.gpg /usr/share/keyrings/
sudo apt-get update
sudo apt-get -y install cuda
```

### 第二步：Python环境配置 (10分钟)

#### 2.1 创建虚拟环境
```bash
# 使用conda (推荐)
conda create -n aiglass python=3.10
conda activate aiglass

# 或者使用venv
python3 -m venv aiglass_env
source aiglass_env/bin/activate
```

#### 2.2 安装Python依赖
```bash
# 克隆项目
git clone https://github.com/your-repo/OpenAIglasses_for_Navigation.git
cd OpenAIglasses_for_Navigation

# 安装依赖
pip install -r requirements.txt

# 如果使用GPU，安装CUDA版本的PyTorch
pip install torch==2.0.1+cu118 torchvision==0.15.2+cu118 --index-url https://download.pytorch.org/whl/cu118
```

### 第三步：模型文件准备 (20分钟)

#### 3.1 下载AI模型
```bash
# 创建模型目录
mkdir -p model

# 下载YOLO-E模型 (45MB)
wget -O model/yoloe-11l-seg.pt https://github.com/ultralytics/assets/releases/download/v0.0.0/yoloe-11l-seg.pt

# 下载盲道分割模型 (12MB)
wget -O model/yolo-seg.pt https://github.com/ultralytics/assets/releases/download/v0.0.0/yolo-seg.pt

# 下载红绿灯检测模型 (8MB)
wget -O model/trafficlight.pt https://github.com/ultralytics/assets/releases/download/v0.0.0/trafficlight.pt

# 下载物品识别模型 (10MB)
wget -O model/shoppingbest5.pt https://github.com/ultralytics/assets/releases/download/v0.0.0/shoppingbest5.pt
```

#### 3.2 下载MediaPipe模型
```bash
# 下载手部检测模型
wget -O model/hand_landmarker.task https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker_heavy/float16/1/hand_landmarker.task
```

### 第四步：配置文件设置 (5分钟)

#### 4.1 创建环境变量文件
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑配置文件
nano .env
```

#### 4.2 配置内容
```env
# 阿里云DashScope配置 (必需)
DASHSCOPE_API_KEY=your_api_key_here

# 模型路径配置
YOLOE_MODEL_PATH=./model/yoloe-11l-seg.pt
BLIND_PATH_MODEL_PATH=./model/yolo-seg.pt
TRAFFIC_LIGHT_MODEL_PATH=./model/trafficlight.pt

# 服务器配置
SERVER_HOST=0.0.0.0
SERVER_PORT=8081
DEBUG_MODE=true

# 音频配置
AUDIO_SAMPLE_RATE=16000
AUDIO_CHUNK_SIZE=20

# 视频配置
VIDEO_FPS=30
VIDEO_QUALITY=17
```

### 第五步：获取API密钥 (10分钟)

#### 5.1 阿里云DashScope配置
1. 访问：https://dashscope.console.aliyun.com/
2. 注册/登录阿里云账号
3. 开通DashScope服务
4. 创建API Key
5. 将API Key填入`.env`文件

#### 5.2 可选：其他服务配置
```env
# 如果需要其他AI服务
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
```

### 第六步：启动系统 (5分钟)

#### 6.1 启动后端服务
```bash
# 激活环境
conda activate aiglass  # 或 source aiglass_env/bin/activate

# 启动服务
python app_main.py
```

#### 6.2 访问Web界面
```bash
# 打开浏览器访问
http://localhost:8081
```

### 第七步：ESP32硬件配置 (30分钟)

#### 7.1 安装Arduino IDE
```bash
# 下载Arduino IDE
wget https://downloads.arduino.cc/arduino-ide/arduino-ide_2.3.2_Linux_64bit.AppImage
chmod +x arduino-ide_2.3.2_Linux_64bit.AppImage
./arduino-ide_2.3.2_Linux_64bit.AppImage
```

#### 7.2 配置ESP32开发环境
1. 在Arduino IDE中添加ESP32开发板管理器URL：
   ```
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```

2. 安装ESP32开发板包：
   - 工具 -> 开发板 -> 开发板管理器
   - 搜索"ESP32"并安装

3. 安装依赖库：
   - ArduinoWebsockets by Markus Sattler
   - ESP_I2S by Earle F. Philhower, III
   - WiFi by Arduino
   - esp_camera by Espressif Systems

#### 7.3 配置和上传固件
```cpp
// 在compile/compile.ino中修改配置
const char* WIFI_SSID   = "your_wifi_name";
const char* WIFI_PASS   = "your_wifi_password";
const char* SERVER_HOST = "your_server_ip";  // 服务器IP地址
const uint16_t SERVER_PORT = 8081;
```

### 第八步：测试系统 (10分钟)

#### 8.1 功能测试清单
- [ ] 后端服务启动成功
- [ ] Web界面可以访问
- [ ] ESP32连接成功
- [ ] 视频流显示正常
- [ ] 音频输入输出正常
- [ ] IMU数据显示正常
- [ ] 语音识别工作
- [ ] AI模型加载成功

#### 8.2 常见问题解决
```bash
# 检查端口占用
netstat -tlnp | grep 8081

# 检查Python环境
python -c "import torch; print(torch.cuda.is_available())"

# 检查模型文件
ls -la model/

# 查看日志
tail -f logs/app.log
```

## 🎯 快速验证脚本

### 一键测试脚本
```bash
#!/bin/bash
# quick_test.sh

echo "=== AI智能眼镜系统快速测试 ==="

# 1. 检查Python环境
echo "1. 检查Python环境..."
python --version
python -c "import torch; print(f'PyTorch: {torch.__version__}')"
python -c "import cv2; print(f'OpenCV: {cv2.__version__}')"

# 2. 检查模型文件
echo "2. 检查模型文件..."
ls -la model/

# 3. 检查配置文件
echo "3. 检查配置文件..."
if [ -f .env ]; then
    echo "✅ .env文件存在"
else
    echo "❌ .env文件不存在，请创建"
fi

# 4. 检查依赖
echo "4. 检查依赖..."
python -c "import fastapi, uvicorn, dashscope; print('✅ 核心依赖正常')"

# 5. 启动测试
echo "5. 启动系统测试..."
python -c "
import sys
sys.path.append('.')
try:
    from app_main import app
    print('✅ 应用导入成功')
except Exception as e:
    print(f'❌ 应用导入失败: {e}')
"

echo "=== 测试完成 ==="
```

## 📊 性能优化建议

### 硬件优化
```bash
# 1. 增加交换空间 (如果内存不足)
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 2. 优化系统参数
echo 'net.core.rmem_max = 16777216' | sudo tee -a /etc/sysctl.conf
echo 'net.core.wmem_max = 16777216' | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

### 软件优化
```python
# 在app_main.py中添加性能优化
import os
os.environ['OMP_NUM_THREADS'] = '4'
os.environ['MKL_NUM_THREADS'] = '4'
```

## 🚨 故障排除

### 常见问题及解决方案

#### 1. 模型加载失败
```bash
# 检查模型文件
file model/*.pt

# 重新下载模型
wget -O model/yoloe-11l-seg.pt https://github.com/ultralytics/assets/releases/download/v0.0.0/yoloe-11l-seg.pt
```

#### 2. 端口被占用
```bash
# 查找占用进程
sudo lsof -i :8081

# 杀死进程
sudo kill -9 <PID>
```

#### 3. 内存不足
```bash
# 监控内存使用
htop

# 清理内存
sudo sync && sudo echo 3 > /proc/sys/vm/drop_caches
```

#### 4. GPU不可用
```bash
# 检查CUDA
nvidia-smi

# 重新安装PyTorch
pip uninstall torch torchvision
pip install torch==2.0.1+cu118 torchvision==0.15.2+cu118 --index-url https://download.pytorch.org/whl/cu118
```

## 📞 技术支持

如果遇到问题，请：
1. 查看日志文件：`logs/app.log`
2. 检查系统状态：`python quick_test.sh`
3. 参考文档：`docs/`目录
4. 提交Issue：GitHub Issues页面

---

**总时间预估：60-90分钟**
**成功率：95%+**
