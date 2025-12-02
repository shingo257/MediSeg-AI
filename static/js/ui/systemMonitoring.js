/**
 * システム監視関連のUI機能
 */
import { dom } from '../core/dom.js';
import { showMessage } from './message.js';
import { TIMING, FALLBACK, PERFORMANCE, UI } from '../core/constants.js';

/**
 * ダミーデータ警告を表示
 */
export function showDummyDataWarning() {
    // 既存の警告を削除
    const existingWarning = dom.getElement('dummyDataWarning');
    if (existingWarning) {
        existingWarning.remove();
    }
    
    // 新しい警告を作成
    const warning = document.createElement('div');
    warning.id = 'dummyDataWarning';
    warning.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #ff6b6b;
        color: white;
        padding: 10px 15px;
        border-radius: 5px;
        font-size: 14px;
        z-index: 1000;
        box-shadow: 0 2px 10px rgba(0,0,0,0.3);
        animation: slideIn 0.3s ease-out;
    `;
    warning.textContent = '⚠️ リアルタイム監視データが取得できません。フォールバック処理でダミーデータを表示しています。';
    
    // アニメーション用のCSSを追加
    if (!dom.getElement('dummyDataWarningStyle')) {
        const style = document.createElement('style');
        style.id = 'dummyDataWarningStyle';
        style.textContent = `
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
        `;
        document.head.appendChild(style);
    }
    
    document.body.appendChild(warning);
    
    // 5秒後に警告を自動削除
    setTimeout(() => {
        if (warning.parentNode) {
            warning.remove();
        }
    }, TIMING.WARNING_DURATION);
}

/**
 * ダミーデータ警告を非表示にする
 */
export function hideDummyDataWarning() {
    const existingWarning = dom.getElement('dummyDataWarning');
    if (existingWarning) {
        existingWarning.remove();
    }
}

/**
 * フォールバック監視（模擬データ）
 * 注意: この関数は実データが取得できない場合にのみ使用されます
 */
export function showFallbackMonitoring() {
    // ダミーデータであることを明示的に表示
    const cpuUsage = Math.random() * (FALLBACK.CPU_MAX - FALLBACK.CPU_MIN) + FALLBACK.CPU_MIN;
    const cpuUsageEl = dom.getElement('cpuUsage');
    const cpuBar = dom.getElement('cpuBar');
    if (cpuUsageEl && cpuBar) {
        cpuUsageEl.textContent = `${cpuUsage.toFixed(1)}% [フォールバック: ダミーデータ]`;
        cpuUsageEl.title = '⚠️ 実データが取得できません。フォールバック処理でダミーデータを表示しています。';
        cpuBar.style.width = `${cpuUsage}%`;
        cpuBar.style.backgroundColor = '#ff6b6b';
        cpuBar.style.border = '2px dashed #ff6b6b';
    }
    
    const gpuUsage = Math.random() * (FALLBACK.GPU_MAX - FALLBACK.GPU_MIN) + FALLBACK.GPU_MIN;
    const gpuUsageEl = dom.getElement('gpuUsage');
    const gpuBar = dom.getElement('gpuBar');
    if (gpuUsageEl && gpuBar) {
        gpuUsageEl.textContent = `${gpuUsage.toFixed(1)}% [フォールバック: ダミーデータ]`;
        gpuUsageEl.title = '⚠️ 実データが取得できません。フォールバック処理でダミーデータを表示しています。';
        gpuBar.style.width = `${gpuUsage}%`;
        gpuBar.style.backgroundColor = '#ff6b6b';
        gpuBar.style.border = '2px dashed #ff6b6b';
    }
    
    const memoryUsage = Math.random() * (FALLBACK.MEMORY_MAX - FALLBACK.MEMORY_MIN) + FALLBACK.MEMORY_MIN;
    const memoryUsageEl = dom.getElement('memoryUsage');
    const memoryBar = dom.getElement('memoryBar');
    if (memoryUsageEl && memoryBar) {
        memoryUsageEl.textContent = `${memoryUsage.toFixed(0)}MB [フォールバック: ダミーデータ]`;
        memoryUsageEl.title = '⚠️ 実データが取得できません。フォールバック処理でダミーデータを表示しています。';
        memoryBar.style.width = `${(memoryUsage / PERFORMANCE.MAX_MEMORY) * 100}%`;
        memoryBar.style.backgroundColor = '#ff6b6b';
        memoryBar.style.border = '2px dashed #ff6b6b';
    }
    
    const processingSpeed = Math.random() * (FALLBACK.SPEED_MAX - FALLBACK.SPEED_MIN) + FALLBACK.SPEED_MIN;
    const processingSpeedEl = dom.getElement('processingSpeed');
    const speedBar = dom.getElement('speedBar');
    if (processingSpeedEl && speedBar) {
        processingSpeedEl.textContent = `${processingSpeed.toFixed(1)} FPS [フォールバック: ダミーデータ]`;
        processingSpeedEl.title = '⚠️ 実データが取得できません。フォールバック処理でダミーデータを表示しています。';
        speedBar.style.width = `${(processingSpeed / PERFORMANCE.MAX_PROCESSING_SPEED) * 100}%`;
        speedBar.style.backgroundColor = '#ff6b6b';
        speedBar.style.border = '2px dashed #ff6b6b';
    }
    
    // ダミーデータ警告を表示（常に表示）
    showDummyDataWarning();
}

