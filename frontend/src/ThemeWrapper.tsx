import React, { useMemo, useState, useEffect } from 'react'
import { ThemeProvider, useTheme } from '@mui/material/styles'
import CssBaseline from '@mui/material/CssBaseline'
import { Toaster } from 'react-hot-toast'
import { useAppStore } from '@store/appStore'
import { createAppTheme } from './theme'

function getEffectiveMode(theme: 'light' | 'dark' | 'auto', systemDark: boolean): 'light' | 'dark' {
  if (theme === 'auto') return systemDark ? 'dark' : 'light'
  return theme
}

const ToasterWithTheme: React.FC = () => {
  const theme = useTheme()
  return (
    <Toaster
      position="top-right"
      toastOptions={{
        duration: 4000,
        style: {
          background: theme.palette.background.paper,
          color: theme.palette.text.primary,
          border: `1px solid ${theme.palette.divider}`,
        },
      }}
    />
  )
}

const ThemeWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { theme: themePreference, preferences } = useAppStore()
  const [systemDark, setSystemDark] = useState(() =>
    typeof window !== 'undefined' && window.matchMedia('(prefers-color-scheme: dark)').matches
  )

  useEffect(() => {
    if (themePreference !== 'auto') return
    const mq = window.matchMedia('(prefers-color-scheme: dark)')
    setSystemDark(mq.matches)
    const handler = () => setSystemDark(mq.matches)
    mq.addEventListener('change', handler)
    return () => mq.removeEventListener('change', handler)
  }, [themePreference])

  const effectiveMode = useMemo(
    () => getEffectiveMode(themePreference, systemDark),
    [themePreference, systemDark]
  )

  const theme = useMemo(
    () => createAppTheme(effectiveMode, preferences.highContrast),
    [effectiveMode, preferences.highContrast]
  )

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <ToasterWithTheme />
      {children}
    </ThemeProvider>
  )
}

export default ThemeWrapper
