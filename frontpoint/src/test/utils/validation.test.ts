import { describe, it, expect } from 'vitest'

// Mock validation utility functions
const validateEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

const validatePassword = (password: string): { isValid: boolean; errors: string[] } => {
  const errors: string[] = []
  
  if (password.length < 8) {
    errors.push('密码长度至少8位')
  }
  
  if (!/[A-Z]/.test(password)) {
    errors.push('密码必须包含大写字母')
  }
  
  if (!/[a-z]/.test(password)) {
    errors.push('密码必须包含小写字母')
  }
  
  if (!/\d/.test(password)) {
    errors.push('密码必须包含数字')
  }
  
  if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
    errors.push('密码必须包含特殊字符')
  }
  
  return {
    isValid: errors.length === 0,
    errors
  }
}

const validateUsername = (username: string): { isValid: boolean; errors: string[] } => {
  const errors: string[] = []
  
  if (username.length < 3) {
    errors.push('用户名长度至少3位')
  }
  
  if (username.length > 20) {
    errors.push('用户名长度不能超过20位')
  }
  
  if (!/^[a-zA-Z0-9_]+$/.test(username)) {
    errors.push('用户名只能包含字母、数字和下划线')
  }
  
  return {
    isValid: errors.length === 0,
    errors
  }
}

const validatePhoneNumber = (phone: string): boolean => {
  const phoneRegex = /^\+?[\d\s\-\(\)]{10,}$/
  return phoneRegex.test(phone)
}

const validateUrl = (url: string): boolean => {
  try {
    new URL(url)
    return true
  } catch {
    return false
  }
}

const validateNumber = (value: string, min?: number, max?: number): { isValid: boolean; errors: string[] } => {
  const errors: string[] = []
  const num = parseFloat(value)
  
  if (isNaN(num)) {
    errors.push('请输入有效的数字')
    return { isValid: false, errors }
  }
  
  if (min !== undefined && num < min) {
    errors.push(`数值不能小于 ${min}`)
  }
  
  if (max !== undefined && num > max) {
    errors.push(`数值不能大于 ${max}`)
  }
  
  return {
    isValid: errors.length === 0,
    errors
  }
}

const validateRequired = (value: string | number | null | undefined): boolean => {
  if (value === null || value === undefined) return false
  if (typeof value === 'string' && value.trim() === '') return false
  return true
}

const validateTradeQuantity = (quantity: string): { isValid: boolean; errors: string[] } => {
  const errors: string[] = []
  const num = parseFloat(quantity)
  
  if (isNaN(num)) {
    errors.push('请输入有效的数量')
    return { isValid: false, errors }
  }
  
  if (num <= 0) {
    errors.push('数量必须大于0')
  }
  
  if (num !== Math.floor(num)) {
    errors.push('数量必须是整数')
  }
  
  return {
    isValid: errors.length === 0,
    errors
  }
}

const validateTradePrice = (price: string): { isValid: boolean; errors: string[] } => {
  const errors: string[] = []
  const num = parseFloat(price)
  
  if (isNaN(num)) {
    errors.push('请输入有效的价格')
    return { isValid: false, errors }
  }
  
  if (num <= 0) {
    errors.push('价格必须大于0')
  }
  
  if (num > 1000000) {
    errors.push('价格不能超过1,000,000')
  }
  
  return {
    isValid: errors.length === 0,
    errors
  }
}

const validatePortfolioName = (name: string): { isValid: boolean; errors: string[] } => {
  const errors: string[] = []
  
  if (!validateRequired(name)) {
    errors.push('投资组合名称不能为空')
    return { isValid: false, errors }
  }
  
  if (name.length < 2) {
    errors.push('投资组合名称至少2个字符')
  }
  
  if (name.length > 50) {
    errors.push('投资组合名称不能超过50个字符')
  }
  
  return {
    isValid: errors.length === 0,
    errors
  }
}

const validateStrategyParameters = (parameters: Record<string, any>): { isValid: boolean; errors: string[] } => {
  const errors: string[] = []
  
  // 检查必需参数
  const requiredParams = ['lookback_period', 'rsi_period', 'position_size_percentage']
  
  for (const param of requiredParams) {
    if (!(param in parameters)) {
      errors.push(`缺少必需参数: ${param}`)
    }
  }
  
  // 检查参数值范围
  if (parameters.lookback_period && (parameters.lookback_period < 5 || parameters.lookback_period > 100)) {
    errors.push('回望周期必须在5-100之间')
  }
  
  if (parameters.rsi_period && (parameters.rsi_period < 5 || parameters.rsi_period > 50)) {
    errors.push('RSI周期必须在5-50之间')
  }
  
  if (parameters.position_size_percentage && (parameters.position_size_percentage <= 0 || parameters.position_size_percentage > 1)) {
    errors.push('持仓大小百分比必须在0-1之间')
  }
  
  return {
    isValid: errors.length === 0,
    errors
  }
}

const validateRiskRuleParameters = (ruleType: string, parameters: Record<string, any>): { isValid: boolean; errors: string[] } => {
  const errors: string[] = []
  
  switch (ruleType) {
    case 'position_size':
      if (!parameters.max_position_size || parameters.max_position_size <= 0) {
        errors.push('最大持仓大小必须大于0')
      }
      if (!parameters.max_position_percentage || parameters.max_position_percentage <= 0 || parameters.max_position_percentage > 1) {
        errors.push('最大持仓百分比必须在0-1之间')
      }
      break
      
    case 'daily_loss':
      if (!parameters.max_daily_loss || parameters.max_daily_loss <= 0) {
        errors.push('最大日损失必须大于0')
      }
      break
      
    case 'max_drawdown':
      if (!parameters.max_drawdown_percentage || parameters.max_drawdown_percentage <= 0 || parameters.max_drawdown_percentage > 1) {
        errors.push('最大回撤百分比必须在0-1之间')
      }
      break
      
    case 'trading_frequency':
      if (!parameters.max_trades_per_day || parameters.max_trades_per_day <= 0) {
        errors.push('每日最大交易次数必须大于0')
      }
      break
      
    default:
      errors.push('未知的风险规则类型')
  }
  
  return {
    isValid: errors.length === 0,
    errors
  }
}

describe('Validation Utils', () => {
  describe('validateEmail', () => {
    it('should validate email correctly', () => {
      expect(validateEmail('test@example.com')).toBe(true)
      expect(validateEmail('user.name@domain.co.uk')).toBe(true)
      expect(validateEmail('invalid-email')).toBe(false)
      expect(validateEmail('@domain.com')).toBe(false)
      expect(validateEmail('user@')).toBe(false)
      expect(validateEmail('')).toBe(false)
    })
  })

  describe('validatePassword', () => {
    it('should validate password correctly', () => {
      const validPassword = 'Password123!'
      const result = validatePassword(validPassword)
      expect(result.isValid).toBe(true)
      expect(result.errors).toHaveLength(0)
    })

    it('should catch password errors', () => {
      const invalidPassword = '123'
      const result = validatePassword(invalidPassword)
      expect(result.isValid).toBe(false)
      expect(result.errors.length).toBeGreaterThan(0)
    })

    it('should require minimum length', () => {
      const result = validatePassword('Pass1!')
      expect(result.isValid).toBe(false)
      expect(result.errors).toContain('密码长度至少8位')
    })

    it('should require uppercase letter', () => {
      const result = validatePassword('password123!')
      expect(result.isValid).toBe(false)
      expect(result.errors).toContain('密码必须包含大写字母')
    })

    it('should require lowercase letter', () => {
      const result = validatePassword('PASSWORD123!')
      expect(result.isValid).toBe(false)
      expect(result.errors).toContain('密码必须包含小写字母')
    })

    it('should require number', () => {
      const result = validatePassword('Password!')
      expect(result.isValid).toBe(false)
      expect(result.errors).toContain('密码必须包含数字')
    })

    it('should require special character', () => {
      const result = validatePassword('Password123')
      expect(result.isValid).toBe(false)
      expect(result.errors).toContain('密码必须包含特殊字符')
    })
  })

  describe('validateUsername', () => {
    it('should validate username correctly', () => {
      const result = validateUsername('testuser123')
      expect(result.isValid).toBe(true)
      expect(result.errors).toHaveLength(0)
    })

    it('should require minimum length', () => {
      const result = validateUsername('ab')
      expect(result.isValid).toBe(false)
      expect(result.errors).toContain('用户名长度至少3位')
    })

    it('should enforce maximum length', () => {
      const result = validateUsername('a'.repeat(21))
      expect(result.isValid).toBe(false)
      expect(result.errors).toContain('用户名长度不能超过20位')
    })

    it('should only allow alphanumeric and underscore', () => {
      const result = validateUsername('test-user')
      expect(result.isValid).toBe(false)
      expect(result.errors).toContain('用户名只能包含字母、数字和下划线')
    })
  })

  describe('validatePhoneNumber', () => {
    it('should validate phone number correctly', () => {
      expect(validatePhoneNumber('1234567890')).toBe(true)
      expect(validatePhoneNumber('+1 234 567 8900')).toBe(true)
      expect(validatePhoneNumber('(123) 456-7890')).toBe(true)
      expect(validatePhoneNumber('123-456-7890')).toBe(true)
      expect(validatePhoneNumber('123')).toBe(false)
      expect(validatePhoneNumber('')).toBe(false)
    })
  })

  describe('validateUrl', () => {
    it('should validate URL correctly', () => {
      expect(validateUrl('https://example.com')).toBe(true)
      expect(validateUrl('http://example.com')).toBe(true)
      expect(validateUrl('ftp://example.com')).toBe(true)
      expect(validateUrl('invalid-url')).toBe(false)
      expect(validateUrl('')).toBe(false)
    })
  })

  describe('validateNumber', () => {
    it('should validate number correctly', () => {
      const result = validateNumber('123.45')
      expect(result.isValid).toBe(true)
      expect(result.errors).toHaveLength(0)
    })

    it('should validate with min/max constraints', () => {
      const result = validateNumber('50', 0, 100)
      expect(result.isValid).toBe(true)
    })

    it('should catch invalid numbers', () => {
      const result = validateNumber('abc')
      expect(result.isValid).toBe(false)
      expect(result.errors).toContain('请输入有效的数字')
    })

    it('should enforce minimum value', () => {
      const result = validateNumber('5', 10)
      expect(result.isValid).toBe(false)
      expect(result.errors).toContain('数值不能小于 10')
    })

    it('should enforce maximum value', () => {
      const result = validateNumber('150', 0, 100)
      expect(result.isValid).toBe(false)
      expect(result.errors).toContain('数值不能大于 100')
    })
  })

  describe('validateRequired', () => {
    it('should validate required fields correctly', () => {
      expect(validateRequired('test')).toBe(true)
      expect(validateRequired(123)).toBe(true)
      expect(validateRequired('')).toBe(false)
      expect(validateRequired('   ')).toBe(false)
      expect(validateRequired(null)).toBe(false)
      expect(validateRequired(undefined)).toBe(false)
    })
  })

  describe('validateTradeQuantity', () => {
    it('should validate trade quantity correctly', () => {
      const result = validateTradeQuantity('100')
      expect(result.isValid).toBe(true)
      expect(result.errors).toHaveLength(0)
    })

    it('should require positive quantity', () => {
      const result = validateTradeQuantity('0')
      expect(result.isValid).toBe(false)
      expect(result.errors).toContain('数量必须大于0')
    })

    it('should require integer quantity', () => {
      const result = validateTradeQuantity('100.5')
      expect(result.isValid).toBe(false)
      expect(result.errors).toContain('数量必须是整数')
    })
  })

  describe('validateTradePrice', () => {
    it('should validate trade price correctly', () => {
      const result = validateTradePrice('150.50')
      expect(result.isValid).toBe(true)
      expect(result.errors).toHaveLength(0)
    })

    it('should require positive price', () => {
      const result = validateTradePrice('0')
      expect(result.isValid).toBe(false)
      expect(result.errors).toContain('价格必须大于0')
    })

    it('should enforce maximum price', () => {
      const result = validateTradePrice('2000000')
      expect(result.isValid).toBe(false)
      expect(result.errors).toContain('价格不能超过1,000,000')
    })
  })

  describe('validatePortfolioName', () => {
    it('should validate portfolio name correctly', () => {
      const result = validatePortfolioName('My Portfolio')
      expect(result.isValid).toBe(true)
      expect(result.errors).toHaveLength(0)
    })

    it('should require non-empty name', () => {
      const result = validatePortfolioName('')
      expect(result.isValid).toBe(false)
      expect(result.errors).toContain('投资组合名称不能为空')
    })

    it('should enforce minimum length', () => {
      const result = validatePortfolioName('A')
      expect(result.isValid).toBe(false)
      expect(result.errors).toContain('投资组合名称至少2个字符')
    })

    it('should enforce maximum length', () => {
      const result = validatePortfolioName('A'.repeat(51))
      expect(result.isValid).toBe(false)
      expect(result.errors).toContain('投资组合名称不能超过50个字符')
    })
  })

  describe('validateStrategyParameters', () => {
    it('should validate strategy parameters correctly', () => {
      const parameters = {
        lookback_period: 20,
        rsi_period: 14,
        position_size_percentage: 0.1
      }
      
      const result = validateStrategyParameters(parameters)
      expect(result.isValid).toBe(true)
      expect(result.errors).toHaveLength(0)
    })

    it('should require all parameters', () => {
      const result = validateStrategyParameters({})
      expect(result.isValid).toBe(false)
      expect(result.errors.length).toBeGreaterThan(0)
    })

    it('should validate parameter ranges', () => {
      const parameters = {
        lookback_period: 2,
        rsi_period: 60,
        position_size_percentage: 1.5
      }
      
      const result = validateStrategyParameters(parameters)
      expect(result.isValid).toBe(false)
      expect(result.errors).toContain('回望周期必须在5-100之间')
      expect(result.errors).toContain('RSI周期必须在5-50之间')
      expect(result.errors).toContain('持仓大小百分比必须在0-1之间')
    })
  })

  describe('validateRiskRuleParameters', () => {
    it('should validate position size rule', () => {
      const parameters = {
        max_position_size: 5000,
        max_position_percentage: 0.2
      }
      
      const result = validateRiskRuleParameters('position_size', parameters)
      expect(result.isValid).toBe(true)
    })

    it('should validate daily loss rule', () => {
      const parameters = {
        max_daily_loss: 1000
      }
      
      const result = validateRiskRuleParameters('daily_loss', parameters)
      expect(result.isValid).toBe(true)
    })

    it('should validate max drawdown rule', () => {
      const parameters = {
        max_drawdown_percentage: 0.1
      }
      
      const result = validateRiskRuleParameters('max_drawdown', parameters)
      expect(result.isValid).toBe(true)
    })

    it('should validate trading frequency rule', () => {
      const parameters = {
        max_trades_per_day: 10
      }
      
      const result = validateRiskRuleParameters('trading_frequency', parameters)
      expect(result.isValid).toBe(true)
    })

    it('should handle unknown rule type', () => {
      const result = validateRiskRuleParameters('unknown', {})
      expect(result.isValid).toBe(false)
      expect(result.errors).toContain('未知的风险规则类型')
    })
  })
})
