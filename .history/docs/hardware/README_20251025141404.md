# 🔧 硬件设计文档

## 📱 ESP32智能眼镜硬件架构

### 核心硬件规格

| 组件 | 型号/规格 | 功能描述 | 技术参数 |
|------|-----------|----------|----------|
| **主控芯片** | XIAO ESP32S3 | 双核处理器 | 240MHz, 512KB SRAM, 8MB Flash |
| **摄像头** | OV5640 | 图像采集 | 5MP, VGA@30fps, JPEG压缩 |
| **麦克风** | PDM数字麦克风 | 语音输入 | 16kHz采样, 单声道 |
| **IMU传感器** | ICM42688 | 姿态感知 | 6轴陀螺仪+加速度计 |
| **音频输出** | I2S数字音频 | 语音反馈 | 16bit/44.1kHz, 立体声 |
| **通信模块** | WiFi 802.11n | 数据传输 | 2.4GHz, 150Mbps |

## 🔌 引脚配置

### 摄像头引脚定义
```cpp
// camera_pins.h - 摄像头引脚配置
#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM     0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27
#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM       5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22
```

### IMU传感器引脚配置
```cpp
// ICM42688 SPI接口配置
#define IMU_CS_PIN        10    // 片选信号
#define IMU_MOSI_PIN      11    // 主出从入
#define IMU_MISO_PIN      13    // 主入从出
#define IMU_SCK_PIN       12    // 时钟信号
```

### 音频引脚配置
```cpp
// I2S音频接口配置
#define I2S_MIC_CLOCK_PIN 42    // 麦克风时钟
#define I2S_MIC_DATA_PIN  41    // 麦克风数据
#define I2S_SPK_BCLK_PIN  2     // 扬声器位时钟
#define I2S_SPK_LRCLK_PIN 1     // 扬声器左右声道时钟
#define I2S_SPK_DOUT_PIN  3     // 扬声器数据输出
```

## 📷 摄像头系统设计

### 技术规格
- **传感器**: OV5640 CMOS图像传感器
- **分辨率**: 最大5MP，实际使用VGA (640×480)
- **帧率**: 30fps (可调节)
- **压缩格式**: JPEG (质量可调)
- **视野角度**: 75° (广角)

### 性能优化策略
```cpp
// 视频传输性能监控
volatile unsigned long frame_captured_count = 0;  // 采集帧计数
volatile unsigned long frame_sent_count = 0;      // 发送帧计数
volatile unsigned long frame_dropped_count = 0;   // 丢弃帧计数
volatile unsigned long ws_send_fail_count = 0;    // WebSocket发送失败计数

// 动态FPS控制
volatile int g_target_fps = 0; // 0=不限，>0 则按该FPS限速发送
```

### 图像质量配置
```cpp
// 摄像头参数设置
framesize_t g_frame_size = FRAMESIZE_VGA;  // 分辨率设置
#define JPEG_QUALITY  17                    // JPEG压缩质量 (1-63)
#define FB_COUNT      2                     // 帧缓冲数量
```

## 🎤 音频系统设计

### 麦克风配置
- **类型**: PDM数字麦克风
- **采样率**: 16kHz (语音识别标准)
- **位深**: 16bit
- **声道**: 单声道
- **数据格式**: PCM16

### 音频处理流程
```cpp
// 音频采集参数
const int SAMPLE_RATE     = 16000;         // 采样率
const int CHUNK_MS        = 20;            // 数据块大小(ms)
const int BYTES_PER_CHUNK = SAMPLE_RATE * CHUNK_MS / 1000 * 2;  // 每块字节数
const int AUDIO_QUEUE_DEPTH = 10;          // 音频队列深度
```

### 扬声器配置
- **类型**: I2S数字音频输出
- **采样率**: 44.1kHz (音频播放标准)
- **位深**: 16bit
- **声道**: 立体声
- **数据格式**: WAV

## 🧭 IMU传感器系统

### ICM42688技术规格
- **类型**: 6轴MEMS传感器
- **接口**: SPI (高速通信)
- **陀螺仪**: ±2000°/s (可配置)
- **加速度计**: ±16g (可配置)
- **采样率**: 最高8kHz
- **功耗**: 低功耗模式 < 1mA

### 数据采集配置
```cpp
// IMU数据采集参数
#define IMU_SAMPLE_RATE   1000    // 采样率 (Hz)
#define IMU_DATA_SIZE     6       // 6轴数据 (3轴陀螺仪 + 3轴加速度计)
#define IMU_PACKET_SIZE   24      // 数据包大小 (6 * 4字节)
```

### 姿态解算算法
```cpp
// 四元数姿态解算
struct Quaternion {
    float w, x, y, z;
};

struct EulerAngles {
    float roll, pitch, yaw;
};

// 姿态数据包结构
struct IMUData {
    float gyro[3];      // 陀螺仪数据 (rad/s)
    float accel[3];     // 加速度数据 (m/s²)
    Quaternion quat;    // 四元数姿态
    EulerAngles euler;  // 欧拉角姿态
    uint32_t timestamp; // 时间戳
};
```

## 📡 通信系统设计

### WiFi连接配置
```cpp
// WiFi网络配置
const char* WIFI_SSID   = "aiglass";           // 网络名称
const char* WIFI_PASS   = "xu137227";          // 网络密码
const char* SERVER_HOST = "47.100.161.139";    // 服务器地址
const uint16_t SERVER_PORT = 8081;             // 服务器端口
```

### WebSocket连接
```cpp
// WebSocket路径定义
static const char* CAM_WS_PATH = "/ws/camera";   // 视频流路径
static const char* AUD_WS_PATH = "/ws_audio";    // 音频流路径
```

### UDP通信
```cpp
// IMU数据UDP传输
WiFiUDP udp;
const uint16_t UDP_PORT = 12345;  // UDP端口
```

## ⚡ 电源管理

### 功耗分析
| 组件 | 工作电流 | 待机电流 | 功耗占比 |
|------|----------|----------|----------|
| **ESP32S3** | 240mA | 10mA | 60% |
| **摄像头** | 120mA | 5mA | 30% |
| **IMU** | 2mA | 0.1mA | 5% |
| **音频** | 50mA | 1mA | 5% |
| **总计** | 412mA | 16.1mA | 100% |

### 电池续航
- **工作模式**: 约2-3小时 (1000mAh电池)
- **待机模式**: 约60小时
- **充电时间**: 2-3小时 (5V/2A充电器)

### 电源优化策略
```cpp
// 动态功耗管理
void enter_light_sleep() {
    // 进入浅睡眠模式
    esp_light_sleep_start();
}

void enter_deep_sleep() {
    // 进入深睡眠模式
    esp_deep_sleep_start();
}

// 组件电源控制
void power_control_camera(bool enable) {
    // 摄像头电源控制
    digitalWrite(CAM_POWER_PIN, enable ? HIGH : LOW);
}
```

## 🔧 硬件调试接口

### 串口调试
```cpp
// 调试输出配置
#define DEBUG_SERIAL Serial
#define DEBUG_BAUD_RATE 115200

// 调试信息输出
void debug_print(const char* message) {
    if (DEBUG_SERIAL) {
        DEBUG_SERIAL.println(message);
    }
}
```

### 性能监控
```cpp
// 系统性能监控
void print_performance_stats() {
    DEBUG_SERIAL.printf("FPS: %d, Free Heap: %d, Uptime: %lu\n", 
                        current_fps, ESP.getFreeHeap(), millis());
}
```

## 🛠️ 硬件组装指南

### 组件清单
- [ ] XIAO ESP32S3开发板 × 1
- [ ] OV5640摄像头模块 × 1
- [ ] PDM数字麦克风 × 1
- [ ] ICM42688 IMU传感器 × 1
- [ ] I2S音频功放模块 × 1
- [ ] 3.7V锂电池 × 1
- [ ] 充电管理模块 × 1
- [ ] 眼镜框架 × 1

### 组装步骤
1. **主板安装**: 将ESP32S3固定在眼镜框架上
2. **摄像头安装**: 将摄像头模块安装在眼镜前方
3. **传感器安装**: 将IMU传感器安装在眼镜侧面
4. **音频模块**: 将麦克风和扬声器安装在合适位置
5. **电源连接**: 连接电池和充电模块
6. **线缆整理**: 整理所有连接线缆

### 注意事项
- **电磁兼容**: 避免高频信号干扰
- **散热设计**: 确保芯片散热良好
- **防水防尘**: 考虑户外使用环境
- **人体工程学**: 确保佩戴舒适

## 🔍 故障排除

### 常见问题
1. **摄像头无法启动**: 检查引脚连接和电源
2. **音频无输出**: 检查I2S配置和功放模块
3. **IMU数据异常**: 检查SPI连接和传感器配置
4. **WiFi连接失败**: 检查网络配置和信号强度

### 调试工具
- **串口监视器**: 查看系统日志
- **示波器**: 检查信号质量
- **万用表**: 测量电压和电流
- **逻辑分析仪**: 分析数字信号

---

**下一步**: 查看 [软件架构文档](../software/README.md) 了解Python后端服务的详细设计。
