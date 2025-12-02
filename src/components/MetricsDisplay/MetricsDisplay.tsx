import React from 'react'
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  LinearProgress,
  Chip,
  IconButton,
  Tooltip,
} from '@mui/material'
import {
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Speed as SpeedIcon,
  Memory as MemoryIcon,
  CheckCircle as CheckIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
} from '@mui/icons-material'
import { motion } from 'framer-motion'

interface MetricsDisplayProps {
  metrics: {
    dice: number
    iou: number
    accuracy: number
    sensitivity: number
    specificity: number
  }
  processingTime?: number
  showDetails?: boolean
}

const MetricsDisplay: React.FC<MetricsDisplayProps> = ({ 
  metrics, 
  processingTime, 
  showDetails = true 
}) => {
  const metricsData = [
    {
      name: 'Dice係数',
      value: metrics.dice,
      description: 'セグメンテーションの重複度を測定',
      icon: <CheckIcon />,
      color: '#1976d2',
      threshold: 0.8,
    },
    {
      name: 'IoU (Intersection over Union)',
      value: metrics.iou,
      description: '交差部分と結合部分の比率',
      icon: <TrendingUpIcon />,
      color: '#388e3c',
      threshold: 0.7,
    },
    {
      name: '精度 (Accuracy)',
      value: metrics.accuracy,
      description: '全体的な予測精度',
      icon: <SpeedIcon />,
      color: '#f57c00',
      threshold: 0.9,
    },
    {
      name: '感度 (Sensitivity)',
      value: metrics.sensitivity,
      description: '真陽性率（検出率）',
      icon: <MemoryIcon />,
      color: '#7b1fa2',
      threshold: 0.8,
    },
    {
      name: '特異度 (Specificity)',
      value: metrics.specificity,
      description: '真陰性率（除外率）',
      icon: <InfoIcon />,
      color: '#d32f2f',
      threshold: 0.9,
    },
  ]

  const getPerformanceColor = (value: number, threshold: number) => {
    if (value >= threshold) return '#4caf50'
    if (value >= threshold * 0.9) return '#8bc34a'
    if (value >= threshold * 0.8) return '#ffc107'
    if (value >= threshold * 0.7) return '#ff9800'
    return '#f44336'
  }

  const getPerformanceLabel = (value: number, threshold: number) => {
    if (value >= threshold) return '優秀'
    if (value >= threshold * 0.9) return '良好'
    if (value >= threshold * 0.8) return '普通'
    if (value >= threshold * 0.7) return '改善必要'
    return '要改善'
  }

  const overallScore = (metrics.dice + metrics.iou + metrics.accuracy) / 3

  return (
    <Box>
      {/* Overall Performance */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              総合評価
            </Typography>
            <Chip
              label={getPerformanceLabel(overallScore, 0.8)}
              sx={{
                backgroundColor: getPerformanceColor(overallScore, 0.8),
                color: 'white',
                fontWeight: 600,
              }}
            />
          </Box>
          
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <Typography variant="h4" sx={{ fontWeight: 700, mr: 2 }}>
              {(overallScore * 100).toFixed(1)}%
            </Typography>
            <Box sx={{ flexGrow: 1 }}>
              <LinearProgress
                variant="determinate"
                value={overallScore * 100}
                sx={{
                  height: 12,
                  borderRadius: 6,
                  backgroundColor: 'rgba(255,255,255,0.1)',
                  '& .MuiLinearProgress-bar': {
                    backgroundColor: getPerformanceColor(overallScore, 0.8),
                  },
                }}
              />
            </Box>
          </Box>

          {processingTime && (
            <Typography variant="body2" color="text.secondary">
              処理時間: {processingTime}秒
            </Typography>
          )}
        </CardContent>
      </Card>

      {/* Individual Metrics */}
      {showDetails && (
        <Grid container spacing={2}>
          {metricsData.map((metric, index) => (
            <Grid item xs={12} sm={6} md={4} key={index}>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: index * 0.1 }}
              >
                <Card
                  sx={{
                    height: '100%',
                    background: 'linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05))',
                    backdropFilter: 'blur(10px)',
                    border: '1px solid rgba(255,255,255,0.1)',
                    transition: 'transform 0.2s ease, box-shadow 0.2s ease',
                    '&:hover': {
                      transform: 'translateY(-2px)',
                      boxShadow: '0 4px 20px rgba(0,0,0,0.1)',
                    },
                  }}
                >
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <Box
                        sx={{
                          p: 1,
                          borderRadius: 2,
                          backgroundColor: `${metric.color}20`,
                          color: metric.color,
                          mr: 2,
                        }}
                      >
                        {metric.icon}
                      </Box>
                      <Box sx={{ flexGrow: 1 }}>
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
                          backgroundColor: getPerformanceColor(metric.value, metric.threshold),
                        },
                      }}
                    />
                    
                    <Box sx={{ mt: 1, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Typography variant="caption" color="text.secondary">
                        {metric.description}
                      </Typography>
                      <Chip
                        label={getPerformanceLabel(metric.value, metric.threshold)}
                        size="small"
                        sx={{
                          backgroundColor: getPerformanceColor(metric.value, metric.threshold),
                          color: 'white',
                          fontSize: '0.7rem',
                        }}
                      />
                    </Box>
                  </CardContent>
                </Card>
              </motion.div>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Performance Insights */}
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
            パフォーマンス分析
          </Typography>
          
          <Box sx={{ space: 2 }}>
            {metrics.dice >= 0.8 && (
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <CheckIcon color="success" sx={{ mr: 1 }} />
                <Typography variant="body2">
                  セグメンテーションの品質が良好です
                </Typography>
              </Box>
            )}
            
            {metrics.sensitivity < 0.8 && (
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <ErrorIcon color="warning" sx={{ mr: 1 }} />
                <Typography variant="body2">
                  感度の改善が必要です。閾値の調整を検討してください
                </Typography>
              </Box>
            )}
            
            {metrics.specificity >= 0.9 && (
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <CheckIcon color="success" sx={{ mr: 1 }} />
                <Typography variant="body2">
                  偽陽性の検出が少なく、特異度が良好です
                </Typography>
              </Box>
            )}
            
            {overallScore >= 0.9 && (
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <TrendingUpIcon color="success" sx={{ mr: 1 }} />
                <Typography variant="body2">
                  全体的に優秀な結果が得られています
                </Typography>
              </Box>
            )}
          </Box>
        </CardContent>
      </Card>
    </Box>
  )
}

export default MetricsDisplay
