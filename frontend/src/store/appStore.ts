import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export interface AppState {
  // Theme
  theme: 'light' | 'dark' | 'auto'
  setTheme: (theme: 'light' | 'dark' | 'auto') => void
  
  // Language
  language: 'ja' | 'en'
  setLanguage: (language: 'ja' | 'en') => void
  
  // UI State
  sidebarOpen: boolean
  setSidebarOpen: (open: boolean) => void
  
  // Current page
  currentPage: string
  setCurrentPage: (page: string) => void
  
  // Loading states
  isLoading: boolean
  setLoading: (loading: boolean) => void
  
  // Error handling
  error: string | null
  setError: (error: string | null) => void
  
  // User preferences
  preferences: {
    autoSave: boolean
    notifications: boolean
    soundEnabled: boolean
    highContrast: boolean
    reducedMotion: boolean
  }
  updatePreferences: (preferences: Partial<AppState['preferences']>) => void
  
  // Recent files
  recentFiles: string[]
  addRecentFile: (file: string) => void
  clearRecentFiles: () => void
  
  // Workspace
  workspace: {
    currentProject: string | null
    projects: string[]
  }
  setCurrentProject: (project: string | null) => void
  addProject: (project: string) => void
}

export const useAppStore = create<AppState>()(
  persist(
    (set, get) => ({
      // Theme
      theme: 'dark',
      setTheme: (theme) => set({ theme }),
      
      // Language
      language: 'ja',
      setLanguage: (language) => set({ language }),
      
      // UI State
      sidebarOpen: true,
      setSidebarOpen: (sidebarOpen) => set({ sidebarOpen }),
      
      // Current page
      currentPage: 'dashboard',
      setCurrentPage: (currentPage) => set({ currentPage }),
      
      // Loading states
      isLoading: false,
      setLoading: (isLoading) => set({ isLoading }),
      
      // Error handling
      error: null,
      setError: (error) => set({ error }),
      
      // User preferences
      preferences: {
        autoSave: true,
        notifications: true,
        soundEnabled: false,
        highContrast: false,
        reducedMotion: false,
      },
      updatePreferences: (newPreferences) =>
        set((state) => ({
          preferences: { ...state.preferences, ...newPreferences },
        })),
      
      // Recent files
      recentFiles: [],
      addRecentFile: (file) =>
        set((state) => ({
          recentFiles: [file, ...state.recentFiles.filter(f => f !== file)].slice(0, 10),
        })),
      clearRecentFiles: () => set({ recentFiles: [] }),
      
      // Workspace
      workspace: {
        currentProject: null,
        projects: [],
      },
      setCurrentProject: (currentProject) =>
        set((state) => ({
          workspace: { ...state.workspace, currentProject },
        })),
      addProject: (project) =>
        set((state) => ({
          workspace: {
            ...state.workspace,
            projects: [...state.workspace.projects, project],
          },
        })),
    }),
    {
      name: 'mediseg-app-store',
      partialize: (state) => ({
        theme: state.theme,
        language: state.language,
        preferences: state.preferences,
        recentFiles: state.recentFiles,
        workspace: state.workspace,
      }),
    }
  )
)
