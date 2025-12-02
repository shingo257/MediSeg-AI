/**
 * StateManager - グローバル状態の一元管理
 * 状態変更の通知メカニズムを実装
 */
export class StateManager {
    constructor() {
        this.state = {
            currentImage: null,
            currentResults: null,
            currentDataset: null,
            currentZoom: 1,
            isPanning: false,
            startX: 0,
            startY: 0,
            offsetX: 0,
            offsetY: 0,
            isMultiView: false,
            is3DView: false,
            isStatsView: false,
            animationId: null,
            currentFrame: 0,
            animationSpeed: 1,
            inferenceController: null
        };
        this.listeners = new Map();
    }

    /**
     * 状態を取得
     * @param {string} key - 状態のキー
     * @returns {*} 状態の値
     */
    get(key) {
        return this.state[key];
    }

    /**
     * 状態を設定
     * @param {string} key - 状態のキー
     * @param {*} value - 設定する値
     * @param {boolean} notify - リスナーに通知するか
     */
    set(key, value, notify = true) {
        const oldValue = this.state[key];
        this.state[key] = value;
        
        if (notify && oldValue !== value) {
            this.notify(key, value, oldValue);
        }
    }

    /**
     * 複数の状態を一度に設定
     * @param {Object} updates - 更新する状態のオブジェクト
     * @param {boolean} notify - リスナーに通知するか
     */
    setMultiple(updates, notify = true) {
        const oldValues = {};
        Object.keys(updates).forEach(key => {
            oldValues[key] = this.state[key];
            this.state[key] = updates[key];
        });

        if (notify) {
            Object.keys(updates).forEach(key => {
                if (oldValues[key] !== updates[key]) {
                    this.notify(key, updates[key], oldValues[key]);
                }
            });
        }
    }

    /**
     * 状態変更リスナーを登録
     * @param {string} key - 監視する状態のキー
     * @param {Function} callback - コールバック関数
     * @returns {Function} 登録解除関数
     */
    subscribe(key, callback) {
        if (!this.listeners.has(key)) {
            this.listeners.set(key, new Set());
        }
        this.listeners.get(key).add(callback);

        // 登録解除関数を返す
        return () => {
            const callbacks = this.listeners.get(key);
            if (callbacks) {
                callbacks.delete(callback);
            }
        };
    }

    /**
     * 状態変更を通知
     * @param {string} key - 変更された状態のキー
     * @param {*} newValue - 新しい値
     * @param {*} oldValue - 古い値
     */
    notify(key, newValue, oldValue) {
        const callbacks = this.listeners.get(key);
        if (callbacks) {
            callbacks.forEach(callback => {
                try {
                    callback(newValue, oldValue, key);
                } catch (error) {
                    console.error(`Error in state listener for ${key}:`, error);
                }
            });
        }
    }

    /**
     * 全状態を取得
     * @returns {Object} 状態オブジェクトのコピー
     */
    getAll() {
        return { ...this.state };
    }

    /**
     * 状態をリセット
     */
    reset() {
        // クリーンアップ
        if (this.state.monitoringInterval) {
            clearInterval(this.state.monitoringInterval);
        }
        if (this.state.animationId) {
            cancelAnimationFrame(this.state.animationId);
        }
        if (this.state.inferenceController && typeof this.state.inferenceController.abort === 'function') {
            try {
                this.state.inferenceController.abort();
            } catch (_) {}
        }
        
        this.state = {
            currentImage: null,
            currentResults: null,
            currentDataset: null,
            currentZoom: 1,
            isPanning: false,
            startX: 0,
            startY: 0,
            offsetX: 0,
            offsetY: 0,
            isMultiView: false,
            is3DView: false,
            isStatsView: false,
            animationId: null,
            currentFrame: 0,
            animationSpeed: 1,
            inferenceController: null,
            monitoringInterval: null
        };
        this.notify('*', null, null);
    }
}

// シングルトンインスタンスをエクスポート
export const state = new StateManager();




