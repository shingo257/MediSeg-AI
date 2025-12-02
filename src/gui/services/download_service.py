"""
ダウンロードサービス
データセットのダウンロード処理と状態管理
"""

import threading
import time
from typing import Dict, Optional, Tuple

from src.data_loaders.download_datasets import DatasetDownloader
from src.data_loaders.real_datasets import RealDatasetDownloader
from src.gui.state.download_state import get_download_state


class DownloadService:
    """ダウンロード処理のサービス"""
    
    def __init__(self, data_dir: str = 'data'):
        self.data_dir = data_dir
        self.downloader = DatasetDownloader(data_dir=data_dir)
        self.real_downloader = RealDatasetDownloader(data_dir=data_dir)
        self.download_state = get_download_state()
    
    def start_download(
        self, 
        dataset_id: str
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        データセットのダウンロードを開始
        
        Args:
            dataset_id: データセットID
            
        Returns:
            (成功, エラーメッセージ, 保存先パス)
        """
        # ダウンロード状態を設定
        self.download_state.set_status(dataset_id, 'downloading', 1, '開始')
        
        def _worker():
            try:
                # 進捗ティッカー
                progress_holder = {'value': 1, 'running': True}
                
                def _ticker():
                    while progress_holder['running'] and progress_holder['value'] < 95:
                        state = self.download_state.get_status(dataset_id)
                        if state and state.get('status') in ('completed', 'error'):
                            break
                        time.sleep(1.0)
                        progress_holder['value'] += 3
                        self.download_state.set_status(
                            dataset_id, 
                            'downloading', 
                            progress_holder['value']
                        )
                
                ticker_thread = threading.Thread(target=_ticker, daemon=True)
                ticker_thread.start()
                
                # 自動ルーティング: まず実データセット辞書を優先、なければ合成側
                route_real = dataset_id in getattr(self.real_downloader, 'datasets', {})
                route_synth = dataset_id in getattr(self.downloader, 'datasets', {})
                
                if not route_real and not route_synth:
                    self.download_state.set_status(
                        dataset_id, 
                        'error', 
                        progress_holder['value'], 
                        'Unknown dataset'
                    )
                    return
                
                if route_real:
                    ok = self.real_downloader.download_dataset(dataset_id)
                else:
                    ok = self.downloader.download_dataset(dataset_id)
                
                progress_holder['running'] = False
                
                if ok:
                    self.download_state.set_status(
                        dataset_id, 
                        'completed', 
                        100, 
                        '完了'
                    )
                else:
                    self.download_state.set_status(
                        dataset_id, 
                        'error', 
                        progress_holder['value'], 
                        '失敗'
                    )
            except Exception as e:
                self.download_state.set_status(dataset_id, 'error', 0, str(e))
        
        # バックグラウンドでダウンロードを開始
        t = threading.Thread(target=_worker, daemon=True)
        t.start()
        
        # 保存先情報を取得
        info = None
        base_path = None
        if dataset_id in getattr(self.real_downloader, 'datasets', {}):
            info = self.real_downloader.datasets.get(dataset_id, {})
            base_path = str(
                (self.real_downloader.data_dir / info.get('extract_to', dataset_id)).resolve()
            )
        elif dataset_id in getattr(self.downloader, 'datasets', {}):
            info = self.downloader.datasets.get(dataset_id, {})
            base_path = str(
                (self.downloader.data_dir / info.get('extract_to', dataset_id)).resolve()
            )
        
        return True, None, base_path
    
    def get_download_status(
        self, 
        dataset_id: str, 
        check_files: bool = False,
        file_checker=None
    ) -> Optional[Dict[str, any]]:
        """
        ダウンロード状態を取得
        
        Args:
            dataset_id: データセットID
            check_files: ファイルの存在をチェックするか
            file_checker: ファイル存在チェック関数
            
        Returns:
            ダウンロード状態
        """
        state = self.download_state.get_status(dataset_id)
        
        # ダウンロード中の状態をチェック
        if state and state.get('status') == 'downloading':
            return state
        
        if check_files and file_checker:
            # 実ファイルの存在を確認
            has_files = file_checker(dataset_id)
            
            if has_files:
                state = {
                    'status': 'completed',
                    'progress': 100,
                    'message': '完了'
                }
                self.download_state.set_status(
                    dataset_id, 
                    'completed', 
                    100, 
                    '完了'
                )
            else:
                # ファイルが存在しない場合「未開始」
                state = {
                    'status': 'idle',
                    'progress': 0,
                    'message': '未開始'
                }
                # 既存の完了/エラー状態は保持（ダウングレード防止）
                existing_state = self.download_state.get_status(dataset_id)
                if existing_state and existing_state.get('status') in ('completed', 'error'):
                    state = existing_state
                else:
                    self.download_state.set_status(
                        dataset_id, 
                        'idle', 
                        0, 
                        '未開始'
                    )
        
        return state

