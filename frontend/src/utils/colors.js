/**
 * Converts a suitability score (0-100) to a color on a red-yellow-green gradient.
 * @param {number} score - Score from 0 to 100
 * @returns {string} Hex color string
 */
export function scoreToColor(score) {
  const s = Math.max(0, Math.min(100, score));

  let r, g, b;

  if (s < 30) {
    // Red to orange
    const t = s / 30;
    r = 220;
    g = Math.round(60 + t * 120);
    b = 40;
  } else if (s < 60) {
    // Orange to yellow
    const t = (s - 30) / 30;
    r = Math.round(220 - t * 30);
    g = Math.round(180 + t * 60);
    b = 40;
  } else {
    // Yellow to green
    const t = (s - 60) / 40;
    r = Math.round(190 - t * 150);
    g = Math.round(240 - t * 30);
    b = Math.round(40 + t * 80);
  }

  return `rgb(${r}, ${g}, ${b})`;
}

/**
 * Returns a color based on substation voltage (kV).
 * @param {number} kv - Voltage in kilovolts
 * @returns {string} Hex color string
 */
export function voltageToColor(kv) {
  if (kv >= 500) return '#ef4444';    // Red - extra high voltage
  if (kv >= 230) return '#f59e0b';    // Amber - high voltage
  if (kv >= 115) return '#3b82f6';    // Blue - medium voltage
  if (kv >= 44) return '#06b6d4';     // Cyan - sub-transmission
  return '#8b5cf6';                    // Purple - distribution
}

/**
 * Returns a marker radius based on substation voltage.
 * @param {number} kv - Voltage in kilovolts
 * @returns {number} Radius in pixels
 */
export function voltageToRadius(kv) {
  if (kv >= 500) return 10;
  if (kv >= 230) return 8;
  if (kv >= 115) return 6;
  if (kv >= 44) return 5;
  return 4;
}

/**
 * Returns opacity based on current zoom level.
 * Higher zoom = more opaque for detail visibility.
 * @param {number} zoom - Current map zoom level
 * @param {number} [minOpacity=0.15] - Minimum opacity at lowest zoom
 * @param {number} [maxOpacity=0.6] - Maximum opacity at highest zoom
 * @returns {number} Opacity value between minOpacity and maxOpacity
 */
export function zoomToOpacity(zoom, minOpacity = 0.15, maxOpacity = 0.6) {
  const minZoom = 6;
  const maxZoom = 16;
  const clampedZoom = Math.max(minZoom, Math.min(maxZoom, zoom));
  const t = (clampedZoom - minZoom) / (maxZoom - minZoom);
  return minOpacity + t * (maxOpacity - minOpacity);
}

/**
 * Returns a CSS class name for a score level.
 * @param {number} score
 * @returns {string}
 */
export function scoreLevel(score) {
  if (score >= 70) return 'high';
  if (score >= 40) return 'medium';
  return 'low';
}
