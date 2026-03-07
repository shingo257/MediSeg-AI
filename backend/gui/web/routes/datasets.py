"""Dataset API routes."""
import os
import base64
import logging
import threading
import time
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import cv2
import numpy as np

from backend.gui.web.state import (
    real_downloader,
    downloader,
    DOWNLOAD_STATUS,
    set_download_status,
    has_any_images,
    EXTENSIONS,
)
from mediseg_ai.utils.exceptions import ValidationError, ModelLoadError, DatasetError

logger = logging.getLogger(__name__)
bp = Blueprint('datasets', __name__, url_prefix='/api/datasets')


@bp.route('/debug-keys')
def debug_dataset_keys():
    try:
        keys = list(getattr(real_downloader, 'datasets', {}).keys())
        return jsonify({'success': True, 'keys': keys})
    except Exception as e:
        logger.exception("Debug dataset keys failed")
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/list')
def list_datasets():
    try:
        datasets = []
        for dataset_id, info in real_downloader.datasets.items():
            base_path = real_downloader.get_dataset_path(dataset_id)
            is_downloaded = bool(base_path) and has_any_images(base_path)
            download_state = DOWNLOAD_STATUS.get(dataset_id)
            is_downloading = download_state and download_state.get('status') == 'downloading'
            if is_downloading:
                progress = download_state.get('progress', 0)
                status, status_text, status_icon = 'downloading', f'ダウンロード中 {progress}%', '⏳'
            elif is_downloaded:
                status, status_text, status_icon = 'downloaded', 'ダウンロード済み', '✅'
            else:
                status, status_text, status_icon = 'available', '利用可能', '⬇️'
            image_count = 'N/A'
            if base_path and os.path.exists(base_path):
                images_dir = os.path.join(str(base_path), info.get('images_dir', '')) if info.get('images_dir') else str(base_path)
                if os.path.exists(images_dir):
                    count = sum(1 for root, _, files in os.walk(images_dir)
                               for f in files if f.lower().endswith(EXTENSIONS))
                    if count > 0:
                        image_count = str(count)
            datasets.append({
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
            })
        return jsonify({'success': True, 'datasets': datasets})
    except (ValidationError, DatasetError, FileNotFoundError):
        raise
    except Exception as e:
        logger.exception("List datasets failed")
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/download', methods=['POST'])
def download_dataset_api():
    data = request.get_json(force=True)
    name = data.get('name')
    if not name:
        raise ValidationError('dataset name is required')
    try:
        set_download_status(name, 'downloading', 1, '開始')

        def _worker():
            try:
                progress_holder = {'value': 1, 'running': True}
                def _ticker():
                    while progress_holder['running'] and progress_holder['value'] < 95:
                        state = DOWNLOAD_STATUS.get(name)
                        if state and state.get('status') in ('completed', 'error'):
                            break
                        time.sleep(1.0)
                        progress_holder['value'] += 3
                        set_download_status(name, 'downloading', progress_holder['value'])
                ticker_thread = threading.Thread(target=_ticker, daemon=True)
                ticker_thread.start()
                route_real = name in getattr(real_downloader, 'datasets', {})
                route_synth = name in getattr(downloader, 'datasets', {})
                if not route_real and not route_synth:
                    set_download_status(name, 'error', progress_holder['value'], 'Unknown dataset')
                    return
                ok = real_downloader.download_dataset(name) if route_real else downloader.download_dataset(name)
                progress_holder['running'] = False
                set_download_status(name, 'completed' if ok else 'error', 100 if ok else progress_holder['value'], '完了' if ok else '失敗')
            except Exception as e:
                set_download_status(name, 'error', 0, str(e))

        threading.Thread(target=_worker, daemon=True).start()
        info = None
        base_path = None
        if name in getattr(real_downloader, 'datasets', {}):
            info = real_downloader.datasets.get(name, {})
            base_path = str((real_downloader.data_dir / info.get('extract_to', name)).resolve())
        elif name in getattr(downloader, 'datasets', {}):
            info = downloader.datasets.get(name, {})
            base_path = str((downloader.data_dir / info.get('extract_to', name)).resolve())
        return jsonify({'success': True, 'started': True, 'target': base_path, 'size': info.get('size') if info else None})
    except ValidationError:
        raise
    except (DatasetError, ModelLoadError):
        raise
    except Exception as e:
        logger.exception("Download dataset API failed")
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/status/<dataset_id>')
def get_dataset_status(dataset_id: str):
    try:
        state = DOWNLOAD_STATUS.get(dataset_id)
        if state and state.get('status') == 'downloading':
            return jsonify({'success': True, 'status': state})
        base_path = real_downloader.get_dataset_path(dataset_id)
        has_files = bool(base_path) and has_any_images(base_path)
        if has_files:
            state = {'status': 'completed', 'progress': 100, 'message': '完了'}
            DOWNLOAD_STATUS[dataset_id] = state
        else:
            state = {'status': 'idle', 'progress': 0, 'message': '未開始'}
            existing_state = DOWNLOAD_STATUS.get(dataset_id)
            if existing_state and existing_state.get('status') in ('completed', 'error'):
                state = existing_state
            else:
                DOWNLOAD_STATUS[dataset_id] = state
        return jsonify({'success': True, 'status': state})
    except Exception as e:
        logger.exception("Get dataset status failed")
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/sample', methods=['POST'])
def sample_dataset_api():
    data = request.get_json(force=True)
    name = data.get('name')
    source = data.get('source', 'synthetic')
    if not name:
        raise ValidationError('dataset name is required')
    try:
        if source == 'real':
            base = real_downloader.get_dataset_path(name)
            info = real_downloader.datasets[name]
        else:
            base = downloader.get_dataset_path(name)
            info = downloader.datasets[name]
        if base is None:
            return jsonify({'error': 'dataset not found locally. download first.'}), 400
        images_dir = os.path.join(str(base), info.get('images_dir', 'images'))
        candidates = []
        for ext in ['.jpg', '.jpeg', '.png', '.bmp']:
            candidates += [os.path.join(images_dir, f) for f in os.listdir(images_dir) if f.lower().endswith(ext)]
        if not candidates:
            return jsonify({'error': 'no images found in dataset'}), 400
        img_path = candidates[0]
        img = cv2.imread(img_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        h, w = img.shape[:2]
        scale = 512 / max(h, w)
        img_resized = cv2.resize(img, (int(w*scale), int(h*scale)))
        _, buf = cv2.imencode('.jpg', cv2.cvtColor(img_resized, cv2.COLOR_RGB2BGR))
        b64 = base64.b64encode(buf).decode()
        return jsonify({'success': True, 'image': b64, 'name': os.path.basename(img_path)})
    except ValidationError:
        raise
    except KeyError:
        raise ValidationError("Dataset not found")
    except Exception as e:
        logger.exception("Sample dataset API failed")
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/details/<dataset_id>')
def get_dataset_details(dataset_id):
    try:
        if dataset_id in getattr(real_downloader, 'datasets', {}):
            info = real_downloader.datasets[dataset_id]
            base = real_downloader.get_dataset_path(dataset_id)
            images_dir = os.path.join(str(base), info.get('images_dir', '')) if base else None
            masks_dir = os.path.join(str(base), info.get('masks_dir', '')) if base else None
            def _count_files(d):
                return sum(len(files) for _, _, files in os.walk(d)) if d and os.path.exists(d) else 0
            payload = {
                'name': info.get('name', dataset_id),
                'description': info.get('description', ''),
                'imageCount': _count_files(images_dir),
                'resolution': info.get('resolution', 'N/A'),
                'size': info.get('size', 'N/A'),
                'format': info.get('format', 'N/A'),
                'category': info.get('type', 'N/A'),
                'files': {'images': _count_files(images_dir), 'masks': _count_files(masks_dir)}
            }
            return jsonify({'success': True, 'data': payload})
        raise FileNotFoundError('Dataset not found')
    except (ValidationError, ModelLoadError, DatasetError, FileNotFoundError):
        raise
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def _to_thumbnail_b64(img_rgb: np.ndarray, max_side: int = 200) -> str:
    h, w = img_rgb.shape[:2]
    scale = max_side / max(h, w)
    new_w, new_h = max(1, int(w * scale)), max(1, int(h * scale))
    thumb = cv2.resize(img_rgb, (new_w, new_h))
    _, buf = cv2.imencode('.png', cv2.cvtColor(thumb, cv2.COLOR_RGB2BGR))
    return base64.b64encode(buf).decode()


def _load_image_any(path: str) -> np.ndarray | None:
    lower = path.lower()
    try:
        if lower.endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff')):
            img = cv2.imread(path)
            return cv2.cvtColor(img, cv2.COLOR_BGR2RGB) if img is not None else None
        if lower.endswith('.dcm'):
            try:
                import pydicom
            except Exception as e:
                logger.debug("DICOM load skipped (pydicom unavailable or error): %s", e)
                return None
            ds = pydicom.dcmread(path, force=True)
            arr = ds.pixel_array.astype(np.float32)
            arr -= arr.min()
            if arr.max() > 0:
                arr /= arr.max()
            arr = (arr * 255).astype(np.uint8)
            return np.stack([arr, arr, arr], axis=-1)
        if lower.endswith(('.nii', '.nii.gz')):
            try:
                import nibabel as nib
            except Exception as e:
                logger.debug("NIfTI load skipped (nibabel unavailable or error): %s", e)
                return None
            img = nib.load(path)
            data = np.asanyarray(img.dataobj)
            if data.ndim == 3:
                z = data.shape[2] // 2
                sl = data[:, :, z]
            elif data.ndim == 4:
                z = data.shape[2] // 2
                sl = data[:, :, z, 0]
            else:
                return None
            sl = sl.astype(np.float32)
            sl -= sl.min()
            if sl.max() > 0:
                sl /= sl.max()
            sl = (sl * 255).astype(np.uint8)
            return np.stack([sl, sl, sl], axis=-1)
    except Exception as e:
        logger.debug("_load_image_any failed for %s: %s", path, e)
    return None


@bp.route('/samples/<dataset_id>')
def get_dataset_samples(dataset_id):
    try:
        samples = []
        base_path = real_downloader.get_dataset_path(dataset_id) if dataset_id in real_downloader.datasets else None
        if base_path and os.path.exists(base_path):
            found_files = []
            for root, _, files in os.walk(base_path):
                for f in files:
                    if f.lower().endswith(EXTENSIONS):
                        found_files.append(os.path.join(root, f))
                if len(found_files) >= 24:
                    break
            for path in found_files[:6]:
                img_rgb = _load_image_any(path)
                if img_rgb is not None:
                    samples.append({'filename': os.path.basename(path), 'image': _to_thumbnail_b64(img_rgb)})
        if not samples:
            raise FileNotFoundError(
                'No images found for this dataset. Please verify dataset path and formats (jpg/png/bmp/tiff/dcm/nii). Upload files using the 📤 button or download the dataset first.'
            )
        return jsonify({'success': True, 'samples': samples})
    except FileNotFoundError:
        raise
    except Exception as e:
        logger.exception("Get dataset samples failed")
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/files/<dataset_id>')
def list_dataset_files(dataset_id: str):
    try:
        kind = request.args.get('kind', 'images')
        limit = int(request.args.get('limit', '50'))
        offset = int(request.args.get('offset', '0'))
        query = (request.args.get('q') or '').lower().strip()
        if dataset_id not in getattr(real_downloader, 'datasets', {}):
            raise FileNotFoundError('Unknown dataset')
        info = real_downloader.datasets[dataset_id]
        base = real_downloader.get_dataset_path(dataset_id)
        if not base:
            return jsonify({'success': True, 'files': [], 'total': 0, 'offset': offset, 'limit': limit})
        subdir = info.get('images_dir' if kind == 'images' else 'masks_dir', '')
        target = os.path.join(str(base), subdir) if subdir else str(base)
        all_files = []
        if os.path.exists(target):
            for root, _, fnames in os.walk(target):
                for f in fnames:
                    fp = os.path.join(root, f)
                    try:
                        size = os.path.getsize(fp)
                    except Exception as e:
                        logger.debug("getsize failed for %s: %s", fp, e)
                        size = None
                    if not query or query in f.lower():
                        all_files.append({'path': fp, 'name': f, 'size': size})
        total = len(all_files)
        page = all_files[offset:min(total, offset + limit)]
        return jsonify({'success': True, 'files': page, 'total': total, 'offset': offset, 'limit': limit, 'q': query})
    except FileNotFoundError:
        raise
    except Exception as e:
        logger.exception("List dataset files failed")
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/ingest/<dataset_id>', methods=['POST'])
def ingest_file(dataset_id: str):
    try:
        if dataset_id not in getattr(real_downloader, 'datasets', {}):
            return jsonify({'success': False, 'error': 'Unknown dataset'}), 404
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        info = real_downloader.datasets[dataset_id]
        base = real_downloader.get_dataset_path(dataset_id)
        if base is None:
            base = real_downloader.data_dir / info.get('extract_to', dataset_id)
            os.makedirs(base, exist_ok=True)
        img_dir = os.path.join(str(base), info.get('images_dir', 'images'))
        os.makedirs(img_dir, exist_ok=True)
        fname = secure_filename(file.filename)
        dest = os.path.join(img_dir, fname)
        file.save(dest)
        return jsonify({'success': True, 'saved_to': dest})
    except (ValidationError, FileNotFoundError):
        raise
    except Exception as e:
        logger.exception("Ingest file failed")
        return jsonify({'success': False, 'error': str(e)}), 500
