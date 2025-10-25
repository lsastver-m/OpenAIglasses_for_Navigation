#!/bin/bash
# AI智能眼镜导航系统一键安装脚本
# 适用于Ubuntu/Debian系统

set -e  # 遇到错误立即退出

echo "🚀 AI智能眼镜导航系统一键安装脚本"
echo "=================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查系统
check_system() {
    log_info "检查系统环境..."
    
    # 检查操作系统
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command -v apt &> /dev/null; then
            OS="ubuntu"
        elif command -v yum &> /dev/null; then
            OS="centos"
        else
            log_error "不支持的操作系统"
            exit 1
        fi
    else
        log_error "仅支持Linux系统"
        exit 1
    fi
    
    log_success "系统检查通过: $OS"
}

# 安装系统依赖
install_system_deps() {
    log_info "安装系统依赖..."
    
    if [[ "$OS" == "ubuntu" ]]; then
        sudo apt update && sudo apt upgrade -y
        sudo apt install -y \
            python3-dev python3-pip build-essential cmake pkg-config \
            libjpeg-dev libtiff5-dev libpng-dev libavcodec-dev \
            libavformat-dev libswscale-dev libgtk2.0-dev \
            libcanberra-gtk-module libcanberra-gtk3-module \
            portaudio19-dev libasound2-dev ffmpeg git curl wget \
            htop iotop nethogs
    elif [[ "$OS" == "centos" ]]; then
        sudo yum update -y
        sudo yum groupinstall -y "Development Tools"
        sudo yum install -y python3-devel python3-pip cmake \
            libjpeg-devel libtiff-devel libpng-devel \
            portaudio-devel alsa-lib-devel ffmpeg git curl wget
    fi
    
    log_success "系统依赖安装完成"
}

# 安装Python环境
install_python_env() {
    log_info "配置Python环境..."
    
    # 检查Python版本
    if ! python3 --version | grep -E "Python 3\.(9|10|11)"; then
        log_warning "Python版本可能不兼容，建议使用3.9-3.11"
    fi
    
    # 创建虚拟环境
    if [ ! -d "aiglass_env" ]; then
        python3 -m venv aiglass_env
        log_success "虚拟环境创建完成"
    else
        log_info "虚拟环境已存在"
    fi
    
    # 激活虚拟环境
    source aiglass_env/bin/activate
    
    # 升级pip
    pip install --upgrade pip
    
    log_success "Python环境配置完成"
}

# 安装Python依赖
install_python_deps() {
    log_info "安装Python依赖..."
    
    # 激活虚拟环境
    source aiglass_env/bin/activate
    
    # 安装基础依赖
    pip install -r requirements.txt
    
    # 检查GPU并安装对应版本的PyTorch
    if command -v nvidia-smi &> /dev/null; then
        log_info "检测到NVIDIA GPU，安装CUDA版本PyTorch..."
        pip install torch==2.0.1+cu118 torchvision==0.15.2+cu118 --index-url https://download.pytorch.org/whl/cu118
    else
        log_info "未检测到GPU，安装CPU版本PyTorch..."
        pip install torch==2.0.1+cpu torchvision==0.15.2+cpu --index-url https://download.pytorch.org/whl/cpu
    fi
    
    log_success "Python依赖安装完成"
}

# 下载模型文件
download_models() {
    log_info "下载AI模型文件..."
    
    # 创建模型目录
    mkdir -p model
    
    # 模型下载列表
    models=(
        "https://github.com/ultralytics/assets/releases/download/v0.0.0/yoloe-11l-seg.pt:model/yoloe-11l-seg.pt"
        "https://github.com/ultralytics/assets/releases/download/v0.0.0/yolo-seg.pt:model/yolo-seg.pt"
        "https://github.com/ultralytics/assets/releases/download/v0.0.0/trafficlight.pt:model/trafficlight.pt"
        "https://github.com/ultralytics/assets/releases/download/v0.0.0/shoppingbest5.pt:model/shoppingbest5.pt"
        "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker_heavy/float16/1/hand_landmarker.task:model/hand_landmarker.task"
    )
    
    for model_info in "${models[@]}"; do
        url=$(echo $model_info | cut -d: -f1)
        file=$(echo $model_info | cut -d: -f2)
        
        if [ ! -f "$file" ]; then
            log_info "下载 $file..."
            wget -O "$file" "$url" || log_warning "下载失败: $file"
        else
            log_info "模型文件已存在: $file"
        fi
    done
    
    log_success "模型文件下载完成"
}

# 创建配置文件
create_config() {
    log_info "创建配置文件..."
    
    if [ ! -f ".env" ]; then
        cat > .env << EOF
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
EOF
        log_success "配置文件创建完成"
    else
        log_info "配置文件已存在"
    fi
}

# 创建启动脚本
create_startup_script() {
    log_info "创建启动脚本..."
    
    cat > start.sh << 'EOF'
#!/bin/bash
# AI智能眼镜导航系统启动脚本

echo "🚀 启动AI智能眼镜导航系统..."

# 激活虚拟环境
source aiglass_env/bin/activate

# 检查配置文件
if [ ! -f ".env" ]; then
    echo "❌ 配置文件不存在，请先运行 ./install.sh"
    exit 1
fi

# 检查模型文件
if [ ! -f "model/yoloe-11l-seg.pt" ]; then
    echo "❌ 模型文件不存在，请先运行 ./install.sh"
    exit 1
fi

# 启动服务
echo "✅ 启动服务..."
python app_main.py
EOF
    
    chmod +x start.sh
    log_success "启动脚本创建完成"
}

# 创建测试脚本
create_test_script() {
    log_info "创建测试脚本..."
    
    cat > test.sh << 'EOF'
#!/bin/bash
# AI智能眼镜导航系统测试脚本

echo "🧪 AI智能眼镜导航系统测试"
echo "=========================="

# 激活虚拟环境
source aiglass_env/bin/activate

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
    echo "❌ .env文件不存在"
fi

# 4. 检查依赖
echo "4. 检查依赖..."
python -c "
try:
    import fastapi, uvicorn, dashscope
    print('✅ 核心依赖正常')
except ImportError as e:
    print(f'❌ 依赖缺失: {e}')
"

# 5. 应用导入测试
echo "5. 应用导入测试..."
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
EOF
    
    chmod +x test.sh
    log_success "测试脚本创建完成"
}

# 主安装流程
main() {
    echo "开始安装AI智能眼镜导航系统..."
    echo "预计时间：30-60分钟"
    echo ""
    
    check_system
    install_system_deps
    install_python_env
    install_python_deps
    download_models
    create_config
    create_startup_script
    create_test_script
    
    echo ""
    log_success "🎉 安装完成！"
    echo ""
    echo "下一步操作："
    echo "1. 编辑配置文件: nano .env"
    echo "2. 获取API密钥: https://dashscope.console.aliyun.com/"
    echo "3. 运行测试: ./test.sh"
    echo "4. 启动系统: ./start.sh"
    echo "5. 访问界面: http://localhost:8081"
    echo ""
    echo "详细说明请查看: QUICK_START.md"
}

# 运行主函数
main "$@"
