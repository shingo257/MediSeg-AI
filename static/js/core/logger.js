/**
 * ロガーユーティリティ
 * 本番環境と開発環境で異なるログレベルを提供
 */

// 開発モードかどうかを判定（本番環境ではfalseに設定）
const isDevelopment = true; // TODO: 環境変数から取得するように変更

/**
 * エラーログを出力
 * @param {string} message - エラーメッセージ
 * @param {Error|any} error - エラーオブジェクト（オプション）
 */
export function logError(message, error = null) {
    if (isDevelopment || error) {
        console.error(message, error || '');
    }
}

/**
 * 警告ログを出力（開発環境のみ）
 * @param {string} message - 警告メッセージ
 * @param {any} data - 追加データ（オプション）
 */
export function logWarning(message, data = null) {
    if (isDevelopment) {
        console.warn(message, data || '');
    }
}

/**
 * 情報ログを出力（開発環境のみ）
 * @param {string} message - 情報メッセージ
 * @param {any} data - 追加データ（オプション）
 */
export function logInfo(message, data = null) {
    if (isDevelopment) {
        console.log(message, data || '');
    }
}

/**
 * デバッグログを出力（開発環境のみ）
 * @param {string} message - デバッグメッセージ
 * @param {any} data - 追加データ（オプション）
 */
export function logDebug(message, data = null) {
    if (isDevelopment) {
        console.debug(message, data || '');
    }
}

