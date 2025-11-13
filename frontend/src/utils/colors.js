/**
 * Color Palette Constants
 * Using Okabe-Ito colorblind-safe palette per Constitution Principle VI
 * Reference: https://jfly.uni-koeln.de/color/
 */

// Okabe-Ito Palette (Colorblind-Safe)
export const COLORS = {
  // Primary colors
  BLACK: '#000000',
  ORANGE: '#E69F00',
  SKY_BLUE: '#56B4E9',
  BLUISH_GREEN: '#009E73',
  YELLOW: '#F0E442',
  BLUE: '#0072B2',
  VERMILLION: '#D55E00',
  REDDISH_PURPLE: '#CC79A7',

  // Grays
  GRAY_DARK: '#333333',
  GRAY: '#999999',
  GRAY_LIGHT: '#CCCCCC',
  GRAY_LIGHTER: '#EEEEEE',
  WHITE: '#FFFFFF',
};

// Chart colors (ordered for maximum distinction)
export const CHART_COLORS = [
  COLORS.BLUE,
  COLORS.ORANGE,
  COLORS.BLUISH_GREEN,
  COLORS.VERMILLION,
  COLORS.SKY_BLUE,
  COLORS.REDDISH_PURPLE,
  COLORS.YELLOW,
  COLORS.BLACK,
];

// Semantic colors
export const STATUS_COLORS = {
  SUCCESS: COLORS.BLUISH_GREEN,
  WARNING: COLORS.ORANGE,
  ERROR: COLORS.VERMILLION,
  INFO: COLORS.BLUE,
};

// Safety rating colors (1-10 scale)
export const SAFETY_COLORS = {
  SAFE: COLORS.BLUISH_GREEN, // 1-3
  MODERATE: COLORS.YELLOW, // 4-6
  CONCERNING: COLORS.ORANGE, // 7-8
  DANGEROUS: COLORS.VERMILLION, // 9-10
};

/**
 * Get color by index for charts
 * @param {number} index - Index for color selection
 * @returns {string} - Hex color code
 */
export const getChartColor = (index) => {
  return CHART_COLORS[index % CHART_COLORS.length];
};

/**
 * Get safety rating color
 * @param {number} rating - Safety rating (1-10)
 * @returns {string} - Hex color code
 */
export const getSafetyColor = (rating) => {
  if (rating <= 3) return SAFETY_COLORS.SAFE;
  if (rating <= 6) return SAFETY_COLORS.MODERATE;
  if (rating <= 8) return SAFETY_COLORS.CONCERNING;
  return SAFETY_COLORS.DANGEROUS;
};

export default COLORS;
