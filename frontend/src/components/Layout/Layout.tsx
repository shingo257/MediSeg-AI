import React, { useState, useEffect } from 'react'
import { Box, useMediaQuery, useTheme } from '@mui/material'
import { motion, AnimatePresence } from 'framer-motion'
import Sidebar from './Sidebar'
import Header from './Header'
import { useAppStore } from '@store/appStore'

interface LayoutProps {
  children: React.ReactNode
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const theme = useTheme()
  const isMobile = useMediaQuery(theme.breakpoints.down('md'))
  const { sidebarOpen, setSidebarOpen } = useAppStore()
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
    // Auto-close sidebar on mobile
    if (isMobile) {
      setSidebarOpen(false)
    }
  }, [isMobile, setSidebarOpen])

  if (!mounted) {
    return <Box>{children}</Box>
  }

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      {/* Sidebar */}
      <AnimatePresence>
        {(sidebarOpen || !isMobile) && (
          <motion.div
            initial={{ x: -300, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: -300, opacity: 0 }}
            transition={{ duration: 0.3, ease: 'easeInOut' }}
            style={{
              position: isMobile ? 'fixed' : 'relative',
              zIndex: isMobile ? 1300 : 'auto',
              height: isMobile ? '100vh' : 'auto',
            }}
          >
            <Sidebar />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main content area */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          display: 'flex',
          flexDirection: 'column',
          minHeight: '100vh',
          transition: 'margin-left 0.3s ease',
          marginLeft: isMobile ? 0 : (sidebarOpen ? '280px' : '80px'),
        }}
      >
        {/* Header */}
        <Header />

        {/* Page content */}
        <Box
          component="div"
          sx={{
            flexGrow: 1,
            padding: { xs: 2, sm: 3 },
            paddingTop: { xs: 1, sm: 2 },
            overflow: 'auto',
          }}
        >
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            {children}
          </motion.div>
        </Box>
      </Box>

      {/* Mobile overlay */}
      {isMobile && sidebarOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.3 }}
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.5)',
            zIndex: 1200,
          }}
          onClick={() => setSidebarOpen(false)}
        />
      )}
    </Box>
  )
}

export default Layout
