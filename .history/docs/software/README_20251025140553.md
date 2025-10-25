# 💻 软件架构文档

## 🏗️ 后端服务架构

### 核心框架
- **Web框架**: FastAPI + Uvicorn
- **异步处理**: asyncio + WebSocket
- **计算机视觉**: OpenCV + NumPy
- **深度学习**: PyTorch + Ultralytics
- **语音处理**: DashScope SDK + PyAudio

## 📁 模块结构

### 主应用层
```
app_main.py                    # FastAPI主服务入口
├── WebSocket路由管理
├── 模型加载与初始化
├── 状态协调与管理
└── 音视频流分发
```

### 导航控制层
```
navigation_master.py           # 导航统领器
├── 状态机管理
├── 工作流协调
├── 语音指令处理
└── 结果整合输出
```

### 工作流模块
```
workflow_blindpath.py          # 盲道导航工作流
├── 盲道分割与检测
├── 障碍物检测
├── 转弯检测
└── 方向引导生成

workflow_crossstreet.py        # 过马路导航工作流
├── 斑马线检测
├── 方向对齐
└── 引导生成

yolomedia.py                   # 物品查找工作流
├── YOLO-E文本提示检测
├── MediaPipe手部追踪
├── 光流目标追踪
└── 手部引导
```

### AI模型层
```
yoloe_backend.py               # YOLO-E开放词汇检测
├── 文本提示设置
├── 实时分割
└── 目标追踪

trafficlight_detection.py      # 红绿灯检测
├── YOLO模型检测
└── HSV颜色分类

obstacle_detector_client.py   # 障碍物检测
├── 白名单类别过滤
├── 路径掩码内检测
└── 物体属性计算
```

### 语音处理层
```
asr_core.py                    # 语音识别核心
├── 实时语音识别
├── VAD语音活动检测
└── 识别结果回调

omni_client.py                 # Qwen-Omni多模态对话
├── 流式对话生成
├── 图像+文本输入
└── 语音输出

audio_player.py                # 音频播放管理
├── TTS语音播放
├── 多路音频混音
└── 线程安全播放
```

### 视频处理层
```
bridge_io.py                    # 线程安全帧缓冲
├── 生产者-消费者模式
├── 原始帧缓存
└── 处理后帧分发

sync_recorder.py               # 音视频同步录制
├── 同步录制视频和音频
├── 自动文件命名
└── 线程安全
```

## 🔄 核心数据流

### 视频处理管道
```python
# 视频流处理流程
def process_video_stream():
    # 1. 接收ESP32视频帧
    raw_jpeg = receive_from_esp32()
    
    # 2. 解码为BGR图像
    frame_bgr = cv2.imdecode(raw_jpeg, cv2.IMREAD_COLOR)
    
    # 3. 状态机处理
    result = navigation_master.process_frame(frame_bgr)
    
    # 4. 编码为JPEG
    processed_jpeg = cv2.imencode('.jpg', result.annotated_image)[1]
    
    # 5. 发送给前端
    send_to_frontend(processed_jpeg)
```

### 音频处理管道
```python
# 音频流处理流程
def process_audio_stream():
    # 1. 接收ESP32音频数据
    pcm_data = receive_from_esp32()
    
    # 2. 语音识别
    text = asr_core.recognize(pcm_data)
    
    # 3. 指令处理
    if text:
        navigation_master.on_voice_command(text)
    
    # 4. TTS语音合成
    audio_response = tts_client.synthesize(response_text)
    
    # 5. 发送给ESP32
    send_to_esp32(audio_response)
```

### IMU数据处理
```python
# IMU数据处理流程
def process_imu_data():
    # 1. 接收UDP数据
    imu_data = receive_udp_data()
    
    # 2. 解析姿态信息
    quaternion = parse_quaternion(imu_data)
    euler_angles = quaternion_to_euler(quaternion)
    
    # 3. 发送给前端
    send_to_frontend({
        'quaternion': quaternion,
        'euler_angles': euler_angles,
        'timestamp': time.time()
    })
```

## 🎛️ 状态机设计

### 状态定义
```python
# 系统状态枚举
IDLE = "IDLE"                          # 空闲状态
CHAT = "CHAT"                          # 对话模式
BLINDPATH_NAV = "BLINDPATH_NAV"        # 盲道导航
SEEKING_CROSSWALK = "SEEKING_CROSSWALK"# 寻找斑马线
CROSSING = "CROSSING"                  # 过马路
ITEM_SEARCH = "ITEM_SEARCH"            # 物品查找
TRAFFIC_LIGHT_DETECTION = "TRAFFIC_LIGHT_DETECTION"  # 红绿灯检测
```

### 状态转换逻辑
```python
class NavigationMaster:
    def __init__(self):
        self.current_state = IDLE
        self.state_history = deque(maxlen=10)
        
    def process_frame(self, frame):
        """处理每一帧，根据当前状态调用相应工作流"""
        if self.current_state == BLINDPATH_NAV:
            return self.blind_path_navigator.process_frame(frame)
        elif self.current_state == CROSSING:
            return self.cross_street_navigator.process_frame(frame)
        elif self.current_state == ITEM_SEARCH:
            return self.item_search_navigator.process_frame(frame)
        # ... 其他状态处理
```

### 状态转换条件
```python
def transition_to_new_state(self, new_state):
    """状态转换逻辑"""
    if self.current_state == IDLE and new_state == BLINDPATH_NAV:
        # 开始盲道导航
        self.start_blind_path_navigation()
    elif self.current_state == BLINDPATH_NAV and new_state == SEEKING_CROSSWALK:
        # 检测到斑马线，准备过马路
        self.prepare_crossing()
    # ... 其他转换逻辑
```

## 🧠 AI模型集成

### 模型加载管理
```python
class ModelManager:
    def __init__(self):
        self.models = {}
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
    def load_models(self):
        """加载所有AI模型"""
        # YOLO-E开放词汇模型
        self.models['yoloe'] = YoloEBackend("yoloe-11l-seg.pt")
        
        # 盲道分割模型
        self.models['blind_path'] = YOLO("yolo-seg.pt")
        
        # 红绿灯检测模型
        self.models['traffic_light'] = YOLO("trafficlight.pt")
        
        # MediaPipe手部检测
        self.models['hands'] = mp.solutions.hands.Hands()
        
        # 障碍物检测模型
        self.models['obstacle'] = ObstacleDetectorClient()
```

### 模型推理管道
```python
def run_ai_inference(self, frame):
    """AI推理管道"""
    results = {}
    
    # 1. 目标检测
    if 'yoloe' in self.models:
        results['detections'] = self.models['yoloe'].segment(frame)
    
    # 2. 手部检测
    if 'hands' in self.models:
        results['hands'] = self.models['hands'].process(frame)
    
    # 3. 盲道检测
    if 'blind_path' in self.models:
        results['blind_path'] = self.models['blind_path'](frame)
    
    return results
```

## 🎤 语音处理系统

### ASR语音识别
```python
class ASRCallback:
    def __init__(self):
        self.asr_client = dash_audio.Recognition()
        
    def on_sentence_end(self, text, is_end):
        """语音识别结果回调"""
        if is_end and text:
            # 处理识别结果
            self.process_voice_command(text)
    
    def process_voice_command(self, text):
        """处理语音指令"""
        # 指令分类
        if "开始导航" in text:
            self.navigation_master.start_blind_path_navigation()
        elif "找物品" in text:
            self.navigation_master.start_item_search()
        # ... 其他指令处理
```

### TTS语音合成
```python
class TTSManager:
    def __init__(self):
        self.tts_client = dash_audio.SpeechSynthesizer()
        
    def synthesize_speech(self, text):
        """语音合成"""
        # 调用阿里云TTS服务
        audio_data = self.tts_client.call(
            model='sambert-zhichu-v1',
            text=text,
            format='wav'
        )
        return audio_data
        
    def play_voice_feedback(self, text):
        """播放语音反馈"""
        audio_data = self.synthesize_speech(text)
        self.audio_player.play_audio_threadsafe(audio_data)
```

## 📹 视频处理系统

### 帧缓冲管理
```python
class BridgeIO:
    def __init__(self):
        self.raw_queue = Queue(maxsize=5)
        self.processed_queue = Queue(maxsize=5)
        
    def push_raw_jpeg(self, jpeg_data):
        """接收原始JPEG帧"""
        if not self.raw_queue.full():
            self.raw_queue.put(jpeg_data)
            
    def wait_raw_bgr(self):
        """获取原始BGR帧"""
        jpeg_data = self.raw_queue.get()
        frame_bgr = cv2.imdecode(jpeg_data, cv2.IMREAD_COLOR)
        return frame_bgr
        
    def send_vis_bgr(self, frame_bgr):
        """发送处理后的帧"""
        if not self.processed_queue.full():
            self.processed_queue.put(frame_bgr)
```

### 视频录制系统
```python
class SyncRecorder:
    def __init__(self):
        self.video_writer = None
        self.audio_writer = None
        self.is_recording = False
        
    def start_recording(self):
        """开始同步录制"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        video_path = f"recordings/video_{timestamp}.avi"
        audio_path = f"recordings/audio_{timestamp}.wav"
        
        # 初始化视频录制器
        self.video_writer = cv2.VideoWriter(
            video_path, cv2.VideoWriter_fourcc(*'XVID'),
            30, (640, 480)
        )
        
        # 初始化音频录制器
        self.audio_writer = wave.open(audio_path, 'wb')
        self.audio_writer.setnchannels(1)
        self.audio_writer.setsampwidth(2)
        self.audio_writer.setframerate(16000)
        
        self.is_recording = True
        
    def record_frame(self, frame):
        """录制视频帧"""
        if self.is_recording and self.video_writer:
            self.video_writer.write(frame)
            
    def record_audio(self, audio_data):
        """录制音频数据"""
        if self.is_recording and self.audio_writer:
            self.audio_writer.writeframes(audio_data)
```

## 🌐 WebSocket通信

### 连接管理
```python
class WebSocketManager:
    def __init__(self):
        self.camera_viewers = set()
        self.audio_connections = set()
        self.imu_connections = set()
        
    async def handle_camera_connection(self, websocket):
        """处理摄像头连接"""
        self.camera_viewers.add(websocket)
        try:
            while True:
                # 发送视频帧
                frame_data = await self.get_next_frame()
                await websocket.send_bytes(frame_data)
        except WebSocketDisconnect:
            self.camera_viewers.remove(websocket)
            
    async def handle_audio_connection(self, websocket):
        """处理音频连接"""
        self.audio_connections.add(websocket)
        try:
            while True:
                # 接收音频数据
                audio_data = await websocket.receive_bytes()
                await self.process_audio_data(audio_data)
        except WebSocketDisconnect:
            self.audio_connections.remove(websocket)
```

### 数据分发
```python
async def broadcast_to_viewers(self, data):
    """广播数据给所有观察者"""
    disconnected = set()
    for viewer in self.camera_viewers:
        try:
            await viewer.send_bytes(data)
        except ConnectionClosed:
            disconnected.add(viewer)
    
    # 清理断开的连接
    self.camera_viewers -= disconnected
```

## 🔧 性能优化

### 异步处理优化
```python
async def process_frame_async(self, frame):
    """异步处理视频帧"""
    # 并行执行多个AI推理任务
    tasks = [
        self.run_object_detection(frame),
        self.run_hand_detection(frame),
        self.run_blind_path_detection(frame)
    ]
    
    results = await asyncio.gather(*tasks)
    return self.combine_results(results)
```

### 内存管理优化
```python
class MemoryManager:
    def __init__(self):
        self.frame_pool = []
        self.max_pool_size = 10
        
    def get_frame_buffer(self):
        """获取帧缓冲区"""
        if self.frame_pool:
            return self.frame_pool.pop()
        return np.zeros((480, 640, 3), dtype=np.uint8)
        
    def return_frame_buffer(self, buffer):
        """归还帧缓冲区"""
        if len(self.frame_pool) < self.max_pool_size:
            self.frame_pool.append(buffer)
```

## 🛡️ 错误处理与恢复

### 异常处理机制
```python
class ErrorHandler:
    def __init__(self):
        self.error_count = 0
        self.max_errors = 10
        
    async def handle_ai_inference_error(self, error):
        """处理AI推理错误"""
        self.error_count += 1
        if self.error_count > self.max_errors:
            # 重启AI服务
            await self.restart_ai_services()
        else:
            # 降级处理
            await self.fallback_processing()
            
    async def handle_websocket_error(self, error):
        """处理WebSocket错误"""
        # 重连机制
        await self.reconnect_websockets()
```

### 系统监控
```python
class SystemMonitor:
    def __init__(self):
        self.cpu_usage = 0
        self.memory_usage = 0
        self.frame_rate = 0
        
    def monitor_performance(self):
        """监控系统性能"""
        # CPU使用率
        self.cpu_usage = psutil.cpu_percent()
        
        # 内存使用率
        self.memory_usage = psutil.virtual_memory().percent
        
        # 帧率统计
        self.frame_rate = self.calculate_frame_rate()
        
        # 性能告警
        if self.cpu_usage > 80:
            self.trigger_performance_alert()
```

---

**下一步**: 查看 [AI模型文档](../ai-models/README.md) 了解深度学习模型的详细设计。
