# 🚀 部署指南

## 📋 系统要求

### 硬件要求
| 组件 | 最低配置 | 推荐配置 |
|------|----------|----------|
| **CPU** | 4核心 2.0GHz | 8核心 3.0GHz+ |
| **内存** | 8GB RAM | 16GB+ RAM |
| **显卡** | 集成显卡 | NVIDIA RTX 3060+ |
| **存储** | 50GB 可用空间 | 100GB+ SSD |
| **网络** | 100Mbps | 1Gbps |

### 软件要求
| 软件 | 版本要求 | 说明 |
|------|----------|------|
| **操作系统** | Ubuntu 20.04+ / Windows 10+ / macOS 12+ | 支持主流操作系统 |
| **Python** | 3.9 - 3.11 | 不支持3.12+ |
| **CUDA** | 11.8+ | GPU加速(可选) |
| **Docker** | 20.10+ | 容器化部署(可选) |

## 🔧 环境配置

### 1. Python环境搭建

#### 使用conda (推荐)
```bash
# 创建虚拟环境
conda create -n aiglass python=3.10
conda activate aiglass

# 安装PyTorch (CPU版本)
conda install pytorch torchvision torchaudio cpuonly -c pytorch

# 安装PyTorch (GPU版本)
conda install pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia
```

#### 使用venv
```bash
# 创建虚拟环境
python -m venv aiglass_env
source aiglass_env/bin/activate  # Linux/macOS
# aiglass_env\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 系统依赖安装

#### Ubuntu/Debian
```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装基础依赖
sudo apt install -y \
    python3-dev \
    python3-pip \
    build-essential \
    cmake \
    pkg-config \
    libjpeg-dev \
    libtiff5-dev \
    libpng-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libgtk2.0-dev \
    libcanberra-gtk-module \
    libcanberra-gtk3-module \
    portaudio19-dev \
    libasound2-dev

# 安装CUDA (可选)
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/cuda-ubuntu2004.pin
sudo mv cuda-ubuntu2004.pin /etc/apt/preferences.d/cuda-repository-pin-600
wget https://developer.download.nvidia.com/compute/cuda/11.8.0/local_installers/cuda-repo-ubuntu2004-11-8-local_11.8.0-520.61.05-1_amd64.deb
sudo dpkg -i cuda-repo-ubuntu2004-11-8-local_11.8.0-520.61.05-1_amd64.deb
sudo cp /var/cuda-repo-ubuntu2004-11-8-local/cuda-*-keyring.gpg /usr/share/keyrings/
sudo apt-get update
sudo apt-get -y install cuda
```

#### Windows
```powershell
# 安装Visual Studio Build Tools
# 下载并安装: https://visualstudio.microsoft.com/visual-cpp-build-tools/

# 安装CUDA Toolkit
# 下载并安装: https://developer.nvidia.com/cuda-downloads

# 安装依赖
pip install -r requirements.txt
```

#### macOS
```bash
# 安装Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安装依赖
brew install portaudio
brew install opencv
pip install -r requirements.txt
```

### 3. 环境变量配置

#### 创建.env文件
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑环境变量
nano .env
```

#### 环境变量配置
```env
# 阿里云DashScope配置
DASHSCOPE_API_KEY=your_api_key_here

# 模型路径配置
YOLOE_MODEL_PATH=/path/to/yoloe-11l-seg.pt
BLIND_PATH_MODEL_PATH=/path/to/yolo-seg.pt
TRAFFIC_LIGHT_MODEL_PATH=/path/to/trafficlight.pt

# 服务器配置
SERVER_HOST=0.0.0.0
SERVER_PORT=8081
DEBUG_MODE=false

# 音频配置
AUDIO_SAMPLE_RATE=16000
AUDIO_CHUNK_SIZE=20

# 视频配置
VIDEO_FPS=30
VIDEO_QUALITY=17
```

## 🐳 Docker部署

### 1. 构建Docker镜像

#### 创建Dockerfile
```dockerfile
# 使用官方Python镜像
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgstreamer1.0-0 \
    libgstreamer-plugins-base1.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 复制requirements文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建非root用户
RUN useradd -m -u 1000 aiglass && chown -R aiglass:aiglass /app
USER aiglass

# 暴露端口
EXPOSE 8081

# 启动命令
CMD ["python", "app_main.py"]
```

#### 构建镜像
```bash
# 构建Docker镜像
docker build -t aiglass:latest .

# 查看镜像
docker images
```

### 2. Docker Compose部署

#### 创建docker-compose.yml
```yaml
version: '3.8'

services:
  aiglass:
    build: .
    ports:
      - "8081:8081"
    volumes:
      - ./model:/app/model
      - ./recordings:/app/recordings
      - ./.env:/app/.env
    environment:
      - PYTHONUNBUFFERED=1
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 8G
        reservations:
          memory: 4G

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - aiglass
    restart: unless-stopped
```

#### 启动服务
```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f aiglass
```

### 3. 生产环境配置

#### Nginx配置
```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream aiglass {
        server aiglass:8081;
    }

    server {
        listen 80;
        server_name your-domain.com;

        location / {
            proxy_pass http://aiglass;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /ws/ {
            proxy_pass http://aiglass;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }
    }
}
```

## 🔧 ESP32固件部署

### 1. 开发环境配置

#### 安装Arduino IDE
```bash
# 下载Arduino IDE
wget https://downloads.arduino.cc/arduino-ide/arduino-ide_2.3.2_Linux_64bit.AppImage
chmod +x arduino-ide_2.3.2_Linux_64bit.AppImage
./arduino-ide_2.3.2_Linux_64bit.AppImage
```

#### 安装ESP32开发板支持
```bash
# 添加ESP32开发板管理器URL
# 在Arduino IDE中: 文件 -> 首选项 -> 附加开发板管理器网址
# 添加: https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json

# 安装ESP32开发板包
# 工具 -> 开发板 -> 开发板管理器 -> 搜索"ESP32" -> 安装
```

### 2. 固件编译与上传

#### 配置开发板
```
开发板: XIAO_ESP32S3
CPU频率: 240MHz
Flash大小: 8MB
分区方案: 默认
上传速度: 921600
端口: /dev/ttyUSB0 (Linux) / COM3 (Windows)
```

#### 安装依赖库
```cpp
// 在Arduino IDE中安装以下库:
// 1. ArduinoWebsockets by Markus Sattler
// 2. ESP_I2S by Earle F. Philhower, III
// 3. WiFi by Arduino
// 4. esp_camera by Espressif Systems
```

#### 编译上传
```bash
# 使用Arduino CLI编译
arduino-cli compile --fqbn esp32:esp32:esp32s3 compile/compile.ino

# 上传固件
arduino-cli upload -p /dev/ttyUSB0 --fqbn esp32:esp32:esp32s3 compile/compile.ino
```

### 3. 固件配置

#### WiFi配置
```cpp
// 在compile.ino中修改WiFi配置
const char* WIFI_SSID   = "your_wifi_name";
const char* WIFI_PASS   = "your_wifi_password";
const char* SERVER_HOST = "your_server_ip";
const uint16_t SERVER_PORT = 8081;
```

#### 摄像头配置
```cpp
// 调整摄像头参数
framesize_t g_frame_size = FRAMESIZE_VGA;  // 分辨率
#define JPEG_QUALITY  17                    // 质量 (1-63)
#define FB_COUNT      2                     // 帧缓冲数量
volatile int g_target_fps = 30;            // 目标帧率
```

## 🚀 生产环境部署

### 1. 系统服务配置

#### 创建systemd服务
```bash
# 创建服务文件
sudo nano /etc/systemd/system/aiglass.service
```

#### 服务配置
```ini
[Unit]
Description=AI Glasses Navigation Service
After=network.target

[Service]
Type=simple
User=aiglass
Group=aiglass
WorkingDirectory=/opt/aiglass
ExecStart=/opt/aiglass/venv/bin/python app_main.py
Restart=always
RestartSec=10
Environment=PYTHONPATH=/opt/aiglass
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```

#### 启动服务
```bash
# 重新加载systemd
sudo systemctl daemon-reload

# 启用服务
sudo systemctl enable aiglass

# 启动服务
sudo systemctl start aiglass

# 查看状态
sudo systemctl status aiglass
```

### 2. 反向代理配置

#### Nginx配置
```nginx
# /etc/nginx/sites-available/aiglass
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8081;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### 启用站点
```bash
# 创建软链接
sudo ln -s /etc/nginx/sites-available/aiglass /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启Nginx
sudo systemctl restart nginx
```

### 3. SSL证书配置

#### 使用Let's Encrypt
```bash
# 安装certbot
sudo apt install certbot python3-certbot-nginx

# 获取SSL证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo crontab -e
# 添加: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 📊 监控与日志

### 1. 系统监控

#### 安装监控工具
```bash
# 安装htop
sudo apt install htop

# 安装iotop
sudo apt install iotop

# 安装nethogs
sudo apt install nethogs
```

#### 性能监控脚本
```bash
#!/bin/bash
# monitor.sh - 系统监控脚本

while true; do
    echo "=== $(date) ==="
    echo "CPU使用率: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)"
    echo "内存使用率: $(free | grep Mem | awk '{printf("%.2f%%", $3/$2 * 100.0)}')"
    echo "磁盘使用率: $(df -h / | awk 'NR==2{printf "%s", $5}')"
    echo "网络连接数: $(netstat -an | grep :8081 | wc -l)"
    echo "---"
    sleep 60
done
```

### 2. 日志管理

#### 配置日志轮转
```bash
# 创建logrotate配置
sudo nano /etc/logrotate.d/aiglass
```

#### 日志轮转配置
```
/opt/aiglass/logs/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 aiglass aiglass
    postrotate
        systemctl reload aiglass
    endscript
}
```

### 3. 健康检查

#### 健康检查脚本
```bash
#!/bin/bash
# health_check.sh - 健康检查脚本

# 检查服务状态
if ! systemctl is-active --quiet aiglass; then
    echo "服务未运行，尝试重启..."
    systemctl restart aiglass
fi

# 检查端口监听
if ! netstat -tlnp | grep :8081; then
    echo "端口8081未监听，检查服务状态..."
    systemctl status aiglass
fi

# 检查API响应
if ! curl -f http://localhost:8081/api/status > /dev/null 2>&1; then
    echo "API无响应，检查服务日志..."
    journalctl -u aiglass --since "5 minutes ago"
fi
```

## 🔧 故障排除

### 常见问题

#### 1. 服务启动失败
```bash
# 查看服务状态
sudo systemctl status aiglass

# 查看详细日志
journalctl -u aiglass -f

# 检查端口占用
sudo netstat -tlnp | grep 8081
```

#### 2. 模型加载失败
```bash
# 检查模型文件
ls -la model/

# 检查权限
sudo chown -R aiglass:aiglass model/

# 检查磁盘空间
df -h
```

#### 3. WebSocket连接失败
```bash
# 检查防火墙
sudo ufw status

# 检查Nginx配置
sudo nginx -t

# 检查服务日志
tail -f /var/log/nginx/error.log
```

### 性能优化

#### 1. 系统优化
```bash
# 调整内核参数
echo 'net.core.rmem_max = 16777216' >> /etc/sysctl.conf
echo 'net.core.wmem_max = 16777216' >> /etc/sysctl.conf
sysctl -p
```

#### 2. 应用优化
```python
# 在app_main.py中添加性能优化
import os
os.environ['OMP_NUM_THREADS'] = '4'
os.environ['MKL_NUM_THREADS'] = '4'
```

---

**完成**: 文档编写已完成！现在您有了完整的项目文档体系。
