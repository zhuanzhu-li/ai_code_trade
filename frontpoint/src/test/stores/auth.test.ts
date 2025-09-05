import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '@/stores/auth'
import { apiClient } from '@/api'
import type { User, LoginRequest, RegisterRequest } from '@/types'

// Mock API client
vi.mock('@/api', () => ({
  apiClient: {
    login: vi.fn(),
    register: vi.fn()
  }
}))

const mockedApiClient = vi.mocked(apiClient)

describe('useAuthStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    localStorage.clear()
    // 重置localStorage mock
    vi.mocked(localStorage.getItem).mockReturnValue(null)
    vi.mocked(localStorage.setItem).mockImplementation(() => {})
    vi.mocked(localStorage.removeItem).mockImplementation(() => {})
  })

  describe('initial state', () => {
    it('should have correct initial state', () => {
      const store = useAuthStore()
      
      expect(store.user).toBeNull()
      expect(store.token).toBeNull()
      expect(store.isAuthenticated).toBe(false)
    })

    it('should load token from localStorage', () => {
      vi.mocked(localStorage.getItem).mockReturnValue('test-token')
      const store = useAuthStore()
      
      expect(store.token).toBe('test-token')
    })
  })

  describe('isAuthenticated computed', () => {
    it('should return false when no token and user', () => {
      const store = useAuthStore()
      expect(store.isAuthenticated).toBe(false)
    })

    it('should return false when only token exists', () => {
      const store = useAuthStore()
      store.token = 'test-token'
      expect(store.isAuthenticated).toBe(false)
    })

    it('should return false when only user exists', () => {
      const store = useAuthStore()
      store.user = { id: 1, username: 'test', email: 'test@test.com' } as User
      expect(store.isAuthenticated).toBe(false)
    })

    it('should return true when both token and user exist', () => {
      const store = useAuthStore()
      store.token = 'test-token'
      store.user = { id: 1, username: 'test', email: 'test@test.com' } as User
      expect(store.isAuthenticated).toBe(true)
    })
  })

  describe('initUser', () => {
    it('should load user from localStorage when token exists but no user', () => {
      const store = useAuthStore()
      const userData = { id: 1, username: 'test', email: 'test@test.com' }
      
      store.token = 'test-token'
      vi.mocked(localStorage.getItem).mockImplementation((key) => {
        if (key === 'user') return JSON.stringify(userData)
        return null
      })
      
      store.initUser()
      
      expect(store.user).toEqual(userData)
    })

    it('should not load user when no token', () => {
      const store = useAuthStore()
      const userData = { id: 1, username: 'test', email: 'test@test.com' }
      
      vi.mocked(localStorage.getItem).mockImplementation((key) => {
        if (key === 'user') return JSON.stringify(userData)
        return null
      })
      
      store.initUser()
      
      expect(store.user).toBeNull()
    })

    it('should not load user when user already exists', () => {
      const store = useAuthStore()
      const existingUser = { id: 1, username: 'existing', email: 'existing@test.com' }
      const localStorageUser = { id: 2, username: 'local', email: 'local@test.com' }
      
      store.token = 'test-token'
      store.user = existingUser as User
      vi.mocked(localStorage.getItem).mockImplementation((key) => {
        if (key === 'user') return JSON.stringify(localStorageUser)
        return null
      })
      
      store.initUser()
      
      expect(store.user).toEqual(existingUser)
    })

    it('should handle invalid JSON in localStorage', () => {
      const store = useAuthStore()
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      
      store.token = 'test-token'
      vi.mocked(localStorage.getItem).mockImplementation((key) => {
        if (key === 'user') return 'invalid-json'
        return null
      })
      
      store.initUser()
      
      expect(consoleSpy).toHaveBeenCalledWith('初始化用户信息失败:', expect.any(Error))
      expect(store.user).toBeNull()
      expect(store.token).toBeNull()
      
      consoleSpy.mockRestore()
    })
  })

  describe('login', () => {
    it('should login successfully', async () => {
      const store = useAuthStore()
      const loginData: LoginRequest = {
        username: 'testuser',
        password: 'password123'
      }
      
      const mockResponse = {
        user: { id: 1, username: 'testuser', email: 'test@test.com' } as User,
        token: 'test-token'
      }
      
      mockedApiClient.login.mockResolvedValue(mockResponse)
      
      const result = await store.login(loginData)
      
      expect(mockedApiClient.login).toHaveBeenCalledWith(loginData)
      expect(store.user).toEqual(mockResponse.user)
      expect(store.token).toEqual(mockResponse.token)
      expect(vi.mocked(localStorage.setItem)).toHaveBeenCalledWith('token', 'test-token')
      expect(vi.mocked(localStorage.setItem)).toHaveBeenCalledWith('user', JSON.stringify(mockResponse.user))
      expect(result).toEqual(mockResponse)
    })

    it('should handle login error', async () => {
      const store = useAuthStore()
      const loginData: LoginRequest = {
        username: 'testuser',
        password: 'wrongpassword'
      }
      
      const error = new Error('Invalid credentials')
      mockedApiClient.login.mockRejectedValue(error)
      
      await expect(store.login(loginData)).rejects.toThrow('Invalid credentials')
      expect(store.user).toBeNull()
      expect(store.token).toBeNull()
    })
  })

  describe('register', () => {
    it('should register successfully', async () => {
      const store = useAuthStore()
      const registerData: RegisterRequest = {
        username: 'newuser',
        email: 'new@test.com',
        password: 'password123'
      }
      
      const mockUser = { id: 2, username: 'newuser', email: 'new@test.com' } as User
      mockedApiClient.register.mockResolvedValue(mockUser)
      
      const result = await store.register(registerData)
      
      expect(mockedApiClient.register).toHaveBeenCalledWith(registerData)
      expect(result).toEqual(mockUser)
    })

    it('should handle register error', async () => {
      const store = useAuthStore()
      const registerData: RegisterRequest = {
        username: 'newuser',
        email: 'new@test.com',
        password: 'password123'
      }
      
      const error = new Error('Username already exists')
      mockedApiClient.register.mockRejectedValue(error)
      
      await expect(store.register(registerData)).rejects.toThrow('Username already exists')
    })
  })

  describe('logout', () => {
    it('should clear user data and localStorage', () => {
      const store = useAuthStore()
      store.user = { id: 1, username: 'test', email: 'test@test.com' } as User
      store.token = 'test-token'
      
      store.logout()
      
      expect(store.user).toBeNull()
      expect(store.token).toBeNull()
      expect(vi.mocked(localStorage.removeItem)).toHaveBeenCalledWith('token')
      expect(vi.mocked(localStorage.removeItem)).toHaveBeenCalledWith('user')
    })
  })

  describe('updateUser', () => {
    it('should update user data and localStorage', () => {
      const store = useAuthStore()
      const originalUser = { id: 1, username: 'test', email: 'test@test.com' } as User
      const updatedUser = { id: 1, username: 'updated', email: 'updated@test.com' } as User
      
      store.user = originalUser
      
      store.updateUser(updatedUser)
      
      expect(store.user).toEqual(updatedUser)
      expect(vi.mocked(localStorage.setItem)).toHaveBeenCalledWith('user', JSON.stringify(updatedUser))
    })
  })
})
