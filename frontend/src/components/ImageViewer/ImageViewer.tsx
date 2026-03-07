import React, { useState, useRef, useEffect, useCallback } from 'react'
import {
  Box,
  Paper,
  IconButton,
  Tooltip,
  Slider,
  Typography,
  Chip,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
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
import { motion } from 'framer-motion'
import { valueToRgb } from './colormaps'

const COLORMAP_OPTIONS = [
  { value: 'red', label: 'Red' },
  { value: 'viridis', label: 'Viridis' },
  { value: 'plasma', label: 'Plasma' },
] as const

interface ImageViewerProps {
  image: File
  result?: any
  threshold?: number
  scaleLabel?: string
}

const ImageViewer: React.FC<ImageViewerProps> = ({
  image,
  result,
  threshold = 0.5,
  scaleLabel,
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const sourceDataRef = useRef<ImageData | null>(null)

  const [zoom, setZoom] = useState(1)
  const [rotation, setRotation] = useState(0)
  const [showOverlay, setShowOverlay] = useState(true)
  const [showMask, setShowMask] = useState(true)
  const [opacity, setOpacity] = useState(0.7)
  const [windowLevel, setWindowLevel] = useState(1)
  const [level, setLevel] = useState(0.5)
  const [colormap, setColormap] = useState<string>('red')
  const [pixelInfo, setPixelInfo] = useState<{ x: number; y: number; value: string } | null>(null)

  const applyWindowLevel = useCallback((data: ImageData, windowVal: number, levelVal: number): ImageData => {
    const out = new ImageData(data.width, data.height)
    const d = data.data
    const o = out.data
    const center = levelVal
    const width = Math.max(0.01, windowVal)
    for (let i = 0; i < d.length; i += 4) {
      const g = d[i] / 255
      const t = (g - center) / width + 0.5
      const v = Math.max(0, Math.min(1, t)) * 255
      o[i] = o[i + 1] = o[i + 2] = v
      o[i + 3] = d[i + 3]
    }
    return out
  }, [])

  useEffect(() => {
    const img = new Image()
    img.onload = () => {
      const canvas = document.createElement('canvas')
      canvas.width = img.width
      canvas.height = img.height
      const ctx = canvas.getContext('2d')
      if (!ctx) return
      ctx.drawImage(img, 0, 0)
      sourceDataRef.current = ctx.getImageData(0, 0, canvas.width, canvas.height)
    }
    img.src = URL.createObjectURL(image)
    return () => URL.revokeObjectURL(img.src)
  }, [image])

  useEffect(() => {
    const canvas = canvasRef.current
    const source = sourceDataRef.current
    if (!canvas || !source) return

    const w = source.width
    const h = source.height
    canvas.width = w
    canvas.height = h
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const wl = applyWindowLevel(source, windowLevel, level)
    const temp = document.createElement('canvas')
    temp.width = w
    temp.height = h
    const tctx = temp.getContext('2d')
    if (!tctx) return
    tctx.putImageData(wl, 0, 0)

    ctx.save()
    ctx.translate(w / 2, h / 2)
    ctx.rotate((rotation * Math.PI) / 180)
    ctx.scale(zoom, zoom)
    ctx.drawImage(temp, -w / 2, -h / 2)
    ctx.restore()

    if (result?.prediction && showOverlay) {
      const overlay = ctx.createImageData(w, h)
      const od = overlay.data
      const pred = result.prediction
      for (let i = 0; i < pred.length; i++) {
        for (let j = 0; j < pred[i].length; j++) {
          const idx = (i * w + j) * 4
          const value = pred[i][j]
          if (value > threshold) {
            const [r, g, b] = valueToRgb(value, colormap)
            od[idx] = r
            od[idx + 1] = g
            od[idx + 2] = b
            od[idx + 3] = opacity * 255
          }
        }
      }
      ctx.putImageData(overlay, 0, 0)
    }

    if (result?.binaryMask && showMask) {
      const mask = ctx.createImageData(w, h)
      const md = mask.data
      const bin = result.binaryMask
      for (let i = 0; i < bin.length; i++) {
        for (let j = 0; j < bin[i].length; j++) {
          const idx = (i * w + j) * 4
          if (bin[i][j] > 0) {
            md[idx] = md[idx + 1] = md[idx + 2] = 255
            md[idx + 3] = opacity * 255
          }
        }
      }
      ctx.putImageData(mask, 0, 0)
    }
  }, [image, result, threshold, showOverlay, showMask, opacity, zoom, rotation, windowLevel, level, colormap, applyWindowLevel])

  const handleZoomIn = () => setZoom(prev => Math.min(prev * 1.2, 5))
  const handleZoomOut = () => setZoom(prev => Math.max(prev / 1.2, 0.1))
  const handleRotate = () => setRotation(prev => (prev + 90) % 360)
  const handleFullscreen = () => canvasRef.current?.requestFullscreen()

  const handleCanvasMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current
    if (!canvas) return
    const rect = canvas.getBoundingClientRect()
    const scaleX = canvas.width / rect.width
    const scaleY = canvas.height / rect.height
    const x = Math.floor((e.clientX - rect.left) * scaleX)
    const y = Math.floor((e.clientY - rect.top) * scaleY)
    if (x >= 0 && x < canvas.width && y >= 0 && y < canvas.height) {
      const ctx = canvas.getContext('2d')
      if (!ctx) return
      const p = ctx.getImageData(x, y, 1, 1).data
      setPixelInfo({
        x,
        y,
        value: `R${p[0]} G${p[1]} B${p[2]}`,
      })
    } else {
      setPixelInfo(null)
    }
  }
  const handleCanvasMouseLeave = () => setPixelInfo(null)

  return (
    <Box>
      <Paper
        variant="outlined"
        sx={{
          p: 2,
          mb: 2,
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
          <Grid item xs={12} sm>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flexWrap: 'wrap' }}>
              <Typography variant="body2" sx={{ minWidth: 56 }}>
                透明度:
              </Typography>
              <Slider
                value={opacity}
                onChange={(_, value) => setOpacity(value as number)}
                min={0}
                max={1}
                step={0.1}
                sx={{ flexGrow: 1, maxWidth: 120 }}
              />
              <Typography variant="body2" sx={{ minWidth: 32 }}>
                {Math.round(opacity * 100)}%
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
            <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>
              ウィンドウ / レベル
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Slider
                value={windowLevel}
                onChange={(_, value) => setWindowLevel(value as number)}
                min={0.2}
                max={2}
                step={0.1}
                sx={{ width: 80 }}
                size="small"
              />
              <Slider
                value={level}
                onChange={(_, value) => setLevel(value as number)}
                min={0}
                max={1}
                step={0.05}
                sx={{ width: 80 }}
                size="small"
              />
            </Box>
          </Grid>
          {result?.prediction && (
            <Grid item xs={12} sm={6} md={3}>
              <FormControl size="small" fullWidth>
                <InputLabel>カラーマップ</InputLabel>
                <Select
                  value={colormap}
                  label="カラーマップ"
                  onChange={e => setColormap(e.target.value)}
                >
                  {COLORMAP_OPTIONS.map(opt => (
                    <MenuItem key={opt.value} value={opt.value}>
                      {opt.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
          )}
        </Grid>
      </Paper>

      <Paper variant="outlined" sx={{ overflow: 'hidden', border: '1px solid', borderColor: 'divider' }}>
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            minHeight: 400,
            bgcolor: 'action.hover',
          }}
        >
          <motion.canvas
            ref={canvasRef}
            onMouseMove={handleCanvasMouseMove}
            onMouseLeave={handleCanvasMouseLeave}
            style={{
              maxWidth: '100%',
              maxHeight: '70vh',
              cursor: 'crosshair',
            }}
          />
        </Box>
      </Paper>

      <Box sx={{ mt: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 1 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
          <Typography variant="body2" color="text.secondary">
            ファイル: {image.name}
          </Typography>
          {pixelInfo && (
            <Typography variant="body2" component="span" sx={{ fontVariantNumeric: 'tabular-nums' }}>
              (x: {pixelInfo.x}, y: {pixelInfo.y}) {pixelInfo.value}
            </Typography>
          )}
        </Box>
        <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
          {scaleLabel && (
            <Typography variant="caption" color="text.secondary">
              {scaleLabel}
            </Typography>
          )}
          <Chip label={`ズーム ${Math.round(zoom * 100)}%`} size="small" variant="outlined" />
          <Chip label={`回転 ${rotation}°`} size="small" variant="outlined" />
        </Box>
      </Box>
    </Box>
  )
}

export default ImageViewer
