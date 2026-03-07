// Common types for MediSeg.AI

export interface ImageData {
  id: string
  name: string
  path: string
  size: number
  width: number
  height: number
  format: string
  uploadedAt: Date
  metadata?: Record<string, any>
}

export interface SegmentationResult {
  id: string
  imageId: string
  modelId: string
  prediction: number[][]
  binaryMask: number[][]
  confidence: number[][]
  metrics: SegmentationMetrics
  processingTime: number
  createdAt: Date
}

export interface SegmentationMetrics {
  dice: number
  iou: number
  accuracy: number
  sensitivity: number
  specificity: number
  precision: number
  recall: number
  f1Score: number
  hausdorffDistance?: number
  averageSurfaceDistance?: number
}

export interface Model {
  id: string
  name: string
  type: 'U-Net' | 'DeepLabV3+' | 'Custom'
  version: string
  description: string
  architecture: string
  parameters: number
  inputSize: [number, number]
  outputClasses: number
  trainedOn: string
  performance: {
    dice: number
    iou: number
    accuracy: number
  }
  isLoaded: boolean
  isTraining: boolean
  createdAt: Date
  updatedAt: Date
}

export interface Dataset {
  id: string
  name: string
  description: string
  type: 'medical' | 'synthetic' | 'custom'
  category: 'brain' | 'lung' | 'skin' | 'cardiac' | 'other'
  format: string[]
  size: string
  imageCount: number
  resolution: string
  status: 'available' | 'downloading' | 'downloaded' | 'error'
  progress: number
  path?: string
  metadata: {
    license: string
    authors: string[]
    citation: string
    url: string
  }
  createdAt: Date
  updatedAt: Date
}

export interface ProcessingJob {
  id: string
  type: 'segmentation' | 'training' | 'evaluation'
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'
  progress: number
  message: string
  input: any
  output?: any
  error?: string
  startedAt: Date
  completedAt?: Date
  estimatedTime?: number
}

export interface SystemMetrics {
  cpu: {
    usage: number
    cores: number
    temperature?: number
  }
  memory: {
    used: number
    total: number
    percentage: number
  }
  gpu?: {
    available: boolean
    usage: number
    memory: {
      used: number
      total: number
      percentage: number
    }
    temperature?: number
    name: string
  }
  disk: {
    used: number
    total: number
    percentage: number
  }
  network: {
    upload: number
    download: number
  }
}

export interface User {
  id: string
  name: string
  email: string
  role: 'admin' | 'user' | 'viewer'
  preferences: UserPreferences
  createdAt: Date
  lastLogin: Date
}

export interface UserPreferences {
  theme: 'light' | 'dark' | 'auto'
  language: 'ja' | 'en'
  notifications: boolean
  autoSave: boolean
  soundEnabled: boolean
  highContrast: boolean
  reducedMotion: boolean
  defaultModel: string
  defaultDataset: string
  workspace: {
    layout: 'grid' | 'list'
    showThumbnails: boolean
    thumbnailSize: 'small' | 'medium' | 'large'
  }
}

export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  error?: string
  message?: string
  timestamp: Date
}

export interface PaginatedResponse<T = any> extends ApiResponse<T[]> {
  pagination: {
    page: number
    limit: number
    total: number
    totalPages: number
  }
}

export interface FilterOptions {
  search?: string
  category?: string
  type?: string
  status?: string
  dateFrom?: Date
  dateTo?: Date
  sortBy?: string
  sortOrder?: 'asc' | 'desc'
}

export interface ExportOptions {
  format: 'png' | 'jpg' | 'tiff' | 'dicom' | 'nifti'
  quality: number
  includeMetadata: boolean
  includeMetrics: boolean
  compression?: boolean
}

// Event types for real-time updates
export interface WebSocketMessage {
  type: 'progress' | 'result' | 'error' | 'notification'
  data: any
  timestamp: Date
}

export interface ProgressUpdate {
  jobId: string
  progress: number
  message: string
  stage: string
}

export interface NotificationMessage {
  id: string
  type: 'info' | 'success' | 'warning' | 'error'
  title: string
  message: string
  duration?: number
  actions?: NotificationAction[]
}

export interface NotificationAction {
  label: string
  action: () => void
  variant?: 'primary' | 'secondary'
}

// 3D Visualization types
export interface VolumeData {
  data: number[][][]
  dimensions: [number, number, number]
  spacing: [number, number, number]
  origin: [number, number, number]
  orientation: number[][]
}

export interface MeshData {
  vertices: number[][]
  faces: number[][]
  normals?: number[][]
  colors?: number[][]
  texture?: string
}

// Keyboard shortcuts
export interface KeyboardShortcut {
  key: string
  ctrl?: boolean
  alt?: boolean
  shift?: boolean
  action: string
  description: string
}

// Form validation
export interface ValidationRule {
  required?: boolean
  minLength?: number
  maxLength?: number
  pattern?: RegExp
  custom?: (value: any) => string | null
}

export interface FormField {
  name: string
  label: string
  type: 'text' | 'email' | 'password' | 'number' | 'select' | 'multiselect' | 'checkbox' | 'radio' | 'file' | 'textarea'
  placeholder?: string
  options?: { value: any; label: string }[]
  validation?: ValidationRule
  defaultValue?: any
  disabled?: boolean
  hidden?: boolean
}
