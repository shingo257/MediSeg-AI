/**
 * モーダル表示管理
 */
import { dom } from '../core/dom.js';
import { escapeHtml } from '../core/utils.js';

/**
 * 画像モーダルを表示（既存のモーダルがあれば削除してから新規作成）
 * @param {string} src - 画像のソース
 * @param {string} title - モーダルのタイトル
 */
export function showImageModal(src, title = '画像詳細') {
    // 既存の画像モーダルを削除
    const existingModal = document.querySelector('.image-modal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // タイトルとsrcをエスケープ（XSS対策）
    const safeTitle = escapeHtml(String(title));
    const safeSrc = escapeHtml(String(src));
    
    const modal = document.createElement('div');
    modal.className = 'modal image-modal';
    modal.setAttribute('role', 'dialog');
    modal.setAttribute('aria-labelledby', 'image-modal-title');
    modal.setAttribute('aria-modal', 'true');
    
    let escapeHandler = null;
    const closeHandler = () => {
        if (escapeHandler) {
            document.removeEventListener('keydown', escapeHandler);
            escapeHandler = null;
        }
        if (modal.parentNode) {
            modal.remove();
        }
    };
    
    escapeHandler = (e) => {
        if (e.key === 'Escape') {
            closeHandler();
        }
    };
    
    document.addEventListener('keydown', escapeHandler);
    
    // innerHTMLの代わりにcreateElementを使用（XSS対策）
    const modalContent = document.createElement('div');
    modalContent.className = 'modal-content';
    modalContent.style.maxWidth = '800px';
    
    const modalHeader = document.createElement('div');
    modalHeader.className = 'modal-header';
    
    const titleH3 = document.createElement('h3');
    titleH3.id = 'image-modal-title';
    titleH3.textContent = safeTitle;
    modalHeader.appendChild(titleH3);
    
    const closeBtn = document.createElement('button');
    closeBtn.className = 'modal-close';
    closeBtn.setAttribute('aria-label', '閉じる');
    closeBtn.title = '閉じる';
    closeBtn.textContent = '×';
    closeBtn.addEventListener('click', closeHandler);
    modalHeader.appendChild(closeBtn);
    
    modalContent.appendChild(modalHeader);
    
    const modalBody = document.createElement('div');
    modalBody.className = 'modal-body';
    
    const img = document.createElement('img');
    img.src = src; // srcは元の値を使用（URLとして有効）
    img.alt = safeTitle;
    img.style.cssText = 'width: 100%; border-radius: 8px; max-height: 70vh; object-fit: contain;';
    modalBody.appendChild(img);
    
    const captionDiv = document.createElement('div');
    captionDiv.style.cssText = 'margin-top: 10px; text-align: center; color: var(--muted); font-size: 0.9rem;';
    captionDiv.textContent = safeTitle;
    modalBody.appendChild(captionDiv);
    
    modalContent.appendChild(modalBody);
    modal.appendChild(modalContent);
    
    // モーダル背景クリックで閉じる
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            closeHandler();
        }
    });
    
    document.body.appendChild(modal);
}

/**
 * データセットモーダルを閉じる
 */
export function closeDatasetModal() {
    const modal = dom.getElement('datasetModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

/**
 * プレビューエリアを閉じる
 */
export function closePreview() {
    const previewArea = dom.getElement('dsPreviewArea');
    if (previewArea) {
        previewArea.style.display = 'none';
    }
}

