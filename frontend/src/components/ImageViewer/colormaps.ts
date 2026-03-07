/**
 * Map segmentation value [0,1] to RGB for overlay colormap
 */
export function valueToRgb(value: number, colormap: string): [number, number, number] {
  const v = Math.max(0, Math.min(1, value))
  switch (colormap) {
    case 'viridis': {
      // Simplified viridis-like: dark purple -> green -> yellow
      if (v < 0.25) return [Math.round(68 + (59 - 68) * (v / 0.25)), Math.round(1 + (82 - 1) * (v / 0.25)), Math.round(84 + (139 - 84) * (v / 0.25))]
      if (v < 0.5) return [Math.round(59 + (33 - 59) * ((v - 0.25) / 0.25)), Math.round(82 + (145 - 82) * ((v - 0.25) / 0.25)), Math.round(139 + (140 - 139) * ((v - 0.25) / 0.25))]
      if (v < 0.75) return [Math.round(33 + (94 - 33) * ((v - 0.5) / 0.25)), Math.round(145 + (201 - 145) * ((v - 0.5) / 0.25)), Math.round(140 + (98 - 140) * ((v - 0.5) / 0.25))]
      return [Math.round(94 + (253 - 94) * ((v - 0.75) / 0.25)), Math.round(201 + (231 - 201) * ((v - 0.75) / 0.25)), Math.round(98 + (36 - 98) * ((v - 0.75) / 0.25))]
    }
    case 'plasma': {
      if (v < 0.25) return [Math.round(13 + (72 - 13) * (v / 0.25)), Math.round(8 + (1 - 8) * (v / 0.25)), Math.round(135 + (181 - 135) * (v / 0.25))]
      if (v < 0.5) return [Math.round(72 + (180 - 72) * ((v - 0.25) / 0.25)), Math.round(1 + (54 - 1) * ((v - 0.25) / 0.25)), Math.round(181 + (74 - 181) * ((v - 0.25) / 0.25))]
      if (v < 0.75) return [Math.round(180 + (249 - 180) * ((v - 0.5) / 0.25)), Math.round(54 + (167 - 54) * ((v - 0.5) / 0.25)), Math.round(74 + (21 - 74) * ((v - 0.75) / 0.25))]
      return [Math.round(249 + (253 - 249) * ((v - 0.75) / 0.25)), Math.round(167 + (231 - 167) * ((v - 0.75) / 0.25)), Math.round(21 + (36 - 21) * ((v - 0.75) / 0.25))]
    }
    case 'red':
    default:
      return [255, Math.round((1 - v) * 80), Math.round((1 - v) * 80)]
  }
}
