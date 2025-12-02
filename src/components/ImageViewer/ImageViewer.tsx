import React, { useState, useRef, useEffect } from 'react'
import {
  Box,
  Paper,
  IconButton,
  Tooltip,
  Slider,
  Typography,
  Chip,
  Grid,
} from '@mui/material'
import {
  ZoomIn as ZoomInIcon,
  ZoomOut as ZoomOutIcon,
  RotateLeft as RotateIcon,
  Fullscreen as FullscreenIcon,
  Visibility as VisibilityIcon,
  VisibilityOff as VisibilityOffIcon,
  Layers as LayersIcon,
} from '@mui/icons-material'
import { motion, AnimatePresence } from 'framer-motion'

interface ImageViewerProps {
  image: File
  result?: any
  threshold?: number
}

const ImageViewer: React.FC<ImageViewerProps> = ({ image, result, threshold = 0.5 }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [zoom, setZoom] = useState(1)
  const [rotation, setRotation] = useState(0)
  const [showOverlay, setShowOverlay] = useState(true)
  const [showMask, setShowMask] = useState(true)
  const [opacity, setOpacity] = useState(0.7)
  const [imageData, setImageData] = useState<ImageData | null>(null)

  useEffect(() => {
    const loadImage = () => {
      const canvas = canvasRef.current
      if (!canvas) return

      const ctx = canvas.getContext('2d')
      if (!ctx) return

      const img = new Image()
      img.onload = () => {
        // Set canvas size
        canvas.width = img.width
        canvas.height = img.height

        // Draw original image
        ctx.save()
        ctx.translate(canvas.width / 2, canvas.height / 2)
        ctx.rotate((rotation * Math.PI) / 180)
        ctx.scale(zoom, zoom)
        ctx.drawImage(img, -img.width / 2, -img.height / 2)
        ctx.restore()

        // Store image data
        setImageData(ctx.getImageData(0, 0, canvas.width, canvas.height))
      }

      img.src = URL.createObjectURL(image)
    }

    loadImage()
  }, [image, zoom, rotation])

  useEffect(() => {
    if (!result || !imageData) return

    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height)

    // Draw original image
    ctx.putImageData(imageData, 0, 0)

    if (showOverlay && result.prediction) {
      // Create overlay
      const overlay = ctx.createImageData(canvas.width, canvas.height)
      const data = overlay.data

      for (let i = 0; i < result.prediction.length; i++) {
        for (let j = 0; j < result.prediction[i].length; j++) {
          const idx = (i * canvas.width + j) * 4
          const value = result.prediction[i][j]
          
          if (value > threshold) {
            // Red overlay for segmentation
            data[idx] = 255 // R
            data[idx + 1] = 0 // G
            data[idx + 2] = 0 // B
            data[idx + 3] = opacity * 255 // A
          }
        }
      }

      ctx.putImageData(overlay, 0, 0)
    }

    if (showMask && result.binaryMask) {
      // Draw binary mask
      const mask = ctx.createImageData(canvas.width, canvas.height)
      const data = mask.data

      for (let i = 0; i < result.binaryMask.length; i++) {
        for (let j = 0; j < result.binaryMask[i].length; j++) {
          const idx = (i * canvas.width + j) * 4
          const value = result.binaryMask[i][j]
          
          if (value > 0) {
            // White mask
            data[idx] = 255 // R
            data[idx + 1] = 255 // G
            data[idx + 2] = 255 // B
            data[idx + 3] = opacity * 255 // A
          }
        }
      }

      ctx.putImageData(mask, 0, 0)
    }
  }, [result, threshold, showOverlay, showMask, opacity, imageData])

  const handleZoomIn = () => {
    setZoom(prev => Math.min(prev * 1.2, 5))
  }

  const handleZoomOut = () => {
    setZoom(prev => Math.max(prev / 1.2, 0.1))
  }

  const handleRotate = () => {
    setRotation(prev => (prev + 90) % 360)
  }

  const handleFullscreen = () => {
    if (canvasRef.current) {
      canvasRef.current.requestFullscreen()
    }
  }

  return (
    <Box>
      {/* Controls */}
      <Paper
        elevation={2}
        sx={{
          p: 2,
          mb: 2,
          backgroundColor: 'background.paper',
          border: '1px solid',
          borderColor: 'divider',
        }}
      >
        <Grid container spacing={2} alignItems="center">
          <Grid item>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Tooltip title="ズームイン">
                <IconButton onClick={handleZoomIn} size="small">
                  <ZoomInIcon />
                </IconButton>
              </Tooltip>
              <Tooltip title="ズームアウト">
                <IconButton onClick={handleZoomOut} size="small">
                  <ZoomOutIcon />
                </IconButton>
              </Tooltip>
              <Tooltip title="回転">
                <IconButton onClick={handleRotate} size="small">
                  <RotateIcon />
                </IconButton>
              </Tooltip>
              <Tooltip title="フルスクリーン">
                <IconButton onClick={handleFullscreen} size="small">
                  <FullscreenIcon />
                </IconButton>
              </Tooltip>
            </Box>
          </Grid>

          <Grid item>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Chip
                icon={showOverlay ? <VisibilityIcon /> : <VisibilityOffIcon />}
                label="オーバーレイ"
                color={showOverlay ? 'primary' : 'default'}
                onClick={() => setShowOverlay(!showOverlay)}
                size="small"
              />
              <Chip
                icon={showMask ? <LayersIcon /> : <VisibilityOffIcon />}
                label="マスク"
                color={showMask ? 'secondary' : 'default'}
                onClick={() => setShowMask(!showMask)}
                size="small"
              />
            </Box>
          </Grid>

          <Grid item xs>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Typography variant="body2" sx={{ minWidth: 60 }}>
                透明度:
              </Typography>
              <Slider
                value={opacity}
                onChange={(_, value) => setOpacity(value as number)}
                min={0}
                max={1}
                step={0.1}
                sx={{ flexGrow: 1 }}
              />
              <Typography variant="body2" sx={{ minWidth: 30 }}>
                {Math.round(opacity * 100)}%
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </Paper>

      {/* Canvas */}
      <Paper
        elevation={3}
        sx={{
          overflow: 'hidden',
          backgroundColor: '#000',
          border: '1px solid',
          borderColor: 'divider',
        }}
      >
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            minHeight: 400,
            backgroundColor: '#1a1a1a',
          }}
        >
          <motion.canvas
            ref={canvasRef}
            style={{
              maxWidth: '100%',
              maxHeight: '100%',
              cursor: 'grab',
            }}
            whileHover={{ scale: 1.01 }}
            transition={{ duration: 0.2 }}
          />
        </Box>
      </Paper>

      {/* Image Info */}
      <Box sx={{ mt: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="body2" color="text.secondary">
          ファイル: {image.name}
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Chip
            label={`ズーム: ${Math.round(zoom * 100)}%`}
            size="small"
            variant="outlined"
          />
          <Chip
            label={`回転: ${rotation}°`}
            size="small"
            variant="outlined"
          />
        </Box>
      </Box>
    </Box>
  )
}

export default ImageViewer
