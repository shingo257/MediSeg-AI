/**
 * アニメーション制御
 */
import { state } from '../core/state.js';
import { dom } from '../core/dom.js';
import { init3DVisualization } from './3d.js';

/**
 * アニメーションを開始
 */
export function startAnimation() {
    const existingAnimationId = state.get('animationId');
    if (existingAnimationId) return;
    
    function animate() {
        const currentFrame = state.get('currentFrame');
        const animationSpeed = state.get('animationSpeed');
        const newFrame = (currentFrame + animationSpeed) % 100;
        
        state.set('currentFrame', newFrame);
        
        const animationFrameEl = dom.getElement('animationFrame');
        if (animationFrameEl) {
            animationFrameEl.value = newFrame;
        }
        
        // アニメーション効果を適用
        const is3DView = state.get('is3DView');
        if (is3DView) {
            init3DVisualization();
        }
        
        const newAnimationId = requestAnimationFrame(animate);
        state.set('animationId', newAnimationId);
    }
    
    const initialAnimationId = requestAnimationFrame(animate);
    state.set('animationId', initialAnimationId);
}

/**
 * アニメーションを一時停止
 */
export function pauseAnimation() {
    const animationId = state.get('animationId');
    if (animationId) {
        cancelAnimationFrame(animationId);
        state.set('animationId', null);
    }
}

/**
 * アニメーションをリセット
 */
export function resetAnimation() {
    pauseAnimation();
    state.set('currentFrame', 0);
    
    const animationFrameEl = dom.getElement('animationFrame');
    if (animationFrameEl) {
        animationFrameEl.value = 0;
    }
}




