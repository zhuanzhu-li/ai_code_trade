import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/dashboard'
    },
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/Login.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/register',
      name: 'Register',
      component: () => import('@/views/Register.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/dashboard',
      name: 'Dashboard',
      component: () => import('@/views/Dashboard.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/portfolios',
      name: 'Portfolios',
      component: () => import('@/views/Portfolios.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/portfolios/:id',
      name: 'PortfolioDetail',
      component: () => import('@/views/PortfolioDetail.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/trading',
      name: 'Trading',
      component: () => import('@/views/Trading.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/strategies',
      name: 'Strategies',
      component: () => import('@/views/Strategies.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/strategies/:id',
      name: 'StrategyDetail',
      component: () => import('@/views/StrategyDetail.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/market',
      name: 'Market',
      component: () => import('@/views/Market.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/risk',
      name: 'Risk',
      component: () => import('@/views/Risk.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/settings',
      name: 'Settings',
      component: () => import('@/views/Settings.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'NotFound',
      component: () => import('@/views/NotFound.vue')
    }
  ]
})

// 路由守卫
router.beforeEach(async (to, _from, next) => {
  const authStore = useAuthStore()
  
  // 初始化用户信息
  if (!authStore.user && authStore.token) {
    await authStore.initUser()
  }
  
  // 检查是否需要认证
  if (to.meta.requiresAuth) {
    if (!authStore.isAuthenticated) {
      ElMessage.warning('请先登录')
      next('/login')
      return
    }
  }
  
  // 如果已登录且访问登录/注册页面，重定向到仪表板
  if ((to.name === 'Login' || to.name === 'Register') && authStore.isAuthenticated) {
    next('/dashboard')
    return
  }
  
  next()
})

export default router
