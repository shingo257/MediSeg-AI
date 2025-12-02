/**
 * メインエントリーポイント
 * 全モジュールをインポートし、イベントリスナーを設定
 */
import { dom } from './core/dom.js';
import { state } from './core/state.js';
import { showMessage, showLoading } from './ui/message.js';
import { updateWorkflowStep } from './ui/workflow.js';
import { closePreview, closeDatasetModal, showImageModal } from './ui/modal.js';
import { showDummyDataWarning, hideDummyDataWarning, showFallbackMonitoring } from './ui/systemMonitoring.js';
import { handleDragOver, handleDragLeave, handleDrop, handleFileSelect, handleFile } from './upload/fileHandler.js';
import { processImage, downloadResults } from './api/segmentation.js';
import { loadDatasets, downloadDataset, showDatasetDetails, previewDataset, loadDataset, showDatasetFiles, setFileListQueryPrompt, ingestFile, loadSelectedDataset, downloadSelectedDataset, filterDatasets, pauseDownload } from './api/datasets.js';
import { initStatisticsCharts } from './charts/init.js';
import { init3DVisualization } from './visualization/3d.js';
import { startAnimation, pauseAnimation, resetAnimation } from './visualization/animation.js';
import { downloadFile } from './core/utils.js';
import { TIMING, PERFORMANCE, MESSAGE_TYPES, ANIMATION } from './core/constants.js';

// グローバルに公開（後方互換性のため、onclick属性などで使用）
// モジュール読み込み後、実際の関数で置き換える
// インラインスクリプトで定義されたラッパー関数を実際の関数で置き換える
window._previewDataset = previewDataset;
window._showDatasetDetails = showDatasetDetails;
window._loadDataset = loadDataset;
window._downloadDataset = downloadDataset;
window._showDatasetFiles = showDatasetFiles;
window._setFileListQueryPrompt = setFileListQueryPrompt;
window._ingestFile = ingestFile;
window._closePreview = closePreview;
window._closeDatasetModal = closeDatasetModal;
window._loadSelectedDataset = loadSelectedDataset;
window._downloadSelectedDataset = downloadSelectedDataset;
window._pauseDownload = pauseDownload;
window._showImageModal = showImageModal;
window._loadDatasets = loadDatasets;  // データセット一覧読み込み

// グローバル関数を実際の関数で置き換える
window.previewDataset = previewDataset;
window.showDatasetDetails = showDatasetDetails;
window.loadDataset = loadDataset;
window.downloadDataset = downloadDataset;
window.showDatasetFiles = showDatasetFiles;
window.setFileListQueryPrompt = setFileListQueryPrompt;
window.ingestFile = ingestFile;
window.closePreview = closePreview;
window.closeDatasetModal = closeDatasetModal;
window.loadSelectedDataset = loadSelectedDataset;
window.downloadSelectedDataset = downloadSelectedDataset;
window.pauseDownload = pauseDownload;
window.showImageModal = showImageModal;
window.loadDatasets = loadDatasets;  // データセット一覧読み込み

/**
 * 閾値スライダーを更新
 */
function updateThreshold() {
    const thresholdSlider = dom.getElement('thresholdSlider');
    const thresholdValue = dom.getElement('thresholdValue');
    if (thresholdSlider && thresholdValue) {
        thresholdValue.textContent = thresholdSlider.value;
    }
}

/**
 * ズームを適用
 */
function applyZoom() {
    const wrapEl = dom.getElement('panZoomWrap');
    if (!wrapEl) return;
    
    const currentZoomValue = state.get('currentZoom') || 1;
    const offsetXValue = state.get('offsetX') || 0;
    const offsetYValue = state.get('offsetY') || 0;
    
    wrapEl.style.transform = `translate(${offsetXValue}px, ${offsetYValue}px) scale(${currentZoomValue})`;
}

// グローバルに公開（後方互換性のため）
window.applyZoom = applyZoom;

/**
 * マルチビュー更新
 */
function updateMultiView() {
    const currentResults = state.get('currentResults');
    if (!currentResults) return;
    
    const currentImage = state.get('currentImage');
    
    // 元画像
            const originalView = dom.getElement('originalView');
            if (originalView && currentImage) {
                originalView.src = `data:image/jpeg;base64,${currentImage}`;
            }
            
            // マスク（簡易生成）
            const maskView = dom.getElement('maskView');
            if (maskView) {
                const maskCanvas = document.createElement('canvas');
                maskCanvas.width = 256;
                maskCanvas.height = 256;
                const ctx = maskCanvas.getContext('2d');
                ctx.fillStyle = '#00ff00';
                ctx.fillRect(50, 50, 100, 100);
                maskView.src = maskCanvas.toDataURL();
            }
            
            // オーバーレイ
            const overlayView = dom.getElement('overlayView');
            if (overlayView) {
                overlayView.src = `data:image/png;base64,${currentResults.visualization}`;
            }
            
            // 輪郭（簡易生成）
            const contourView = dom.getElement('contourView');
    if (contourView) {
        const contourCanvas = document.createElement('canvas');
        contourCanvas.width = 256;
        contourCanvas.height = 256;
        const contourCtx = contourCanvas.getContext('2d');
        contourCtx.strokeStyle = '#ff0000';
        contourCtx.lineWidth = 2;
        contourCtx.beginPath();
        contourCtx.arc(128, 128, 50, 0, 2 * Math.PI);
        contourCtx.stroke();
        contourView.src = contourCanvas.toDataURL();
    }
}

/**
 * システム監視を更新
 */
async function updateSystemMonitoring() {
    try {
        const data = await fetch('/api/system/monitoring').then(r => r.json());
        
        if (data && data.success) {
            // 実際のデータが取得できた場合
            hideDummyDataWarning();
            
            // CPU使用率
            const cpuUsage = dom.getElement('cpuUsage');
            const cpuBar = dom.getElement('cpuBar');
            if (cpuUsage && cpuBar && typeof data.cpu_usage === 'number') {
                cpuUsage.textContent = `${data.cpu_usage.toFixed(1)}%`;
                cpuBar.style.width = `${Math.min(Math.max(0, data.cpu_usage), 100)}%`;
                cpuBar.style.backgroundColor = '#4ecdc4';
                cpuBar.style.border = 'none';
            }
            
            // GPU使用率
            const gpuUsage = dom.getElement('gpuUsage');
            const gpuBar = dom.getElement('gpuBar');
            if (gpuUsage && gpuBar) {
                if (data.gpu_available && typeof data.gpu_usage === 'number') {
                    gpuUsage.textContent = `${data.gpu_usage.toFixed(1)}%`;
                    gpuUsage.title = '';
                    gpuBar.style.width = `${Math.min(Math.max(0, data.gpu_usage), 100)}%`;
                    gpuBar.style.backgroundColor = '#4ecdc4';
                    gpuBar.style.border = 'none';
                } else {
                    gpuUsage.textContent = '未接続';
                    gpuUsage.title = '';
                    gpuBar.style.width = '0%';
                    gpuBar.style.backgroundColor = '#ffa726';
                    gpuBar.style.border = 'none';
                }
            }
            
            // メモリ使用量
            const memoryUsage = dom.getElement('memoryUsage');
            const memoryBar = dom.getElement('memoryBar');
            if (memoryUsage && memoryBar && typeof data.memory_usage === 'number') {
                memoryUsage.textContent = `${data.memory_usage.toFixed(0)}MB`;
                memoryUsage.title = '';
                memoryBar.style.width = `${Math.min(Math.max(0, (data.memory_usage / PERFORMANCE.MAX_MEMORY) * 100), 100)}%`;
                memoryBar.style.backgroundColor = '#4ecdc4';
                memoryBar.style.border = 'none';
            }
            
            // 処理速度
            const processingSpeed = dom.getElement('processingSpeed');
            const speedBar = dom.getElement('speedBar');
            if (processingSpeed && speedBar && typeof data.processing_speed === 'number') {
                processingSpeed.textContent = `${data.processing_speed.toFixed(1)} FPS`;
                processingSpeed.title = '';
                speedBar.style.width = `${Math.min(Math.max(0, (data.processing_speed / PERFORMANCE.MAX_PROCESSING_SPEED) * 100), 100)}%`;
                speedBar.style.backgroundColor = '#4ecdc4';
                speedBar.style.border = 'none';
            }
        } else {
            console.error('システム監視データの取得に失敗:', data?.error || 'Unknown error');
            // エラー時は模擬データを表示
            showFallbackMonitoring();
        }
    } catch (error) {
        console.error('システム監視API呼び出しエラー:', error);
        // エラー時は模擬データを表示
        showFallbackMonitoring();
    }
}

/**
 * 初期化
 */
function init() {
    // アップロードエリアのイベントリスナー
    const uploadArea = dom.getElement('uploadArea');
    const fileInput = dom.getElement('fileInput');
    
    if (uploadArea) {
        uploadArea.addEventListener('click', () => {
            if (fileInput) fileInput.click();
        });
        
        uploadArea.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                if (fileInput) fileInput.click();
            }
        });
        
        uploadArea.addEventListener('dragover', handleDragOver);
        uploadArea.addEventListener('dragleave', handleDragLeave);
        uploadArea.addEventListener('drop', handleDrop);
    }
    
    if (fileInput) {
        fileInput.addEventListener('change', handleFileSelect);
    }
    
    // 処理ボタン
    const processBtn = dom.getElement('processBtn');
    if (processBtn) {
        processBtn.addEventListener('click', processImage);
    }
    
    // ダウンロードボタン
    const downloadBtn = dom.getElement('downloadBtn');
    if (downloadBtn) {
        downloadBtn.addEventListener('click', downloadResults);
    }
    
    // 閾値スライダー
    const thresholdSlider = dom.getElement('thresholdSlider');
    if (thresholdSlider) {
        thresholdSlider.addEventListener('input', updateThreshold);
    }
    
    // データセット一覧を初期読み込み
    loadDatasets().catch(err => {
        console.error('Failed to load datasets on init:', err);
        showMessage('データセット一覧の読み込みに失敗しました。', MESSAGE_TYPES.WARNING);
    });
    
    // データセット管理ボタン
    const dsRefreshBtn = dom.getElement('dsRefresh');
    const dsDownloadBtn = dom.getElement('dsDownload');
    const dsPreviewBtn = dom.getElement('dsPreview');
    
    if (dsRefreshBtn) dsRefreshBtn.addEventListener('click', loadDatasets);
    if (dsDownloadBtn) dsDownloadBtn.addEventListener('click', downloadDataset);
    if (dsPreviewBtn) {
        dsPreviewBtn.addEventListener('click', () => {
            const sel = dom.getElement('dsSelect');
            if (sel && sel.value) previewDataset(sel.value);
        });
    }
    
    // ズーム制御
    const zoomInBtn = dom.getElement('zoomIn');
    const zoomOutBtn = dom.getElement('zoomOut');
    const resetViewBtn = dom.getElement('resetView');
    
    if (zoomInBtn) {
        dom.on(zoomInBtn, 'click', () => {
            let currentZoom = state.get('currentZoom') || 1;
            currentZoom = Math.min(5, currentZoom + 0.1);
            state.set('currentZoom', currentZoom);
            applyZoom();
        });
    }
    
    if (zoomOutBtn) {
        dom.on(zoomOutBtn, 'click', () => {
            let currentZoom = state.get('currentZoom') || 1;
            currentZoom = Math.max(0.2, currentZoom - 0.1);
            state.set('currentZoom', currentZoom);
            applyZoom();
        });
    }
    
    if (resetViewBtn) {
        dom.on(resetViewBtn, 'click', () => {
            state.set('currentZoom', 1);
            state.set('offsetX', 0);
            state.set('offsetY', 0);
            applyZoom();
        });
    }
    
    // パン操作
    const imgContainer = dom.getElement('imageDisplay');
    if (imgContainer) {
        dom.on(imgContainer, 'mousedown', (e) => {
            const currentOffsetX = state.get('offsetX') || 0;
            const currentOffsetY = state.get('offsetY') || 0;
            const startX = e.clientX - currentOffsetX;
            const startY = e.clientY - currentOffsetY;
            state.set('isPanning', true);
            state.set('startX', startX);
            state.set('startY', startY);
        });
    }
    
    dom.on(window, 'mouseup', () => {
        state.set('isPanning', false);
    });
    
    dom.on(window, 'mousemove', (e) => {
        if (!state.get('isPanning')) return;
        const startX = state.get('startX') || 0;
        const startY = state.get('startY') || 0;
        state.set('offsetX', e.clientX - startX);
        state.set('offsetY', e.clientY - startY);
        applyZoom();
    });
    
    // オーバーレイ不透明度
    const overlayAlpha = dom.getElement('overlayAlpha');
    if (overlayAlpha) {
        overlayAlpha.addEventListener('input', () => {
            const img = dom.getElementById('resultImg');
            if (img) img.style.opacity = overlayAlpha.value;
        });
    }
    
    // マルチビュー切り替え
    const toggleMultiViewBtn = dom.getElement('toggleMultiView');
    if (toggleMultiViewBtn) {
        toggleMultiViewBtn.addEventListener('click', () => {
            const isMultiView = !state.get('isMultiView');
            state.set('isMultiView', isMultiView);
            
            const container = dom.getElement('multiViewContainer');
            const mainDisplay = dom.getElement('imageDisplay');
            
            if (isMultiView) {
                if (container) container.style.display = 'grid';
                if (mainDisplay) mainDisplay.style.display = 'none';
                updateMultiView();
            } else {
                if (container) container.style.display = 'none';
                if (mainDisplay) mainDisplay.style.display = 'block';
            }
        });
    }
    
    // 3D表示切り替え
    const toggle3DBtn = dom.getElement('toggle3D');
    if (toggle3DBtn) {
        toggle3DBtn.addEventListener('click', () => {
            const is3DView = !state.get('is3DView');
            state.set('is3DView', is3DView);
            
            const container = dom.getElement('viz3DContainer');
            const mainDisplay = dom.getElement('imageDisplay');
            
            if (is3DView) {
                if (container) container.style.display = 'block';
                if (mainDisplay) mainDisplay.style.display = 'none';
                init3DVisualization();
            } else {
                if (container) container.style.display = 'none';
                if (mainDisplay) mainDisplay.style.display = 'block';
            }
        });
    }
    
    // 統計表示切り替え
    const toggleStatsBtn = dom.getElement('toggleStats');
    if (toggleStatsBtn) {
        toggleStatsBtn.addEventListener('click', () => {
            const isStatsView = !state.get('isStatsView');
            state.set('isStatsView', isStatsView);
            
            const container = dom.getElement('statsContainer');
            
            if (isStatsView) {
                if (container) container.style.display = 'grid';
                initStatisticsCharts();
            } else {
                if (container) container.style.display = 'none';
            }
        });
    }
    
    // アニメーション制御
    const playBtn = dom.getElement('playAnimation');
    const pauseBtn = dom.getElement('pauseAnimation');
    const resetBtn = dom.getElement('resetAnimation');
    const animSpeed = dom.getElement('animationSpeed');
    
    if (playBtn) playBtn.addEventListener('click', startAnimation);
    if (pauseBtn) pauseBtn.addEventListener('click', pauseAnimation);
    if (resetBtn) resetBtn.addEventListener('click', resetAnimation);
    if (animSpeed) {
        animSpeed.addEventListener('input', (e) => {
            const speed = parseFloat(e.target.value);
            // バリデーション: 定数を使用
            const validSpeed = isNaN(speed) 
                ? ANIMATION.DEFAULT_SPEED 
                : Math.max(ANIMATION.MIN_SPEED, Math.min(ANIMATION.MAX_SPEED, speed));
            state.set('animationSpeed', validSpeed);
        });
    }
    
    // 分析タブ切り替え（イベント委譲を使用してパフォーマンス向上）
    const tabContainer = document.querySelector('.tabs');
    if (tabContainer) {
        // タブボタンとコンテンツを一度だけ取得してキャッシュ
        const tabButtons = Array.from(document.querySelectorAll('.tab-btn'));
        const tabContents = Array.from(document.querySelectorAll('.tab-content'));
        
        tabContainer.addEventListener('click', (e) => {
            const btn = e.target.closest('.tab-btn');
            if (!btn) return;
            
            const tabName = btn.dataset.tab;
            if (!tabName) return;
            
            // キャッシュされた要素を使用
            tabButtons.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));
            
            btn.classList.add('active');
            const tabContent = dom.getElement(`${tabName}-tab`);
            if (tabContent) tabContent.classList.add('active');
        });
    }
    
    // 設定値の更新
    const learningRateEl = dom.getElement('learningRate');
    if (learningRateEl) {
        learningRateEl.addEventListener('input', (e) => {
            const valueEl = dom.getElement('learningRateValue');
            if (valueEl) {
                valueEl.textContent = e.target.value;
            }
        });
    }
    
    // バッチ処理ボタン
    const batchProcessBtn = dom.getElement('batchProcessBtn');
    if (batchProcessBtn) {
        batchProcessBtn.addEventListener('click', () => {
            showMessage('バッチ処理機能は開発中です。', MESSAGE_TYPES.INFO);
        });
    }
    
    // 比較分析ボタン
    const compareBtn = dom.getElement('compareBtn');
    if (compareBtn) {
        compareBtn.addEventListener('click', () => {
            showMessage('比較分析機能は開発中です。', MESSAGE_TYPES.INFO);
        });
    }
    
    // フィルター機能
    const dsSource = dom.getElement('dsSource');
    const dsCategory = dom.getElement('dsCategory');
    const dsSize = dom.getElement('dsSize');
    
    if (dsSource) dsSource.addEventListener('change', filterDatasets);
    if (dsCategory) dsCategory.addEventListener('change', filterDatasets);
    if (dsSize) dsSize.addEventListener('change', filterDatasets);
    
    // システム監視の定期更新（クリーンアップ可能にする）
    const monitoringInterval = setInterval(updateSystemMonitoring, TIMING.MONITORING_INTERVAL);
    state.set('monitoringInterval', monitoringInterval);
    updateSystemMonitoring();
    
    // グローバルエラーハンドラー（未処理のPromise拒否をキャッチ）
    window.addEventListener('unhandledrejection', (event) => {
        console.error('Unhandled promise rejection:', event.reason);
        showMessage('予期しないエラーが発生しました。', MESSAGE_TYPES.ERROR);
        // デフォルトのエラー処理を防ぐ（オプション）
        // event.preventDefault();
    });
    
    // グローバルエラーハンドラー（通常のエラー）
    window.addEventListener('error', (event) => {
        console.error('Global error:', event.error);
        // ユーザーに表示する必要があるエラーのみ表示
        if (event.error && event.error.message) {
            // 既に表示されている可能性があるため、重複を避ける
        }
    });
    
    // ページアンロード時にクリーンアップ
    window.addEventListener('beforeunload', () => {
        // インターバルのクリーンアップ
        const monitoringInterval = state.get('monitoringInterval');
        if (monitoringInterval) {
            clearInterval(monitoringInterval);
        }
        
        // アニメーションフレームのクリーンアップ
        const animationId = state.get('animationId');
        if (animationId) {
            cancelAnimationFrame(animationId);
        }
        
        // 推論のキャンセル
        const controller = state.get('inferenceController');
        if (controller && typeof controller.abort === 'function') {
            try {
                controller.abort();
            } catch (_) {}
        }
    });
    
    // 初期値設定
    updateThreshold();
    // loadDatasets()は既に240行目で呼ばれているため、ここでは呼ばない
    
    // 推論キャンセルボタンを追加（重複チェック）
    const processBtnEl = dom.getElement('processBtn');
    if (processBtnEl && !dom.getElement('cancelProcessBtn')) {
        const cancelBtn = document.createElement('button');
        cancelBtn.id = 'cancelProcessBtn';
        cancelBtn.className = 'btn';
        cancelBtn.textContent = '⛔ 中止';
        cancelBtn.style.marginLeft = '10px';
        cancelBtn.addEventListener('click', () => {
            const controller = state.get('inferenceController');
            if (controller) {
                try {
                    controller.abort();
                } catch (_) {}
            }
            showLoading(false);
        });
        processBtnEl.insertAdjacentElement('afterend', cancelBtn);
    }
}

// DOMContentLoadedで初期化
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}

