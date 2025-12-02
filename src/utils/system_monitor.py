"""
システムリソース監視ユーティリティ
実際のCPU、GPU、メモリ使用率を取得する機能
Google Colaboratory環境にも対応
"""

import time
import threading
from typing import Dict, Optional
import torch

# psutilのインポート（Colab環境で利用できない場合がある）
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("⚠️  psutil not available, using fallback monitoring")

class SystemMonitor:
    """システムリソース監視クラス"""
    
    def __init__(self):
        self.cpu_usage = 0.0
        self.memory_usage = 0.0
        self.gpu_usage = 0.0
        self.gpu_memory_usage = 0.0
        self.gpu_available = False
        self.processing_speed = 0.0
        self.frame_count = 0
        self.last_time = time.time()
        self.monitoring = False
        self.monitor_thread = None
        
    def start_monitoring(self):
        """監視を開始"""
        if not self.monitoring:
            try:
                # 初期データを即座に取得
                self._update_metrics()
                self.monitoring = True
                self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
                self.monitor_thread.start()
                print("✅ System monitoring started successfully")
            except Exception as e:
                print(f"❌ Failed to start system monitoring: {e}")
                # エラーが発生してもアプリケーションは続行
                self.monitoring = False
    
    def _update_metrics(self):
        """メトリクスを更新"""
        try:
            # CPU使用率
            if PSUTIL_AVAILABLE:
                self.cpu_usage = psutil.cpu_percent(interval=0.1)
            else:
                # Colab環境でのフォールバック
                self.cpu_usage = 0.0  # Colabでは正確なCPU使用率は取得困難
            
            # メモリ使用率
            if PSUTIL_AVAILABLE:
                memory = psutil.virtual_memory()
                self.memory_usage = memory.used / (1024 * 1024)  # MB
            else:
                # Colab環境でのフォールバック（torchのメモリ情報を使用）
                if torch.cuda.is_available():
                    self.memory_usage = torch.cuda.memory_allocated() / (1024 * 1024)  # MB
                else:
                    self.memory_usage = 0.0
            
            # GPU使用率（CUDAが利用可能な場合）
            if torch.cuda.is_available():
                try:
                    gpu_memory = torch.cuda.memory_allocated() / (1024 * 1024)  # MB
                    gpu_memory_total = torch.cuda.get_device_properties(0).total_memory / (1024 * 1024)  # MB
                    self.gpu_usage = (gpu_memory / gpu_memory_total) * 100
                    self.gpu_memory_usage = gpu_memory
                    self.gpu_available = True
                except Exception:
                    self.gpu_usage = 0.0
                    self.gpu_memory_usage = 0.0
                    self.gpu_available = False
            else:
                self.gpu_usage = 0.0
                self.gpu_memory_usage = 0.0
                self.gpu_available = False
        except Exception as e:
            print(f"メトリクス更新エラー: {e}")
    
    def stop_monitoring(self):
        """監視を停止"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)
    
    def _monitor_loop(self):
        """監視ループ"""
        while self.monitoring:
            try:
                # メトリクスを更新
                self._update_metrics()
                
                # 処理速度（FPS）の計算
                current_time = time.time()
                self.frame_count += 1
                if current_time - self.last_time >= 1.0:  # 1秒ごとに更新
                    self.processing_speed = self.frame_count / (current_time - self.last_time)
                    self.frame_count = 0
                    self.last_time = current_time
                
                time.sleep(0.5)  # 0.5秒間隔で更新
                
            except Exception as e:
                print(f"監視エラー: {e}")
                time.sleep(1.0)
    
    def get_system_metrics(self) -> Dict[str, float]:
        """現在のシステムメトリクスを取得"""
        # 監視が動作していない場合は、即座にデータを取得
        if not self.monitoring:
            try:
                self._update_metrics()
            except Exception as e:
                print(f"⚠️ Failed to get real-time metrics: {e}")
                # フォールバック: 基本的なシステム情報を取得
                if PSUTIL_AVAILABLE:
                    try:
                        self.cpu_usage = psutil.cpu_percent()
                        memory = psutil.virtual_memory()
                        self.memory_usage = memory.used / (1024 * 1024)
                    except Exception:
                        # 最終的なフォールバック
                        self.cpu_usage = 0.0
                        self.memory_usage = 0.0
                else:
                    # Colab環境でのフォールバック
                    self.cpu_usage = 0.0
                    if torch.cuda.is_available():
                        self.memory_usage = torch.cuda.memory_allocated() / (1024 * 1024)
                    else:
                        self.memory_usage = 0.0
        
        return {
            'cpu_usage': self.cpu_usage,
            'memory_usage': self.memory_usage,
            'gpu_usage': self.gpu_usage,
            'gpu_memory_usage': self.gpu_memory_usage,
            'gpu_available': self.gpu_available,
            'processing_speed': self.processing_speed
        }
    
    def get_detailed_info(self) -> Dict[str, any]:
        """詳細なシステム情報を取得"""
        try:
            # CPU情報
            if PSUTIL_AVAILABLE:
                cpu_count = psutil.cpu_count()
                cpu_freq = psutil.cpu_freq()
            else:
                import os
                cpu_count = os.cpu_count() or 1
                cpu_freq = None
            
            # メモリ情報
            if PSUTIL_AVAILABLE:
                memory = psutil.virtual_memory()
                memory_info = {
                    'total': memory.total / (1024 * 1024),  # MB
                    'available': memory.available / (1024 * 1024),  # MB
                    'used': memory.used / (1024 * 1024),  # MB
                    'usage_percent': memory.percent
                }
            else:
                # Colab環境でのフォールバック
                if torch.cuda.is_available():
                    gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024 * 1024)
                    gpu_allocated = torch.cuda.memory_allocated() / (1024 * 1024)
                    memory_info = {
                        'total': gpu_memory,
                        'available': gpu_memory - gpu_allocated,
                        'used': gpu_allocated,
                        'usage_percent': (gpu_allocated / gpu_memory) * 100 if gpu_memory > 0 else 0
                    }
                else:
                    memory_info = {
                        'total': 0,
                        'available': 0,
                        'used': 0,
                        'usage_percent': 0
                    }
            
            # ディスク情報
            if PSUTIL_AVAILABLE:
                disk = psutil.disk_usage('/')
                disk_info = {
                    'total': disk.total / (1024 * 1024 * 1024),  # GB
                    'used': disk.used / (1024 * 1024 * 1024),  # GB
                    'free': disk.free / (1024 * 1024 * 1024),  # GB
                    'usage_percent': (disk.used / disk.total) * 100
                }
            else:
                # Colab環境ではディスク情報は取得困難
                disk_info = {
                    'total': 0,
                    'used': 0,
                    'free': 0,
                    'usage_percent': 0
                }
            
            # GPU情報
            gpu_info = {}
            if torch.cuda.is_available():
                gpu_info = {
                    'name': torch.cuda.get_device_name(0),
                    'memory_total': torch.cuda.get_device_properties(0).total_memory / (1024 * 1024),  # MB
                    'memory_allocated': torch.cuda.memory_allocated() / (1024 * 1024),  # MB
                    'memory_cached': torch.cuda.memory_reserved() / (1024 * 1024),  # MB
                }
            
            return {
                'cpu': {
                    'count': cpu_count,
                    'frequency': cpu_freq.current if cpu_freq else 0,
                    'usage_percent': self.cpu_usage
                },
                'memory': memory_info,
                'disk': disk_info,
                'gpu': gpu_info
            }
        except Exception as e:
            print(f"詳細情報取得エラー: {e}")
            return {}

# グローバル監視インスタンス
system_monitor = SystemMonitor()
