/**
 * 領域統計チャート
 */

/**
 * 領域統計チャートを描画
 * @param {CanvasRenderingContext2D} ctx - キャンバスコンテキスト
 * @param {number} width - キャンバス幅
 * @param {number} height - キャンバス高さ
 */
export function drawRegionChart(ctx, width, height) {
    ctx.clearRect(0, 0, width, height);
    
    // 円グラフ風の表示
    const centerX = width / 2;
    const centerY = height / 2;
    const radius = Math.min(width, height) / 2 - 20;
    
    const data = [
        {label: '背景', value: 0.6, color: '#2c3e50'},
        {label: '病変', value: 0.3, color: '#e74c3c'},
        {label: '境界', value: 0.1, color: '#f39c12'}
    ];
    
    let currentAngle = 0;
    data.forEach(item => {
        const sliceAngle = item.value * 2 * Math.PI;
        
        ctx.beginPath();
        ctx.moveTo(centerX, centerY);
        ctx.arc(centerX, centerY, radius, currentAngle, currentAngle + sliceAngle);
        ctx.closePath();
        ctx.fillStyle = item.color;
        ctx.fill();
        
        // ラベル
        const labelAngle = currentAngle + sliceAngle / 2;
        const labelX = centerX + Math.cos(labelAngle) * (radius + 20);
        const labelY = centerY + Math.sin(labelAngle) * (radius + 20);
        
        ctx.fillStyle = '#fff';
        ctx.font = '12px Arial';
        ctx.textAlign = 'center';
        ctx.fillText(item.label, labelX, labelY);
        
        currentAngle += sliceAngle;
    });
}




