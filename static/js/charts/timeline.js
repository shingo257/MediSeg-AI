/**
 * 時系列変化チャート
 */

/**
 * 時系列変化チャートを描画
 * @param {CanvasRenderingContext2D} ctx - キャンバスコンテキスト
 * @param {number} width - キャンバス幅
 * @param {number} height - キャンバス高さ
 */
export function drawTimelineChart(ctx, width, height) {
    ctx.clearRect(0, 0, width, height);
    
    const points = 20;
    const stepX = width / points;
    
    ctx.strokeStyle = '#4ecdc4';
    ctx.lineWidth = 2;
    ctx.beginPath();
    
    for (let i = 0; i < points; i++) {
        const x = i * stepX;
        const y = height - (Math.sin(i * 0.3) * 0.5 + 0.5) * (height - 40) - 20;
        
        if (i === 0) {
            ctx.moveTo(x, y);
        } else {
            ctx.lineTo(x, y);
        }
    }
    ctx.stroke();
    
    // グリッド線
    ctx.strokeStyle = 'rgba(255,255,255,0.2)';
    ctx.lineWidth = 1;
    for (let i = 0; i <= 5; i++) {
        const y = (height / 5) * i;
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(width, y);
        ctx.stroke();
    }
}




