// src/utils/formatters.js

/**
 * Format currency values
 * @param {number} value - The amount to format
 * @param {string} currency - Currency symbol (default: '₹')
 * @param {number} decimals - Decimal places (default: 2)
 * @returns {string} Formatted currency string
 */
export function formatCurrency(value, currency = '₹', decimals = 2) {
  if (isNaN(value)) return `${currency}0.00`
  
  const numericValue = parseFloat(value)
  const formattedValue = numericValue.toFixed(decimals)
    .replace(/\d(?=(\d{3})+\.)/g, '$&,')
  
  return `${currency}${formattedValue}`
}

/**
 * Format date for display
 * @param {Date|string} date - Date object or ISO string
 * @param {string} locale - Locale (default: 'en-IN')
 * @returns {string} Formatted date string
 */
export function formatDate(date, locale = 'en-IN') {
  const options = { 
    year: 'numeric', 
    month: 'short', 
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }
  
  const dateObj = date instanceof Date ? date : new Date(date)
  return dateObj.toLocaleDateString(locale, options)
}

/**
 * Format phone numbers
 * @param {string} phone - Raw phone number string
 * @returns {string} Formatted phone number
 */
export function formatPhone(phone) {
  if (!phone) return ''
  
  // Remove all non-digit characters
  const cleaned = phone.toString().replace(/\D/g, '')
  
  // Format Indian phone numbers
  if (cleaned.length === 10) {
    return cleaned.replace(/(\d{3})(\d{3})(\d{4})/, '$1-$2-$3')
  }
  
  // Format with country code
  if (cleaned.length > 10) {
    return `+${cleaned.slice(0, cleaned.length-10)} ${cleaned.slice(-10).replace(/(\d{3})(\d{3})(\d{4})/, '$1-$2-$3')}`
  }
  
  return phone
}

/**
 * Truncate long text with ellipsis
 * @param {string} text - Input text
 * @param {number} maxLength - Maximum length before truncation
 * @returns {string} Truncated text
 */
export function truncateText(text, maxLength = 50) {
  if (!text) return ''
  return text.length > maxLength 
    ? `${text.substring(0, maxLength)}...` 
    : text
}

/**
 * Format percentage values
 * @param {number} value - Percentage value
 * @param {number} decimals - Decimal places (default: 2)
 * @returns {string} Formatted percentage
 */
export function formatPercentage(value, decimals = 2) {
  if (isNaN(value)) return '0%'
  return `${parseFloat(value).toFixed(decimals)}%`
}

/**
 * Format bill number with prefix/sequence
 * @param {string} prefix - Bill prefix (e.g., 'TEMP')
 * @param {number} number - Bill sequence number
 * @param {string} [suffix=''] - Optional suffix
 * @returns {string} Formatted bill number
 */
export function formatBillNumber(prefix, number, suffix = '') {
  const paddedNumber = number.toString().padStart(5, '0')
  return `${prefix}-${paddedNumber}${suffix ? `-${suffix}` : ''}`
}

/**
 * Format product SKU/code
 * @param {string} category - Product category code
 * @param {string} id - Product ID
 * @param {string} [variant=''] - Product variant
 * @returns {string} Formatted SKU
 */
export function formatSKU(category, id, variant = '') {
  return `${category.toUpperCase().substring(0, 3)}-${id}${variant ? `-${variant}` : ''}`
}