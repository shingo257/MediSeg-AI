/**
 * 3D可視化関連
 */
import { dom } from '../core/dom.js';

/**
 * 3D可視化を初期化
 */
export function init3DVisualization() {
    const canvas = dom.getElement('viz3DCanvas');
    if (!canvas) return;
    
    // キャンバスサイズを設定
    if (!canvas.width) canvas.width = canvas.offsetWidth || 400;
    if (!canvas.height) canvas.height = canvas.offsetHeight || 400;
    
    const ctx = canvas.getContext('2d');
    draw3D(ctx, canvas.width, canvas.height);
}

/**
 * 3D描画
 * @param {CanvasRenderingContext2D} ctx - キャンバスコンテキスト
 * @param {number} width - キャンバス幅
 * @param {number} height - キャンバス高さ
 */
export function draw3D(ctx, width, height) {
    ctx.clearRect(0, 0, width, height);
    
    // 3D効果の描画
    const centerX = width / 2;
    const centerY = height / 2;
    const radius = 100;
    
    // 球体の描画
    const gradient = ctx.createRadialGradient(centerX-30, centerY-30, 0, centerX, centerY, radius);
    gradient.addColorStop(0, '#4ecdc4');
    gradient.addColorStop(1, '#2c3e50');
    
    ctx.fillStyle = gradient;
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
    ctx.fill();
    
    // グリッド線
    ctx.strokeStyle = 'rgba(255,255,255,0.3)';
    ctx.lineWidth = 1;
    for (let i = 0; i < 10; i++) {
        const y = (height / 10) * i;
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(width, y);
        ctx.stroke();
    }
}

