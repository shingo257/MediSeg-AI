/**
 * DOMHelper - DOM操作の統一管理クラス
 * document.getElementByIdの重複を削減し、要素取得とイベントリスナー管理を一元化
 */
export class DOMHelper {
    constructor() {
        this.cache = new Map();
    }

    /**
     * 要素を取得（キャッシュ付き）
     * @param {string} id - 要素ID
     * @returns {HTMLElement|null}
     */
    getElement(id) {
        if (!this.cache.has(id)) {
            const element = document.getElementById(id);
            if (element) {
                this.cache.set(id, element);
            }
        }
        return this.cache.get(id) || null;
    }

    /**
     * 複数の要素を一度に取得
     * @param {string[]} ids - 要素IDの配列
     * @returns {Object} IDをキーとした要素オブジェクト
     */
    getElements(ids) {
        const elements = {};
        ids.forEach(id => {
            elements[id] = this.getElement(id);
        });
        return elements;
    }

    /**
     * 要素を取得（キャッシュなし）
     * @param {string} id - 要素ID
     * @returns {HTMLElement|null}
     */
    getElementById(id) {
        return document.getElementById(id);
    }

    /**
     * クエリセレクター
     * @param {string} selector - CSSセレクター
     * @returns {HTMLElement|null}
     */
    querySelector(selector) {
        return document.querySelector(selector);
    }

    /**
     * クエリセレクター（複数）
     * @param {string} selector - CSSセレクター
     * @returns {NodeList}
     */
    querySelectorAll(selector) {
        return document.querySelectorAll(selector);
    }

    /**
     * イベントリスナーを安全に追加（簡易版）
     * @param {HTMLElement|Window|Document} element - 要素（ID文字列または要素オブジェクト）
     * @param {string} event - イベントタイプ
     * @param {Function} handler - イベントハンドラー
     */
    on(element, event, handler) {
        if (typeof element === 'string') {
            element = this.getElement(element);
        }
        if (element) {
            element.addEventListener(event, handler);
        }
    }

    /**
     * イベントリスナーを削除（簡易版）
     * @param {HTMLElement|Window|Document} element - 要素（ID文字列または要素オブジェクト）
     * @param {string} event - イベントタイプ
     * @param {Function} handler - イベントハンドラー
     */
    off(element, event, handler) {
        if (typeof element === 'string') {
            element = this.getElement(element);
        }
        if (element) {
            element.removeEventListener(event, handler);
        }
    }

    /**
     * イベントリスナーを安全に追加
     * @param {string} id - 要素ID
     * @param {string} event - イベントタイプ
     * @param {Function} handler - イベントハンドラー
     * @param {boolean} useCache - キャッシュを使用するか
     */
    addEventListener(id, event, handler, useCache = true) {
        const element = useCache ? this.getElement(id) : this.getElementById(id);
        if (element) {
            element.addEventListener(event, handler);
        }
    }

    /**
     * イベントリスナーを削除
     * @param {string} id - 要素ID
     * @param {string} event - イベントタイプ
     * @param {Function} handler - イベントハンドラー
     */
    removeEventListener(id, event, handler) {
        const element = this.getElement(id);
        if (element) {
            element.removeEventListener(event, handler);
        }
    }

    /**
     * キャッシュをクリア
     */
    clearCache() {
        this.cache.clear();
    }

    /**
     * 特定の要素のキャッシュをクリア
     * @param {string} id - 要素ID
     */
    clearElementCache(id) {
        this.cache.delete(id);
    }
}

// シングルトンインスタンスをエクスポート
export const dom = new DOMHelper();

