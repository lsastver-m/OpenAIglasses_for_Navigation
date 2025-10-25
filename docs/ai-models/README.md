# 🤖 AI模型文档

## 📊 模型概览

本项目集成了多个深度学习模型，实现智能导航辅助功能。所有模型都经过优化，确保在边缘设备上的实时性能。

### 模型列表
| 模型名称 | 功能 | 框架 | 大小 | 精度 |
|----------|------|------|------|------|
| **YOLO-E** | 开放词汇目标检测 | Ultralytics | 45MB | 95%+ |
| **盲道分割** | 盲道识别与分割 | YOLO-Seg | 12MB | 92%+ |
| **红绿灯检测** | 交通信号识别 | YOLO | 8MB | 98%+ |
| **手部检测** | 手部关键点追踪 | MediaPipe | 15MB | 96%+ |
| **障碍物检测** | 障碍物识别 | YOLO | 10MB | 90%+ |

## 🎯 YOLO-E 开放词汇模型

### 模型架构
```python
class YoloEBackend:
    def __init__(self, model_path: str):
        self.model = YOLO(model_path)
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)
        
    def set_text_classes(self, names: List[str]):
        """设置文本提示类别"""
        self.model.set_classes(names, self.model.get_text_pe(names))
```

### 技术规格
- **基础模型**: YOLO-E 11L
- **输入尺寸**: 640×640
- **输出**: 边界框 + 分割掩码
- **推理速度**: 30ms (RTX 3060)
- **内存占用**: 2GB VRAM

### 使用示例
```python
# 初始化模型
yoloe = YoloEBackend("yoloe-11l-seg.pt")

# 设置检测类别
classes = ["盲道", "斑马线", "红绿灯", "障碍物"]
yoloe.set_text_classes(classes)

# 执行检测
results = yoloe.segment(
    frame_bgr,
    conf=0.20,
    iou=0.45,
    imgsz=640
)

# 处理结果
for mask, box, cls_id, name in zip(
    results['masks'], 
    results['boxes'], 
    results['cls_ids'], 
    results['names']
):
    print(f"检测到: {name}, 置信度: {cls_id}")
```

## 🛤️ 盲道分割模型

### 模型特点
- **专门训练**: 针对盲道特征优化
- **高精度**: 在盲道数据集上达到92%+准确率
- **实时性**: 推理时间 < 50ms
- **鲁棒性**: 适应不同光照和天气条件

### 技术实现
```python
class BlindPathDetector:
    def __init__(self):
        self.model = YOLO("yolo-seg.pt")
        self.confidence_threshold = 0.3
        
    def detect_blind_path(self, frame):
        """检测盲道"""
        results = self.model(frame, conf=self.confidence_threshold)
        
        blind_path_masks = []
        for result in results:
            if result.names[result.boxes.cls[0]] == "blind_path":
                mask = result.masks.data[0].cpu().numpy()
                blind_path_masks.append(mask)
                
        return blind_path_masks
```

### 后处理算法
```python
def process_blind_path_mask(self, mask):
    """处理盲道掩码"""
    # 形态学操作
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    
    # 连通域分析
    num_labels, labels = cv2.connectedComponents(mask)
    
    # 选择最大连通域
    largest_component = self.get_largest_component(labels)
    
    return largest_component
```

## 🚦 红绿灯检测模型

### 模型架构
```python
class TrafficLightDetector:
    def __init__(self):
        self.yolo_model = YOLO("trafficlight.pt")
        self.hsv_ranges = {
            'red': [(0, 50, 50), (10, 255, 255)],
            'green': [(40, 50, 50), (80, 255, 255)],
            'yellow': [(20, 50, 50), (30, 255, 255)]
        }
        
    def detect_traffic_light(self, frame):
        """检测红绿灯"""
        # YOLO检测
        yolo_results = self.yolo_model(frame, conf=0.5)
        
        # HSV颜色分析
        hsv_results = self.analyze_hsv_colors(frame, yolo_results)
        
        # 结果融合
        final_result = self.fuse_detection_results(yolo_results, hsv_results)
        
        return final_result
```

### 颜色识别算法
```python
def analyze_hsv_colors(self, frame, detections):
    """HSV颜色分析"""
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    results = []
    for detection in detections:
        x1, y1, x2, y2 = detection.boxes.xyxy[0]
        roi = hsv_frame[int(y1):int(y2), int(x1):int(x2)]
        
        # 分析ROI中的颜色
        color = self.dominant_color(roi)
        results.append({
            'box': [x1, y1, x2, y2],
            'color': color,
            'confidence': detection.boxes.conf[0]
        })
    
    return results
```

## ✋ 手部检测模型

### MediaPipe集成
```python
class HandDetector:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
    def detect_hands(self, frame):
        """检测手部关键点"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        
        hand_landmarks = []
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # 提取关键点坐标
                landmarks = self.extract_landmarks(hand_landmarks)
                hand_landmarks.append(landmarks)
                
        return hand_landmarks
```

### 手部追踪算法
```python
def track_hand_movement(self, current_landmarks, previous_landmarks):
    """追踪手部运动"""
    if not previous_landmarks:
        return None
        
    # 计算关键点位移
    displacement = self.calculate_displacement(
        current_landmarks, 
        previous_landmarks
    )
    
    # 运动方向分析
    direction = self.analyze_movement_direction(displacement)
    
    # 手势识别
    gesture = self.recognize_gesture(current_landmarks)
    
    return {
        'displacement': displacement,
        'direction': direction,
        'gesture': gesture
    }
```

## 🚧 障碍物检测模型

### 多类别检测
```python
class ObstacleDetector:
    def __init__(self):
        self.model = YOLO("obstacle.pt")
        self.whitelist_classes = [
            "person", "car", "bicycle", "motorcycle", 
            "bus", "truck", "traffic_cone", "barrier"
        ]
        
    def detect_obstacles(self, frame, path_mask=None):
        """检测障碍物"""
        results = self.model(frame, conf=0.3)
        
        obstacles = []
        for result in results:
            for i, cls_id in enumerate(result.boxes.cls):
                class_name = result.names[int(cls_id)]
                
                if class_name in self.whitelist_classes:
                    # 计算障碍物属性
                    obstacle_info = self.analyze_obstacle(
                        result.boxes.xyxy[i],
                        result.boxes.conf[i],
                        class_name,
                        path_mask
                    )
                    obstacles.append(obstacle_info)
                    
        return obstacles
```

### 障碍物分析
```python
def analyze_obstacle(self, bbox, confidence, class_name, path_mask):
    """分析障碍物属性"""
    x1, y1, x2, y2 = bbox
    
    # 计算面积
    area = (x2 - x1) * (y2 - y1)
    
    # 计算中心点
    center_x = (x1 + x2) / 2
    center_y = (y1 + y2) / 2
    
    # 检查是否在路径上
    in_path = self.check_in_path(center_x, center_y, path_mask)
    
    # 计算危险度
    danger_level = self.calculate_danger_level(
        class_name, area, confidence, in_path
    )
    
    return {
        'bbox': bbox,
        'class_name': class_name,
        'confidence': confidence,
        'area': area,
        'center': (center_x, center_y),
        'in_path': in_path,
        'danger_level': danger_level
    }
```

## 🔄 模型推理优化

### 批处理推理
```python
class BatchInference:
    def __init__(self, batch_size=4):
        self.batch_size = batch_size
        self.frame_queue = Queue(maxsize=batch_size)
        
    async def batch_inference(self, frames):
        """批处理推理"""
        if len(frames) < self.batch_size:
            # 填充到批次大小
            frames.extend([frames[-1]] * (self.batch_size - len(frames)))
            
        # 批量推理
        results = await self.run_batch_inference(frames)
        
        return results[:len(frames)]  # 返回原始数量的结果
```

### 模型量化
```python
def quantize_model(self, model_path):
    """模型量化"""
    # 加载模型
    model = torch.load(model_path)
    
    # 量化配置
    quantization_config = torch.quantization.get_default_qconfig('fbgemm')
    
    # 应用量化
    quantized_model = torch.quantization.quantize_dynamic(
        model, 
        {torch.nn.Linear}, 
        dtype=torch.qint8
    )
    
    return quantized_model
```

### 内存管理
```python
class ModelMemoryManager:
    def __init__(self):
        self.model_cache = {}
        self.max_cache_size = 3
        
    def load_model(self, model_name):
        """动态加载模型"""
        if model_name in self.model_cache:
            return self.model_cache[model_name]
            
        # 检查缓存大小
        if len(self.model_cache) >= self.max_cache_size:
            # 移除最久未使用的模型
            oldest_model = min(self.model_cache.keys())
            del self.model_cache[oldest_model]
            
        # 加载新模型
        model = self.load_model_from_disk(model_name)
        self.model_cache[model_name] = model
        
        return model
```

## 📈 性能监控

### 推理性能统计
```python
class InferenceProfiler:
    def __init__(self):
        self.inference_times = deque(maxlen=100)
        self.memory_usage = deque(maxlen=100)
        
    def profile_inference(self, model_name, inference_func, *args):
        """性能分析"""
        start_time = time.time()
        start_memory = torch.cuda.memory_allocated()
        
        # 执行推理
        result = inference_func(*args)
        
        end_time = time.time()
        end_memory = torch.cuda.memory_allocated()
        
        # 记录性能数据
        inference_time = end_time - start_time
        memory_usage = end_memory - start_memory
        
        self.inference_times.append(inference_time)
        self.memory_usage.append(memory_usage)
        
        return result
        
    def get_performance_stats(self):
        """获取性能统计"""
        return {
            'avg_inference_time': np.mean(self.inference_times),
            'max_inference_time': np.max(self.inference_times),
            'avg_memory_usage': np.mean(self.memory_usage),
            'max_memory_usage': np.max(self.memory_usage)
        }
```

### 模型精度评估
```python
def evaluate_model_accuracy(self, model, test_dataset):
    """评估模型精度"""
    model.eval()
    correct_predictions = 0
    total_predictions = 0
    
    with torch.no_grad():
        for batch in test_dataset:
            inputs, labels = batch
            outputs = model(inputs)
            predictions = torch.argmax(outputs, dim=1)
            
            correct_predictions += (predictions == labels).sum().item()
            total_predictions += labels.size(0)
            
    accuracy = correct_predictions / total_predictions
    return accuracy
```

## 🔧 模型部署

### Docker容器化
```dockerfile
# Dockerfile for AI models
FROM pytorch/pytorch:2.0.1-cuda11.8-cudnn8-devel

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install -r requirements.txt

# 复制模型文件
COPY model/ ./model/

# 复制代码
COPY . .

# 启动服务
CMD ["python", "app_main.py"]
```

### 模型版本管理
```python
class ModelVersionManager:
    def __init__(self):
        self.model_versions = {
            'yoloe': 'v1.2.0',
            'blind_path': 'v2.1.0',
            'traffic_light': 'v1.0.0',
            'hand_detection': 'v1.5.0'
        }
        
    def check_model_updates(self):
        """检查模型更新"""
        for model_name, current_version in self.model_versions.items():
            latest_version = self.get_latest_version(model_name)
            if latest_version != current_version:
                self.update_model(model_name, latest_version)
```

---

**下一步**: 查看 [API接口文档](../api/README.md) 了解系统接口设计。
