/**
 * ファイルアップロード処理
 */
import { apiClient } from '../api/client.js';
import { state } from '../core/state.js';
import { dom } from '../core/dom.js';
import { showMessage, showLoading } from '../ui/message.js';
import { updateWorkflowStep } from '../ui/workflow.js';
import { setElementDisabled, formatFileSize } from '../core/utils.js';
import { MESSAGE_TYPES, FILE } from '../core/constants.js';

/**
 * ドラッグオーバー処理
 * @param {Event} e - イベント
 */
export function handleDragOver(e) {
    e.preventDefault();
    const uploadArea = dom.getElement('uploadArea');
    if (uploadArea) {
        uploadArea.classList.add('dragover');
    }
}

/**
 * ドラッグリーブ処理
 * @param {Event} e - イベント
 */
export function handleDragLeave(e) {
    e.preventDefault();
    const uploadArea = dom.getElement('uploadArea');
    if (uploadArea) {
        uploadArea.classList.remove('dragover');
    }
}

/**
 * ドロップ処理
 * @param {Event} e - イベント
 */
export function handleDrop(e) {
    e.preventDefault();
    const uploadArea = dom.getElement('uploadArea');
    if (uploadArea) {
        uploadArea.classList.remove('dragover');
    }
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
}

/**
 * ファイル選択処理
 * @param {Event} e - イベント
 */
export function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        handleFile(file);
    }
}

/**
 * ファイル処理
 * @param {File} file - アップロードするファイル
 */
export async function handleFile(file) {
    // ファイルの存在チェック
    if (!file) {
        showMessage('ファイルが選択されていません。', MESSAGE_TYPES.ERROR);
        return;
    }
    
    // ファイルタイプのバリデーション
    if (!file.type || !FILE.VALID_IMAGE_TYPES.includes(file.type.toLowerCase())) {
        showMessage('画像ファイルを選択してください。対応形式: JPEG, PNG, GIF, BMP, WebP', MESSAGE_TYPES.ERROR);
        return;
    }
    
    // ファイルサイズのバリデーション
    if (file.size > FILE.MAX_SIZE) {
        showMessage(`ファイルサイズが大きすぎます。最大サイズ: ${formatFileSize(FILE.MAX_SIZE)}（現在: ${formatFileSize(file.size)}）`, MESSAGE_TYPES.ERROR);
        return;
    }

    try {
        const data = await apiClient.uploadFile('/api/upload', file);

        if (data.success) {
            state.set('currentImage', data.image);
            
            const imageDisplay = dom.getElement('imageDisplay');
            if (imageDisplay) {
                // 既存の画像を削除
                imageDisplay.innerHTML = '';
                // 新しい画像を作成
                const img = document.createElement('img');
                img.src = `data:image/jpeg;base64,${data.image}`;
                img.alt = 'Uploaded Image';
                imageDisplay.appendChild(img);
            }

            const processBtn = dom.getElement('processBtn');
            const batchProcessBtn = dom.getElement('batchProcessBtn');
            const compareBtn = dom.getElement('compareBtn');
            
            if (processBtn) setElementDisabled(processBtn, false);
            if (batchProcessBtn) setElementDisabled(batchProcessBtn, false);
            if (compareBtn) setElementDisabled(compareBtn, false);

            showMessage('画像がアップロードされました！', MESSAGE_TYPES.SUCCESS);
            updateWorkflowStep(2);
        } else {
            showMessage(data.error || 'アップロードに失敗しました。', MESSAGE_TYPES.ERROR);
        }
    } catch (error) {
        showMessage('アップロード中にエラーが発生しました。', MESSAGE_TYPES.ERROR);
        console.error('Upload error:', error);
    }
}




