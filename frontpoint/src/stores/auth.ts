import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiClient } from '@/api'
import type { User, LoginRequest, RegisterRequest } from '@/types'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('token'))

  const isAuthenticated = computed(() => !!token.value && !!user.value)

  // 初始化用户信息
  const initUser = async () => {
    if (token.value && !user.value) {
      try {
        // 这里需要根据实际API调整，假设有一个获取当前用户信息的接口
        const userData = localStorage.getItem('user')
        if (userData) {
          user.value = JSON.parse(userData)
        }
      } catch (error) {
        console.error('初始化用户信息失败:', error)
        logout()
      }
    }
  }

  // 登录
  const login = async (loginData: LoginRequest) => {
    try {
      const response = await apiClient.login(loginData)
      user.value = response.user
      token.value = response.token
      
      localStorage.setItem('token', response.token)
      localStorage.setItem('user', JSON.stringify(response.user))
      
      return response
    } catch (error) {
      throw error
    }
  }

  // 注册
  const register = async (registerData: RegisterRequest) => {
    try {
      const newUser = await apiClient.register(registerData)
      return newUser
    } catch (error) {
      throw error
    }
  }

  // 登出
  const logout = () => {
    user.value = null
    token.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  // 更新用户信息
  const updateUser = (userData: User) => {
    user.value = userData
    localStorage.setItem('user', JSON.stringify(userData))
  }

  return {
    user,
    token,
    isAuthenticated,
    initUser,
    login,
    register,
    logout,
    updateUser
  }
})
