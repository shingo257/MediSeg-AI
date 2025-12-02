import React, { createContext, useContext, useState, useEffect } from 'react'
import { useAppStore } from '@store/appStore'

interface AccessibilityContextType {
  // High contrast mode
  highContrast: boolean
  setHighContrast: (enabled: boolean) => void
  
  // Reduced motion
  reducedMotion: boolean
  setReducedMotion: (enabled: boolean) => void
  
  // Font size
  fontSize: 'small' | 'medium' | 'large'
  setFontSize: (size: 'small' | 'medium' | 'large') => void
  
  // Focus indicators
  showFocusIndicators: boolean
  setShowFocusIndicators: (enabled: boolean) => void
  
  // Screen reader announcements
  announce: (message: string) => void
  
  // Language
  language: 'ja' | 'en'
  setLanguage: (lang: 'ja' | 'en') => void
}

const AccessibilityContext = createContext<AccessibilityContextType | undefined>(undefined)

export const useAccessibility = () => {
  const context = useContext(AccessibilityContext)
  if (!context) {
    throw new Error('useAccessibility must be used within an AccessibilityProvider')
  }
  return context
}

interface AccessibilityProviderProps {
  children: React.ReactNode
}

export const AccessibilityProvider: React.FC<AccessibilityProviderProps> = ({ children }) => {
  const { preferences, updatePreferences, language, setLanguage } = useAppStore()
  const [fontSize, setFontSize] = useState<'small' | 'medium' | 'large'>('medium')

  // Apply accessibility preferences
  useEffect(() => {
    const root = document.documentElement
    
    // High contrast
    if (preferences.highContrast) {
      root.classList.add('high-contrast')
    } else {
      root.classList.remove('high-contrast')
    }
    
    // Reduced motion
    if (preferences.reducedMotion) {
      root.classList.add('reduced-motion')
    } else {
      root.classList.remove('reduced-motion')
    }
    
    // Font size
    root.style.fontSize = fontSize === 'small' ? '14px' : fontSize === 'large' ? '18px' : '16px'
  }, [preferences.highContrast, preferences.reducedMotion, fontSize])

  // Screen reader announcements
  const announce = (message: string) => {
    const announcement = document.createElement('div')
    announcement.setAttribute('aria-live', 'polite')
    announcement.setAttribute('aria-atomic', 'true')
    announcement.style.position = 'absolute'
    announcement.style.left = '-10000px'
    announcement.style.width = '1px'
    announcement.style.height = '1px'
    announcement.style.overflow = 'hidden'
    announcement.textContent = message
    
    document.body.appendChild(announcement)
    
    setTimeout(() => {
      document.body.removeChild(announcement)
    }, 1000)
  }

  const contextValue: AccessibilityContextType = {
    highContrast: preferences.highContrast,
    setHighContrast: (enabled: boolean) => updatePreferences({ highContrast: enabled }),
    
    reducedMotion: preferences.reducedMotion,
    setReducedMotion: (enabled: boolean) => updatePreferences({ reducedMotion: enabled }),
    
    fontSize,
    setFontSize,
    
    showFocusIndicators: true, // Always show focus indicators for accessibility
    setShowFocusIndicators: () => {}, // Not implemented yet
    
    announce,
    
    language,
    setLanguage,
  }

  return (
    <AccessibilityContext.Provider value={contextValue}>
      {children}
    </AccessibilityContext.Provider>
  )
}
