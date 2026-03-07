import React from 'react'
import {
  Box,
  Grid,
  Typography,
  Card,
  CardContent,
  LinearProgress,
  Chip,
  Alert,
  Skeleton,
} from '@mui/material'
import {
  AutoFixHigh as SegmentationIcon,
  Storage as DatasetIcon,
  Psychology as ModelIcon,
  Analytics as AnalyticsIcon,
  TrendingUp as TrendingUpIcon,
  Speed as SpeedIcon,
  CloudDownload as DownloadIcon,
  Memory as MemoryIcon,
  Monitor as MonitorIcon,
} from '@mui/icons-material'
import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { useQuery } from 'react-query'
import PageHeader from '@components/Layout/PageHeader'

async function fetchSystemMonitoring() {
  const r = await fetch('/api/system/monitoring')
  if (!r.ok) throw new Error('Failed to fetch')
  const j = await r.json()
  if (!j.success) throw new Error(j.error || 'Failed')
  return j
}

const Dashboard: React.FC = () => {
  const navigate = useNavigate()
  const { data: systemData, isLoading: systemLoading, error: systemError } = useQuery(
    'system-monitoring',
    fetchSystemMonitoring,
    { refetchInterval: 10000 }
  )

  const stats = [
    {
      title: '処理済み画像',
      value: '1,247',
      change: '+12%',
      trend: 'up',
      icon: <SegmentationIcon />,
      color: '#1976d2',
    },
    {
      title: '利用可能データセット',
      value: '8',
      change: '+2',
      trend: 'up',
      icon: <DatasetIcon />,
      color: '#388e3c',
    },
    {
      title: 'アクティブモデル',
      value: '3',
      change: '0',
      trend: 'stable',
      icon: <ModelIcon />,
      color: '#f57c00',
    },
    {
      title: '平均精度',
      value: '94.2%',
      change: '+2.1%',
      trend: 'up',
      icon: <AnalyticsIcon />,
      color: '#7b1fa2',
    },
  ]

  const recentActivities = [
    {
      id: 1,
      type: 'segmentation',
      title: '脳腫瘍セグメンテーション完了',
      description: 'BraTS2020データセットでU-Netモデルを使用',
      time: '2分前',
      status: 'completed',
    },
    {
      id: 2,
      type: 'download',
      title: 'ISICデータセットダウンロード完了',
      description: '皮膚病変セグメンテーション用データセット',
      time: '15分前',
      status: 'completed',
    },
    {
      id: 3,
      type: 'training',
      title: 'DeepLabV3+モデル訓練中',
      description: 'Pascal VOCデータセットで訓練実行中',
      time: '1時間前',
      status: 'running',
    },
  ]

  const quickActions = [
    {
      title: '新しいセグメンテーション',
      description: '画像をアップロードしてセグメンテーションを実行',
      icon: <SegmentationIcon />,
      action: () => navigate('/segmentation'),
      color: '#1976d2',
    },
    {
      title: 'データセット管理',
      description: 'データセットのダウンロードと管理',
      icon: <DatasetIcon />,
      action: () => navigate('/datasets'),
      color: '#388e3c',
    },
    {
      title: 'モデル比較',
      description: '異なるモデルの性能を比較',
      icon: <ModelIcon />,
      action: () => navigate('/models'),
      color: '#f57c00',
    },
    {
      title: '分析レポート',
      description: '詳細な分析とレポートを表示',
      icon: <AnalyticsIcon />,
      action: () => navigate('/analytics'),
      color: '#7b1fa2',
    },
  ]

  return (
    <Box sx={{ flexGrow: 1 }}>
      <PageHeader
        title="ダッシュボード"
        description="MediSeg.AIプラットフォームの概要とクイックアクセス"
      />

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {stats.map((stat, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: index * 0.1 }}
            >
              <Card
                sx={{
                  height: '100%',
                  transition: 'box-shadow 0.2s ease',
                  '&:hover': {
                    boxShadow: 2,
                  },
                }}
              >
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <Box
                      sx={{
                        p: 1,
                        borderRadius: 2,
                        backgroundColor: `${stat.color}20`,
                        color: stat.color,
                        mr: 2,
                      }}
                    >
                      {stat.icon}
                    </Box>
                    <Box sx={{ flexGrow: 1 }}>
                      <Typography variant="h4" component="div" sx={{ fontWeight: 700 }}>
                        {stat.value}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {stat.title}
                      </Typography>
                    </Box>
                  </Box>
                  
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Chip
                      label={stat.change}
                      size="small"
                      color={stat.trend === 'up' ? 'success' : stat.trend === 'down' ? 'error' : 'default'}
                      icon={stat.trend === 'up' ? <TrendingUpIcon /> : undefined}
                      sx={{ mr: 1 }}
                    />
                    <Typography variant="caption" color="text.secondary">
                      前回比
                    </Typography>
                  </Box>
                </CardContent>
              </Card>
            </motion.div>
          </Grid>
        ))}
      </Grid>

      <Grid container spacing={3}>
        {/* Quick Actions */}
        <Grid item xs={12} md={8}>
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3 }}
          >
            <Card sx={{ height: '100%', transition: 'box-shadow 0.2s ease', '&:hover': { boxShadow: 2 } }}>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                  クイックアクション
                </Typography>
                <Grid container spacing={2}>
                  {quickActions.map((action, index) => (
                    <Grid item xs={12} sm={6} key={index}>
                      <motion.div
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                      >
                        <Card
                          variant="outlined"
                          sx={{
                            cursor: 'pointer',
                            transition: 'box-shadow 0.2s ease, border-color 0.2s ease',
                            '&:hover': {
                              boxShadow: 2,
                              borderColor: action.color,
                            },
                          }}
                          onClick={action.action}
                        >
                          <CardContent sx={{ p: 2 }}>
                            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                              <Box
                                sx={{
                                  p: 1,
                                  borderRadius: 1,
                                  backgroundColor: `${action.color}20`,
                                  color: action.color,
                                  mr: 2,
                                }}
                              >
                                {action.icon}
                              </Box>
                              <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                                {action.title}
                              </Typography>
                            </Box>
                            <Typography variant="body2" color="text.secondary">
                              {action.description}
                            </Typography>
                          </CardContent>
                        </Card>
                      </motion.div>
                    </Grid>
                  ))}
                </Grid>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        {/* Recent Activities */}
        <Grid item xs={12} md={4}>
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3 }}
          >
            <Card sx={{ height: '100%', transition: 'box-shadow 0.2s ease', '&:hover': { boxShadow: 2 } }}>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                  最近のアクティビティ
                </Typography>
                
                <Box sx={{ mt: 2 }}>
                  {recentActivities.length === 0 ? (
                    <Typography variant="body2" color="text.secondary">
                      アクティビティはありません
                    </Typography>
                  ) : (
                    recentActivities.map((activity, index) => (
                    <motion.div
                      key={activity.id}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.3, delay: index * 0.1 }}
                    >
                      <Box
                        sx={{
                          p: 2,
                          mb: 2,
                          borderRadius: 2,
                          backgroundColor: 'background.default',
                          border: '1px solid',
                          borderColor: 'divider',
                        }}
                      >
                        <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 1 }}>
                          <Box
                            sx={{
                              p: 0.5,
                              borderRadius: 1,
                              backgroundColor: 'primary.main',
                              color: 'primary.contrastText',
                              mr: 2,
                              mt: 0.5,
                            }}
                          >
                            {activity.type === 'segmentation' && <SegmentationIcon fontSize="small" />}
                            {activity.type === 'download' && <DownloadIcon fontSize="small" />}
                            {activity.type === 'training' && <SpeedIcon fontSize="small" />}
                          </Box>
                          
                          <Box sx={{ flexGrow: 1 }}>
                            <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                              {activity.title}
                            </Typography>
                            <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                              {activity.description}
                            </Typography>
                            
                            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                              <Typography variant="caption" color="text.secondary">
                                {activity.time}
                              </Typography>
                              
                              <Chip
                                label={activity.status === 'completed' ? '完了' : '実行中'}
                                size="small"
                                color={activity.status === 'completed' ? 'success' : 'primary'}
                                variant="outlined"
                              />
                            </Box>
                            
                            {activity.status === 'running' && (
                              <LinearProgress sx={{ mt: 1 }} />
                            )}
                          </Box>
                        </Box>
                      </Box>
                    </motion.div>
                  ))
                  )}
                </Box>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        {/* System monitoring */}
        <Grid item xs={12}>
          <Card sx={{ transition: 'box-shadow 0.2s ease', '&:hover': { boxShadow: 2 } }}>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                システム状態
              </Typography>
              {systemLoading && (
                <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                  <Skeleton variant="rounded" width={120} height={32} />
                  <Skeleton variant="rounded" width={120} height={32} />
                </Box>
              )}
              {systemError && (
                <Alert severity="info">
                  システムメトリクスを取得できません（API に接続していない可能性があります）
                </Alert>
              )}
              {systemData && !systemError && (
                <Box sx={{ display: 'flex', gap: 3, flexWrap: 'wrap', alignItems: 'center' }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <MonitorIcon fontSize="small" color="action" />
                    <Typography variant="body2">CPU: {Number(systemData.cpu_usage ?? 0).toFixed(1)}%</Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <MemoryIcon fontSize="small" color="action" />
                    <Typography variant="body2">
                      メモリ: {Number(systemData.memory_usage ?? 0).toFixed(0)} MB
                    </Typography>
                  </Box>
                  {systemData.gpu_available && (
                    <Typography variant="body2">
                      GPU: {Number(systemData.gpu_usage ?? 0).toFixed(1)}%
                    </Typography>
                  )}
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  )
}

export default Dashboard
