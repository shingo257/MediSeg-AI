"""
データセットサービス
データセットの管理と操作
"""

import os
from typing import Dict, List, Optional, Any
from pathlib import Path

from src.data_loaders.download_datasets import DatasetDownloader
from src.data_loaders.real_datasets import RealDatasetDownloader
from src.gui.utils.image_utils import has_any_images, load_image_any, to_thumbnail_b64, EXTENSIONS
from src.gui.state.download_state import get_download_state


class DatasetService:
    """データセット管理のサービス"""
    
    def __init__(self, data_dir: str = 'data'):
        self.data_dir = data_dir
        self.downloader = DatasetDownloader(data_dir=data_dir)
        self.real_downloader = RealDatasetDownloader(data_dir=data_dir)
        self.download_state = get_download_state()
    
    def list_datasets(self) -> List[Dict[str, Any]]:
        """
        利用可能なデータセット一覧を取得
        
        Returns:
            データセット情報のリスト
        """
        datasets = []
        
        # 実際のデータセット情報を取得
        for dataset_id, info in self.real_downloader.datasets.items():
            # ダウンロード状態を確認（実ファイルの有無で判定）
            base_path = self.real_downloader.get_dataset_path(dataset_id)
            is_downloaded = bool(base_path) and has_any_images(str(base_path))
            
            # ダウンロード中の状態をチェック
            download_state = self.download_state.get_status(dataset_id)
            is_downloading = download_state and download_state.get('status') == 'downloading'
            
            # ステータスを決定
            if is_downloading:
                progress = download_state.get('progress', 0)
                status = 'downloading'
                status_text = f'ダウンロード中 {progress}%'
                status_icon = '⏳'
            elif is_downloaded:
                status = 'downloaded'
                status_text = 'ダウンロード済み'
                status_icon = '✅'
            else:
                status = 'available'
                status_text = '利用可能'
                status_icon = '⬇️'
            
            # 実データから画像数を取得
            image_count = 'N/A'
            if base_path and os.path.exists(base_path):
                images_dir = os.path.join(
                    str(base_path), 
                    info.get('images_dir', '')
                ) if info.get('images_dir') else str(base_path)
                if os.path.exists(images_dir):
                    count = sum(
                        1 for root, _, files in os.walk(images_dir) 
                        for f in files if f.lower().endswith(EXTENSIONS)
                    )
                    if count > 0:
                        image_count = str(count)
            
            dataset = {
                'id': dataset_id,
                'name': info.get('name', dataset_id),
                'description': info.get('description', ''),
                'icon': info.get('icon', '🏥'),
                'imageCount': image_count,
                'resolution': info.get('resolution', 'N/A'),
                'size': info.get('size', 'N/A'),
                'format': info.get('format', 'N/A'),
                'status': status,
                'statusText': status_text,
                'statusIcon': status_icon,
                'downloaded': is_downloaded,
                'is_downloading': is_downloading
            }
            datasets.append(dataset)
        
        return datasets
    
    def get_dataset_details(self, dataset_id: str) -> Optional[Dict[str, Any]]:
        """
        データセットの詳細情報を取得
        
        Args:
            dataset_id: データセットID
            
        Returns:
            データセット詳細情報、存在しない場合はNone
        """
        if dataset_id not in self.real_downloader.datasets:
            return None
        
        info = self.real_downloader.datasets[dataset_id]
        base_path = self.real_downloader.get_dataset_path(dataset_id)
        
        if base_path is None:
            return None
        
        images_dir = os.path.join(str(base_path), info.get('images_dir', '')) if info.get('images_dir') else str(base_path)
        masks_dir = os.path.join(str(base_path), info.get('masks_dir', '')) if info.get('masks_dir') else str(base_path)
        
        def _count_files(d):
            cnt = 0
            if d and os.path.exists(d):
                for _, _, files in os.walk(d):
                    cnt += len(files)
            return cnt
        
        images_count = _count_files(images_dir)
        masks_count = _count_files(masks_dir)
        
        return {
            'name': info.get('name', dataset_id),
            'description': info.get('description', ''),
            'imageCount': images_count,
            'resolution': info.get('resolution', 'N/A'),
            'size': info.get('size', 'N/A'),
            'format': info.get('format', 'N/A'),
            'category': info.get('type', 'N/A'),
            'files': {
                'images': images_count,
                'masks': masks_count
            }
        }
    
    def get_dataset_samples(self, dataset_id: str, max_samples: int = 6) -> List[Dict[str, str]]:
        """
        データセットのサンプル画像を取得
        
        Args:
            dataset_id: データセットID
            max_samples: 最大サンプル数
            
        Returns:
            サンプル画像のリスト
        """
        samples: List[Dict[str, str]] = []
        
        base_path = None
        if dataset_id in self.real_downloader.datasets:
            base_path = self.real_downloader.get_dataset_path(dataset_id)
        
        if base_path and os.path.exists(base_path):
            # 再帰的に拡張子マッチを探索
            found_files = []
            for root, _, files in os.walk(base_path):
                for f in files:
                    if f.lower().endswith(EXTENSIONS):
                        found_files.append(os.path.join(root, f))
                if len(found_files) >= max_samples * 4:  # 余裕を持って探索
                    break
            
            # 最大サンプル数を可視化
            for path in found_files[:max_samples]:
                img_rgb = load_image_any(path)
                if img_rgb is None:
                    continue
                b64 = to_thumbnail_b64(img_rgb)
                samples.append({'filename': os.path.basename(path), 'image': b64})
        
        return samples
    
    def list_dataset_files(
        self, 
        dataset_id: str, 
        kind: str = 'images',
        limit: int = 50,
        offset: int = 0,
        query: str = ''
    ) -> Dict[str, Any]:
        """
        データセットのファイル一覧を取得
        
        Args:
            dataset_id: データセットID
            kind: ファイル種別 ('images' or 'labels')
            limit: 取得件数
            offset: オフセット
            query: 検索クエリ
            
        Returns:
            ファイル一覧情報
        """
        if dataset_id not in self.real_downloader.datasets:
            return {'files': [], 'total': 0, 'offset': offset, 'limit': limit}
        
        info = self.real_downloader.datasets[dataset_id]
        base = self.real_downloader.get_dataset_path(dataset_id)
        
        if not base:
            return {'files': [], 'total': 0, 'offset': offset, 'limit': limit}
        
        subdir = info.get('images_dir' if kind == 'images' else 'masks_dir', '')
        target = os.path.join(str(base), subdir) if subdir else str(base)
        
        all_files = []
        if os.path.exists(target):
            for root, _, fnames in os.walk(target):
                for f in fnames:
                    fp = os.path.join(root, f)
                    try:
                        size = os.path.getsize(fp)
                    except Exception:
                        size = None
                    if not query or query in f.lower():
                        all_files.append({'path': fp, 'name': f, 'size': size})
        
        total = len(all_files)
        end = min(total, offset + limit)
        page = all_files[offset:end]
        
        return {
            'files': page,
            'total': total,
            'offset': offset,
            'limit': limit,
            'q': query
        }
    
    def ingest_file(self, dataset_id: str, file, filename: str) -> Optional[str]:
        """
        ファイルをデータセットに取り込む
        
        Args:
            dataset_id: データセットID
            file: ファイルオブジェクト
            filename: ファイル名
            
        Returns:
            保存先パス、失敗時はNone
        """
        if dataset_id not in self.real_downloader.datasets:
            return None
        
        info = self.real_downloader.datasets[dataset_id]
        base = self.real_downloader.get_dataset_path(dataset_id)
        
        if base is None:
            # ディレクトリを作成
            base = self.real_downloader.data_dir / info.get('extract_to', dataset_id)
            os.makedirs(base, exist_ok=True)
        
        img_dir = os.path.join(str(base), info.get('images_dir', 'images'))
        os.makedirs(img_dir, exist_ok=True)
        
        from werkzeug.utils import secure_filename
        fname = secure_filename(filename)
        dest = os.path.join(img_dir, fname)
        file.save(dest)
        
        return dest

