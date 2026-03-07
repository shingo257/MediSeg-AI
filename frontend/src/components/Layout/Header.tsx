import React, { useState } from 'react'
import {
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Box,
  Badge,
  Menu,
  MenuItem,
  Avatar,
  Divider,
  ListItemIcon,
  ListItemText,
  Tooltip,
  useTheme,
  useMediaQuery,
} from '@mui/material'
import {
  Menu as MenuIcon,
  Notifications as NotificationsIcon,
  Settings as SettingsIcon,
  AccountCircle as AccountIcon,
  Logout as LogoutIcon,
  Brightness4 as DarkModeIcon,
  Brightness7 as LightModeIcon,
  Language as LanguageIcon,
  Help as HelpIcon,
} from '@mui/icons-material'
import { motion } from 'framer-motion'
import { useAppStore } from '@store/appStore'

const Header: React.FC = () => {
  const theme = useTheme()
  const isMobile = useMediaQuery(theme.breakpoints.down('md'))
  const { 
    sidebarOpen, 
    setSidebarOpen, 
    theme: appTheme, 
    setTheme,
    language,
    setLanguage 
  } = useAppStore()
  
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null)
  const [notificationAnchor, setNotificationAnchor] = useState<null | HTMLElement>(null)

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget)
  }

  const handleMenuClose = () => {
    setAnchorEl(null)
  }

  const handleNotificationOpen = (event: React.MouseEvent<HTMLElement>) => {
    setNotificationAnchor(event.currentTarget)
  }

  const handleNotificationClose = () => {
    setNotificationAnchor(null)
  }

  const toggleTheme = () => {
    setTheme(appTheme === 'dark' ? 'light' : 'dark')
  }

  const toggleLanguage = () => {
    setLanguage(language === 'ja' ? 'en' : 'ja')
  }

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen)
  }

  return (
    <AppBar
      position="sticky"
      elevation={0}
      sx={{
        backgroundColor: 'background.paper',
        borderBottom: '1px solid',
        borderColor: 'divider',
        color: 'text.primary',
      }}
    >
      <Toolbar sx={{ justifyContent: 'space-between' }}>
        {/* Left side */}
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          {isMobile && (
            <IconButton
              edge="start"
              color="inherit"
              onClick={toggleSidebar}
              sx={{ marginRight: 2 }}
            >
              <MenuIcon />
            </IconButton>
          )}
          
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3 }}
          >
            <Typography
              variant="h6"
              component="div"
              sx={{
                fontWeight: 600,
                color: 'primary.main',
                display: { xs: 'none', sm: 'block' },
              }}
            >
              MediSeg.AI
            </Typography>
          </motion.div>
        </Box>

        {/* Right side */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {/* Theme toggle */}
          <Tooltip title={appTheme === 'dark' ? 'ライトモード' : 'ダークモード'}>
            <IconButton onClick={toggleTheme} size="small">
              {appTheme === 'dark' ? <LightModeIcon /> : <DarkModeIcon />}
            </IconButton>
          </Tooltip>

          {/* Language toggle */}
          <Tooltip title={language === 'ja' ? 'English' : '日本語'}>
            <IconButton onClick={toggleLanguage} size="small">
              <LanguageIcon />
            </IconButton>
          </Tooltip>

          {/* Notifications */}
          <Tooltip title="通知">
            <IconButton onClick={handleNotificationOpen} size="small">
              <Badge badgeContent={0} color="error">
                <NotificationsIcon />
              </Badge>
            </IconButton>
          </Tooltip>

          {/* User menu */}
          <Tooltip title="ユーザーメニュー">
            <IconButton onClick={handleMenuOpen} size="small">
              <Avatar sx={{ width: 32, height: 32, fontSize: '0.875rem' }}>
                U
              </Avatar>
            </IconButton>
          </Tooltip>
        </Box>
      </Toolbar>

      {/* User menu dropdown */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
        PaperProps={{
          sx: {
            mt: 1.5,
            minWidth: 200,
            backgroundColor: 'background.paper',
            border: '1px solid',
            borderColor: 'divider',
          },
        }}
        transformOrigin={{ horizontal: 'right', vertical: 'top' }}
        anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
      >
        <MenuItem onClick={handleMenuClose}>
          <ListItemIcon>
            <AccountIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>プロフィール</ListItemText>
        </MenuItem>
        
        <MenuItem onClick={handleMenuClose}>
          <ListItemIcon>
            <SettingsIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>設定</ListItemText>
        </MenuItem>
        
        <MenuItem onClick={handleMenuClose}>
          <ListItemIcon>
            <HelpIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>ヘルプ</ListItemText>
        </MenuItem>
        
        <Divider />
        
        <MenuItem onClick={handleMenuClose}>
          <ListItemIcon>
            <LogoutIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>ログアウト</ListItemText>
        </MenuItem>
      </Menu>

      {/* Notifications dropdown */}
      <Menu
        anchorEl={notificationAnchor}
        open={Boolean(notificationAnchor)}
        onClose={handleNotificationClose}
        PaperProps={{
          sx: {
            mt: 1.5,
            minWidth: 300,
            maxHeight: 400,
            backgroundColor: 'background.paper',
            border: '1px solid',
            borderColor: 'divider',
          },
        }}
        transformOrigin={{ horizontal: 'right', vertical: 'top' }}
        anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
      >
        <Box sx={{ padding: 2, borderBottom: '1px solid', borderColor: 'divider' }}>
          <Typography variant="h6" sx={{ fontWeight: 600 }}>
            通知
          </Typography>
        </Box>
        
        <MenuItem onClick={handleNotificationClose}>
          <ListItemText
            primary="新しいモデルが利用可能です"
            secondary="2時間前"
            primaryTypographyProps={{ fontSize: '0.875rem' }}
            secondaryTypographyProps={{ fontSize: '0.75rem' }}
          />
        </MenuItem>
        
        <MenuItem onClick={handleNotificationClose}>
          <ListItemText
            primary="データセットのダウンロードが完了しました"
            secondary="4時間前"
            primaryTypographyProps={{ fontSize: '0.875rem' }}
            secondaryTypographyProps={{ fontSize: '0.75rem' }}
          />
        </MenuItem>
        
        <MenuItem onClick={handleNotificationClose}>
          <ListItemText
            primary="システムメンテナンスのお知らせ"
            secondary="1日前"
            primaryTypographyProps={{ fontSize: '0.875rem' }}
            secondaryTypographyProps={{ fontSize: '0.75rem' }}
          />
        </MenuItem>
      </Menu>
    </AppBar>
  )
}

export default Header
