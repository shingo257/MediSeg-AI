/**
 * セグメンテーション処理API
 */
import { apiClient } from './client.js';
import { state } from '../core/state.js';
import { dom } from '../core/dom.js';
import { showMessage, showLoading } from '../ui/message.js';
import { updateWorkflowStep } from '../ui/workflow.js';
import { escapeHtml, setElementDisabled } from '../core/utils.js';
import { SEGMENTATION, MESSAGE_TYPES } from '../core/constants.js';

/**
 * 画像処理（セグメンテーション）
 */
export async function processImage() {
    const currentImage = state.get('currentImage');
    if (!currentImage) {
        showMessage('まず画像をアップロードしてください。', MESSAGE_TYPES.ERROR);
        return;
    }

    showLoading(true);
    const processBtn = dom.getElement('processBtn');
    if (processBtn) {
        setElementDisabled(processBtn, true);
    }

    // AbortController でキャンセル可能に
    const existingController = state.get('inferenceController');
    if (existingController && typeof existingController.abort === 'function') {
        try {
            existingController.abort();
        } catch (_) {}
    }
    
    const controller = new AbortController();
    state.set('inferenceController', controller);

    const modelSelect = dom.getElement('modelSelect');
    const thresholdSlider = dom.getElement('thresholdSlider');
    
    // 閾値のバリデーション
    const thresholdValue = parseFloat(thresholdSlider?.value || SEGMENTATION.DEFAULT_THRESHOLD);
    const validThreshold = isNaN(thresholdValue) 
        ? SEGMENTATION.DEFAULT_THRESHOLD 
        : Math.max(SEGMENTATION.MIN_THRESHOLD, Math.min(SEGMENTATION.MAX_THRESHOLD, thresholdValue));
    
    const data = {
        model: modelSelect?.value || SEGMENTATION.DEFAULT_MODEL,
        threshold: validThreshold
    };

    try {
        const result = await apiClient.post('/api/process', data, {
            signal: controller.signal
        });

        if (result.success) {
            state.set('currentResults', result);
            displayResults(result);
            
            const downloadBtn = dom.getElement('downloadBtn');
            if (downloadBtn) setElementDisabled(downloadBtn, false);
            
            showMessage('セグメンテーションが完了しました！', MESSAGE_TYPES.SUCCESS);
            updateWorkflowStep(3);
            updateAnalysisData(result);
        } else {
            showMessage(result.error || '処理に失敗しました。', MESSAGE_TYPES.ERROR);
        }
    } catch (error) {
        if (error && error.name === 'AbortError') {
            showMessage('処理を中止しました。', MESSAGE_TYPES.ERROR);
        } else {
            showMessage('処理中にエラーが発生しました。', MESSAGE_TYPES.ERROR);
        }
        console.error('Process error:', error);
    } finally {
        showLoading(false);
        if (processBtn) {
            setElementDisabled(processBtn, false);
        }
    }
}

/**
 * 結果を表示
 * @param {Object} data - 結果データ
 */
function displayResults(data) {
    // 可視化画像の表示
    const wrap = dom.getElement('panZoomWrap');
    if (wrap && data.visualization) {
        // 既存の画像を削除
        const existingImg = wrap.querySelector('#resultImg');
        if (existingImg) {
            existingImg.remove();
        }
        
        // 新しい画像を作成（innerHTMLではなくcreateElementを使用）
        const img = document.createElement('img');
        img.id = 'resultImg';
        img.src = `data:image/png;base64,${data.visualization}`;
        img.alt = 'Segmentation Results';
        wrap.appendChild(img);
        
        state.set('currentZoom', 1);
        state.set('offsetX', 0);
        state.set('offsetY', 0);
        // applyZoomはmain.jsでグローバルに公開されている
        if (window.applyZoom) {
            window.applyZoom();
        }
    }
    
    // メトリクスの表示
    const metricsDisplay = dom.getElement('metricsDisplay');
    if (metricsDisplay && data.metrics) {
        const metrics = data.metrics;
        
        // innerHTMLではなくcreateElementを使用（XSS対策）
        metricsDisplay.innerHTML = '';
        
        const metricsList = [
            { label: 'Dice Score', value: metrics.dice },
            { label: 'IoU', value: metrics.iou },
            { label: 'Accuracy', value: metrics.accuracy },
            { label: 'Sensitivity', value: metrics.sensitivity },
            { label: 'Specificity', value: metrics.specificity }
        ];
        
        metricsList.forEach(metric => {
            if (typeof metric.value === 'number' && !isNaN(metric.value)) {
                const card = document.createElement('div');
                card.className = 'metric-card';
                
                // XSS対策: innerHTMLの代わりにcreateElementとtextContentを使用
                const valueDiv = document.createElement('div');
                valueDiv.className = 'metric-value';
                valueDiv.textContent = metric.value.toFixed(3);
                
                const labelDiv = document.createElement('div');
                labelDiv.className = 'metric-label';
                labelDiv.textContent = escapeHtml(metric.label);
                
                card.appendChild(valueDiv);
                card.appendChild(labelDiv);
                metricsDisplay.appendChild(card);
            }
        });
    }
}

/**
 * 結果をダウンロード
 */
export async function downloadResults() {
    const currentResults = state.get('currentResults');
    if (!currentResults) {
        showMessage('ダウンロードする結果がありません。', MESSAGE_TYPES.ERROR);
        return;
    }

    try {
        const blob = await apiClient.downloadBlob('/api/download');
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'mediseg_results.png';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        showMessage('結果をダウンロードしました！', MESSAGE_TYPES.SUCCESS);
    } catch (error) {
        showMessage('ダウンロード中にエラーが発生しました。', MESSAGE_TYPES.ERROR);
        console.error('Download error:', error);
    }
}

/**
 * 分析データを更新
 * @param {Object} data - 分析データ
 */
function updateAnalysisData(data) {
    const metrics = data.metrics || {};
    const stats = data.stats || {};
    
    const diceValue = dom.getElement('diceValue');
    const iouValue = dom.getElement('iouValue');
    const hausdorffValue = dom.getElement('hausdorffValue');
    
    if (diceValue) diceValue.textContent = metrics.dice ? metrics.dice.toFixed(3) : '0.000';
    if (iouValue) iouValue.textContent = metrics.iou ? metrics.iou.toFixed(3) : '0.000';
    if (hausdorffValue) hausdorffValue.textContent = metrics.hausdorff ? metrics.hausdorff.toFixed(3) : '0.000';
    
    // 統計情報を更新（実データを使用）
    const lesionArea = stats.lesionArea || 0;
    const perimeter = stats.perimeter || 0;
    const circularity = stats.circularity || 0;
    
    const lesionAreaEl = dom.getElement('lesionArea');
    const perimeterEl = dom.getElement('perimeter');
    const circularityEl = dom.getElement('circularity');
    
    if (lesionAreaEl) lesionAreaEl.textContent = `${lesionArea} px²`;
    if (perimeterEl) perimeterEl.textContent = `${perimeter} px`;
    if (circularityEl) circularityEl.textContent = circularity.toFixed(3);
}


