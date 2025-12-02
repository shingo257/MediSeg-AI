/**
 * データセット管理機能
 */
import { apiClient } from './client.js';
import { state } from '../core/state.js';
import { dom } from '../core/dom.js';
import { showMessage, showLoading } from '../ui/message.js';
import { updateWorkflowStep } from '../ui/workflow.js';
import { showImageModal, closeDatasetModal } from '../ui/modal.js';
import { escapeHtml, setElementsDisabled, setElementDisabled } from '../core/utils.js';
import { TIMING, UI, MESSAGE_TYPES } from '../core/constants.js';

/**
 * データセット一覧を読み込み
 */
export async function loadDatasets() {
    try {
        showLoading(true);
        const data = await apiClient.get('/api/datasets/list');
        
        if (data && data.success && Array.isArray(data.datasets)) {
            updateDatasetList(data.datasets);
            if (data.datasets.length > 0) {
                showMessage('データセット一覧を更新しました。', MESSAGE_TYPES.INFO);
            } else {
                showMessage('データセットが見つかりませんでした。', MESSAGE_TYPES.INFO);
            }
        } else {
            const errorMsg = data?.error || 'データセット一覧の取得に失敗しました。';
            console.error('Load datasets failed:', errorMsg, data);
            showMessage(errorMsg, MESSAGE_TYPES.ERROR);
        }
    } catch (e) {
        console.error('Load datasets error:', e);
        showMessage('データセット一覧の取得に失敗しました: ' + (e.message || String(e)), MESSAGE_TYPES.ERROR);
    } finally {
        showLoading(false);
    }
}

/**
 * データセット一覧を更新
 * @param {Array} datasets - データセット配列
 */
export function updateDatasetList(datasets) {
    const datasetList = dom.getElement('datasetList');
    if (!datasetList) return;
    
    datasetList.innerHTML = '';
    
    datasets.forEach(dataset => {
        if (!dataset || !dataset.id) {
            console.warn('Invalid dataset entry:', dataset);
            return;
        }
        
        const item = document.createElement('div');
        item.className = 'dataset-item';
        
        // 安全にプロパティを取得（未定義の場合はデフォルト値を使用）
        const icon = dataset.icon || '🏥';
        const name = escapeHtml(dataset.name || dataset.id || 'Unknown Dataset');
        const description = escapeHtml(dataset.description || '');
        const imageCount = escapeHtml(String(dataset.imageCount || 'N/A'));
        const resolution = escapeHtml(String(dataset.resolution || 'N/A'));
        const size = escapeHtml(String(dataset.size || 'N/A'));
        const format = escapeHtml(String(dataset.format || 'N/A'));
        const status = escapeHtml(String(dataset.status || 'available'));
        const statusIcon = dataset.statusIcon || '⬇️';
        const statusText = escapeHtml(String(dataset.statusText || '利用可能'));
        
        // dataset.idをエスケープ（XSS対策）
        const safeId = escapeHtml(String(dataset.id));
        
        // innerHTMLの代わりにcreateElementを使用（XSS対策）
        item.className = 'dataset-item';
        
        // アイコン
        const iconDiv = document.createElement('div');
        iconDiv.className = 'dataset-icon';
        iconDiv.textContent = icon;
        item.appendChild(iconDiv);
        
        // 情報エリア
        const infoDiv = document.createElement('div');
        infoDiv.className = 'dataset-info';
        
        const nameH4 = document.createElement('h4');
        nameH4.textContent = name;
        infoDiv.appendChild(nameH4);
        
        const descP = document.createElement('p');
        descP.textContent = description;
        infoDiv.appendChild(descP);
        
        // メタ情報
        const metaDiv = document.createElement('div');
        metaDiv.className = 'dataset-meta';
        
        const metaItems = [
            { icon: '📊', text: imageCount },
            { icon: '📐', text: resolution },
            { icon: '💾', text: size },
            { icon: '📁', text: format }
        ];
        
        metaItems.forEach(meta => {
            const span = document.createElement('span');
            span.className = 'meta-item';
            span.textContent = `${meta.icon} ${meta.text}`;
            metaDiv.appendChild(span);
        });
        
        infoDiv.appendChild(metaDiv);
        
        // ステータス
        const statusDiv = document.createElement('div');
        statusDiv.className = 'dataset-status';
        statusDiv.setAttribute('aria-live', 'polite');
        
        const statusSpan = document.createElement('span');
        statusSpan.id = `dsStatus-${safeId}`;
        statusSpan.className = `status-badge ${status}`;
        statusSpan.textContent = `${statusIcon} ${statusText}`;
        statusDiv.appendChild(statusSpan);
        
        const progressDiv = document.createElement('div');
        progressDiv.id = `dsProgress-${safeId}`;
        progressDiv.className = 'progress';
        progressDiv.style.cssText = 'height:6px;background:#333;border-radius:4px;margin-top:6px;display:none;';
        const barDiv = document.createElement('div');
        barDiv.className = 'bar';
        barDiv.style.cssText = 'height:100%;width:0%;background:#4ecdc4;border-radius:4px;';
        progressDiv.appendChild(barDiv);
        statusDiv.appendChild(progressDiv);
        
        infoDiv.appendChild(statusDiv);
        item.appendChild(infoDiv);
        
        // アクションエリア
        const actionsDiv = document.createElement('div');
        actionsDiv.className = 'dataset-actions';
        
        const buttons = [
            { id: `btnPrev-${safeId}`, onclick: () => window.previewDataset(safeId), title: 'プレビュー', icon: '👀' },
            { id: `btnInfo-${safeId}`, onclick: () => window.showDatasetDetails(safeId), title: '詳細', icon: 'ℹ️' },
            { id: `btnLoad-${safeId}`, onclick: () => window.loadDataset(safeId), title: '読み込み', icon: '📂' },
            { id: `btnDl-${safeId}`, onclick: () => window.downloadDataset(safeId), title: 'ダウンロード', icon: '⬇️' },
            { id: `btnRetry-${safeId}`, onclick: () => window.downloadDataset(safeId), title: '再試行', icon: '🔁' },
            { id: `btnFiles-${safeId}`, onclick: () => window.showDatasetFiles(safeId), title: 'ファイル一覧', icon: '📄' },
            { id: `btnSearch-${safeId}`, onclick: () => window.setFileListQueryPrompt(safeId), title: '検索語設定', icon: '🔎' }
        ];
        
        buttons.forEach(btn => {
            const button = document.createElement('button');
            button.id = btn.id;
            button.className = 'btn-icon';
            button.title = btn.title;
            button.textContent = btn.icon;
            button.addEventListener('click', btn.onclick);
            actionsDiv.appendChild(button);
        });
        
        // ファイルアップロード
        const uploadLabel = document.createElement('label');
        uploadLabel.className = 'btn-icon';
        uploadLabel.title = 'アップロード';
        uploadLabel.textContent = '📤';
        const fileInput = document.createElement('input');
        fileInput.id = `fileIn-${safeId}`;
        fileInput.type = 'file';
        fileInput.style.display = 'none';
        fileInput.addEventListener('change', (e) => {
            window.ingestFile(safeId, e.target.files);
        });
        uploadLabel.appendChild(fileInput);
        actionsDiv.appendChild(uploadLabel);
        
        item.appendChild(actionsDiv);
        datasetList.appendChild(item);
    });
}

/**
 * データセットをダウンロード
 * @param {string} datasetId - データセットID
 */
export async function downloadDataset(datasetId) {
    const dsSelect = dom.getElement('dsSelect');
    const name = datasetId || (dsSelect?.value || null);
    if (!name) {
        showMessage('データセットが選択されていません。', MESSAGE_TYPES.WARNING);
        return;
    }
    
    // 行ボタンを無効化
    const ids = [`btnPrev-${name}`, `btnInfo-${name}`, `btnLoad-${name}`, `btnDl-${name}`, `btnRetry-${name}`];
    const toEnable = [];
        ids.forEach(id => {
            const el = dom.getElement(id);
            if (el) {
                setElementsDisabled([el], true);
                toEnable.push(el);
            }
        });
    
    showLoading(true);
    showMessage(`${name} のダウンロードを開始しました。`, MESSAGE_TYPES.INFO);

    try {
        const data = await apiClient.post('/api/datasets/download', { name });

        if (!data.success) {
            showMessage(data.error || 'ダウンロード開始に失敗しました。', MESSAGE_TYPES.ERROR);
            showLoading(false);
            setElementsDisabled(toEnable, false);
            return;
        }

        const badge = dom.getElement(`dsStatus-${name}`);
        const prog = dom.getElement(`dsProgress-${name}`);
        const bar = prog ? prog.querySelector('.bar') : null;
        let done = false;
        let lastUpdateTs = 0;
        let interval = TIMING.POLL_INTERVAL;
        let pollTimeout = null;
        const maxPollTime = TIMING.POLL_TIMEOUT;
        const startTime = Date.now();
        
        // クリーンアップ関数（確実にタイマーをクリア）
        const cleanup = () => {
            if (pollTimeout) {
                clearTimeout(pollTimeout);
                pollTimeout = null;
            }
        };
        
        // 共通のクリーンアップ処理
        const finishPolling = (errorType = '') => {
            done = true;
            cleanup();
            showLoading(false);
            setElementsDisabled(toEnable, false);
            if (prog) prog.style.display = 'none';
            if (badge) {
                if (errorType === 'timeout') {
                    badge.className = 'status-badge error';
                    badge.textContent = '⚠️ タイムアウト';
                } else if (errorType === 'error') {
                    badge.className = 'status-badge error';
                    badge.textContent = '⚠️ エラー';
                }
            }
        };
        
        const poll = async () => {
            // タイムアウトチェック
            if (Date.now() - startTime > maxPollTime) {
                showMessage(`${name} のダウンロードがタイムアウトしました。`, MESSAGE_TYPES.ERROR);
                finishPolling('timeout');
                return;
            }
            
            try {
                const sdata = await apiClient.get(`/api/datasets/status/${name}`);
                if (sdata && sdata.success) {
                    const st = sdata.status || {};
                    const pct = st.progress ?? 0;
                    const msg = st.message ?? '';
                    const now = Date.now();
                    
                    if (badge && now - lastUpdateTs > TIMING.STATUS_UPDATE_THROTTLE) {
                        lastUpdateTs = now;
                        badge.className = 'status-badge downloading';
                        badge.textContent = `⏳ ダウンロード中 ${pct}%`;
                    }
                    if (prog) prog.style.display = 'block';
                    if (bar) bar.style.width = `${Math.max(0, Math.min(100, pct))}%`;
                    showMessage(`${name} ダウンロード中... ${pct}% ${msg}`, MESSAGE_TYPES.INFO);

                    if (st.status === 'completed') {
                        done = true;
                        cleanup();
                        if (badge) {
                            badge.className = 'status-badge downloaded';
                            badge.textContent = '✅ ダウンロード済み';
                        }
                        showMessage(`${name} のダウンロードが完了しました。`, MESSAGE_TYPES.SUCCESS);
                        showLoading(false);
                        setElementsDisabled(toEnable, false);
                        if (prog) prog.style.display = 'none';
                        loadDatasets();
                        return;
                    }
                    if (st.status === 'error') {
                        done = true;
                        cleanup();
                        if (badge) {
                            badge.className = 'status-badge error';
                            badge.textContent = '⚠️ 失敗';
                        }
                        showMessage(`エラー: ${msg || '不明なエラー'}`, MESSAGE_TYPES.ERROR);
                        showLoading(false);
                        setElementsDisabled(toEnable, false);
                        if (prog) prog.style.display = 'none';
                        return;
                    }
                    interval = Math.min(TIMING.POLL_INTERVAL_MAX, pct ? TIMING.POLL_INTERVAL : interval + TIMING.POLL_INTERVAL_INCREMENT);
                }
            } catch (e) {
                console.error('status poll error', e);
                // エラーが続く場合はポーリングを停止
                if (Date.now() - startTime > TIMING.POLL_ERROR_TIMEOUT) {
                    showMessage(`${name} のダウンロード状態の取得に失敗しました。`, MESSAGE_TYPES.ERROR);
                    finishPolling('error');
                    return;
                }
            }
            if (!done) {
                pollTimeout = setTimeout(poll, interval);
            }
        };
        
        // エラー時に確実にクリーンアップ
        try {
            poll();
        } catch (error) {
            console.error('Poll initialization error:', error);
            cleanup();
            finishPolling('error');
        }

    } catch (error) {
        console.error('Download error:', error);
        showMessage('データセットのダウンロードに失敗しました。', MESSAGE_TYPES.ERROR);
        showLoading(false);
        const ids = [`btnPrev-${name}`, `btnInfo-${name}`, `btnLoad-${name}`, `btnDl-${name}`, `btnRetry-${name}`];
        ids.forEach(id => {
            const el = dom.getElement(id);
            if (el) {
                el.removeAttribute('aria-disabled');
                el.disabled = false;
            }
        });
    }
}

/**
 * データセットの詳細を表示
 * @param {string} datasetId - データセットID
 */
export async function showDatasetDetails(datasetId) {
    const modal = dom.getElement('datasetModal');
    if (!modal) {
        showMessage('モーダルが見つかりません。', MESSAGE_TYPES.ERROR);
        return;
    }
    
    // APIからデータセット情報を取得
    try {
        const data = await apiClient.get(`/api/datasets/details/${datasetId}`);
        
        if (!data.success || !data.data) {
            showMessage('データセット情報の取得に失敗しました。', MESSAGE_TYPES.ERROR);
            return;
        }
        
        const dataset = data.data;
        
        state.set('currentDataset', datasetId);
        
        // 基本情報を更新
        const detailName = dom.getElement('detailName');
        const detailDescription = dom.getElement('detailDescription');
        const detailImageCount = dom.getElement('detailImageCount');
        const detailResolution = dom.getElement('detailResolution');
        const detailSize = dom.getElement('detailSize');
        const detailFormat = dom.getElement('detailFormat');
        
        if (detailName) detailName.textContent = dataset.name || datasetId;
        if (detailDescription) detailDescription.textContent = dataset.description || '';
        if (detailImageCount) detailImageCount.textContent = dataset.imageCount || dataset.image_count || 'N/A';
        if (detailResolution) detailResolution.textContent = dataset.resolution || 'N/A';
        if (detailSize) detailSize.textContent = dataset.size || 'N/A';
        if (detailFormat) detailFormat.textContent = dataset.format || 'N/A';
        
        // 統計情報を更新（実データがある場合のみ）
        const statMean = dom.getElement('statMean');
        const statStd = dom.getElement('statStd');
        const statMin = dom.getElement('statMin');
        const statMax = dom.getElement('statMax');
        
        if (dataset.stats) {
            if (statMean) statMean.textContent = (dataset.stats.mean || 0).toFixed(2);
            if (statStd) statStd.textContent = (dataset.stats.std || 0).toFixed(2);
            if (statMin) statMin.textContent = (dataset.stats.min || 0).toFixed(2);
            if (statMax) statMax.textContent = (dataset.stats.max || 0).toFixed(2);
        }
        
        // 使用方法を更新
        const usageInfo = dom.getElement('usageInfo');
        if (usageInfo) usageInfo.textContent = dataset.usage || dataset.description || '';
        
        // サンプル画像を取得（APIから）
        try {
            const samplesData = await apiClient.get(`/api/datasets/samples/${datasetId}`);
            if (samplesData.success && samplesData.samples && samplesData.samples.length > 0) {
                generateSampleImagesFromData(samplesData.samples);
            } else {
                generateSampleImagesPlaceholder(datasetId);
            }
        } catch (e) {
            console.error('Failed to load samples:', e);
            generateSampleImagesPlaceholder(datasetId);
        }
        
        modal.style.display = 'flex';
    } catch (error) {
        console.error('Show dataset details error:', error);
            showMessage('データセット情報の取得に失敗しました。', MESSAGE_TYPES.ERROR);
    }
}

/**
 * サンプル画像を実データから生成
 * @param {Array} samples - サンプル画像データ
 */
function generateSampleImagesFromData(samples) {
    const gallery = dom.getElement('sampleGallery');
    if (!gallery) return;
    
    gallery.innerHTML = '';
    
    samples.slice(0, UI.MAX_SAMPLE_IMAGES).forEach((sample, i) => {
        const img = document.createElement('img');
        img.src = `data:image/png;base64,${sample.image}`;
        img.alt = sample.filename || `Sample ${i + 1}`;
        img.title = sample.filename || `Sample ${i + 1}`;
        img.style.cursor = 'pointer';
        img.onclick = () => showImageModal(img.src, sample.filename || `Sample ${i + 1}`);
        gallery.appendChild(img);
    });
}

/**
 * サンプル画像のプレースホルダーを生成（実データがない場合）
 * @param {string} datasetId - データセットID
 */
function generateSampleImagesPlaceholder(datasetId) {
    const gallery = dom.getElement('sampleGallery');
    if (!gallery) return;
    
    gallery.innerHTML = `
        <div style="text-align: center; padding: 20px; color: var(--muted);">
            <p style="margin-bottom: 10px;">⚠️ サンプル画像がありません</p>
            <p style="font-size: 0.9em; color: #ff6b6b;">（実データが取得できませんでした）</p>
            <p style="font-size: 0.85em; margin-top: 10px; color: var(--muted);">
                データセットをダウンロードするか、ファイルをアップロードしてください。
            </p>
        </div>
    `;
}

/**
 * データセットをプレビュー
 * @param {string} datasetId - データセットID
 */
export async function previewDataset(datasetId) {
    const previewArea = dom.getElement('dsPreviewArea');
    const previewContent = dom.getElement('previewContent');
    
    if (!previewArea || !previewContent) {
        showMessage('プレビューエリアが見つかりません。', MESSAGE_TYPES.ERROR);
        return;
    }
    
    showLoading(true);
    previewContent.innerHTML = '';
    
    try {
        const data = await apiClient.get(`/api/datasets/samples/${datasetId}`);
        
        if (data.success && data.samples) {
            data.samples.forEach((sample) => {
                const img = document.createElement('img');
                img.src = `data:image/png;base64,${sample.image}`;
                img.alt = sample.filename;
                img.title = sample.filename;
                img.style.cursor = 'pointer';
                img.onclick = () => showImageModal(img.src, sample.filename);
                previewContent.appendChild(img);
            });
        } else {
            const help = '画像が見つかりませんでした。次のいずれかを実行してください: 1) データセットをダウンロード（⬇️ボタン）、2) ファイルをアップロード（📤ボタン）、3) 手動でファイルを配置。';
            showMessage('⚠️ ' + (data.error || 'サンプル画像が見つかりません。') + ' （実データが利用できません） ' + help, MESSAGE_TYPES.WARNING);
        }
        
        previewArea.style.display = 'block';
        showMessage(`${datasetId} データセットのプレビューを表示しました。`, MESSAGE_TYPES.SUCCESS);
        
    } catch (error) {
        console.error('Preview error:', error);
        showMessage('プレビューの取得に失敗しました。', MESSAGE_TYPES.ERROR);
    } finally {
        showLoading(false);
    }
}

/**
 * データセットを読み込み
 * @param {string} datasetId - データセットID
 */
export async function loadDataset(datasetId) {
    showLoading(true);
    showMessage(`${datasetId} データセットを読み込み中...`, MESSAGE_TYPES.INFO);
    
    try {
        const data = await apiClient.get(`/api/datasets/details/${datasetId}`);
        
        if (data.success) {
            showMessage(`${data.data.name} データセットが正常に読み込まれました。`, MESSAGE_TYPES.SUCCESS);
            updateWorkflowStep(2);
            updateDatasetInfo(data.data);
        } else {
            showMessage(data.error || 'データセットの読み込みに失敗しました。', MESSAGE_TYPES.ERROR);
        }
    } catch (error) {
        console.error('Load dataset error:', error);
        showMessage('データセットの読み込みに失敗しました。', MESSAGE_TYPES.ERROR);
    } finally {
        showLoading(false);
    }
}

/**
 * データセット情報を更新
 * @param {Object} datasetInfo - データセット情報
 */
export function updateDatasetInfo(datasetInfo) {
    const diceValue = dom.getElement('diceValue');
    const iouValue = dom.getElement('iouValue');
    const lesionArea = dom.getElement('lesionArea');
    
    if (diceValue) diceValue.textContent = datasetInfo.stats?.mean?.toFixed(3) || '0.000';
    if (iouValue) iouValue.textContent = datasetInfo.stats?.std?.toFixed(3) || '0.000';
    if (lesionArea) lesionArea.textContent = `${datasetInfo.imageCount || 'N/A'} 画像`;
}

/**
 * 選択されたデータセットを読み込み
 */
export function loadSelectedDataset() {
    const currentDataset = state.get('currentDataset');
    if (currentDataset) {
        loadDataset(currentDataset);
        closeDatasetModal();
    } else {
        showMessage('データセットが選択されていません。', MESSAGE_TYPES.WARNING);
    }
}

/**
 * 選択されたデータセットをダウンロード
 */
export function downloadSelectedDataset() {
    const currentDataset = state.get('currentDataset');
    if (currentDataset) {
        downloadDataset(currentDataset);
        closeDatasetModal();
    } else {
        showMessage('データセットが選択されていません。', MESSAGE_TYPES.WARNING);
    }
}

/**
 * データセットをフィルター
 */
export function filterDatasets() {
    const sourceEl = dom.getElement('dsSource');
    const categoryEl = dom.getElement('dsCategory');
    const sizeEl = dom.getElement('dsSize');
    
    if (!sourceEl || !categoryEl || !sizeEl) return;
    
    const source = sourceEl.value;
    const category = categoryEl.value;
    const size = sizeEl.value;
    
    // 実際の実装では、フィルター条件に基づいてデータセット一覧を更新
    showMessage(`フィルター: ${source}, ${category}, ${size}`, MESSAGE_TYPES.INFO);
}

/**
 * ダウンロードを一時停止
 * @param {string} datasetId - データセットID
 */
export function pauseDownload(datasetId) {
    showMessage(`${datasetId} のダウンロードを一時停止しました。`, MESSAGE_TYPES.INFO);
}

/**
 * ファイル一覧を表示
 * @param {string} datasetId - データセットID
 * @param {number} offset - オフセット
 */
export async function showDatasetFiles(datasetId, offset = 0) {
    try {
        if (window.__fileListCurrentId !== datasetId) {
            window.__fileListCurrentId = datasetId;
            window.__fileListOffset = 0;
        }
        const q = (window.__fileListQuery || '').trim();
        const data = await apiClient.get(`/api/datasets/files/${datasetId}`, {
            kind: 'images',
            limit: 20,
            offset: offset,
            q: q
        });
        
        if (!data.success) {
            showMessage('ファイル一覧の取得に失敗しました。', MESSAGE_TYPES.ERROR);
            return;
        }
        
        const files = data.files || [];
        if (files.length === 0) {
            showMessage('ファイルは見つかりませんでした。', MESSAGE_TYPES.WARNING);
            return;
        }
        
        const msg = files.map(f => `- ${f.name} (${f.size ?? 'N/A'} bytes)`).join('\n');
        const footer = (data.total > data.offset + data.limit) ? `\n...さらに表示するにはもう一度📄を押してください（次の20件）。` : '';
        const qline = q ? `検索: ${q}\n` : '';
        showMessage(`${qline}(${data.offset+1}-${data.offset+files.length}/${data.total})\n${msg}${footer}`, MESSAGE_TYPES.INFO);
        window.__fileListOffset = (data.offset + data.limit);
    } catch (e) {
        console.error('list files error', e);
        showMessage('ファイル一覧の取得に失敗しました。', MESSAGE_TYPES.ERROR);
    }
}

/**
 * ファイル検索クエリを設定
 * @param {string} q - 検索クエリ
 */
export function setFileListQuery(q) {
    window.__fileListQuery = q || '';
    showMessage(`検索語を設定: ${window.__fileListQuery}`, MESSAGE_TYPES.INFO);
}

/**
 * ファイル検索クエリをプロンプトで設定
 * @param {string} datasetId - データセットID
 */
export function setFileListQueryPrompt(datasetId) {
    const cur = window.__fileListQuery || '';
    const q = prompt('ファイル名に含まれる文字列で検索（空で解除）', cur);
    if (q !== null) {
        setFileListQuery(q);
        window.__fileListOffset = 0;
        showDatasetFiles(datasetId, 0);
    }
}

/**
 * ファイルを取り込み
 * @param {string} datasetId - データセットID
 * @param {FileList} files - ファイルリスト
 */
export async function ingestFile(datasetId, files) {
    try {
        if (!files || files.length === 0) return;
        const f = files[0];
        showLoading(true);
        
        const data = await apiClient.uploadFile(`/api/datasets/ingest/${datasetId}`, f);
        
        if (!data.success) {
            showMessage(data.error || '取り込みに失敗しました。', MESSAGE_TYPES.ERROR);
            return;
        }
        
        showMessage('ファイルを取り込みました: ' + (data.saved_to || f.name), MESSAGE_TYPES.SUCCESS);
        loadDatasets();
    } catch (e) {
        console.error('ingest error', e);
        showMessage('取り込みに失敗しました。', MESSAGE_TYPES.ERROR);
    } finally {
        showLoading(false);
    }
}

