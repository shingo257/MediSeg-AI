"""Segmentation and main page routes."""
import io
import os
import base64
import logging
import tempfile
from flask import Blueprint, request, jsonify, send_file, render_template
from werkzeug.utils import secure_filename
import cv2
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from backend.gui.web import state as app_state
from backend.gui.web.web_gui import STATIC_DIR
from backend.gui.web.services import process_image, create_visualization

logger = logging.getLogger(__name__)
bp = Blueprint('segmentation', __name__)


def _serve_react_index():
    """Serve React SPA index.html from static build output if present."""
    index_path = os.path.join(STATIC_DIR, 'index.html')
    if os.path.isfile(index_path):
        return send_file(index_path, mimetype='text/html')
    return render_template('index.html')


@bp.route('/')
def index():
    """Main page: serve React SPA if built, else legacy template."""
    return _serve_react_index()


@bp.route('/api/models')
def get_models():
    """List available models."""
    return jsonify(list(app_state.models.keys()))


@bp.route('/api/upload', methods=['POST'])
def upload_image():
    """Upload image."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join('uploads', filename)
        os.makedirs('uploads', exist_ok=True)
        file.save(filepath)
        image = cv2.imread(filepath)
        if image is not None:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            app_state.current_image = image.copy()
            _, buffer = cv2.imencode('.jpg', cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
            image_base64 = base64.b64encode(buffer).decode()
            return jsonify({
                'success': True,
                'filename': filename,
                'image': image_base64,
                'shape': image.shape
            })
        return jsonify({'error': 'Invalid image file'}), 400
    return jsonify({'error': 'Upload failed'}), 500


@bp.route('/api/process', methods=['POST'])
def process_image_api():
    """Run segmentation. Uses a unique temp file to avoid concurrent request overwrite."""
    data = request.get_json()
    model_type = data.get('model', 'U-Net')
    threshold = data.get('threshold', 0.5)
    if app_state.current_image is None:
        return jsonify({'error': 'No image loaded'}), 400
    fd, temp_path = tempfile.mkstemp(suffix='.jpg')
    try:
        os.close(fd)
        cv2.imwrite(temp_path, cv2.cvtColor(app_state.current_image, cv2.COLOR_RGB2BGR))
        results, error = process_image(temp_path, model_type, threshold)
        if error:
            return jsonify({'error': error}), 500
        visualization = create_visualization(
            app_state.current_image,
            results['prediction'],
            results['binary_mask'],
            results['metrics']
        )
        return jsonify({
            'success': True,
            'visualization': visualization,
            'metrics': results['metrics'],
            'model_type': model_type
        })
    finally:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass


@bp.route('/api/download', methods=['GET'])
def download_results():
    """Download results image (in-memory, no temp file left on disk)."""
    if app_state.current_results is None:
        return jsonify({'error': 'No results available'}), 400
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.patch.set_facecolor('#2b2b2b')
    axes[0].imshow(app_state.current_image)
    axes[0].set_title('Original', color='white')
    axes[0].axis('off')
    axes[1].imshow(app_state.current_results['prediction'], cmap='viridis')
    axes[1].set_title('Prediction', color='white')
    axes[1].axis('off')
    axes[2].imshow(app_state.current_results['binary_mask'], cmap='gray')
    axes[2].set_title('Binary Mask', color='white')
    axes[2].axis('off')
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight',
                facecolor='#2b2b2b', edgecolor='none')
    plt.close()
    buffer.seek(0)
    return send_file(
        buffer,
        mimetype='image/png',
        as_attachment=True,
        download_name='mediseg_results.png',
    )


@bp.route('/api/export/metrics', methods=['GET'])
def export_metrics_csv():
    """Export metrics as CSV (in-memory, no temp file left on disk)."""
    if app_state.current_results is None:
        return jsonify({'error': 'No results available'}), 400
    metrics = app_state.current_results.get('metrics', {})
    buffer = io.BytesIO()
    buffer.write(b'metric,value\n')
    for k, v in metrics.items():
        buffer.write(f'{k},{v}\n'.encode('utf-8'))
    buffer.seek(0)
    return send_file(
        buffer,
        mimetype='text/csv',
        as_attachment=True,
        download_name='mediseg_metrics.csv',
    )


@bp.route('/<path:path>')
def serve_spa(path):
    """Serve React SPA index.html for client-side routes (e.g. /dashboard, /segmentation)."""
    if path.startswith('api/'):
        return jsonify({'error': 'Not found'}), 404
    return _serve_react_index()
