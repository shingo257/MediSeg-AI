import React from 'react'
import {
  Box,
  Card,
  CardContent,
  Typography,
  Switch,
  FormControlLabel,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Divider,
  Alert,
  AlertTitle,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
} from '@mui/material'
import {
  Accessibility as AccessibilityIcon,
  Visibility as VisibilityIcon,
  VisibilityOff as VisibilityOffIcon,
  Speed as SpeedIcon,
  TextFields as TextFieldsIcon,
  Language as LanguageIcon,
  Keyboard as KeyboardIcon,
  ScreenReader as ScreenReaderIcon,
} from '@mui/icons-material'
import { motion } from 'framer-motion'
import { useAccessibility } from './AccessibilityProvider'

const AccessibilitySettings: React.FC = () => {
  const {
    highContrast,
    setHighContrast,
    reducedMotion,
    setReducedMotion,
    fontSize,
    setFontSize,
    showFocusIndicators,
    language,
    setLanguage,
  } = useAccessibility()

  const accessibilityFeatures = [
    {
      icon: <VisibilityIcon />,
      title: '高コントラストモード',
      description: '背景と文字のコントラストを高くして視認性を向上',
      enabled: highContrast,
      onToggle: setHighContrast,
    },
    {
      icon: <SpeedIcon />,
      title: 'アニメーション軽減',
      description: 'アニメーションやトランジションを最小限に抑制',
      enabled: reducedMotion,
      onToggle: setReducedMotion,
    },
    {
      icon: <TextFieldsIcon />,
      title: 'フォントサイズ調整',
      description: 'テキストのサイズを調整して読みやすさを向上',
      enabled: true,
      onToggle: () => {},
    },
    {
      icon: <KeyboardIcon />,
      title: 'フォーカス表示',
      description: 'キーボードナビゲーション時のフォーカス表示を強化',
      enabled: showFocusIndicators,
      onToggle: () => {},
    },
  ]

  const keyboardShortcuts = [
    { keys: 'Ctrl + 1-5', description: 'ページ間の移動' },
    { keys: 'Ctrl + B', description: 'サイドバーの表示/非表示' },
    { keys: 'Ctrl + O', description: 'ファイルを開く' },
    { keys: 'Ctrl + S', description: '結果を保存' },
    { keys: 'F1 または Shift + ?', description: 'ヘルプを表示' },
    { keys: 'Escape', description: 'エラーをクリア' },
  ]

  return (
    <Box>
      <Typography variant="h5" gutterBottom sx={{ fontWeight: 600, mb: 3 }}>
        アクセシビリティ設定
      </Typography>

      {/* Accessibility Features */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
            <AccessibilityIcon sx={{ mr: 2, color: 'primary.main' }} />
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              アクセシビリティ機能
            </Typography>
          </Box>

          <List>
            {accessibilityFeatures.map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3, delay: index * 0.1 }}
              >
                <ListItem sx={{ px: 0 }}>
                  <ListItemIcon>
                    {feature.icon}
                  </ListItemIcon>
                  <ListItemText
                    primary={feature.title}
                    secondary={feature.description}
                    primaryTypographyProps={{ fontWeight: 500 }}
                  />
                  {feature.title === 'フォントサイズ調整' ? (
                    <FormControl size="small" sx={{ minWidth: 120 }}>
                      <Select
                        value={fontSize}
                        onChange={(e) => setFontSize(e.target.value as 'small' | 'medium' | 'large')}
                      >
                        <MenuItem value="small">小</MenuItem>
                        <MenuItem value="medium">中</MenuItem>
                        <MenuItem value="large">大</MenuItem>
                      </Select>
                    </FormControl>
                  ) : (
                    <Switch
                      checked={feature.enabled}
                      onChange={(e) => feature.onToggle(e.target.checked)}
                      color="primary"
                    />
                  )}
                </ListItem>
              </motion.div>
            ))}
          </List>
        </CardContent>
      </Card>

      {/* Language Settings */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <LanguageIcon sx={{ mr: 2, color: 'primary.main' }} />
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              言語設定
            </Typography>
          </Box>

          <FormControl fullWidth>
            <InputLabel>表示言語</InputLabel>
            <Select
              value={language}
              onChange={(e) => setLanguage(e.target.value as 'ja' | 'en')}
              label="表示言語"
            >
              <MenuItem value="ja">日本語</MenuItem>
              <MenuItem value="en">English</MenuItem>
            </Select>
          </FormControl>
        </CardContent>
      </Card>

      {/* Keyboard Shortcuts */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <KeyboardIcon sx={{ mr: 2, color: 'primary.main' }} />
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              キーボードショートカット
            </Typography>
          </Box>

          <List>
            {keyboardShortcuts.map((shortcut, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3, delay: index * 0.1 }}
              >
                <ListItem sx={{ px: 0 }}>
                  <ListItemText
                    primary={shortcut.description}
                    secondary={shortcut.keys}
                  />
                  <Chip
                    label={shortcut.keys}
                    size="small"
                    variant="outlined"
                    sx={{ fontFamily: 'monospace' }}
                  />
                </ListItem>
              </motion.div>
            ))}
          </List>
        </CardContent>
      </Card>

      {/* Accessibility Information */}
      <Alert severity="info" sx={{ mb: 3 }}>
        <AlertTitle>アクセシビリティについて</AlertTitle>
        MediSeg.AIは、すべてのユーザーが利用できるよう設計されています。
        スクリーンリーダー、キーボードナビゲーション、高コントラスト表示など、
        様々なアクセシビリティ機能をサポートしています。
      </Alert>

      {/* Screen Reader Support */}
      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <ScreenReaderIcon sx={{ mr: 2, color: 'primary.main' }} />
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              スクリーンリーダーサポート
            </Typography>
          </Box>

          <Typography variant="body2" color="text.secondary" paragraph>
            MediSeg.AIは以下のスクリーンリーダーと互換性があります：
          </Typography>

          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            <Chip label="NVDA" color="primary" variant="outlined" />
            <Chip label="JAWS" color="primary" variant="outlined" />
            <Chip label="VoiceOver" color="primary" variant="outlined" />
            <Chip label="TalkBack" color="primary" variant="outlined" />
          </Box>

          <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
            すべての画像には適切なalt属性が設定され、
            セグメンテーション結果は音声で読み上げられます。
          </Typography>
        </CardContent>
      </Card>
    </Box>
  )
}

export default AccessibilitySettings
