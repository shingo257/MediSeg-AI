import React, { useState } from 'react'
import {
  Box,
  Typography,
  Tabs,
  Tab,
  Card,
  CardContent,
  Grid,
  Switch,
  FormControlLabel,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Slider,
  Divider,
  Alert,
  Button,
  LinearProgress,
} from '@mui/material'
import {
  Settings as SettingsIcon,
  Palette as PaletteIcon,
  Notifications as NotificationsIcon,
  Security as SecurityIcon,
  Storage as StorageIcon,
  Accessibility as AccessibilityIcon,
} from '@mui/icons-material'
import { motion } from 'framer-motion'
import { useAppStore } from '@store/appStore'
import AccessibilitySettings from '@components/Accessibility/AccessibilitySettings'
import PageHeader from '@components/Layout/PageHeader'

interface TabPanelProps {
  children?: React.ReactNode
  index: number
  value: number
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`settings-tabpanel-${index}`}
      aria-labelledby={`settings-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ py: 3 }}>
          {children}
        </Box>
      )}
    </div>
  )
}

const Settings: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0)
  const {
    theme,
    setTheme,
    language,
    setLanguage,
    preferences,
    updatePreferences,
  } = useAppStore()

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue)
  }

  const settingsTabs = [
    { label: '一般', icon: <SettingsIcon /> },
    { label: 'テーマ', icon: <PaletteIcon /> },
    { label: '通知', icon: <NotificationsIcon /> },
    { label: 'アクセシビリティ', icon: <AccessibilityIcon /> },
    { label: 'セキュリティ', icon: <SecurityIcon /> },
    { label: 'ストレージ', icon: <StorageIcon /> },
  ]

  return (
    <Box sx={{ flexGrow: 1 }}>
      <PageHeader
        title="設定"
        description="アプリケーションの設定をカスタマイズします"
      />

      <Card>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs
            value={activeTab}
            onChange={handleTabChange}
            variant="scrollable"
            scrollButtons="auto"
            sx={{ px: 2 }}
          >
            {settingsTabs.map((tab, index) => (
              <Tab
                key={index}
                icon={tab.icon}
                label={tab.label}
                iconPosition="start"
                sx={{ minHeight: 64 }}
              />
            ))}
          </Tabs>
        </Box>

        {/* General Settings */}
        <TabPanel value={activeTab} index={0}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                    基本設定
                  </Typography>
                  
                  <FormControl fullWidth sx={{ mb: 3 }}>
                    <InputLabel>言語</InputLabel>
                    <Select
                      value={language}
                      onChange={(e) => setLanguage(e.target.value as 'ja' | 'en')}
                      label="言語"
                    >
                      <MenuItem value="ja">日本語</MenuItem>
                      <MenuItem value="en">English</MenuItem>
                    </Select>
                  </FormControl>

                  <FormControlLabel
                    control={
                      <Switch
                        checked={preferences.autoSave}
                        onChange={(e) => updatePreferences({ autoSave: e.target.checked })}
                        color="primary"
                      />
                    }
                    label="自動保存を有効にする"
                  />

                  <FormControlLabel
                    control={
                      <Switch
                        checked={preferences.soundEnabled}
                        onChange={(e) => updatePreferences({ soundEnabled: e.target.checked })}
                        color="primary"
                      />
                    }
                    label="サウンドを有効にする"
                  />
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                    ワークスペース
                  </Typography>
                  
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    最近使用したファイル
                  </Typography>
                  
                  <Alert severity="info" sx={{ mb: 2 }}>
                    最近使用したファイルはありません
                  </Alert>

                  <Button variant="outlined" size="small">
                    履歴をクリア
                  </Button>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </TabPanel>

        {/* Theme Settings */}
        <TabPanel value={activeTab} index={1}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                    テーマ設定
                  </Typography>
                  
                  <FormControl fullWidth sx={{ mb: 3 }}>
                    <InputLabel>テーマ</InputLabel>
                    <Select
                      value={theme}
                      onChange={(e) => setTheme(e.target.value as 'light' | 'dark' | 'auto')}
                      label="テーマ"
                    >
                      <MenuItem value="light">ライト</MenuItem>
                      <MenuItem value="dark">ダーク</MenuItem>
                      <MenuItem value="auto">システム設定に従う</MenuItem>
                    </Select>
                  </FormControl>

                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    カスタムカラー（開発中）
                  </Typography>
                  <Slider
                    defaultValue={30}
                    disabled
                    sx={{ mb: 2 }}
                  />
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                    プレビュー
                  </Typography>
                  
                  <Box
                    sx={{
                      p: 3,
                      backgroundColor: theme === 'dark' ? '#1a1a1a' : '#f5f5f5',
                      borderRadius: 2,
                      border: '1px solid',
                      borderColor: 'divider',
                    }}
                  >
                    <Typography variant="h6" gutterBottom>
                      サンプルテキスト
                    </Typography>
                    <Typography variant="body2" color="text.secondary" paragraph>
                      これはテーマのプレビューです。設定を変更すると、
                      アプリケーション全体に反映されます。
                    </Typography>
                    <Button variant="contained" size="small">
                      サンプルボタン
                    </Button>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </TabPanel>

        {/* Notification Settings */}
        <TabPanel value={activeTab} index={2}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                    通知設定
                  </Typography>
                  
                  <FormControlLabel
                    control={
                      <Switch
                        checked={preferences.notifications}
                        onChange={(e) => updatePreferences({ notifications: e.target.checked })}
                        color="primary"
                      />
                    }
                    label="通知を有効にする"
                  />

                  <Divider sx={{ my: 2 }} />

                  <Typography variant="subtitle2" gutterBottom>
                    通知の種類
                  </Typography>
                  
                  <FormControlLabel
                    control={<Switch defaultChecked color="primary" />}
                    label="処理完了通知"
                  />
                  
                  <FormControlLabel
                    control={<Switch defaultChecked color="primary" />}
                    label="エラー通知"
                  />
                  
                  <FormControlLabel
                    control={<Switch color="primary" />}
                    label="システム更新通知"
                  />
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                    通知のテスト
                  </Typography>
                  
                  <Typography variant="body2" color="text.secondary" paragraph>
                    通知設定をテストできます
                  </Typography>
                  
                  <Button variant="outlined" size="small" sx={{ mr: 1 }}>
                    成功通知
                  </Button>
                  <Button variant="outlined" size="small" sx={{ mr: 1 }}>
                    エラー通知
                  </Button>
                  <Button variant="outlined" size="small">
                    情報通知
                  </Button>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </TabPanel>

        {/* Accessibility Settings */}
        <TabPanel value={activeTab} index={3}>
          <AccessibilitySettings />
        </TabPanel>

        {/* Security Settings */}
        <TabPanel value={activeTab} index={4}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                    セキュリティ設定
                  </Typography>
                  
                  <Alert severity="info" sx={{ mb: 2 }}>
                    セキュリティ機能は開発中です
                  </Alert>
                  
                  <FormControlLabel
                    control={<Switch disabled color="primary" />}
                    label="二要素認証"
                  />
                  
                  <FormControlLabel
                    control={<Switch disabled color="primary" />}
                    label="セッションタイムアウト"
                  />
                  
                  <FormControlLabel
                    control={<Switch disabled color="primary" />}
                    label="データ暗号化"
                  />
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                    プライバシー
                  </Typography>
                  
                  <FormControlLabel
                    control={<Switch defaultChecked color="primary" />}
                    label="使用統計の送信"
                  />
                  
                  <FormControlLabel
                    control={<Switch defaultChecked color="primary" />}
                    label="エラーレポートの送信"
                  />
                  
                  <FormControlLabel
                    control={<Switch color="primary" />}
                    label="マーケティング通知"
                  />
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </TabPanel>

        {/* Storage Settings */}
        <TabPanel value={activeTab} index={5}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                    ストレージ管理
                  </Typography>
                  
                  <Typography variant="body2" color="text.secondary" paragraph>
                    使用中のストレージ容量
                  </Typography>
                  
                  <Box sx={{ mb: 2 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="body2">データセット</Typography>
                      <Typography variant="body2">2.3 GB</Typography>
                    </Box>
                    <LinearProgress variant="determinate" value={60} sx={{ mb: 2 }} />
                  </Box>
                  
                  <Box sx={{ mb: 2 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="body2">モデル</Typography>
                      <Typography variant="body2">1.1 GB</Typography>
                    </Box>
                    <LinearProgress variant="determinate" value={30} sx={{ mb: 2 }} />
                  </Box>
                  
                  <Box sx={{ mb: 2 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="body2">キャッシュ</Typography>
                      <Typography variant="body2">0.3 GB</Typography>
                    </Box>
                    <LinearProgress variant="determinate" value={10} />
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                    クリーンアップ
                  </Typography>
                  
                  <Typography variant="body2" color="text.secondary" paragraph>
                    不要なファイルを削除してストレージを解放できます
                  </Typography>
                  
                  <Button variant="outlined" size="small" sx={{ mr: 1, mb: 1 }}>
                    キャッシュをクリア
                  </Button>
                  <Button variant="outlined" size="small" sx={{ mr: 1, mb: 1 }}>
                    一時ファイルを削除
                  </Button>
                  <Button variant="outlined" size="small" sx={{ mb: 1 }}>
                    ログファイルを削除
                  </Button>
                  
                  <Divider sx={{ my: 2 }} />
                  
                  <Button variant="contained" color="error" size="small">
                    すべてのデータをリセット
                  </Button>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </TabPanel>
      </Card>
    </Box>
  )
}

export default Settings
