import React from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import {
  Box,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Divider,
  Typography,
  Tooltip,
  IconButton,
  useTheme,
  useMediaQuery,
} from '@mui/material'
import {
  Dashboard as DashboardIcon,
  AutoFixHigh as SegmentationIcon,
  Storage as DatasetsIcon,
  Psychology as ModelsIcon,
  Analytics as AnalyticsIcon,
  Settings as SettingsIcon,
  Help as HelpIcon,
  ChevronLeft as ChevronLeftIcon,
  ChevronRight as ChevronRightIcon,
} from '@mui/icons-material'
import { motion } from 'framer-motion'
import { useAppStore } from '@store/appStore'

interface MenuItem {
  id: string
  label: string
  icon: React.ReactElement
  path: string
  badge?: string | number
}

const menuItems: MenuItem[] = [
  {
    id: 'dashboard',
    label: 'ダッシュボード',
    icon: <DashboardIcon />,
    path: '/dashboard',
  },
  {
    id: 'segmentation',
    label: 'セグメンテーション',
    icon: <SegmentationIcon />,
    path: '/segmentation',
  },
  {
    id: 'datasets',
    label: 'データセット',
    icon: <DatasetsIcon />,
    path: '/datasets',
  },
  {
    id: 'models',
    label: 'モデル',
    icon: <ModelsIcon />,
    path: '/models',
  },
  {
    id: 'analytics',
    label: '分析',
    icon: <AnalyticsIcon />,
    path: '/analytics',
  },
  {
    id: 'settings',
    label: '設定',
    icon: <SettingsIcon />,
    path: '/settings',
  },
  {
    id: 'help',
    label: 'ヘルプ',
    icon: <HelpIcon />,
    path: '/help',
  },
]

const Sidebar: React.FC = () => {
  const theme = useTheme()
  const isMobile = useMediaQuery(theme.breakpoints.down('md'))
  const navigate = useNavigate()
  const location = useLocation()
  const { sidebarOpen, setSidebarOpen } = useAppStore()

  const handleNavigation = (path: string) => {
    navigate(path)
    if (isMobile) {
      setSidebarOpen(false)
    }
  }

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen)
  }

  return (
    <Box
      sx={{
        width: sidebarOpen ? 280 : 80,
        height: '100vh',
        backgroundColor: 'background.paper',
        borderRight: '1px solid',
        borderColor: 'divider',
        display: 'flex',
        flexDirection: 'column',
        transition: 'width 0.3s ease',
        overflow: 'hidden',
        position: 'relative',
      }}
    >
      {/* Header */}
      <Box
        sx={{
          padding: 2,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          minHeight: 64,
        }}
      >
        {sidebarOpen && (
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3 }}
          >
            <Typography
              variant="h6"
              sx={{
                fontWeight: 700,
                color: 'primary.main',
              }}
            >
              MediSeg.AI
            </Typography>
          </motion.div>
        )}
        
        <Tooltip title={sidebarOpen ? 'サイドバーを閉じる' : 'サイドバーを開く'}>
          <IconButton onClick={toggleSidebar} size="small">
            {sidebarOpen ? <ChevronLeftIcon /> : <ChevronRightIcon />}
          </IconButton>
        </Tooltip>
      </Box>

      <Divider />

      {/* Navigation */}
      <Box sx={{ flexGrow: 1, overflow: 'auto' }}>
        <List sx={{ padding: 1 }}>
          {menuItems.map((item, index) => {
            const isActive = location.pathname === item.path
            
            return (
              <motion.div
                key={item.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3, delay: index * 0.1 }}
              >
                <ListItem disablePadding sx={{ marginBottom: 0.5 }}>
                  <Tooltip
                    title={!sidebarOpen ? item.label : ''}
                    placement="right"
                    arrow
                  >
                    <ListItemButton
                      onClick={() => handleNavigation(item.path)}
                      sx={{
                        borderRadius: 2,
                        margin: 0.5,
                        backgroundColor: isActive ? 'primary.main' : 'transparent',
                        color: isActive ? 'primary.contrastText' : 'text.primary',
                        '&:hover': {
                          backgroundColor: isActive 
                            ? 'primary.dark' 
                            : 'action.hover',
                        },
                        transition: 'all 0.2s ease',
                        minHeight: 48,
                        justifyContent: sidebarOpen ? 'flex-start' : 'center',
                      }}
                    >
                      <ListItemIcon
                        sx={{
                          color: 'inherit',
                          minWidth: sidebarOpen ? 40 : 'auto',
                          justifyContent: 'center',
                        }}
                      >
                        {item.icon}
                      </ListItemIcon>
                      
                      {sidebarOpen && (
                        <motion.div
                          initial={{ opacity: 0, width: 0 }}
                          animate={{ opacity: 1, width: 'auto' }}
                          transition={{ duration: 0.3 }}
                          style={{ overflow: 'hidden' }}
                        >
                          <ListItemText
                            primary={item.label}
                            primaryTypographyProps={{
                              fontSize: '0.875rem',
                              fontWeight: isActive ? 600 : 400,
                            }}
                          />
                        </motion.div>
                      )}
                      
                      {item.badge && sidebarOpen && (
                        <Box
                          sx={{
                            backgroundColor: 'error.main',
                            color: 'error.contrastText',
                            borderRadius: '50%',
                            minWidth: 20,
                            height: 20,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            fontSize: '0.75rem',
                            fontWeight: 600,
                            marginLeft: 1,
                          }}
                        >
                          {item.badge}
                        </Box>
                      )}
                    </ListItemButton>
                  </Tooltip>
                </ListItem>
              </motion.div>
            )
          })}
        </List>
      </Box>

      {/* Footer */}
      <Box sx={{ padding: 2 }}>
        <Divider sx={{ marginBottom: 2 }} />
        
        {sidebarOpen && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            <Typography
              variant="caption"
              color="text.secondary"
              sx={{ display: 'block', textAlign: 'center' }}
            >
              MediSeg.AI v1.0.0
            </Typography>
            <Typography
              variant="caption"
              color="text.secondary"
              sx={{ display: 'block', textAlign: 'center' }}
            >
              Medical AI Platform
            </Typography>
          </motion.div>
        )}
      </Box>
    </Box>
  )
}

export default Sidebar
