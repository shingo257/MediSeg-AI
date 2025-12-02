/**
 * 信頼度ヒートマップ
 */

/**
 * 信頼度ヒートマップを描画
 * @param {CanvasRenderingContext2D} ctx - キャンバスコンテキスト
 * @param {number} width - キャンバス幅
 * @param {number} height - キャンバス高さ
 * @param {Array<Array<number>>} confidenceData - 信頼度データ（2次元配列、オプション）
 */
export function drawConfidenceHeatmap(ctx, width, height, confidenceData = null) {
    ctx.clearRect(0, 0, width, height);
    
    const cellSize = 8;
    const cols = Math.floor(width / cellSize);
    const rows = Math.floor(height / cellSize);
    
    // 実データがない場合は空のヒートマップを表示
    if (!confidenceData || !Array.isArray(confidenceData) || confidenceData.length === 0) {
        ctx.fillStyle = '#2c3e50';
        ctx.fillRect(0, 0, width, height);
        ctx.fillStyle = '#ff6b6b';
        ctx.font = 'bold 14px Arial';
        ctx.textAlign = 'center';
        ctx.fillText('データなし', width / 2, height / 2 - 10);
        ctx.fillStyle = '#9fb2c8';
        ctx.font = '12px Arial';
        ctx.fillText('（実データが利用できません）', width / 2, height / 2 + 10);
        return;
    }
    
    // 実データを使用してヒートマップを描画
    for (let row = 0; row < rows; row++) {
        for (let col = 0; col < cols; col++) {
            let intensity = 0;
            if (confidenceData[row] && confidenceData[row][col] !== undefined) {
                intensity = Math.max(0, Math.min(1, confidenceData[row][col]));
            }
            const hue = intensity * 120; // 緑から赤
            ctx.fillStyle = `hsl(${hue}, 100%, 50%)`;
            ctx.fillRect(col * cellSize, row * cellSize, cellSize, cellSize);
        }
    }
}




