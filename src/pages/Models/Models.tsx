import React, { useState } from 'react'
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Chip,
  LinearProgress,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
} from '@mui/material'
import {
  Psychology as ModelIcon,
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  Download as DownloadIcon,
  Upload as UploadIcon,
  Compare as CompareIcon,
  TrendingUp as TrendingUpIcon,
  Speed as SpeedIcon,
  Memory as MemoryIcon,
  CheckCircle as CheckIcon,
  Error as ErrorIcon,
} from '@mui/icons-material'
import { motion } from 'framer-motion'

interface Model {
  id: string
  name: string
  type: string
  description: string
  accuracy: number
  speed: number
  memory: number
  parameters: string
  status: 'available' | 'training' | 'error' | 'loaded'
  trainedOn: string
  lastUpdated: string
}

const Models: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0)
  const [selectedModel, setSelectedModel] = useState<Model | null>(null)
  const [compareDialogOpen, setCompareDialogOpen] = useState(false)

  const models: Model[] = [
    {
      id: 'unet',
      name: 'U-Net',
      type: 'Encoder-Decoder',
      description: '医療画像セグメンテーションに最適化されたU-Netアーキテクチャ',
      accuracy: 94.2,
      speed: 85,
      memory: 70,
      parameters: '31.0M',
      status: 'loaded',
      trainedOn: 'BraTS2020, ISIC2018',
      lastUpdated: '2024-01-15',
    },
    {
      id: 'deeplabv3plus',
      name: 'DeepLabV3+',
      type: 'Atrous Convolution',
      description: '高精度なセグメンテーションのためのDeepLabV3+モデル',
      accuracy: 96.1,
      speed: 65,
      memory: 85,
      parameters: '59.3M',
      status: 'available',
      trainedOn: 'Pascal VOC, COCO',
      lastUpdated: '2024-01-10',
    },
    {
      id: 'custom-unet',
      name: 'Custom U-Net',
      type: 'Custom Architecture',
      description: 'カスタム設計のU-Netモデル（実験的）',
      accuracy: 92.8,
      speed: 90,
      memory: 60,
      parameters: '25.7M',
      status: 'training',
      trainedOn: 'Custom Dataset',
      lastUpdated: '2024-01-20',
    },
  ]

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'loaded': return 'success'
      case 'available': return 'primary'
      case 'training': return 'warning'
      case 'error': return 'error'
      default: return 'default'
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'loaded': return '読み込み済み'
      case 'available': return '利用可能'
      case 'training': return '訓練中'
      case 'error': return 'エラー'
      default: return '不明'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'loaded': return <CheckIcon />
      case 'available': return <ModelIcon />
      case 'training': return <LinearProgress size={16} />
      case 'error': return <ErrorIcon />
      default: return <ModelIcon />
    }
  }

  const performanceData = [
    { model: 'U-Net', dice: 0.942, iou: 0.891, accuracy: 0.956, speed: 85 },
    { model: 'DeepLabV3+', dice: 0.961, iou: 0.925, accuracy: 0.971, speed: 65 },
    { model: 'Custom U-Net', dice: 0.928, iou: 0.867, accuracy: 0.943, speed: 90 },
  ]

  return (
    <Box sx={{ flexGrow: 1 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography
          variant="h4"
          component="h1"
          gutterBottom
          sx={{
            fontWeight: 700,
            background: 'linear-gradient(135deg, #1976d2, #42a5f5)',
            backgroundClip: 'text',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
          }}
        >
          モデル管理
        </Typography>
        <Typography variant="body1" color="text.secondary">
          AIモデルの管理と性能比較
        </Typography>
      </Box>

      {/* Tabs */}
      <Box sx={{ mb: 3 }}>
        <Tabs value={activeTab} onChange={(_, value) => setActiveTab(value)}>
          <Tab label="利用可能なモデル" />
          <Tab label="性能比較" />
          <Tab label="カスタムモデル" />
        </Tabs>
      </Box>

      {/* Available Models */}
      {activeTab === 0 && (
        <Grid container spacing={3}>
          {models.map((model, index) => (
            <Grid item xs={12} sm={6} md={4} key={model.id}>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: index * 0.1 }}
              >
                <Card
                  sx={{
                    height: '100%',
                    display: 'flex',
                    flexDirection: 'column',
                    transition: 'transform 0.2s ease, box-shadow 0.2s ease',
                    '&:hover': {
                      transform: 'translateY(-4px)',
                      boxShadow: '0 8px 25px rgba(0,0,0,0.15)',
                    },
                  }}
                >
                  <CardContent sx={{ flexGrow: 1 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <ModelIcon sx={{ mr: 2, color: 'primary.main' }} />
                      <Box sx={{ flexGrow: 1 }}>
                        <Typography variant="h6" sx={{ fontWeight: 600 }}>
                          {model.name}
                        </Typography>
                        <Chip
                          label={model.type}
                          size="small"
                          variant="outlined"
                        />
                      </Box>
                    </Box>

                    <Typography variant="body2" color="text.secondary" paragraph>
                      {model.description}
                    </Typography>

                    {/* Performance Metrics */}
                    <Box sx={{ mb: 2 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                        <TrendingUpIcon sx={{ mr: 1, fontSize: 16, color: 'success.main' }} />
                        <Typography variant="body2" sx={{ flexGrow: 1 }}>
                          精度
                        </Typography>
                        <Typography variant="body2" sx={{ fontWeight: 600 }}>
                          {model.accuracy}%
                        </Typography>
                      </Box>
                      <LinearProgress
                        variant="determinate"
                        value={model.accuracy}
                        sx={{ height: 6, borderRadius: 3, mb: 1 }}
                      />

                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                        <SpeedIcon sx={{ mr: 1, fontSize: 16, color: 'info.main' }} />
                        <Typography variant="body2" sx={{ flexGrow: 1 }}>
                          速度
                        </Typography>
                        <Typography variant="body2" sx={{ fontWeight: 600 }}>
                          {model.speed}%
                        </Typography>
                      </Box>
                      <LinearProgress
                        variant="determinate"
                        value={model.speed}
                        sx={{ height: 6, borderRadius: 3, mb: 1 }}
                      />

                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                        <MemoryIcon sx={{ mr: 1, fontSize: 16, color: 'warning.main' }} />
                        <Typography variant="body2" sx={{ flexGrow: 1 }}>
                          メモリ
                        </Typography>
                        <Typography variant="body2" sx={{ fontWeight: 600 }}>
                          {model.memory}%
                        </Typography>
                      </Box>
                      <LinearProgress
                        variant="determinate"
                        value={model.memory}
                        sx={{ height: 6, borderRadius: 3 }}
                      />
                    </Box>

                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <Chip
                        icon={getStatusIcon(model.status)}
                        label={getStatusText(model.status)}
                        color={getStatusColor(model.status)}
                        size="small"
                      />
                    </Box>

                    <Typography variant="caption" color="text.secondary">
                      パラメータ数: {model.parameters} | 最終更新: {model.lastUpdated}
                    </Typography>
                  </CardContent>

                  <CardActions sx={{ p: 2, pt: 0 }}>
                    {model.status === 'available' && (
                      <Button
                        variant="contained"
                        startIcon={<PlayIcon />}
                        fullWidth
                        sx={{ mr: 1 }}
                      >
                        読み込み
                      </Button>
                    )}
                    {model.status === 'loaded' && (
                      <Button
                        variant="outlined"
                        startIcon={<StopIcon />}
                        fullWidth
                        sx={{ mr: 1 }}
                      >
                        アンロード
                      </Button>
                    )}
                    {model.status === 'training' && (
                      <Button
                        variant="outlined"
                        startIcon={<StopIcon />}
                        fullWidth
                        sx={{ mr: 1 }}
                        color="error"
                      >
                        停止
                      </Button>
                    )}
                    <Tooltip title="詳細情報">
                      <IconButton>
                        <ModelIcon />
                      </IconButton>
                    </Tooltip>
                  </CardActions>
                </Card>
              </motion.div>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Performance Comparison */}
      {activeTab === 1 && (
        <Box>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              モデル性能比較
            </Typography>
            <Button
              variant="outlined"
              startIcon={<CompareIcon />}
              onClick={() => setCompareDialogOpen(true)}
            >
              詳細比較
            </Button>
          </Box>

          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>モデル</TableCell>
                  <TableCell align="right">Dice係数</TableCell>
                  <TableCell align="right">IoU</TableCell>
                  <TableCell align="right">精度</TableCell>
                  <TableCell align="right">速度</TableCell>
                  <TableCell align="right">パラメータ数</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {performanceData.map((row, index) => (
                  <motion.tr
                    key={row.model}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.3, delay: index * 0.1 }}
                  >
                    <TableCell component="th" scope="row">
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <ModelIcon sx={{ mr: 1, color: 'primary.main' }} />
                        {row.model}
                      </Box>
                    </TableCell>
                    <TableCell align="right">
                      <Chip
                        label={(row.dice * 100).toFixed(1) + '%'}
                        color={row.dice > 0.9 ? 'success' : row.dice > 0.8 ? 'primary' : 'default'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell align="right">
                      <Chip
                        label={(row.iou * 100).toFixed(1) + '%'}
                        color={row.iou > 0.8 ? 'success' : row.iou > 0.7 ? 'primary' : 'default'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell align="right">
                      <Chip
                        label={(row.accuracy * 100).toFixed(1) + '%'}
                        color={row.accuracy > 0.95 ? 'success' : row.accuracy > 0.9 ? 'primary' : 'default'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell align="right">
                      <Chip
                        label={row.speed + '%'}
                        color={row.speed > 80 ? 'success' : row.speed > 60 ? 'primary' : 'default'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell align="right">
                      {row.model === 'U-Net' && '31.0M'}
                      {row.model === 'DeepLabV3+' && '59.3M'}
                      {row.model === 'Custom U-Net' && '25.7M'}
                    </TableCell>
                  </motion.tr>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Box>
      )}

      {/* Custom Models */}
      {activeTab === 2 && (
        <Box>
          <Alert severity="info" sx={{ mb: 3 }}>
            カスタムモデル機能は開発中です。独自のモデルをアップロードして使用できます。
          </Alert>

          <Card>
            <CardContent sx={{ textAlign: 'center', py: 8 }}>
              <ModelIcon sx={{ fontSize: 64, mb: 2, opacity: 0.5 }} />
              <Typography variant="h6" gutterBottom>
                カスタムモデル
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                独自のAIモデルをアップロードして使用できます
              </Typography>
              <Button
                variant="contained"
                startIcon={<UploadIcon />}
                size="large"
                sx={{ mr: 2 }}
              >
                モデルをアップロード
              </Button>
              <Button
                variant="outlined"
                startIcon={<DownloadIcon />}
                size="large"
              >
                テンプレートをダウンロード
              </Button>
            </CardContent>
          </Card>
        </Box>
      )}

      {/* Compare Dialog */}
      <Dialog
        open={compareDialogOpen}
        onClose={() => setCompareDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          モデル詳細比較
        </DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" paragraph>
            各モデルの詳細な性能指標と特徴を比較できます。
          </Typography>
          {/* Add detailed comparison content here */}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCompareDialogOpen(false)}>
            閉じる
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default Models
