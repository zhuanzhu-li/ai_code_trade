<template>
  <div class="layout-container">
    <!-- 侧边栏 -->
    <div class="sidebar" :class="{ collapsed: sidebarCollapsed }">
      <div class="sidebar-header">
        <div class="logo">
          <el-icon size="24" color="#409eff">
            <TrendCharts />
          </el-icon>
          <span v-if="!sidebarCollapsed" class="logo-text">量化交易</span>
        </div>
        <el-button
          type="text"
          :icon="sidebarCollapsed ? Expand : Fold"
          class="collapse-btn"
          @click="toggleSidebar"
        />
      </div>
      
      <el-menu
        :default-active="activeMenu"
        :collapse="sidebarCollapsed"
        :unique-opened="true"
        router
        class="sidebar-menu"
      >
        <el-menu-item index="/dashboard">
          <el-icon><Odometer /></el-icon>
          <span>仪表板</span>
        </el-menu-item>
        
        <el-menu-item index="/portfolios">
          <el-icon><Wallet /></el-icon>
          <span>投资组合</span>
        </el-menu-item>
        
        <el-menu-item index="/trading">
          <el-icon><TrendCharts /></el-icon>
          <span>交易管理</span>
        </el-menu-item>
        
        <el-menu-item index="/strategies">
          <el-icon><Setting /></el-icon>
          <span>策略管理</span>
        </el-menu-item>
        
        <el-menu-item index="/market">
          <el-icon><DataLine /></el-icon>
          <span>市场数据</span>
        </el-menu-item>
        
        <el-menu-item index="/risk">
          <el-icon><Warning /></el-icon>
          <span>风险管理</span>
        </el-menu-item>
      </el-menu>
    </div>
    
    <!-- 主内容区 -->
    <div class="main-container">
      <!-- 顶部导航栏 -->
      <div class="header">
        <div class="header-left">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item
              v-for="item in breadcrumbs"
              :key="item.path"
              :to="item.path"
            >
              {{ item.name }}
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        
        <div class="header-right">
          <!-- 主题切换 -->
          <el-tooltip content="切换主题" placement="bottom">
            <el-button
              type="text"
              :icon="isDark ? Sunny : Moon"
              class="theme-btn"
              @click="toggleTheme"
            />
          </el-tooltip>
          
          <!-- 用户菜单 -->
          <el-dropdown @command="handleUserCommand">
            <div class="user-info">
              <el-avatar :size="32" :src="userAvatar">
                {{ userStore.user?.username?.charAt(0).toUpperCase() }}
              </el-avatar>
              <span class="username">{{ userStore.user?.username }}</span>
              <el-icon><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>
                  个人资料
                </el-dropdown-item>
                <el-dropdown-item command="settings">
                  <el-icon><Setting /></el-icon>
                  系统设置
                </el-dropdown-item>
                <el-dropdown-item divided command="logout">
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
      
      <!-- 页面内容 -->
      <div class="content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  TrendCharts,
  Expand,
  Fold,
  Odometer,
  Wallet,
  Setting,
  DataLine,
  Warning,
  Sunny,
  Moon,
  ArrowDown,
  User,
  SwitchButton
} from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const userStore = useAuthStore()

const sidebarCollapsed = ref(false)
const isDark = ref(false)

const activeMenu = computed(() => route.path)

const userAvatar = computed(() => {
  // 这里可以从用户信息中获取头像URL
  return ''
})

const breadcrumbs = computed(() => {
  const matched = route.matched.filter(item => item.meta && item.meta.title)
  const breadcrumbMap: Record<string, string> = {
    '/dashboard': '仪表板',
    '/portfolios': '投资组合',
    '/trading': '交易管理',
    '/strategies': '策略管理',
    '/market': '市场数据',
    '/risk': '风险管理',
    '/settings': '系统设置'
  }
  
  return matched.map(item => ({
    name: breadcrumbMap[item.path] || item.meta?.title || '未知页面',
    path: item.path
  }))
})

const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

const toggleTheme = () => {
  isDark.value = !isDark.value
  document.documentElement.classList.toggle('dark', isDark.value)
  localStorage.setItem('theme', isDark.value ? 'dark' : 'light')
}

const handleUserCommand = async (command: string) => {
  switch (command) {
    case 'profile':
      ElMessage.info('个人资料功能开发中')
      break
    case 'settings':
      router.push('/settings')
      break
    case 'logout':
      try {
        await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        userStore.logout()
        ElMessage.success('已退出登录')
        router.push('/login')
      } catch {
        // 用户取消
      }
      break
  }
}

// 初始化主题
const initTheme = () => {
  const savedTheme = localStorage.getItem('theme')
  if (savedTheme === 'dark') {
    isDark.value = true
    document.documentElement.classList.add('dark')
  }
}

// 监听路由变化，更新面包屑
watch(route, () => {
  // 可以在这里添加其他路由变化时的逻辑
}, { immediate: true })

// 初始化
initTheme()
</script>

<style lang="scss" scoped>
.layout-container {
  display: flex;
  height: 100vh;
  background: var(--bg-page);
}

.sidebar {
  width: 240px;
  background: var(--bg-base);
  border-right: 1px solid var(--border-light);
  transition: width 0.3s ease;
  overflow: hidden;
  
  &.collapsed {
    width: 64px;
  }
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  border-bottom: 1px solid var(--border-light);
  height: 64px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.logo-text {
  white-space: nowrap;
  transition: opacity 0.3s ease;
}

.collapse-btn {
  padding: 4px;
  font-size: 16px;
}

.sidebar-menu {
  border: none;
  height: calc(100vh - 64px);
  overflow-y: auto;
  
  .el-menu-item {
    height: 48px;
    line-height: 48px;
    
    &:hover {
      background: var(--bg-light);
    }
    
    &.is-active {
      background: #e6f7ff;
      color: var(--primary-color);
    }
  }
}

.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.header {
  height: 64px;
  background: var(--bg-base);
  border-bottom: 1px solid var(--border-light);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  box-shadow: var(--shadow-light);
}

.header-left {
  flex: 1;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.theme-btn {
  font-size: 18px;
  padding: 8px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.3s ease;
  
  &:hover {
    background: var(--bg-light);
  }
}

.username {
  font-size: 14px;
  color: var(--text-primary);
  white-space: nowrap;
}

.content {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
  background: var(--bg-page);
}

// 响应式设计
@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    left: 0;
    top: 0;
    height: 100vh;
    z-index: 1000;
    transform: translateX(-100%);
    transition: transform 0.3s ease;
    
    &:not(.collapsed) {
      transform: translateX(0);
    }
  }
  
  .main-container {
    margin-left: 0;
  }
  
  .header {
    padding: 0 16px;
  }
  
  .content {
    padding: 16px;
  }
  
  .username {
    display: none;
  }
}

// 动画
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
