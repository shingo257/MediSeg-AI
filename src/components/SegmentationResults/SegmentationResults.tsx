import React, { useState } from 'react'
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Tabs,
  Tab,
  LinearProgress,
  Chip,
  IconButton,
  Tooltip,
} from '@mui/material'
import {
  TrendingUp as TrendingUpIcon,
  Speed as SpeedIcon,
  CheckCircle as CheckIcon,
  Error as ErrorIcon,
  Download as DownloadIcon,
  Share as ShareIcon,
} from '@mui/icons-material'
import { motion } from 'framer-motion'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, BarChart, Bar } from 'recharts'

interface SegmentationResultsProps {
  result: {
    prediction: number[][]
    binaryMask: number[][]
    metrics: {
      dice: number
      iou: number
      accuracy: number
      sensitivity: number
      specificity: number
    }
    processingTime: number
  }
}

const SegmentationResults: React.FC<SegmentationResultsProps> = ({ result }) => {
  const [activeTab, setActiveTab] = useState(0)

  const metricsData = [
    { name: 'Dice係数', value: result.metrics.dice, color: '#1976d2' },
    { name: 'IoU', value: result.metrics.iou, color: '#388e3c' },
    { name: '精度', value: result.metrics.accuracy, color: '#f57c00' },
    { name: '感度', value: result.metrics.sensitivity, color: '#7b1fa2' },
    { name: '特異度', value: result.metrics.specificity, color: '#d32f2f' },
  ]

  const performanceData = [
    { name: '前処理', time: 0.3, percentage: 13 },
    { name: '推論', time: 1.5, percentage: 65 },
    { name: '後処理', time: 0.5, percentage: 22 },
  ]

  // 実データから信頼度データを取得
  // TODO: 実際のセグメンテーション結果から信頼度データを取得する必要があります
  const confidenceData = props.result?.confidenceData || []

  const getPerformanceColor = (value: number) => {
    if (value >= 0.9) return '#4caf50'
    if (value >= 0.8) return '#8bc34a'
    if (value >= 0.7) return '#ffc107'
    if (value >= 0.6) return '#ff9800'
    return '#f44336'
  }

  const getPerformanceLabel = (value: number) => {
    if (value >= 0.9) return '優秀'
    if (value >= 0.8) return '良好'
    if (value >= 0.7) return '普通'
    if (value >= 0.6) return '改善必要'
    return '要改善'
  }

  return (
    <Box>
      <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
        セグメンテーション結果
      </Typography>

      <Tabs
        value={activeTab}
        onChange={(_, value) => setActiveTab(value)}
        sx={{ mb: 3 }}
      >
        <Tab label="メトリクス" />
        <Tab label="パフォーマンス" />
        <Tab label="詳細分析" />
      </Tabs>

      {/* Metrics Tab */}
      {activeTab === 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          <Grid container spacing={3}>
            {metricsData.map((metric, index) => (
              <Grid item xs={12} sm={6} md={4} key={index}>
                <Card
                  sx={{
                    background: 'linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05))',
                    backdropFilter: 'blur(10px)',
                    border: '1px solid rgba(255,255,255,0.1)',
                  }}
                >
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <Box
                        sx={{
                          width: 40,
                          height: 40,
                          borderRadius: '50%',
                          backgroundColor: `${metric.color}20`,
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          mr: 2,
                        }}
                      >
                        <TrendingUpIcon sx={{ color: metric.color }} />
                      </Box>
                      <Box>
                        <Typography variant="h6" sx={{ fontWeight: 600 }}>
                          {(metric.value * 100).toFixed(1)}%
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {metric.name}
                        </Typography>
                      </Box>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={metric.value * 100}
                      sx={{
                        height: 8,
                        borderRadius: 4,
                        backgroundColor: 'rgba(255,255,255,0.1)',
                        '& .MuiLinearProgress-bar': {
                          backgroundColor: metric.color,
                        },
                      }}
                    />
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>

          {/* Overall Performance */}
          <Card sx={{ mt: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                総合評価
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                <Chip
                  label={getPerformanceLabel(result.metrics.dice)}
                  sx={{
                    backgroundColor: getPerformanceColor(result.metrics.dice),
                    color: 'white',
                    fontWeight: 600,
                  }}
                />
                <Typography variant="body2" color="text.secondary">
                  処理時間: {result.processingTime}秒
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', gap: 1 }}>
                <Tooltip title="結果をダウンロード">
                  <IconButton color="primary">
                    <DownloadIcon />
                  </IconButton>
                </Tooltip>
                <Tooltip title="結果を共有">
                  <IconButton color="primary">
                    <ShareIcon />
                  </IconButton>
                </Tooltip>
              </Box>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Performance Tab */}
      {activeTab === 1 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                    処理時間の内訳
                  </Typography>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={performanceData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" />
                      <YAxis />
                      <RechartsTooltip />
                      <Bar dataKey="time" fill="#1976d2" />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                    信頼度分布
                  </Typography>
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={confidenceData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="x" />
                      <YAxis domain={[0, 1]} />
                      <RechartsTooltip />
                      <Line
                        type="monotone"
                        dataKey="confidence"
                        stroke="#42a5f5"
                        strokeWidth={2}
                        dot={{ fill: '#1976d2', strokeWidth: 2, r: 4 }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </motion.div>
      )}

      {/* Detailed Analysis Tab */}
      {activeTab === 2 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                    品質指標
                  </Typography>
                  <Box sx={{ space: 2 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="body2">境界の精度</Typography>
                      <Typography variant="body2" sx={{ fontWeight: 600 }}>
                        {(result.metrics.dice * 100).toFixed(1)}%
                      </Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={result.metrics.dice * 100}
                      sx={{ mb: 2 }}
                    />

                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="body2">領域の一貫性</Typography>
                      <Typography variant="body2" sx={{ fontWeight: 600 }}>
                        {(result.metrics.iou * 100).toFixed(1)}%
                      </Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={result.metrics.iou * 100}
                      sx={{ mb: 2 }}
                    />

                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="body2">全体的な精度</Typography>
                      <Typography variant="body2" sx={{ fontWeight: 600 }}>
                        {(result.metrics.accuracy * 100).toFixed(1)}%
                      </Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={result.metrics.accuracy * 100}
                    />
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                    推奨事項
                  </Typography>
                  <Box sx={{ space: 2 }}>
                    {result.metrics.dice < 0.8 && (
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                        <ErrorIcon color="warning" sx={{ mr: 1 }} />
                        <Typography variant="body2">
                          閾値の調整を検討してください
                        </Typography>
                      </Box>
                    )}
                    
                    {result.metrics.sensitivity < 0.8 && (
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                        <ErrorIcon color="warning" sx={{ mr: 1 }} />
                        <Typography variant="body2">
                          感度の改善が必要です
                        </Typography>
                      </Box>
                    )}

                    {result.metrics.dice >= 0.8 && (
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                        <CheckIcon color="success" sx={{ mr: 1 }} />
                        <Typography variant="body2">
                          良好な結果が得られています
                        </Typography>
                      </Box>
                    )}

                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <SpeedIcon color="info" sx={{ mr: 1 }} />
                      <Typography variant="body2">
                        処理時間: {result.processingTime}秒
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </motion.div>
      )}
    </Box>
  )
}

export default SegmentationResults
