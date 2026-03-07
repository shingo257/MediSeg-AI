import React, { useState, useCallback } from 'react'
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Slider,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  IconButton,
  Tooltip,
  Alert,
  LinearProgress,
} from '@mui/material'
import {
  CloudUpload as UploadIcon,
  PlayArrow as PlayIcon,
  Download as DownloadIcon,
  Settings as SettingsIcon,
  ZoomIn as ZoomInIcon,
  ZoomOut as ZoomOutIcon,
  RotateLeft as RotateIcon,
  Fullscreen as FullscreenIcon,
  FileDownload as FileDownloadIcon,
  ContentCopy as ContentCopyIcon,
} from '@mui/icons-material'
import { motion, AnimatePresence } from 'framer-motion'
import { useDropzone } from 'react-dropzone'
import ImageViewer from '@components/ImageViewer/ImageViewer'
import SegmentationResults from '@components/SegmentationResults/SegmentationResults'
import ModelSelector from '@components/ModelSelector/ModelSelector'
import MetricsDisplay from '@components/MetricsDisplay/MetricsDisplay'
import PageHeader from '@components/Layout/PageHeader'

interface SegmentationState {
  image: File | null
  result: any | null
  runAt: string | null
  isProcessing: boolean
  progress: number
  error: string | null
}

const Segmentation: React.FC = () => {
  const [state, setState] = useState<SegmentationState>({
    image: null,
    result: null,
    runAt: null,
    isProcessing: false,
    progress: 0,
    error: null,
  })

  const [selectedModel, setSelectedModel] = useState('U-Net')
  const [threshold, setThreshold] = useState(0.5)
  const [showSettings, setShowSettings] = useState(false)

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0]
    if (file) {
      setState(prev => ({
        ...prev,
        image: file,
        result: null,
        error: null,
      }))
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.dcm', '.nii', '.nii.gz'],
    },
    multiple: false,
  })

  const handleProcess = async () => {
    if (!state.image) return

    setState(prev => ({
      ...prev,
      isProcessing: true,
      progress: 0,
      error: null,
    }))

    try {
      // 実際のAPIを呼び出してセグメンテーションを実行
      // TODO: 実際のAPIエンドポイントに接続する必要があります
      const formData = new FormData()
      formData.append('image', state.image)
      
      const response = await fetch('/api/segment', {
        method: 'POST',
        body: formData,
      })
      
      if (!response.ok) {
        throw new Error('セグメンテーション処理に失敗しました')
      }
      
      const result = await response.json()
      
      if (!result.success) {
        throw new Error(result.error || 'セグメンテーション処理に失敗しました')
      }

      setState(prev => ({
        ...prev,
        result: result.data,
        runAt: new Date().toISOString(),
        isProcessing: false,
        progress: 100,
      }))
    } catch (error) {
      setState(prev => ({
        ...prev,
        error: '処理中にエラーが発生しました',
        isProcessing: false,
        progress: 0,
      }))
    }
  }

  const handleDownload = () => {
    // Implement download functionality
    console.log('Downloading results...')
  }

  const runInfoText = state.runAt
    ? [
        `model: ${selectedModel}`,
        `threshold: ${threshold}`,
        `runAt: ${state.runAt}`,
        state.image ? `fileName: ${state.image.name}` : '',
      ]
        .filter(Boolean)
        .join('\n')
    : ''

  const handleCopyRunInfo = async () => {
    if (!runInfoText) return
    try {
      await navigator.clipboard.writeText(runInfoText)
      // Could use toast here
    } catch {
      // ignore
    }
  }

  const exportMetricsCsv = () => {
    if (!state.result?.metrics || !state.runAt) return
    const m = state.result.metrics
    const headers = [
      'dice',
      'iou',
      'accuracy',
      'sensitivity',
      'specificity',
      'processingTime_sec',
      'model',
      'threshold',
      'runAt',
      'fileName',
    ]
    const row = [
      m.dice,
      m.iou,
      m.accuracy,
      m.sensitivity,
      m.specificity,
      state.result.processingTime ?? '',
      selectedModel,
      threshold,
      state.runAt,
      state.image?.name ?? '',
    ].join(',')
    const csv = [headers.join(','), row].join('\n')
    const blob = new Blob(['\uFEFF' + csv], { type: 'text/csv;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `mediseg_metrics_${state.runAt.replace(/[:.]/g, '-').slice(0, 19)}.csv`
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <Box sx={{ flexGrow: 1 }}>
      <PageHeader
        title="セグメンテーション"
        description="医療画像の自動セグメンテーションを実行します"
      />

      <Grid container spacing={3}>
        {/* Left Panel - Controls */}
        <Grid item xs={12} md={4}>
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3 }}
          >
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                  画像アップロード
                </Typography>
                
                <Box
                  {...getRootProps()}
                  sx={{
                    border: '2px dashed',
                    borderColor: isDragActive ? 'primary.main' : 'divider',
                    borderRadius: 2,
                    p: 4,
                    textAlign: 'center',
                    cursor: 'pointer',
                    backgroundColor: isDragActive ? 'primary.main' : 'transparent',
                    color: isDragActive ? 'primary.contrastText' : 'text.primary',
                    transition: 'all 0.2s ease',
                    '&:hover': {
                      borderColor: 'primary.main',
                      backgroundColor: 'primary.main',
                      color: 'primary.contrastText',
                    },
                  }}
                >
                  <input {...getInputProps()} />
                  <UploadIcon sx={{ fontSize: 48, mb: 2 }} />
                  <Typography variant="body1" gutterBottom>
                    {isDragActive
                      ? 'ファイルをドロップしてください'
                      : '画像をドラッグ&ドロップまたはクリックして選択'}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    対応形式: PNG, JPG, DICOM, NIfTI
                  </Typography>
                </Box>

                {state.image && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3 }}
                  >
                    <Box sx={{ mt: 2, p: 2, backgroundColor: 'background.default', borderRadius: 1 }}>
                      <Typography variant="body2" sx={{ fontWeight: 600 }}>
                        選択されたファイル:
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {state.image.name}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {(state.image.size / 1024 / 1024).toFixed(2)} MB
                      </Typography>
                    </Box>
                  </motion.div>
                )}
              </CardContent>
            </Card>

            {/* Model Selection */}
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                  <Typography variant="h6" sx={{ fontWeight: 600 }}>
                    モデル選択
                  </Typography>
                  <IconButton
                    size="small"
                    onClick={() => setShowSettings(!showSettings)}
                  >
                    <SettingsIcon />
                  </IconButton>
                </Box>

                <ModelSelector
                  selectedModel={selectedModel}
                  onModelChange={setSelectedModel}
                />

                {showSettings && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    transition={{ duration: 0.3 }}
                  >
                    <Box sx={{ mt: 2 }}>
                      <Typography variant="body2" gutterBottom>
                        閾値: {threshold.toFixed(2)}
                      </Typography>
                      <Slider
                        value={threshold}
                        onChange={(_, value) => setThreshold(value as number)}
                        min={0}
                        max={1}
                        step={0.01}
                        marks={[
                          { value: 0, label: '0' },
                          { value: 0.5, label: '0.5' },
                          { value: 1, label: '1' },
                        ]}
                      />
                    </Box>
                  </motion.div>
                )}
              </CardContent>
            </Card>

            {/* Process Button */}
            <Card>
              <CardContent>
                <Button
                  variant="contained"
                  size="large"
                  fullWidth
                  startIcon={<PlayIcon />}
                  onClick={handleProcess}
                  disabled={!state.image || state.isProcessing}
                  sx={{ mb: 2 }}
                >
                  {state.isProcessing ? '処理中...' : 'セグメンテーション実行'}
                </Button>

                {state.isProcessing && (
                  <Box sx={{ mb: 2 }}>
                    <LinearProgress variant="determinate" value={state.progress} />
                    <Typography variant="caption" color="text.secondary" sx={{ mt: 1 }}>
                      進行状況: {state.progress}%
                    </Typography>
                  </Box>
                )}

                {state.error && (
                  <Alert severity="error" sx={{ mb: 2 }}>
                    {state.error}
                  </Alert>
                )}

                {state.result && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3 }}
                  >
                    <Button
                      variant="outlined"
                      size="large"
                      fullWidth
                      startIcon={<DownloadIcon />}
                      onClick={handleDownload}
                    >
                      結果をダウンロード
                    </Button>
                  </motion.div>
                )}
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        {/* Right Panel - Results */}
        <Grid item xs={12} md={8}>
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3 }}
          >
            {state.image ? (
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                    <Typography variant="h6" sx={{ fontWeight: 600 }}>
                      セグメンテーション結果
                    </Typography>
                    <Box>
                      <Tooltip title="ズームイン">
                        <IconButton size="small">
                          <ZoomInIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="ズームアウト">
                        <IconButton size="small">
                          <ZoomOutIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="回転">
                        <IconButton size="small">
                          <RotateIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="フルスクリーン">
                        <IconButton size="small">
                          <FullscreenIcon />
                        </IconButton>
                      </Tooltip>
                    </Box>
                  </Box>

                  <ImageViewer
                    image={state.image}
                    result={state.result}
                    threshold={threshold}
                  />

                  {state.result && (
                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.3, delay: 0.2 }}
                    >
                      <Box sx={{ mt: 3 }}>
                        {/* Run info & export */}
                        <Card variant="outlined" sx={{ mb: 2 }}>
                          <CardContent>
                            <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
                              実行情報（再現性）
                            </Typography>
                            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2, alignItems: 'center' }}>
                              <Chip size="small" label={`モデル: ${selectedModel}`} variant="outlined" />
                              <Chip size="small" label={`閾値: ${threshold}`} variant="outlined" />
                              {state.runAt && (
                                <Chip size="small" label={`実行: ${state.runAt}`} variant="outlined" sx={{ maxWidth: 280 }} />
                              )}
                              <Tooltip title="実行情報をコピー">
                                <IconButton size="small" onClick={handleCopyRunInfo} disabled={!runInfoText}>
                                  <ContentCopyIcon />
                                </IconButton>
                              </Tooltip>
                              {state.result?.metrics && (
                                <Button
                                  size="small"
                                  startIcon={<FileDownloadIcon />}
                                  onClick={exportMetricsCsv}
                                  variant="outlined"
                                >
                                  メトリクスを CSV でダウンロード
                                </Button>
                              )}
                            </Box>
                          </CardContent>
                        </Card>
                        <SegmentationResults result={state.result} />
                      </Box>
                    </motion.div>
                  )}
                </CardContent>
              </Card>
            ) : (
              <Card>
                <CardContent>
                  <Box
                    sx={{
                      textAlign: 'center',
                      py: 8,
                      color: 'text.secondary',
                    }}
                  >
                    <UploadIcon sx={{ fontSize: 64, mb: 2, opacity: 0.5 }} />
                    <Typography variant="h6" gutterBottom>
                      画像をアップロードしてください
                    </Typography>
                    <Typography variant="body2">
                      セグメンテーションを実行するには、まず画像をアップロードしてください
                    </Typography>
                  </Box>
                </CardContent>
              </Card>
            )}
          </motion.div>
        </Grid>
      </Grid>
    </Box>
  )
}

export default Segmentation
