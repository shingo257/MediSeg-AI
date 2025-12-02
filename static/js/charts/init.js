/**
 * 統計チャート初期化
 */
import { dom } from '../core/dom.js';
import { drawMetricsChart } from './metrics.js';
import { drawConfidenceHeatmap } from './heatmap.js';
import { drawRegionChart } from './region.js';
import { drawTimelineChart } from './timeline.js';

/**
 * 統計チャートを初期化
 */
export function initStatisticsCharts() {
    // メトリクス分布チャート
    const metricsCanvas = dom.getElement('metricsChart');
    if (metricsCanvas) {
        // キャンバスサイズを設定
        if (!metricsCanvas.width) metricsCanvas.width = metricsCanvas.offsetWidth || 300;
        if (!metricsCanvas.height) metricsCanvas.height = metricsCanvas.offsetHeight || 200;
        const metricsCtx = metricsCanvas.getContext('2d');
        drawMetricsChart(metricsCtx, metricsCanvas.width, metricsCanvas.height);
    }
    
    // 信頼度ヒートマップ
    const confidenceCanvas = dom.getElement('confidenceChart');
    if (confidenceCanvas) {
        if (!confidenceCanvas.width) confidenceCanvas.width = confidenceCanvas.offsetWidth || 300;
        if (!confidenceCanvas.height) confidenceCanvas.height = confidenceCanvas.offsetHeight || 200;
        const confidenceCtx = confidenceCanvas.getContext('2d');
        drawConfidenceHeatmap(confidenceCtx, confidenceCanvas.width, confidenceCanvas.height);
    }
    
    // 領域統計
    const regionCanvas = dom.getElement('regionChart');
    if (regionCanvas) {
        if (!regionCanvas.width) regionCanvas.width = regionCanvas.offsetWidth || 300;
        if (!regionCanvas.height) regionCanvas.height = regionCanvas.offsetHeight || 200;
        const regionCtx = regionCanvas.getContext('2d');
        drawRegionChart(regionCtx, regionCanvas.width, regionCanvas.height);
    }
    
    // 時系列変化
    const timelineCanvas = dom.getElement('timelineChart');
    if (timelineCanvas) {
        if (!timelineCanvas.width) timelineCanvas.width = timelineCanvas.offsetWidth || 300;
        if (!timelineCanvas.height) timelineCanvas.height = timelineCanvas.offsetHeight || 200;
        const timelineCtx = timelineCanvas.getContext('2d');
        drawTimelineChart(timelineCtx, timelineCanvas.width, timelineCanvas.height);
    }
}

