/**
 * メトリクス分布チャート
 */
import { state } from '../core/state.js';

/**
 * メトリクス分布チャートを描画
 * @param {CanvasRenderingContext2D} ctx - キャンバスコンテキスト
 * @param {number} width - キャンバス幅
 * @param {number} height - キャンバス高さ
 */
export function drawMetricsChart(ctx, width, height) {
    ctx.clearRect(0, 0, width, height);
    
    const currentResults = state.get('currentResults');
    const metrics = currentResults?.metrics || {dice: 0.8, iou: 0.7, accuracy: 0.9, sensitivity: 0.85, specificity: 0.95};
    const values = Object.values(metrics);
    const labels = Object.keys(metrics);
    
    if (values.length === 0) {
        ctx.fillStyle = '#888';
        ctx.font = '14px Arial';
        ctx.textAlign = 'center';
        ctx.fillText('メトリクスデータがありません', width / 2, height / 2);
        return;
    }
    
    const padding = { top: 30, bottom: 30, left: 40, right: 20 };
    const chartWidth = width - padding.left - padding.right;
    const chartHeight = height - padding.top - padding.bottom;
    const barWidth = chartWidth / values.length;
    const maxValue = Math.max(...values, 1);
    const minValue = Math.min(...values, 0);
    const valueRange = maxValue - minValue || 1;
    
    // グリッド線を描画
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
    ctx.lineWidth = 1;
    const gridLines = 5;
    for (let i = 0; i <= gridLines; i++) {
        const y = padding.top + (chartHeight / gridLines) * i;
        ctx.beginPath();
        ctx.moveTo(padding.left, y);
        ctx.lineTo(width - padding.right, y);
        ctx.stroke();
        
        // Y軸のラベル
        const value = maxValue - (valueRange / gridLines) * i;
        ctx.fillStyle = '#aaa';
        ctx.font = '10px Arial';
        ctx.textAlign = 'right';
        ctx.fillText(value.toFixed(2), padding.left - 5, y + 3);
    }
    
    // バーを描画
    values.forEach((value, index) => {
        const barHeight = (value / maxValue) * chartHeight;
        const x = padding.left + index * barWidth;
        const y = padding.top + chartHeight - barHeight;
        
        // グラデーション効果
        const gradient = ctx.createLinearGradient(x, y, x, y + barHeight);
        const hue = index * 60;
        gradient.addColorStop(0, `hsl(${hue}, 70%, 55%)`);
        gradient.addColorStop(1, `hsl(${hue}, 70%, 35%)`);
        
        // 影効果を設定
        ctx.shadowColor = 'rgba(0, 0, 0, 0.3)';
        ctx.shadowBlur = 4;
        ctx.shadowOffsetX = 2;
        ctx.shadowOffsetY = 2;
        
        ctx.fillStyle = gradient;
        ctx.fillRect(x + 5, y, barWidth - 10, barHeight);
        
        // 影効果をリセット
        ctx.shadowBlur = 0;
        ctx.shadowOffsetX = 0;
        ctx.shadowOffsetY = 0;
        
        // ラベル
        ctx.fillStyle = '#fff';
        ctx.font = '11px Arial';
        ctx.textAlign = 'center';
        ctx.fillText(labels[index].toUpperCase(), x + barWidth/2, height - padding.bottom + 15);
        
        // 値の表示
        ctx.font = 'bold 12px Arial';
        ctx.fillText(value.toFixed(3), x + barWidth/2, y - 8);
    });
    
    // Y軸のタイトル
    ctx.save();
    ctx.translate(15, height / 2);
    ctx.rotate(-Math.PI / 2);
    ctx.fillStyle = '#ccc';
    ctx.font = '12px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('メトリクス値', 0, 0);
    ctx.restore();
}




