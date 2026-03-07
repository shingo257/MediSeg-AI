"""
Shared application state for Web GUI.
Used by web_gui and route blueprints to avoid circular imports.
"""
import os
from pathlib import Path

from mediseg_ai.data_loaders.download_datasets import DatasetDownloader
from mediseg_ai.data_loaders.real_datasets import RealDatasetDownloader
import time

DATA_DIR = os.environ.get('DATA_DIR', 'data')
EXTENSIONS = ('.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff', '.dcm', '.nii', '.nii.gz')

models = {}
current_image = None
current_results = None
DOWNLOAD_STATUS = {}

downloader = DatasetDownloader(data_dir=DATA_DIR)
real_downloader = RealDatasetDownloader(data_dir=DATA_DIR)

BUILD_INFO = {
    'app': 'MediSeg.AI',
    'version': 'web_gui.samples-real-only',
    'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S'),
}


def set_download_status(dataset_id: str, status: str, progress: int = None, message: str = None):
    state = DOWNLOAD_STATUS.get(dataset_id, {'status': 'idle', 'progress': 0, 'message': ''})
    if state.get('status') in ('completed', 'error'):
        return state
    state['status'] = status
    if progress is not None:
        state['progress'] = max(0, min(100, int(progress)))
    if message is not None:
        state['message'] = message
    DOWNLOAD_STATUS[dataset_id] = state
    return state


def has_any_images(path: str) -> bool:
    if not path or not os.path.exists(path):
        return False
    for root, _, files in os.walk(path):
        for f in files:
            if f.lower().endswith(EXTENSIONS):
                return True
    return False
