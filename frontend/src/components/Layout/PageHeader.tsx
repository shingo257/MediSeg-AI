import React from 'react'
import { Box, Typography } from '@mui/material'

interface PageHeaderProps {
  title: string
  description?: string
}

const PageHeader: React.FC<PageHeaderProps> = ({ title, description }) => (
  <Box sx={{ mb: 4 }}>
    <Typography
      variant="h4"
      component="h1"
      gutterBottom
      sx={{
        fontWeight: 700,
        color: 'primary.main',
        letterSpacing: '-0.02em',
      }}
    >
      {title}
    </Typography>
    {description && (
      <Typography variant="body1" color="text.secondary" sx={{ maxWidth: 720 }}>
        {description}
      </Typography>
    )}
  </Box>
)

export default PageHeader
