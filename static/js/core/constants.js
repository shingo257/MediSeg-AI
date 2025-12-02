/**
 * アプリケーション定数
 * マジックナンバーを定数として定義し、保守性と一貫性を向上
 * 
 * @module constants
 */

/**
 * タイミング関連の定数
 * システム監視、メッセージ表示、ポーリングなどの時間間隔を定義
 * @type {Object}
 */
export const TIMING = {
    MONITORING_INTERVAL: 1000,        // システム監視の更新間隔（ミリ秒）
    MESSAGE_DURATION: 5000,           // メッセージ表示時間（ミリ秒）
    WARNING_DURATION: 5000,            // 警告表示時間（ミリ秒）
    POLL_INTERVAL: 1200,               // ダウンロード状態ポーリング間隔（ミリ秒）
    POLL_INTERVAL_MAX: 5000,           // ポーリング間隔の最大値（ミリ秒）
    POLL_INTERVAL_INCREMENT: 400,     // ポーリング間隔の増分（ミリ秒）
    POLL_TIMEOUT: 30 * 60 * 1000,     // ポーリングタイムアウト（30分）
    POLL_ERROR_TIMEOUT: 60000,         // エラー時のポーリングタイムアウト（1分）
    STATUS_UPDATE_THROTTLE: 500         // ステータス更新のスロットル（ミリ秒）
};

/**
 * パフォーマンス関連の定数
 * 処理速度、メモリ、3D可視化などの上限値を定義
 * @type {Object}
 */
export const PERFORMANCE = {
    MAX_PROCESSING_SPEED: 30,          // 最大処理速度（FPS）
    MAX_MEMORY: 10000,                 // 最大メモリ（MB）
    MAX_POINTS_3D: 1000                // 3D可視化の最大点数
};

/**
 * UI関連の定数
 * z-index、表示数などのUI設定値を定義
 * @type {Object}
 */
export const UI = {
    Z_INDEX_WARNING: 1000,             // 警告のz-index
    MAX_SAMPLE_IMAGES: 6               // サンプル画像の最大表示数
};

/**
 * セグメンテーション関連の定数
 * デフォルトモデル、閾値などのセグメンテーション設定を定義
 * @type {Object}
 */
export const SEGMENTATION = {
    DEFAULT_MODEL: 'unet',             // デフォルトモデル
    DEFAULT_THRESHOLD: 0.5,             // デフォルト閾値
    MIN_THRESHOLD: 0.0,                 // 最小閾値
    MAX_THRESHOLD: 1.0                  // 最大閾値
};

/**
 * フォールバック関連の定数
 * 実データが取得できない場合のダミーデータの範囲を定義
 * @type {Object}
 */
export const FALLBACK = {
    CPU_MIN: 0,                        // CPU使用率の最小値（%）
    CPU_MAX: 100,                      // CPU使用率の最大値（%）
    GPU_MIN: 0,                        // GPU使用率の最小値（%）
    GPU_MAX: 100,                       // GPU使用率の最大値（%）
    MEMORY_MIN: 2000,                  // メモリ使用量の最小値（MB）
    MEMORY_MAX: 10000,                 // メモリ使用量の最大値（MB）
    SPEED_MIN: 5,                      // 処理速度の最小値（FPS）
    SPEED_MAX: 30                      // 処理速度の最大値（FPS）
};

/**
 * メッセージタイプ
 * UIで使用するメッセージの種類を定義
 * @type {Object}
 */
export const MESSAGE_TYPES = {
    SUCCESS: 'success',
    ERROR: 'error',
    WARNING: 'warning',
    INFO: 'info'
};

/**
 * ステータスタイプ
 * データセットの状態を表すタイプを定義
 * @type {Object}
 */
export const STATUS_TYPES = {
    AVAILABLE: 'available',
    DOWNLOADING: 'downloading',
    DOWNLOADED: 'downloaded',
    ERROR: 'error'
};

/**
 * ファイル関連の定数
 * ファイルサイズ、有効な画像タイプなどを定義
 * @type {Object}
 */
export const FILE = {
    MAX_SIZE: 50 * 1024 * 1024,           // 最大ファイルサイズ（50MB）
    VALID_IMAGE_TYPES: [                   // 有効な画像タイプ
        'image/jpeg',
        'image/jpg',
        'image/png',
        'image/gif',
        'image/bmp',
        'image/webp'
    ]
};

/**
 * アニメーション関連の定数
 * アニメーション速度の範囲などを定義
 * @type {Object}
 */
export const ANIMATION = {
    MIN_SPEED: 0.1,                        // 最小アニメーション速度
    MAX_SPEED: 5.0,                        // 最大アニメーション速度
    DEFAULT_SPEED: 1.0                     // デフォルトアニメーション速度
};

