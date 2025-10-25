# bridge_io.py
# -*- coding: utf-8 -*-
"""
视频流桥接器 - 线程安全帧缓冲
==========================

这是AI智能眼镜导航系统的视频流处理核心模块，负责：
1. 原始JPEG帧缓冲管理
2. 线程安全的帧分发
3. 视频流格式转换
4. 前端数据推送
5. UI文本消息传递

主要功能：
- 帧缓冲：管理原始JPEG帧的缓冲队列
- 格式转换：JPEG到BGR的实时转换
- 线程安全：多线程环境下的安全操作
- 数据分发：向前端推送处理后的帧
- 消息传递：UI文本消息的传递

技术特点：
- 线程安全设计
- 实时帧处理
- 内存高效管理
- 低延迟传输
- 异常容错处理

数据流：
ESP32摄像头 -> JPEG帧 -> 缓冲队列 -> BGR转换 -> AI处理 -> 结果推送

作者：AI智能眼镜开发团队
版本：v2.4
"""

import threading
from collections import deque
import time
import cv2
import numpy as np

# ===== 全局配置 =====
# 原始JPEG帧缓冲（只保留最新 N 帧）
_MAX_BUF = 4
_frames = deque(maxlen=_MAX_BUF)
_cond = threading.Condition()

# ===== 回调函数管理 =====
# 向前端发送JPEG的回调，由 app_main.py 在启动时注册
_sender_lock = threading.Lock()
_sender_cb = None

# 向前端发送UI文本的回调（由 app_main.py 在启动时注册）
_ui_sender_lock = threading.Lock()
_ui_sender_cb = None

def set_sender(cb):
    """由 app_main.py 调用，注册一个函数：cb(jpeg_bytes)->None"""
    global _sender_cb
    with _sender_lock:
        _sender_cb = cb

def set_ui_sender(cb):
    """由 app_main.py 调用，注册一个函数：cb(text:str)->None"""
    global _ui_sender_cb
    with _ui_sender_lock:
        _ui_sender_cb = cb

def push_raw_jpeg(jpeg_bytes: bytes):
    """由 app_main.py 在收到 /ws/camera 帧时调用"""
    if not jpeg_bytes:
        return
    with _cond:
        _frames.append((time.time(), jpeg_bytes))
        _cond.notify_all()

def wait_raw_bgr(timeout_sec: float = 0.5):
    """被 YOLO/MediaPipe 脚本调用：等待并拿到最新一帧BGR；超时返回 None"""
    t_end = time.time() + timeout_sec
    last = None
    while time.time() < t_end:
        with _cond:
            if _frames:
                last = _frames[-1]
        if last is None:
            time.sleep(0.01)
            continue
        # 解码JPEG为BGR
        ts, jpeg = last
        arr = np.frombuffer(jpeg, dtype=np.uint8)
        bgr = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if bgr is not None:
            # 在最源头进行镜像处理
            #bgr = cv2.flip(bgr, 1)
            return bgr
        # 解码失败，稍等重试
        time.sleep(0.01)
    return None

def send_vis_bgr(bgr, quality: int = 80):
    """被 YOLO/MediaPipe 脚本调用：把处理后画面推给前端 viewer"""
    if bgr is None:
        return
    
    # 直接编码，不做任何增强处理
    ok, enc = cv2.imencode(".jpg", bgr, [int(cv2.IMWRITE_JPEG_QUALITY), int(quality)])
    if not ok:
        return
    with _sender_lock:
        cb = _sender_cb
    if cb:
        try:
            cb(enc.tobytes())
        except Exception:
            pass

def send_ui_final(text: str):
    """把一条UI文案作为 final answer 推给前端（线程安全回调）"""
    if not text:
        return
    with _ui_sender_lock:
        cb = _ui_sender_cb
    if cb:
        try:
            cb(str(text))
        except Exception:
            pass
