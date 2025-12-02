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
} from '@mui/material'
import {
  CloudDownload as DownloadIcon,
  Storage as StorageIcon,
  Info as InfoIcon,
  PlayArrow as PlayIcon,
  Delete as DeleteIcon,
  Refresh as RefreshIcon,
  Add as AddIcon,
} from '@mui/icons-material'
import { motion } from 'framer-motion'

interface Dataset {
  id: string
  name: string
  description: string
  category: string
  size: string
  imageCount: number
  status: 'available' | 'downloading' | 'downloaded' | 'error'
  progress: number
  icon: string
}

const Datasets: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0)
  const [selectedDataset, setSelectedDataset] = useState<Dataset | null>(null)
  const [downloadDialogOpen, setDownloadDialogOpen] = useState(false)

  const datasets: Dataset[] = [
    {
      id: 'brats2020',
      name: 'BraTS 2020',
      description: '脳腫瘍セグメンテーション用MRIデータセット',
      category: '脳',
      size: '2.1 GB',
      imageCount: 369,
      status: 'downloaded',
      progress: 100,
      icon: '🧠',
    },
    {
      id: 'isic2018',
      name: 'ISIC 2018',
      description: '皮膚病変セグメンテーション用ダーモスコピー画像',
      category: '皮膚',
      size: '1.8 GB',
      imageCount: 2594,
      status: 'downloaded',
      progress: 100,
      icon: '🩺',
    },
    {
      id: 'covid19',
      name: 'COVID-19 Radiography',
      description: 'COVID-19胸部X線画像セグメンテーション',
      category: '胸部',
      size: '1.2 GB',
      imageCount: 1200,
      status: 'downloading',
      progress: 65,
      icon: '🫁',
    },
    {
      id: 'lits',
      name: 'LiTS',
      description: '肝臓・腫瘍セグメンテーション用CT画像',
      category: '腹部',
      size: '3.5 GB',
      imageCount: 201,
      status: 'available',
      progress: 0,
      icon: '🫀',
    },
  ]

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'downloaded': return 'success'
      case 'downloading': return 'primary'
      case 'available': return 'default'
      case 'error': return 'error'
      default: return 'default'
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'downloaded': return 'ダウンロード済み'
      case 'downloading': return 'ダウンロード中'
      case 'available': return '利用可能'
      case 'error': return 'エラー'
      default: return '不明'
    }
  }

  const handleDownload = (dataset: Dataset) => {
    setSelectedDataset(dataset)
    setDownloadDialogOpen(true)
  }

  const handleConfirmDownload = () => {
    // Implement download logic
    console.log('Downloading dataset:', selectedDataset?.name)
    setDownloadDialogOpen(false)
  }

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
          データセット管理
        </Typography>
        <Typography variant="body1" color="text.secondary">
          医療画像データセットのダウンロードと管理
        </Typography>
      </Box>

      {/* Tabs */}
      <Box sx={{ mb: 3 }}>
        <Tabs value={activeTab} onChange={(_, value) => setActiveTab(value)}>
          <Tab label="利用可能なデータセット" />
          <Tab label="ダウンロード済み" />
          <Tab label="カスタムデータセット" />
        </Tabs>
      </Box>

      {/* Available Datasets */}
      {activeTab === 0 && (
        <Grid container spacing={3}>
          {datasets.map((dataset, index) => (
            <Grid item xs={12} sm={6} md={4} key={dataset.id}>
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
                      <Typography variant="h4" sx={{ mr: 2 }}>
                        {dataset.icon}
                      </Typography>
                      <Box sx={{ flexGrow: 1 }}>
                        <Typography variant="h6" sx={{ fontWeight: 600 }}>
                          {dataset.name}
                        </Typography>
                        <Chip
                          label={dataset.category}
                          size="small"
                          color="primary"
                          variant="outlined"
                        />
                      </Box>
                    </Box>

                    <Typography variant="body2" color="text.secondary" paragraph>
                      {dataset.description}
                    </Typography>

                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="body2">サイズ:</Typography>
                      <Typography variant="body2" sx={{ fontWeight: 600 }}>
                        {dataset.size}
                      </Typography>
                    </Box>

                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                      <Typography variant="body2">画像数:</Typography>
                      <Typography variant="body2" sx={{ fontWeight: 600 }}>
                        {dataset.imageCount.toLocaleString()}
                      </Typography>
                    </Box>

                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <Chip
                        label={getStatusText(dataset.status)}
                        color={getStatusColor(dataset.status)}
                        size="small"
                        sx={{ mr: 1 }}
                      />
                      {dataset.status === 'downloading' && (
                        <Typography variant="caption" color="text.secondary">
                          {dataset.progress}%
                        </Typography>
                      )}
                    </Box>

                    {dataset.status === 'downloading' && (
                      <LinearProgress
                        variant="determinate"
                        value={dataset.progress}
                        sx={{ mb: 2 }}
                      />
                    )}
                  </CardContent>

                  <CardActions sx={{ p: 2, pt: 0 }}>
                    <Button
                      variant="contained"
                      startIcon={<DownloadIcon />}
                      onClick={() => handleDownload(dataset)}
                      disabled={dataset.status === 'downloading'}
                      fullWidth
                    >
                      {dataset.status === 'downloaded' ? '再ダウンロード' : 'ダウンロード'}
                    </Button>
                    <Tooltip title="詳細情報">
                      <IconButton>
                        <InfoIcon />
                      </IconButton>
                    </Tooltip>
                  </CardActions>
                </Card>
              </motion.div>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Downloaded Datasets */}
      {activeTab === 1 && (
        <Grid container spacing={3}>
          {datasets.filter(d => d.status === 'downloaded').map((dataset, index) => (
            <Grid item xs={12} sm={6} md={4} key={dataset.id}>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: index * 0.1 }}
              >
                <Card>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <Typography variant="h4" sx={{ mr: 2 }}>
                        {dataset.icon}
                      </Typography>
                      <Box sx={{ flexGrow: 1 }}>
                        <Typography variant="h6" sx={{ fontWeight: 600 }}>
                          {dataset.name}
                        </Typography>
                        <Chip
                          label="ダウンロード済み"
                          color="success"
                          size="small"
                        />
                      </Box>
                    </Box>

                    <Typography variant="body2" color="text.secondary" paragraph>
                      {dataset.description}
                    </Typography>

                    <Box sx={{ display: 'flex', gap: 1, mt: 2 }}>
                      <Button
                        variant="outlined"
                        startIcon={<PlayIcon />}
                        size="small"
                        fullWidth
                      >
                        使用
                      </Button>
                      <Button
                        variant="outlined"
                        startIcon={<DeleteIcon />}
                        size="small"
                        color="error"
                      >
                        削除
                      </Button>
                    </Box>
                  </CardContent>
                </Card>
              </motion.div>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Custom Datasets */}
      {activeTab === 2 && (
        <Box>
          <Alert severity="info" sx={{ mb: 3 }}>
            カスタムデータセット機能は開発中です。独自のデータセットをアップロードして使用できます。
          </Alert>

          <Card>
            <CardContent sx={{ textAlign: 'center', py: 8 }}>
              <StorageIcon sx={{ fontSize: 64, mb: 2, opacity: 0.5 }} />
              <Typography variant="h6" gutterBottom>
                カスタムデータセット
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                独自の医療画像データセットをアップロードして使用できます
              </Typography>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                size="large"
              >
                データセットをアップロード
              </Button>
            </CardContent>
          </Card>
        </Box>
      )}

      {/* Download Dialog */}
      <Dialog
        open={downloadDialogOpen}
        onClose={() => setDownloadDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          データセットのダウンロード
        </DialogTitle>
        <DialogContent>
          {selectedDataset && (
            <Box>
              <Typography variant="body1" paragraph>
                <strong>{selectedDataset.name}</strong> をダウンロードしますか？
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                {selectedDataset.description}
              </Typography>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2">サイズ:</Typography>
                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                  {selectedDataset.size}
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="body2">画像数:</Typography>
                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                  {selectedDataset.imageCount.toLocaleString()}
                </Typography>
              </Box>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDownloadDialogOpen(false)}>
            キャンセル
          </Button>
          <Button
            variant="contained"
            onClick={handleConfirmDownload}
            startIcon={<DownloadIcon />}
          >
            ダウンロード開始
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default Datasets
