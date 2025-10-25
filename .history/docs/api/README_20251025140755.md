# 🔌 API接口文档

## 📡 接口概览

本项目提供RESTful API和WebSocket接口，支持实时音视频传输、语音识别、AI导航等功能。

### 接口分类
- **WebSocket接口**: 实时音视频流、IMU数据
- **REST API**: 系统控制、状态查询
- **HTTP接口**: 静态资源、音频流

## 🌐 WebSocket接口

### 1. 视频流接口

#### 连接路径
```
ws://server:port/ws/camera
```

#### 功能描述
- 接收ESP32摄像头视频流
- 发送处理后的视频帧给前端
- 支持多客户端连接

#### 数据格式
```json
{
  "type": "video_frame",
  "data": "base64_encoded_jpeg",
  "timestamp": 1640995200.123,
  "frame_id": 12345
}
```

#### 客户端连接示例
```javascript
const cameraSocket = new WebSocket('ws://localhost:8081/ws/camera');

cameraSocket.onopen = function() {
    console.log('摄像头连接已建立');
};

cameraSocket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    if (data.type === 'video_frame') {
        // 显示视频帧
        displayVideoFrame(data.data);
    }
};
```

### 2. 音频流接口

#### 连接路径
```
ws://server:port/ws_audio
```

#### 功能描述
- 接收ESP32麦克风音频流
- 发送TTS音频给ESP32
- 双向音频通信

#### 数据格式
```json
{
  "type": "audio_chunk",
  "data": "base64_encoded_pcm",
  "sample_rate": 16000,
  "channels": 1,
  "timestamp": 1640995200.123
}
```

#### 音频处理示例
```python
async def handle_audio_connection(websocket: WebSocket):
    """处理音频连接"""
    await websocket.accept()
    
    try:
        while True:
            # 接收音频数据
            data = await websocket.receive_bytes()
            
            # 语音识别
            text = await asr_core.recognize(data)
            
            if text:
                # 处理语音指令
                response = await navigation_master.process_voice_command(text)
                
                # 发送TTS音频
                if response.audio:
                    await websocket.send_bytes(response.audio)
                    
    except WebSocketDisconnect:
        print("音频连接断开")
```

### 3. IMU数据接口

#### 连接路径
```
ws://server:port/ws
```

#### 功能描述
- 接收ESP32 IMU传感器数据
- 发送姿态信息给前端
- 3D可视化支持

#### 数据格式
```json
{
  "type": "imu_data",
  "quaternion": {
    "w": 0.707,
    "x": 0.0,
    "y": 0.0,
    "z": 0.707
  },
  "euler_angles": {
    "roll": 0.0,
    "pitch": 0.0,
    "yaw": 90.0
  },
  "gyroscope": {
    "x": 0.1,
    "y": 0.2,
    "z": 0.3
  },
  "accelerometer": {
    "x": 0.0,
    "y": 0.0,
    "z": 9.8
  },
  "timestamp": 1640995200.123
}
```

## 🔗 REST API接口

### 1. 系统状态接口

#### 获取系统状态
```http
GET /api/status
```

**响应示例**:
```json
{
  "status": "running",
  "current_mode": "BLINDPATH_NAV",
  "fps": 30,
  "cpu_usage": 45.2,
  "memory_usage": 67.8,
  "active_connections": {
    "camera": 2,
    "audio": 1,
    "imu": 1
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### 切换导航模式
```http
POST /api/navigation/mode
Content-Type: application/json

{
  "mode": "BLINDPATH_NAV",
  "parameters": {
    "confidence_threshold": 0.3,
    "detection_range": 5.0
  }
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "导航模式已切换",
  "current_mode": "BLINDPATH_NAV",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### 2. AI模型接口

#### 获取模型状态
```http
GET /api/models/status
```

**响应示例**:
```json
{
  "models": {
    "yoloe": {
      "status": "loaded",
      "version": "v1.2.0",
      "inference_time": 25.5,
      "memory_usage": 1024
    },
    "blind_path": {
      "status": "loaded",
      "version": "v2.1.0",
      "inference_time": 15.2,
      "memory_usage": 512
    },
    "traffic_light": {
      "status": "loaded",
      "version": "v1.0.0",
      "inference_time": 8.1,
      "memory_usage": 256
    }
  }
}
```

#### 重新加载模型
```http
POST /api/models/reload
Content-Type: application/json

{
  "model_name": "yoloe",
  "version": "v1.3.0"
}
```

### 3. 配置管理接口

#### 获取系统配置
```http
GET /api/config
```

**响应示例**:
```json
{
  "camera": {
    "resolution": "VGA",
    "fps": 30,
    "quality": 17
  },
  "audio": {
    "sample_rate": 16000,
    "channels": 1,
    "chunk_size": 20
  },
  "imu": {
    "sample_rate": 1000,
    "data_format": "quaternion"
  },
  "ai": {
    "confidence_threshold": 0.3,
    "iou_threshold": 0.45
  }
}
```

#### 更新系统配置
```http
PUT /api/config
Content-Type: application/json

{
  "camera": {
    "fps": 25
  },
  "ai": {
    "confidence_threshold": 0.4
  }
}
```

## 🎵 音频流接口

### 音频流播放
```http
GET /stream.wav
```

**功能描述**:
- 提供实时音频流
- 支持TTS语音播放
- 格式: WAV格式

**响应头**:
```
Content-Type: audio/wav
Cache-Control: no-cache
Connection: keep-alive
```

## 📊 数据流接口

### 1. 视频流处理

#### 视频帧处理流程
```python
@app.websocket("/ws/camera")
async def camera_endpoint(websocket: WebSocket):
    """摄像头WebSocket端点"""
    await websocket.accept()
    
    try:
        while True:
            # 接收原始视频帧
            data = await websocket.receive_bytes()
            
            # 解码JPEG
            frame = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
            
            # AI处理
            result = await navigation_master.process_frame(frame)
            
            # 编码处理后的帧
            _, encoded = cv2.imencode('.jpg', result.annotated_image)
            
            # 发送给前端
            await camera_viewers.broadcast(encoded.tobytes())
            
    except WebSocketDisconnect:
        camera_viewers.remove(websocket)
```

### 2. 音频流处理

#### 音频数据处理流程
```python
@app.websocket("/ws_audio")
async def audio_endpoint(websocket: WebSocket):
    """音频WebSocket端点"""
    await websocket.accept()
    
    try:
        while True:
            # 接收音频数据
            audio_data = await websocket.receive_bytes()
            
            # 语音识别
            text = await asr_core.recognize(audio_data)
            
            if text:
                # 处理语音指令
                response = await navigation_master.process_voice_command(text)
                
                # 生成TTS音频
                if response.audio_text:
                    tts_audio = await tts_client.synthesize(response.audio_text)
                    await websocket.send_bytes(tts_audio)
                    
    except WebSocketDisconnect:
        print("音频连接断开")
```

### 3. IMU数据处理

#### IMU数据流处理
```python
@app.websocket("/ws")
async def imu_endpoint(websocket: WebSocket):
    """IMU数据WebSocket端点"""
    await websocket.accept()
    
    try:
        while True:
            # 接收IMU数据
            data = await websocket.receive_json()
            
            # 处理姿态数据
            imu_data = process_imu_data(data)
            
            # 发送给前端
            await imu_viewers.broadcast(imu_data)
            
    except WebSocketDisconnect:
        imu_viewers.remove(websocket)
```

## 🔐 认证与安全

### API密钥认证
```http
GET /api/status
Authorization: Bearer your-api-key
```

### 请求限制
```python
# 速率限制配置
RATE_LIMITS = {
    "camera": "30fps",
    "audio": "50req/min",
    "api": "100req/min"
}
```

### 数据验证
```python
from pydantic import BaseModel, Field

class NavigationModeRequest(BaseModel):
    mode: str = Field(..., regex="^(IDLE|CHAT|BLINDPATH_NAV|CROSSING|ITEM_SEARCH)$")
    parameters: dict = Field(default_factory=dict)
    
class ConfigUpdateRequest(BaseModel):
    camera: dict = Field(default_factory=dict)
    audio: dict = Field(default_factory=dict)
    ai: dict = Field(default_factory=dict)
```

## 📈 性能监控接口

### 系统性能指标
```http
GET /api/metrics
```

**响应示例**:
```json
{
  "system": {
    "cpu_usage": 45.2,
    "memory_usage": 67.8,
    "disk_usage": 23.1,
    "network_usage": 12.5
  },
  "ai_models": {
    "yoloe": {
      "inference_time": 25.5,
      "memory_usage": 1024,
      "throughput": 39.2
    }
  },
  "connections": {
    "camera": 2,
    "audio": 1,
    "imu": 1,
    "total": 4
  }
}
```

### 实时日志接口
```http
GET /api/logs?level=info&limit=100
```

**响应示例**:
```json
{
  "logs": [
    {
      "timestamp": "2024-01-01T12:00:00Z",
      "level": "INFO",
      "message": "视频帧处理完成",
      "module": "camera_processor"
    }
  ],
  "total": 100,
  "has_more": true
}
```

## 🛠️ 错误处理

### 错误响应格式
```json
{
  "error": {
    "code": "INVALID_MODE",
    "message": "无效的导航模式",
    "details": {
      "provided_mode": "INVALID",
      "valid_modes": ["IDLE", "CHAT", "BLINDPATH_NAV", "CROSSING", "ITEM_SEARCH"]
    },
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

### 常见错误码
| 错误码 | 描述 | 解决方案 |
|--------|------|----------|
| `INVALID_MODE` | 无效的导航模式 | 使用有效的模式名称 |
| `MODEL_NOT_LOADED` | 模型未加载 | 检查模型文件是否存在 |
| `CONNECTION_FAILED` | 连接失败 | 检查网络连接 |
| `AUTHENTICATION_FAILED` | 认证失败 | 检查API密钥 |

## 📝 接口测试

### 使用curl测试
```bash
# 获取系统状态
curl -X GET http://localhost:8081/api/status

# 切换导航模式
curl -X POST http://localhost:8081/api/navigation/mode \
  -H "Content-Type: application/json" \
  -d '{"mode": "BLINDPATH_NAV"}'

# 获取模型状态
curl -X GET http://localhost:8081/api/models/status
```

### 使用Python测试
```python
import requests
import websocket
import json

# 测试REST API
response = requests.get('http://localhost:8081/api/status')
print(response.json())

# 测试WebSocket
def on_message(ws, message):
    print(f"收到消息: {message}")

ws = websocket.WebSocketApp("ws://localhost:8081/ws/camera",
                           on_message=on_message)
ws.run_forever()
```

---

**下一步**: 查看 [部署指南](../deployment/README.md) 了解系统部署配置。
