import { createTheme, PaletteMode, ThemeOptions } from '@mui/material/styles'

const getPalette = (mode: PaletteMode, highContrast: boolean) => {
  const isDark = mode === 'dark'
  const bgDefault = isDark ? '#0a0a0a' : '#f5f5f5'
  const bgPaper = isDark ? '#1a1a1a' : '#ffffff'
  const textPrimary = isDark ? '#ffffff' : '#1a1a1a'
  const textSecondary = isDark ? '#b0b0b0' : '#64748b'
  const divider = isDark ? '#333' : 'rgba(0,0,0,0.12)'

  if (highContrast) {
    return {
      mode,
      primary: {
        main: '#1565c0',
        light: '#1976d2',
        dark: '#0d47a1',
      },
      secondary: {
        main: '#9a0036',
        light: '#dc004e',
        dark: '#6a0026',
      },
      background: {
        default: isDark ? '#000000' : '#ffffff',
        paper: isDark ? '#0d0d0d' : '#fafafa',
      },
      text: {
        primary: isDark ? '#ffffff' : '#000000',
        secondary: isDark ? '#e0e0e0' : '#424242',
      },
      divider: isDark ? '#555' : 'rgba(0,0,0,0.2)',
    }
  }

  return {
    mode,
    primary: {
      main: '#1976d2',
      light: '#42a5f5',
      dark: '#1565c0',
    },
    secondary: {
      main: '#dc004e',
      light: '#ff5983',
      dark: '#9a0036',
    },
    background: {
      default: bgDefault,
      paper: bgPaper,
    },
    text: {
      primary: textPrimary,
      secondary: textSecondary,
    },
    divider,
  }
}

export function createAppTheme(mode: PaletteMode, highContrast = false): ReturnType<typeof createTheme> {
  const palette = getPalette(mode, highContrast) as ThemeOptions['palette']
  return createTheme({
    palette,
    typography: {
      fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
      h1: { fontWeight: 700, fontSize: '2.5rem' },
      h2: { fontWeight: 600, fontSize: '2rem' },
      h3: { fontWeight: 600, fontSize: '1.75rem' },
      h4: { fontWeight: 500, fontSize: '1.5rem' },
      h5: { fontWeight: 500, fontSize: '1.25rem' },
      h6: { fontWeight: 500, fontSize: '1rem' },
      body1: { lineHeight: 1.6 },
      body2: { lineHeight: 1.5 },
      caption: { fontSize: '0.8125rem' },
    },
    shape: { borderRadius: 12 },
    components: {
      MuiButton: {
        styleOverrides: {
          root: {
            textTransform: 'none',
            fontWeight: 500,
            borderRadius: 8,
          },
        },
      },
      MuiCard: {
        styleOverrides: {
          root: {
            backgroundImage: 'none',
            border: '1px solid',
            borderColor: palette?.divider ?? (mode === 'dark' ? '#333' : 'rgba(0,0,0,0.12)'),
          },
        },
      },
      MuiPaper: {
        styleOverrides: {
          root: {
            backgroundImage: 'none',
          },
        },
      },
    },
  })
}
