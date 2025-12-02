/**
 * 汎用ユーティリティ関数
 */

/**
 * デバウンス関数
 * @param {Function} func - 実行する関数
 * @param {number} wait - 待機時間（ミリ秒）
 * @returns {Function} デバウンスされた関数
 */
export function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * スロットル関数
 * @param {Function} func - 実行する関数
 * @param {number} limit - 制限時間（ミリ秒）
 * @returns {Function} スロットルされた関数
 */
export function throttle(func, limit) {
    let inThrottle;
    return function executedFunction(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/**
 * ファイル名から拡張子を取得
 * @param {string} filename - ファイル名
 * @returns {string} 拡張子
 */
export function getFileExtension(filename) {
    return filename.slice((filename.lastIndexOf('.') - 1 >>> 0) + 2);
}

/**
 * ファイルサイズを人間が読める形式に変換
 * @param {number} bytes - バイト数
 * @returns {string} フォーマットされたサイズ
 */
export function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

/**
 * 数値を指定された小数点以下桁数でフォーマット
 * @param {number} value - 数値
 * @param {number} decimals - 小数点以下桁数
 * @returns {string} フォーマットされた数値
 */
export function formatNumber(value, decimals = 2) {
    const num = Number(value);
    if (isNaN(num)) {
        return '0.' + '0'.repeat(decimals);
    }
    return num.toFixed(decimals);
}

/**
 * パーセンテージを計算
 * @param {number} value - 値
 * @param {number} max - 最大値
 * @returns {number} パーセンテージ
 */
export function calculatePercentage(value, max) {
    if (max === 0) return 0;
    return Math.max(0, Math.min(100, (value / max) * 100));
}

/**
 * クラス名を条件付きで結合
 * @param {...(string|Object)} classes - クラス名または条件付きオブジェクト
 * @returns {string} 結合されたクラス名
 */
export function classNames(...classes) {
    return classes
        .filter(Boolean)
        .map(cls => {
            if (typeof cls === 'string') return cls;
            if (typeof cls === 'object') {
                return Object.keys(cls)
                    .filter(key => cls[key])
                    .join(' ');
            }
            return '';
        })
        .join(' ')
        .trim();
}

/**
 * 画像をBase64に変換
 * @param {File} file - 画像ファイル
 * @returns {Promise<string>} Base64文字列
 */
export function fileToBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result);
        reader.onerror = reject;
        reader.readAsDataURL(file);
    });
}

/**
 * Base64データURLからBlobを作成
 * @param {string} dataURL - Base64データURL
 * @returns {Blob} Blobオブジェクト
 * @throws {Error} 無効なデータURLの場合
 */
export function dataURLToBlob(dataURL) {
    if (!dataURL || typeof dataURL !== 'string') {
        throw new Error('Invalid dataURL: must be a non-empty string');
    }
    
    const arr = dataURL.split(',');
    if (arr.length !== 2) {
        throw new Error('Invalid dataURL format');
    }
    
    const mimeMatch = arr[0].match(/:(.*?);/);
    if (!mimeMatch) {
        throw new Error('Invalid dataURL: MIME type not found');
    }
    
    const mime = mimeMatch[1];
    let bstr;
    try {
        bstr = atob(arr[1]);
    } catch (error) {
        throw new Error('Invalid dataURL: base64 decode failed');
    }
    
    let n = bstr.length;
    const u8arr = new Uint8Array(n);
    while (n--) {
        u8arr[n] = bstr.charCodeAt(n);
    }
    return new Blob([u8arr], { type: mime });
}

/**
 * HTMLエスケープ関数（XSS対策）
 * @param {string} str - エスケープする文字列
 * @returns {string} エスケープされた文字列
 */
export function escapeHtml(str) {
    if (typeof str !== 'string') {
        str = String(str);
    }
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return str.replace(/[&<>"']/g, m => map[m]);
}

/**
 * ファイルをダウンロード
 * @param {Blob|string} data - ダウンロードするデータ
 * @param {string} filename - ファイル名
 * @param {string} mimeType - MIMEタイプ（オプション）
 */
export function downloadFile(data, filename, mimeType = null) {
    try {
        let blob;
        if (data instanceof Blob) {
            blob = data;
        } else if (typeof data === 'string' && data.startsWith('data:')) {
            blob = dataURLToBlob(data);
        } else {
            // 文字列データの場合
            blob = new Blob([data], { type: mimeType || 'text/plain' });
        }
        
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.style.display = 'none';
        document.body.appendChild(a);
        a.click();
        
        // クリーンアップ
        setTimeout(() => {
            window.URL.revokeObjectURL(url);
            if (a.parentNode) {
                document.body.removeChild(a);
            }
        }, 100);
    } catch (error) {
        console.error('Download error:', error);
        throw error;
    }
}

/**
 * 遅延実行
 * @param {number} ms - 遅延時間（ミリ秒）
 * @returns {Promise<void>} Promise
 */
export function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * ボタンまたは要素を無効化
 * @param {HTMLElement|string} element - 要素または要素ID
 * @param {boolean} disabled - 無効化するかどうか
 */
export function setElementDisabled(element, disabled) {
    if (typeof element === 'string') {
        element = document.getElementById(element);
    }
    if (!element) return;
    
    // disabledプロパティを持つ要素のみ処理
    if ('disabled' in element) {
        element.disabled = disabled;
        if (disabled) {
            element.setAttribute('aria-disabled', 'true');
        } else {
            element.removeAttribute('aria-disabled');
        }
    }
}

/**
 * 複数の要素を一度に無効化/有効化
 * @param {Array<HTMLElement|string>} elements - 要素または要素IDの配列
 * @param {boolean} disabled - 無効化するかどうか
 */
export function setElementsDisabled(elements, disabled) {
    elements.forEach(el => setElementDisabled(el, disabled));
}




