/**
 * ワークフロー管理
 */
import { dom } from '../core/dom.js';

/**
 * ワークフローステップを更新
 * @param {number} stepNumber - ステップ番号（1-3）
 */
export function updateWorkflowStep(stepNumber) {
    // 全てのステップを非アクティブに
    const steps = dom.querySelectorAll('.step');
    if (steps && steps.length > 0) {
        steps.forEach(step => {
            step.classList.remove('active');
        });
    }
    
    // 指定されたステップをアクティブに
    const targetStep = dom.getElement(`step${stepNumber}`);
    if (targetStep) {
        targetStep.classList.add('active');
    }
}

