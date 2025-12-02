"""
ダウンロード状態管理クラス
"""

from typing import Dict, Optional
from threading import Lock


class DownloadState:
    """ダウンロード状態の管理クラス"""
    
    def __init__(self):
        # dataset_id -> {status: str, progress: int, message: str}
        self._states: Dict[str, Dict[str, any]] = {}
        self._lock = Lock()
    
    def set_status(
        self, 
        dataset_id: str, 
        status: str, 
        progress: Optional[int] = None, 
        message: Optional[str] = None
    ) -> Dict[str, any]:
        """
        ダウンロード状態を設定
        
        Args:
            dataset_id: データセットID
            status: ステータス ('idle', 'downloading', 'completed', 'error')
            progress: 進捗率 (0-100)
            message: メッセージ
            
        Returns:
            更新後の状態
        """
        with self._lock:
            state = self._states.get(dataset_id, {
                'status': 'idle', 
                'progress': 0, 
                'message': ''
            })
            
            # 既に完了/エラーなら以降の更新で上書きしない（ダウングレード防止）
            if state.get('status') in ('completed', 'error'):
                return state
            
            state['status'] = status
            if progress is not None:
                state['progress'] = max(0, min(100, int(progress)))
            if message is not None:
                state['message'] = message
            
            self._states[dataset_id] = state
            return state
    
    def get_status(self, dataset_id: str) -> Optional[Dict[str, any]]:
        """ダウンロード状態を取得"""
        with self._lock:
            return self._states.get(dataset_id)
    
    def get_all_statuses(self) -> Dict[str, Dict[str, any]]:
        """すべてのダウンロード状態を取得"""
        with self._lock:
            return self._states.copy()
    
    def clear_status(self, dataset_id: str) -> None:
        """ダウンロード状態をクリア"""
        with self._lock:
            if dataset_id in self._states:
                del self._states[dataset_id]
    
    def clear_all(self) -> None:
        """すべてのダウンロード状態をクリア"""
        with self._lock:
            self._states.clear()


# グローバルインスタンス（後方互換性のため）
_download_state = DownloadState()

def get_download_state() -> DownloadState:
    """ダウンロード状態のシングルトンインスタンスを取得"""
    return _download_state

