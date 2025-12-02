/**
 * APIClient - API呼び出しの統一管理
 * エラーハンドリングとローディング状態を統一管理
 */
export class APIClient {
    constructor(baseURL = '') {
        this.baseURL = baseURL;
        this.defaultHeaders = {
            'Content-Type': 'application/json'
        };
    }

    /**
     * リクエストを送信
     * @param {string} url - エンドポイントURL
     * @param {Object} options - fetchオプション
     * @returns {Promise<Response>}
     */
    async request(url, options = {}) {
        const fullUrl = `${this.baseURL}${url}`;
        const config = {
            ...options,
            headers: {
                ...this.defaultHeaders,
                ...options.headers
            }
        };

        try {
            const response = await fetch(fullUrl, config);
            return response;
        } catch (error) {
            throw new Error(`Network error: ${error.message}`);
        }
    }

    /**
     * JSONリクエストを送信
     * @param {string} url - エンドポイントURL
     * @param {Object} options - fetchオプション
     * @returns {Promise<Object>}
     */
    async requestJSON(url, options = {}) {
        const response = await this.request(url, options);
        
        if (!response.ok) {
            // エラーレスポンスの本文を取得してより詳細なエラーメッセージを提供
            let errorMessage = `HTTP error! status: ${response.status}`;
            try {
                const errorData = await response.json();
                if (errorData.error) {
                    errorMessage = errorData.error;
                } else if (errorData.message) {
                    errorMessage = errorData.message;
                }
            } catch (_) {
                // JSON解析に失敗した場合はステータステキストを使用
                try {
                    const text = await response.text();
                    if (text) {
                        errorMessage = text.substring(0, 200); // 長すぎる場合は切り詰め
                    }
                } catch (_) {
                    // テキスト取得にも失敗した場合はデフォルトメッセージを使用
                }
            }
            throw new Error(errorMessage);
        }

        try {
            const data = await response.json();
            return data;
        } catch (error) {
            throw new Error(`Failed to parse JSON: ${error.message}`);
        }
    }

    /**
     * GETリクエスト
     * @param {string} url - エンドポイントURL
     * @param {Object} params - クエリパラメータ
     * @returns {Promise<Object>}
     */
    async get(url, params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const fullUrl = queryString ? `${url}?${queryString}` : url;
        return this.requestJSON(fullUrl, {
            method: 'GET'
        });
    }

    /**
     * POSTリクエスト
     * @param {string} url - エンドポイントURL
     * @param {Object} data - 送信データ
     * @param {Object} options - 追加オプション
     * @returns {Promise<Object>}
     */
    async post(url, data = null, options = {}) {
        const config = {
            method: 'POST',
            ...options
        };

        // headersが未定義の場合は初期化
        if (!config.headers) {
            config.headers = {};
        }

        if (data instanceof FormData) {
            // FormDataの場合はContent-Typeを設定しない（ブラウザが自動設定）
            delete config.headers['Content-Type'];
            config.body = data;
        } else if (data) {
            config.body = JSON.stringify(data);
        }

        return this.requestJSON(url, config);
    }

    /**
     * PUTリクエスト
     * @param {string} url - エンドポイントURL
     * @param {Object} data - 送信データ
     * @returns {Promise<Object>}
     */
    async put(url, data = {}) {
        return this.requestJSON(url, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    /**
     * DELETEリクエスト
     * @param {string} url - エンドポイントURL
     * @returns {Promise<Object>}
     */
    async delete(url) {
        return this.requestJSON(url, {
            method: 'DELETE'
        });
    }

    /**
     * ファイルアップロード
     * @param {string} url - エンドポイントURL
     * @param {File} file - アップロードするファイル
     * @param {Object} options - 追加オプション
     * @returns {Promise<Object>}
     */
    async uploadFile(url, file, options = {}) {
        const formData = new FormData();
        formData.append('file', file);

        return this.post(url, formData, options);
    }

    /**
     * ダウンロード（Blob）
     * @param {string} url - エンドポイントURL
     * @returns {Promise<Blob>}
     */
    async downloadBlob(url) {
        const response = await this.request(url, {
            method: 'GET'
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return response.blob();
    }

    /**
     * AbortController付きリクエスト
     * @param {string} url - エンドポイントURL
     * @param {Object} options - fetchオプション
     * @returns {Object} { response, controller }
     */
    createAbortableRequest(url, options = {}) {
        const controller = new AbortController();
        const requestPromise = this.requestJSON(url, {
            ...options,
            signal: controller.signal
        });

        return {
            promise: requestPromise,
            controller: controller,
            abort: () => controller.abort()
        };
    }
}

// デフォルトインスタンスをエクスポート
export const apiClient = new APIClient();




