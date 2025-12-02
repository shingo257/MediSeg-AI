import { useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAppStore } from '@store/appStore'
import toast from 'react-hot-toast'

interface KeyboardShortcut {
  key: string
  ctrl?: boolean
  alt?: boolean
  shift?: boolean
  action: () => void
  description: string
  category: string
}

export const useKeyboardShortcuts = () => {
  const navigate = useNavigate()
  const { sidebarOpen, setSidebarOpen, setError } = useAppStore()

  const shortcuts: KeyboardShortcut[] = [
    // Navigation shortcuts
    {
      key: '1',
      ctrl: true,
      action: () => navigate('/dashboard'),
      description: 'ダッシュボードに移動',
      category: 'ナビゲーション',
    },
    {
      key: '2',
      ctrl: true,
      action: () => navigate('/segmentation'),
      description: 'セグメンテーションに移動',
      category: 'ナビゲーション',
    },
    {
      key: '3',
      ctrl: true,
      action: () => navigate('/datasets'),
      description: 'データセットに移動',
      category: 'ナビゲーション',
    },
    {
      key: '4',
      ctrl: true,
      action: () => navigate('/models'),
      description: 'モデルに移動',
      category: 'ナビゲーション',
    },
    {
      key: '5',
      ctrl: true,
      action: () => navigate('/analytics'),
      description: '分析に移動',
      category: 'ナビゲーション',
    },

    // UI shortcuts
    {
      key: 'b',
      ctrl: true,
      action: () => setSidebarOpen(!sidebarOpen),
      description: 'サイドバーの表示/非表示',
      category: 'UI',
    },
    {
      key: 'Escape',
      action: () => {
        setError(null)
        toast.dismiss()
      },
      description: 'エラーをクリア',
      category: 'UI',
    },

    // File operations
    {
      key: 'o',
      ctrl: true,
      action: () => {
        // Trigger file upload
        const input = document.createElement('input')
        input.type = 'file'
        input.accept = 'image/*'
        input.click()
      },
      description: 'ファイルを開く',
      category: 'ファイル操作',
    },
    {
      key: 's',
      ctrl: true,
      action: () => {
        toast.success('保存機能は実装中です')
      },
      description: '結果を保存',
      category: 'ファイル操作',
    },

    // Help
    {
      key: 'F1',
      action: () => {
        toast('キーボードショートカット一覧を表示', {
          duration: 3000,
          icon: '⌨️',
        })
      },
      description: 'ヘルプを表示',
      category: 'ヘルプ',
    },
    {
      key: '?',
      shift: true,
      action: () => {
        toast('キーボードショートカット一覧を表示', {
          duration: 3000,
          icon: '⌨️',
        })
      },
      description: 'ショートカット一覧',
      category: 'ヘルプ',
    },
  ]

  const handleKeyDown = useCallback((event: KeyboardEvent) => {
    // Don't trigger shortcuts when typing in input fields
    if (
      event.target instanceof HTMLInputElement ||
      event.target instanceof HTMLTextAreaElement ||
      event.target instanceof HTMLSelectElement ||
      (event.target as HTMLElement)?.contentEditable === 'true'
    ) {
      return
    }

    const pressedKey = event.key.toLowerCase()
    const isCtrl = event.ctrlKey || event.metaKey
    const isAlt = event.altKey
    const isShift = event.shiftKey

    // Find matching shortcut
    const shortcut = shortcuts.find(s => {
      const keyMatch = s.key.toLowerCase() === pressedKey
      const ctrlMatch = (s.ctrl || false) === isCtrl
      const altMatch = (s.alt || false) === isAlt
      const shiftMatch = (s.shift || false) === isShift

      return keyMatch && ctrlMatch && altMatch && shiftMatch
    })

    if (shortcut) {
      event.preventDefault()
      shortcut.action()
      
      // Show toast for non-navigation shortcuts
      if (!shortcut.description.includes('移動')) {
        toast.success(shortcut.description, {
          duration: 1500,
          icon: '⌨️',
        })
      }
    }
  }, [shortcuts, sidebarOpen, setSidebarOpen, setError, navigate])

  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown)
    return () => {
      document.removeEventListener('keydown', handleKeyDown)
    }
  }, [handleKeyDown])

  return {
    shortcuts,
    showShortcuts: () => {
      const shortcutsByCategory = shortcuts.reduce((acc, shortcut) => {
        if (!acc[shortcut.category]) {
          acc[shortcut.category] = []
        }
        acc[shortcut.category].push(shortcut)
        return acc
      }, {} as Record<string, KeyboardShortcut[]>)

      let message = 'キーボードショートカット:\n\n'
      
      Object.entries(shortcutsByCategory).forEach(([category, categoryShortcuts]) => {
        message += `${category}:\n`
        categoryShortcuts.forEach(shortcut => {
          const keys = []
          if (shortcut.ctrl) keys.push('Ctrl')
          if (shortcut.alt) keys.push('Alt')
          if (shortcut.shift) keys.push('Shift')
          keys.push(shortcut.key)
          
          message += `  ${keys.join(' + ')}: ${shortcut.description}\n`
        })
        message += '\n'
      })

      toast(message, {
        duration: 8000,
        icon: '⌨️',
      })
    },
  }
}
