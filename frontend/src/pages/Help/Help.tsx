import React, { useState } from 'react'
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  Alert,
  AlertTitle,
  Divider,
} from '@mui/material'
import {
  ExpandMore as ExpandMoreIcon,
  Help as HelpIcon,
  VideoLibrary as VideoIcon,
  Book as BookIcon,
  Support as SupportIcon,
  BugReport as BugIcon,
  Keyboard as KeyboardIcon,
  Accessibility as AccessibilityIcon,
  Speed as SpeedIcon,
  Security as SecurityIcon,
} from '@mui/icons-material'
import { motion } from 'framer-motion'
import PageHeader from '@components/Layout/PageHeader'

const Help: React.FC = () => {
  const [expanded, setExpanded] = useState<string | false>('getting-started')

  const handleChange = (panel: string) => (event: React.SyntheticEvent, isExpanded: boolean) => {
    setExpanded(isExpanded ? panel : false)
  }

  const quickStartSteps = [
    {
      step: 1,
      title: 'データセットのダウンロード',
      description: '医療画像データセットをダウンロードします',
      icon: <BookIcon />,
    },
    {
      step: 2,
      title: 'モデルの選択',
      description: 'セグメンテーション用のAIモデルを選択します',
      icon: <SpeedIcon />,
    },
    {
      step: 3,
      title: '画像のアップロード',
      description: 'セグメンテーションしたい画像をアップロードします',
      icon: <HelpIcon />,
    },
    {
      step: 4,
      title: 'セグメンテーション実行',
      description: 'AIモデルでセグメンテーションを実行します',
      icon: <SpeedIcon />,
    },
  ]

  const faqItems = [
    {
      question: 'どのような画像形式がサポートされていますか？',
      answer: 'PNG、JPEG、DICOM、NIfTI形式の画像をサポートしています。最大ファイルサイズは16MBです。',
    },
    {
      question: 'セグメンテーションの精度を向上させるには？',
      answer: '高解像度の画像を使用し、適切な閾値を設定することで精度を向上させることができます。',
    },
    {
      question: 'カスタムモデルを使用できますか？',
      answer: 'はい、独自のモデルをアップロードして使用することができます。詳細はモデル管理ページをご確認ください。',
    },
    {
      question: '処理時間はどのくらいかかりますか？',
      answer: '画像のサイズとモデルによって異なりますが、通常2-5秒程度です。',
    },
    {
      question: '結果をエクスポートできますか？',
      answer: 'はい、PNG、JPEG、DICOM形式で結果をエクスポートできます。',
    },
  ]

  const keyboardShortcuts = [
    { keys: 'Ctrl + 1-5', description: 'ページ間の移動' },
    { keys: 'Ctrl + B', description: 'サイドバーの表示/非表示' },
    { keys: 'Ctrl + O', description: 'ファイルを開く' },
    { keys: 'Ctrl + S', description: '結果を保存' },
    { keys: 'F1', description: 'ヘルプを表示' },
    { keys: 'Escape', description: 'エラーをクリア' },
  ]

  const supportOptions = [
    {
      title: 'ドキュメント',
      description: '詳細な使用方法とAPI仕様',
      icon: <BookIcon />,
      action: () => window.open('https://docs.mediseg.ai', '_blank'),
    },
    {
      title: '動画チュートリアル',
      description: 'ステップバイステップの動画ガイド',
      icon: <VideoIcon />,
      action: () => window.open('https://youtube.com/mediseg', '_blank'),
    },
    {
      title: 'コミュニティフォーラム',
      description: 'ユーザーコミュニティでの質問と回答',
      icon: <SupportIcon />,
      action: () => window.open('https://forum.mediseg.ai', '_blank'),
    },
    {
      title: 'バグレポート',
      description: '問題の報告とフィードバック',
      icon: <BugIcon />,
      action: () => window.open('https://github.com/mediseg/issues', '_blank'),
    },
  ]

  return (
    <Box sx={{ flexGrow: 1 }}>
      <PageHeader
        title="ヘルプ & サポート"
        description="MediSeg.AIの使用方法とサポート情報"
      />

      {/* Quick Start */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, mb: 3 }}>
            クイックスタートガイド
          </Typography>
          <Grid container spacing={3}>
            {quickStartSteps.map((step, index) => (
              <Grid item xs={12} sm={6} md={3} key={index}>
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: index * 0.1 }}
                >
                  <Card
                    variant="outlined"
                    sx={{
                      height: '100%',
                      textAlign: 'center',
                      transition: 'transform 0.2s ease',
                      '&:hover': {
                        transform: 'translateY(-4px)',
                      },
                    }}
                  >
                    <CardContent>
                      <Box
                        sx={{
                          width: 60,
                          height: 60,
                          borderRadius: '50%',
                          backgroundColor: 'primary.main',
                          color: 'primary.contrastText',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          mx: 'auto',
                          mb: 2,
                        }}
                      >
                        {step.icon}
                      </Box>
                      <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                        ステップ {step.step}
                      </Typography>
                      <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 600 }}>
                        {step.title}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {step.description}
                      </Typography>
                    </CardContent>
                  </Card>
                </motion.div>
              </Grid>
            ))}
          </Grid>
        </CardContent>
      </Card>

      <Grid container spacing={3}>
        {/* FAQ */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, mb: 3 }}>
                よくある質問 (FAQ)
              </Typography>
              
              {faqItems.map((item, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: index * 0.1 }}
                >
                  <Accordion
                    expanded={expanded === `faq-${index}`}
                    onChange={handleChange(`faq-${index}`)}
                    sx={{ mb: 1 }}
                  >
                    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                      <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                        {item.question}
                      </Typography>
                    </AccordionSummary>
                    <AccordionDetails>
                      <Typography variant="body2" color="text.secondary">
                        {item.answer}
                      </Typography>
                    </AccordionDetails>
                  </Accordion>
                </motion.div>
              ))}
            </CardContent>
          </Card>
        </Grid>

        {/* Support Options */}
        <Grid item xs={12} md={4}>
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, mb: 3 }}>
                サポートオプション
              </Typography>
              
              {supportOptions.map((option, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.3, delay: index * 0.1 }}
                >
                  <Card
                    variant="outlined"
                    sx={{
                      mb: 2,
                      cursor: 'pointer',
                      transition: 'all 0.2s ease',
                      '&:hover': {
                        backgroundColor: 'action.hover',
                        transform: 'translateY(-2px)',
                      },
                    }}
                    onClick={option.action}
                  >
                    <CardContent sx={{ p: 2 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                        {option.icon}
                        <Typography variant="subtitle2" sx={{ fontWeight: 600, ml: 1 }}>
                          {option.title}
                        </Typography>
                      </Box>
                      <Typography variant="body2" color="text.secondary">
                        {option.description}
                      </Typography>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </CardContent>
          </Card>

          {/* Keyboard Shortcuts */}
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, mb: 3 }}>
                キーボードショートカット
              </Typography>
              
              <List dense>
                {keyboardShortcuts.map((shortcut, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.3, delay: index * 0.1 }}
                  >
                    <ListItem sx={{ px: 0 }}>
                      <ListItemIcon>
                        <KeyboardIcon />
                      </ListItemIcon>
                      <ListItemText
                        primary={shortcut.description}
                        secondary={
                          <Chip
                            label={shortcut.keys}
                            size="small"
                            variant="outlined"
                            sx={{ fontFamily: 'monospace', mt: 0.5 }}
                          />
                        }
                      />
                    </ListItem>
                  </motion.div>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* System Information */}
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, mb: 3 }}>
            システム情報
          </Typography>
          
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Alert severity="info">
                <AlertTitle>バージョン情報</AlertTitle>
                <Typography variant="body2">
                  MediSeg.AI v1.0.0<br />
                  最終更新: 2024年1月20日<br />
                  ビルド: web_gui.samples-real-only
                </Typography>
              </Alert>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Alert severity="success">
                <AlertTitle>システムステータス</AlertTitle>
                <Typography variant="body2">
                  すべてのシステムが正常に動作しています<br />
                  GPU: 利用可能<br />
                  メモリ: 十分な空き容量があります
                </Typography>
              </Alert>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    </Box>
  )
}

export default Help
