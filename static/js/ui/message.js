/**
 * UI通知機能（メッセージ表示、ローディング表示）
 */
import { dom } from '../core/dom.js';
import { TIMING, MESSAGE_TYPES } from '../core/constants.js';

/**
 * メッセージを表示
 * @param {string} message - 表示するメッセージ
 * @param {string} type - メッセージタイプ（'success', 'error', 'warning', 'info'）
 * @param {number} duration - 表示時間（ミリ秒、デフォルト: 5000）
 */
// メッセージタイマーの管理（クリーンアップ用）
let messageTimer = null;

export function showMessage(message, type = MESSAGE_TYPES.INFO, duration = TIMING.MESSAGE_DURATION) {
    const messageArea = dom.getElement('messageArea');
    if (!messageArea) return;

    // 既存のタイマーをクリア
    if (messageTimer) {
        clearTimeout(messageTimer);
        messageTimer = null;
    }

    // 安全な型のみ許可
    const safeType = Object.values(MESSAGE_TYPES).includes(type) ? type : MESSAGE_TYPES.INFO;
    
    // XSS対策: innerHTMLの代わりにcreateElementを使用
    messageArea.innerHTML = '';
    const messageDiv = document.createElement('div');
    messageDiv.className = safeType;
    // textContentを使用することで自動的にエスケープされる（XSS対策）
    messageDiv.textContent = message;
    messageArea.appendChild(messageDiv);
    
    if (duration > 0) {
        messageTimer = setTimeout(() => {
            messageArea.innerHTML = '';
            messageTimer = null;
        }, duration);
    }
}

/**
 * ローディング表示
 * @param {boolean} show - 表示するかどうか
 */
export function showLoading(show) {
    const loading = dom.getElement('loading');
    if (loading) {
        loading.style.display = show ? 'block' : 'none';
    }
}




