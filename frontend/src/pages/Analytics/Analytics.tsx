import React, { useState } from 'react'
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Tabs,
  Tab,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  useTheme,
} from '@mui/material'
import {
  Analytics as AnalyticsIcon,
  TrendingUp as TrendingUpIcon,
  Speed as SpeedIcon,
  Memory as MemoryIcon,
  Psychology as ModelIcon,
} from '@mui/icons-material'
import { motion } from 'framer-motion'
import PageHeader from '@components/Layout/PageHeader'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  AreaChart,
  Area,
} from 'recharts'
import PageHeader from '@components/Layout/PageHeader'

const Analytics: React.FC = () => {
  const theme = useTheme()
  const [activeTab, setActiveTab] = useState(0)
  const [timeRange, setTimeRange] = useState('7d')

  // 実データをAPIから取得
  // TODO: 実際のAPIエンドポイントからデータを取得する必要があります
  const [performanceData, setPerformanceData] = useState<Array<{date: string, dice: number, iou: number, accuracy: number}>>([])
  const [modelUsageData, setModelUsageData] = useState<Array<{name: string, value: number, color: string}>>([])
  const [processingTimeData, setProcessingTimeData] = useState<Array<{model: string, avgTime: number, minTime: number, maxTime: number}>>([])
  const [datasetStats, setDatasetStats] = useState<Array<{name: string, processed: number, accuracy: number, avgTime: number}>>([])
  
  // データが取得できない場合は空配列を表示
  // useEffect(() => {
  //   fetch('/api/analytics/performance')
  //     .then(res => res.json())
  //     .then(data => setPerformanceData(data))
  //     .catch(err => console.error('Failed to load performance data:', err))
  // }, [])

  const stats = [
    {
      title: '総処理数',
      value: '1,247',
      change: '+12%',
      trend: 'up',
      icon: <AnalyticsIcon />,
      color: '#1976d2',
    },
    {
      title: '平均精度',
      value: '94.2%',
      change: '+2.1%',
      trend: 'up',
      icon: <TrendingUpIcon />,
      color: '#388e3c',
    },
    {
      title: '平均処理時間',
      value: '2.3秒',
      change: '-0.5秒',
      trend: 'up',
      icon: <SpeedIcon />,
      color: '#f57c00',
    },
    {
      title: 'アクティブモデル',
      value: '3',
      change: '0',
      trend: 'stable',
      icon: <ModelIcon />,
      color: '#7b1fa2',
    },
  ]

  return (
    <Box sx={{ flexGrow: 1 }}>
      <PageHeader
        title="分析ダッシュボード"
        description="システムの使用状況とパフォーマンス分析"
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
                  '&:hover': { boxShadow: 2 },
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
                  
                  <Chip
                    label={stat.change}
                    size="small"
                    color={stat.trend === 'up' ? 'success' : stat.trend === 'down' ? 'error' : 'default'}
                    icon={stat.trend === 'up' ? <TrendingUpIcon /> : undefined}
                  />
                </CardContent>
              </Card>
            </motion.div>
          </Grid>
        ))}
      </Grid>

      {/* Time Range Selector */}
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h6" sx={{ fontWeight: 600 }}>
          パフォーマンス分析
        </Typography>
        <FormControl size="small" sx={{ minWidth: 120 }}>
          <InputLabel>期間</InputLabel>
          <Select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            label="期間"
          >
            <MenuItem value="24h">24時間</MenuItem>
            <MenuItem value="7d">7日間</MenuItem>
            <MenuItem value="30d">30日間</MenuItem>
            <MenuItem value="90d">90日間</MenuItem>
          </Select>
        </FormControl>
      </Box>

      {/* Tabs */}
      <Box sx={{ mb: 3 }}>
        <Tabs value={activeTab} onChange={(_, value) => setActiveTab(value)}>
          <Tab label="パフォーマンス" />
          <Tab label="モデル使用状況" />
          <Tab label="データセット分析" />
          <Tab label="システム監視" />
        </Tabs>
      </Box>

      {/* Performance Tab */}
      {activeTab === 0 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.3 }}
            >
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                    精度の推移
                  </Typography>
                  {performanceData.length > 0 ? (
                    <ResponsiveContainer width="100%" height={300}>
                      <LineChart data={performanceData}>
                        <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} />
                        <XAxis dataKey="date" stroke={theme.palette.text.secondary} />
                        <YAxis domain={[0.7, 1.0]} stroke={theme.palette.text.secondary} />
                        <RechartsTooltip
                          contentStyle={{
                            backgroundColor: theme.palette.background.paper,
                            border: `1px solid ${theme.palette.divider}`,
                          }}
                        />
                        <Line type="monotone" dataKey="dice" stroke={theme.palette.primary.main} strokeWidth={2} name="Dice係数" />
                        <Line type="monotone" dataKey="iou" stroke={theme.palette.success.main} strokeWidth={2} name="IoU" />
                        <Line type="monotone" dataKey="accuracy" stroke={theme.palette.warning.main} strokeWidth={2} name="精度" />
                      </LineChart>
                    </ResponsiveContainer>
                  ) : (
                    <Box sx={{ height: 300, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'text.secondary' }}>
                      <Typography>データがありません。API から取得するか、処理を実行すると表示されます。</Typography>
                    </Box>
                  )}
                </CardContent>
              </Card>
            </motion.div>
          </Grid>

          <Grid item xs={12} md={4}>
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.3 }}
            >
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                    処理時間の分布
                  </Typography>
                  {processingTimeData.length > 0 ? (
                    <ResponsiveContainer width="100%" height={300}>
                      <BarChart data={processingTimeData}>
                        <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} />
                        <XAxis dataKey="model" stroke={theme.palette.text.secondary} />
                        <YAxis stroke={theme.palette.text.secondary} />
                        <RechartsTooltip
                          contentStyle={{
                            backgroundColor: theme.palette.background.paper,
                            border: `1px solid ${theme.palette.divider}`,
                          }}
                        />
                        <Bar dataKey="avgTime" fill={theme.palette.primary.main} name="平均時間(秒)" />
                      </BarChart>
                    </ResponsiveContainer>
                  ) : (
                    <Box sx={{ height: 300, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'text.secondary' }}>
                      <Typography>データがありません</Typography>
                    </Box>
                  )}
                </CardContent>
              </Card>
            </motion.div>
          </Grid>
        </Grid>
      )}

      {/* Model Usage Tab */}
      {activeTab === 1 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
            >
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                    モデル使用率
                  </Typography>
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={modelUsageData}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {modelUsageData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <RechartsTooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </motion.div>
          </Grid>

          <Grid item xs={12} md={6}>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: 0.1 }}
            >
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                    モデル別性能
                  </Typography>
                  <ResponsiveContainer width="100%" height={300}>
                    <AreaChart data={performanceData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <RechartsTooltip />
                      <Area
                        type="monotone"
                        dataKey="dice"
                        stackId="1"
                        stroke="#1976d2"
                        fill="#1976d2"
                        name="Dice係数"
                      />
                      <Area
                        type="monotone"
                        dataKey="iou"
                        stackId="2"
                        stroke="#388e3c"
                        fill="#388e3c"
                        name="IoU"
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </motion.div>
          </Grid>
        </Grid>
      )}

      {/* Dataset Analysis Tab */}
      {activeTab === 2 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                データセット別分析
              </Typography>
              <Grid container spacing={3}>
                {datasetStats.map((dataset, index) => (
                  <Grid item xs={12} md={4} key={index}>
                    <Card variant="outlined">
                      <CardContent>
                        <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                          {dataset.name}
                        </Typography>
                        <Box sx={{ mb: 2 }}>
                          <Typography variant="body2" color="text.secondary">
                            処理済み画像数
                          </Typography>
                          <Typography variant="h5" sx={{ fontWeight: 600 }}>
                            {dataset.processed}
                          </Typography>
                        </Box>
                        <Box sx={{ mb: 2 }}>
                          <Typography variant="body2" color="text.secondary">
                            平均精度
                          </Typography>
                          <Typography variant="h6" sx={{ fontWeight: 600, color: 'success.main' }}>
                            {dataset.accuracy}%
                          </Typography>
                        </Box>
                        <Box>
                          <Typography variant="body2" color="text.secondary">
                            平均処理時間
                          </Typography>
                          <Typography variant="h6" sx={{ fontWeight: 600 }}>
                            {dataset.avgTime}秒
                          </Typography>
                        </Box>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* System Monitoring Tab */}
      {activeTab === 3 && (
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
                    CPU使用率
                  </Typography>
                  <ResponsiveContainer width="100%" height={200}>
                    <AreaChart data={performanceData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis domain={[0, 100]} />
                      <RechartsTooltip />
                      <Area
                        type="monotone"
                        dataKey="dice"
                        stroke="#1976d2"
                        fill="#1976d2"
                        name="CPU使用率(%)"
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                    メモリ使用率
                  </Typography>
                  <ResponsiveContainer width="100%" height={200}>
                    <AreaChart data={performanceData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis domain={[0, 100]} />
                      <RechartsTooltip />
                      <Area
                        type="monotone"
                        dataKey="iou"
                        stroke="#388e3c"
                        fill="#388e3c"
                        name="メモリ使用率(%)"
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </motion.div>
      )}
    </Box>
  )
}

export default Analytics
