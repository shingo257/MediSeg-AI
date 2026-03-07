import React, { Suspense, lazy } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { Box, CircularProgress, useTheme } from '@mui/material'
import { motion } from 'framer-motion'
import { useAppStore } from '@store/appStore'
import Layout from '@components/Layout/Layout'
import ErrorBoundary from '@components/ErrorBoundary/ErrorBoundary'
import { AccessibilityProvider } from '@components/Accessibility/AccessibilityProvider'
import { useKeyboardShortcuts } from '@hooks/useKeyboardShortcuts'

// Lazy load pages for better performance
const Dashboard = lazy(() => import('@pages/Dashboard/Dashboard'))
const Segmentation = lazy(() => import('@pages/Segmentation/Segmentation'))
const Datasets = lazy(() => import('@pages/Datasets/Datasets'))
const Models = lazy(() => import('@pages/Models/Models'))
const Analytics = lazy(() => import('@pages/Analytics/Analytics'))
const Settings = lazy(() => import('@pages/Settings/Settings'))
const Help = lazy(() => import('@pages/Help/Help'))

// Loading component
const PageLoader = () => (
  <Box
    display="flex"
    justifyContent="center"
    alignItems="center"
    minHeight="60vh"
  >
    <motion.div
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
    >
      <CircularProgress size={60} thickness={4} />
    </motion.div>
  </Box>
)

const AppContent: React.FC = () => {
  const theme = useTheme()
  useKeyboardShortcuts()

  return (
    <Box
      sx={{
        minHeight: '100vh',
        bgcolor: 'background.default',
        transition: 'background-color 0.3s ease',
      }}
    >
      <Layout>
        <Suspense fallback={<PageLoader />}>
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/segmentation" element={<Segmentation />} />
            <Route path="/datasets" element={<Datasets />} />
            <Route path="/models" element={<Models />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="/help" element={<Help />} />
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </Suspense>
      </Layout>
    </Box>
  )
}

const App: React.FC = () => {
  return (
    <ErrorBoundary>
      <AccessibilityProvider>
        <AppContent />
      </AccessibilityProvider>
    </ErrorBoundary>
  )
}

export default App
