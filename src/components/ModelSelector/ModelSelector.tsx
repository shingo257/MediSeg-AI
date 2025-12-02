import React from 'react'
import {
  Box,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Card,
  CardContent,
  Typography,
  Chip,
  LinearProgress,
  IconButton,
  Tooltip,
} from '@mui/material'
import {
  Psychology as ModelIcon,
  Speed as SpeedIcon,
  Memory as MemoryIcon,
  CheckCircle as CheckIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
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
  status: 'available' | 'loading' | 'error'
  parameters: string
  trainedOn: string
}

interface ModelSelectorProps {
  selectedModel: string
  onModelChange: (model: string) => void
}

const models: Model[] = [
  {
    id: 'U-Net',
    name: 'U-Net',
    type: 'Encoder-Decoder',
    description: '医療画像セグメンテーションに最適化されたU-Netアーキテクチャ',
    accuracy: 94.2,
    speed: 85,
    memory: 70,
    status: 'available',
    parameters: '31.0M',
    trainedOn: 'BraTS2020, ISIC2018',
  },
  {
    id: 'DeepLabV3+',
    name: 'DeepLabV3+',
    type: 'Atrous Convolution',
    description: '高精度なセグメンテーションのためのDeepLabV3+モデル',
    accuracy: 96.1,
    speed: 65,
    memory: 85,
    status: 'available',
    parameters: '59.3M',
    trainedOn: 'Pascal VOC, COCO',
  },
  {
    id: 'Custom-UNet',
    name: 'Custom U-Net',
    type: 'Custom Architecture',
    description: 'カスタム設計のU-Netモデル（実験的）',
    accuracy: 92.8,
    speed: 90,
    memory: 60,
    status: 'loading',
    parameters: '25.7M',
    trainedOn: 'Custom Dataset',
  },
]

const ModelSelector: React.FC<ModelSelectorProps> = ({ selectedModel, onModelChange }) => {
  const selectedModelData = models.find(model => model.id === selectedModel)

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'available': return 'success'
      case 'loading': return 'warning'
      case 'error': return 'error'
      default: return 'default'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'available': return <CheckIcon />
      case 'loading': return <LinearProgress size={16} />
      case 'error': return <ErrorIcon />
      default: return <InfoIcon />
    }
  }

  return (
    <Box>
      <FormControl fullWidth>
        <InputLabel>モデル</InputLabel>
        <Select
          value={selectedModel}
          onChange={(e) => onModelChange(e.target.value)}
          label="モデル"
        >
          {models.map((model) => (
            <MenuItem key={model.id} value={model.id}>
              <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                <ModelIcon sx={{ mr: 2, color: 'primary.main' }} />
                <Box sx={{ flexGrow: 1 }}>
                  <Typography variant="body1" sx={{ fontWeight: 600 }}>
                    {model.name}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {model.type}
                  </Typography>
                </Box>
                <Chip
                  icon={getStatusIcon(model.status)}
                  label={model.status === 'available' ? '利用可能' : 
                         model.status === 'loading' ? '読み込み中' : 'エラー'}
                  color={getStatusColor(model.status)}
                  size="small"
                />
              </Box>
            </MenuItem>
          ))}
        </Select>
      </FormControl>

      {selectedModelData && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          <Card sx={{ mt: 2 }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <ModelIcon sx={{ mr: 1, color: 'primary.main' }} />
                <Typography variant="h6" sx={{ fontWeight: 600 }}>
                  {selectedModelData.name}
                </Typography>
                <Chip
                  label={selectedModelData.type}
                  size="small"
                  variant="outlined"
                  sx={{ ml: 2 }}
                />
              </Box>

              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                {selectedModelData.description}
              </Typography>

              <Grid container spacing={2}>
                <Grid item xs={12} sm={4}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <SpeedIcon sx={{ mr: 1, fontSize: 16, color: 'success.main' }} />
                    <Typography variant="body2" sx={{ flexGrow: 1 }}>
                      精度
                    </Typography>
                    <Typography variant="body2" sx={{ fontWeight: 600 }}>
                      {selectedModelData.accuracy}%
                    </Typography>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={selectedModelData.accuracy}
                    sx={{ height: 6, borderRadius: 3 }}
                  />
                </Grid>

                <Grid item xs={12} sm={4}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <SpeedIcon sx={{ mr: 1, fontSize: 16, color: 'info.main' }} />
                    <Typography variant="body2" sx={{ flexGrow: 1 }}>
                      速度
                    </Typography>
                    <Typography variant="body2" sx={{ fontWeight: 600 }}>
                      {selectedModelData.speed}%
                    </Typography>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={selectedModelData.speed}
                    sx={{ height: 6, borderRadius: 3 }}
                  />
                </Grid>

                <Grid item xs={12} sm={4}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <MemoryIcon sx={{ mr: 1, fontSize: 16, color: 'warning.main' }} />
                    <Typography variant="body2" sx={{ flexGrow: 1 }}>
                      メモリ
                    </Typography>
                    <Typography variant="body2" sx={{ fontWeight: 600 }}>
                      {selectedModelData.memory}%
                    </Typography>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={selectedModelData.memory}
                    sx={{ height: 6, borderRadius: 3 }}
                  />
                </Grid>
              </Grid>

              <Box sx={{ mt: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Box>
                  <Typography variant="caption" color="text.secondary">
                    パラメータ数: {selectedModelData.parameters}
                  </Typography>
                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
                    訓練データ: {selectedModelData.trainedOn}
                  </Typography>
                </Box>
                
                <Tooltip title="モデルの詳細情報">
                  <IconButton size="small">
                    <InfoIcon />
                  </IconButton>
                </Tooltip>
              </Box>
            </CardContent>
          </Card>
        </motion.div>
      )}
    </Box>
  )
}

export default ModelSelector
