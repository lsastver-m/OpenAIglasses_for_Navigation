# 🛠️ 开发环境搭建

## 📋 开发环境要求

### 硬件要求
| 组件 | 最低配置 | 推荐配置 |
|------|----------|----------|
| **CPU** | 4核心 2.0GHz | 8核心 3.0GHz+ |
| **内存** | 8GB RAM | 16GB+ RAM |
| **显卡** | 集成显卡 | NVIDIA RTX 3060+ |
| **存储** | 50GB 可用空间 | 100GB+ SSD |

### 软件要求
| 软件 | 版本要求 | 说明 |
|------|----------|------|
| **操作系统** | Ubuntu 20.04+ / Windows 10+ / macOS 12+ | 支持主流操作系统 |
| **Python** | 3.9 - 3.11 | 不支持3.12+ |
| **Node.js** | 16.0+ | 前端开发(可选) |
| **Git** | 2.0+ | 版本控制 |
| **Docker** | 20.10+ | 容器化开发(可选) |

## 🔧 环境配置步骤

### 1. 克隆项目
```bash
# 克隆项目到本地
git clone https://github.com/your-repo/OpenAIglasses_for_Navigation.git
cd OpenAIglasses_for_Navigation

# 查看项目结构
ls -la
```

### 2. Python环境配置

#### 使用conda (推荐)
```bash
# 安装Anaconda/Miniconda
# 下载地址: https://www.anaconda.com/products/distribution

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

# 激活虚拟环境
# Linux/macOS:
source aiglass_env/bin/activate
# Windows:
aiglass_env\Scripts\activate

# 升级pip
pip install --upgrade pip
```

### 3. 安装Python依赖
```bash
# 安装基础依赖
pip install -r requirements.txt

# 安装开发依赖
pip install -r requirements-dev.txt

# 验证安装
python -c "import torch; print(torch.__version__)"
python -c "import cv2; print(cv2.__version__)"
```

### 4. 系统依赖安装

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
    libasound2-dev \
    ffmpeg \
    git

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
# 下载地址: https://visualstudio.microsoft.com/visual-cpp-build-tools/

# 安装CUDA Toolkit
# 下载地址: https://developer.nvidia.com/cuda-downloads

# 安装Git
# 下载地址: https://git-scm.com/download/win

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
brew install ffmpeg
brew install git

# 安装Python依赖
pip install -r requirements.txt
```

### 5. 环境变量配置
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
DEBUG_MODE=true

# 开发配置
LOG_LEVEL=DEBUG
ENABLE_HOT_RELOAD=true
```

## 🚀 开发工具配置

### 1. IDE配置

#### VS Code配置
```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": "./aiglass_env/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests/"],
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        "**/node_modules": true
    }
}
```

#### PyCharm配置
```python
# 配置Python解释器
# File -> Settings -> Project -> Python Interpreter
# 选择虚拟环境中的Python解释器

# 配置代码检查
# File -> Settings -> Editor -> Inspections
# 启用Python代码检查

# 配置代码格式化
# File -> Settings -> Editor -> Code Style -> Python
# 设置代码风格
```

### 2. 代码质量工具

#### 安装开发工具
```bash
# 安装代码质量工具
pip install black flake8 pylint pytest pytest-cov

# 安装类型检查工具
pip install mypy

# 安装安全扫描工具
pip install bandit safety
```

#### 配置代码格式化
```bash
# 配置Black
black --line-length 88 --target-version py39 .

# 配置flake8
flake8 --max-line-length 88 --extend-ignore E203,W503 .

# 配置pylint
pylint --rcfile=.pylintrc .
```

#### 配置测试
```bash
# 运行测试
pytest tests/ -v

# 运行测试并生成覆盖率报告
pytest tests/ --cov=. --cov-report=html

# 运行特定测试
pytest tests/test_navigation.py::test_blind_path_navigation -v
```

### 3. Git配置

#### Git钩子配置
```bash
# 安装pre-commit
pip install pre-commit

# 配置pre-commit
pre-commit install

# 创建.pre-commit-config.yaml
cat > .pre-commit-config.yaml << EOF
repos:
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black
        language_version: python3.9
  - repo: https://github.com/pycqa/flake8
    rev: 4.0.1
    hooks:
      - id: flake8
  - repo: https://github.com/pycqa/isort
    rev: 5.10.1
    hooks:
      - id: isort
EOF
```

#### Git工作流配置
```bash
# 配置Git用户信息
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# 配置Git别名
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.ci commit
git config --global alias.st status
```

## 🔧 ESP32开发环境

### 1. Arduino IDE配置

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

#### 安装依赖库
```cpp
// 在Arduino IDE中安装以下库:
// 1. ArduinoWebsockets by Markus Sattler
// 2. ESP_I2S by Earle F. Philhower, III
// 3. WiFi by Arduino
// 4. esp_camera by Espressif Systems
```

### 2. 固件开发配置

#### 开发板配置
```
开发板: XIAO_ESP32S3
CPU频率: 240MHz
Flash大小: 8MB
分区方案: 默认
上传速度: 921600
端口: /dev/ttyUSB0 (Linux) / COM3 (Windows)
```

#### 编译配置
```bash
# 使用Arduino CLI编译
arduino-cli compile --fqbn esp32:esp32:esp32s3 compile/compile.ino

# 上传固件
arduino-cli upload -p /dev/ttyUSB0 --fqbn esp32:esp32:esp32s3 compile/compile.ino
```

## 🐳 Docker开发环境

### 1. Docker配置

#### 创建Dockerfile
```dockerfile
# Dockerfile.dev
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
COPY requirements.txt requirements-dev.txt ./

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r requirements-dev.txt

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

#### 创建docker-compose.yml
```yaml
version: '3.8'

services:
  aiglass-dev:
    build:
      context: .
      dockerfile: Dockerfile.dev
    ports:
      - "8081:8081"
    volumes:
      - .:/app
      - ./model:/app/model
      - ./recordings:/app/recordings
    environment:
      - PYTHONUNBUFFERED=1
      - DEBUG_MODE=true
    restart: unless-stopped
    command: python app_main.py
```

### 2. 开发容器使用

#### 启动开发容器
```bash
# 构建开发镜像
docker-compose -f docker-compose.dev.yml build

# 启动开发容器
docker-compose -f docker-compose.dev.yml up -d

# 查看容器状态
docker-compose -f docker-compose.dev.yml ps

# 查看容器日志
docker-compose -f docker-compose.dev.yml logs -f
```

#### 进入开发容器
```bash
# 进入容器
docker-compose -f docker-compose.dev.yml exec aiglass-dev bash

# 在容器中运行命令
docker-compose -f docker-compose.dev.yml exec aiglass-dev python -m pytest tests/
```

## 🧪 测试环境配置

### 1. 单元测试配置

#### 创建测试目录结构
```bash
# 创建测试目录
mkdir -p tests/{unit,integration,e2e}

# 创建测试文件
touch tests/__init__.py
touch tests/unit/__init__.py
touch tests/integration/__init__.py
touch tests/e2e/__init__.py
```

#### 配置pytest
```python
# conftest.py
import pytest
import asyncio
from fastapi.testclient import TestClient
from app_main import app

@pytest.fixture
def client():
    """测试客户端"""
    return TestClient(app)

@pytest.fixture
def event_loop():
    """事件循环"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()
```

#### 编写测试用例
```python
# tests/unit/test_navigation.py
import pytest
from navigation_master import NavigationMaster

class TestNavigationMaster:
    def test_initial_state(self):
        """测试初始状态"""
        master = NavigationMaster()
        assert master.current_state == "IDLE"
    
    def test_state_transition(self):
        """测试状态转换"""
        master = NavigationMaster()
        master.transition_to_new_state("BLINDPATH_NAV")
        assert master.current_state == "BLINDPATH_NAV"
```

### 2. 集成测试配置

#### 配置测试数据库
```python
# tests/integration/test_api.py
import pytest
from fastapi.testclient import TestClient
from app_main import app

class TestAPI:
    def test_status_endpoint(self, client):
        """测试状态接口"""
        response = client.get("/api/status")
        assert response.status_code == 200
        assert "status" in response.json()
    
    def test_navigation_mode_endpoint(self, client):
        """测试导航模式接口"""
        response = client.post("/api/navigation/mode", json={"mode": "BLINDPATH_NAV"})
        assert response.status_code == 200
        assert response.json()["success"] == True
```

### 3. 端到端测试配置

#### 配置E2E测试
```python
# tests/e2e/test_full_workflow.py
import pytest
import asyncio
from app_main import app

class TestFullWorkflow:
    @pytest.mark.asyncio
    async def test_blind_path_navigation(self):
        """测试盲道导航完整流程"""
        # 模拟视频帧
        frame = create_test_frame()
        
        # 测试导航处理
        result = await navigation_master.process_frame(frame)
        
        # 验证结果
        assert result.state == "BLINDPATH_NAV"
        assert result.guidance_text is not None
```

## 📊 性能分析工具

### 1. 性能监控配置

#### 安装性能分析工具
```bash
# 安装性能分析工具
pip install memory-profiler line-profiler py-spy

# 安装系统监控工具
sudo apt install htop iotop nethogs
```

#### 配置性能分析
```python
# 内存分析
from memory_profiler import profile

@profile
def process_frame(self, frame):
    """处理视频帧"""
    # 处理逻辑
    pass

# 时间分析
import time
import functools

def timing(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} 耗时: {end - start:.4f}秒")
        return result
    return wrapper
```

### 2. 代码分析工具

#### 配置代码分析
```bash
# 运行代码分析
pylint app_main.py navigation_master.py

# 运行安全扫描
bandit -r . -f json -o bandit-report.json

# 运行依赖检查
safety check --json --output safety-report.json
```

## 🔧 调试配置

### 1. 调试器配置

#### VS Code调试配置
```json
// .vscode/launch.json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: 当前文件",
            "type": "python",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}"
        },
        {
            "name": "Python: 应用主程序",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/app_main.py",
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}",
            "env": {
                "PYTHONPATH": "${workspaceFolder}"
            }
        }
    ]
}
```

#### PyCharm调试配置
```python
# 配置调试器
# Run -> Edit Configurations -> Python
# 设置脚本路径: app_main.py
# 设置工作目录: 项目根目录
# 设置环境变量: PYTHONPATH=项目根目录
```

### 2. 日志配置

#### 配置日志系统
```python
# logging_config.py
import logging
import logging.config

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
        'detailed': {
            'format': '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s'
        }
    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
        },
        'file': {
            'level': 'DEBUG',
            'formatter': 'detailed',
            'class': 'logging.FileHandler',
            'filename': 'logs/app.log',
            'mode': 'a',
        }
    },
    'loggers': {
        '': {
            'handlers': ['default', 'file'],
            'level': 'DEBUG',
            'propagate': False
        }
    }
}

logging.config.dictConfig(LOGGING_CONFIG)
```

## 🚀 快速开始开发

### 1. 启动开发服务器
```bash
# 激活虚拟环境
conda activate aiglass

# 启动开发服务器
python app_main.py

# 或者使用开发模式
python -m uvicorn app_main:app --reload --host 0.0.0.0 --port 8081
```

### 2. 访问开发界面
```bash
# 打开浏览器访问
http://localhost:8081

# 或者使用curl测试API
curl http://localhost:8081/api/status
```

### 3. 运行测试
```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试
pytest tests/unit/test_navigation.py -v

# 运行测试并生成覆盖率报告
pytest tests/ --cov=. --cov-report=html
```

---

**提示**: 开发环境配置完成后，请参考 [用户手册](../user-guide/README.md) 了解系统使用方法。
