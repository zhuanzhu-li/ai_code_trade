import { vi } from 'vitest'
import { config } from '@vue/test-utils'

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
  length: 0,
  key: vi.fn()
}

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock
})

// Mock Element Plus
vi.mock('element-plus', () => ({
  ElMessage: {
    success: vi.fn(),
    error: vi.fn(),
    warning: vi.fn(),
    info: vi.fn()
  },
  ElMessageBox: {
    confirm: vi.fn(),
    alert: vi.fn(),
    prompt: vi.fn()
  },
  ElContainer: { name: 'ElContainer' },
  ElHeader: { name: 'ElHeader' },
  ElMain: { name: 'ElMain' },
  ElAside: { name: 'ElAside' },
  ElMenu: { name: 'ElMenu' },
  ElMenuItem: { name: 'ElMenuItem' },
  ElSubMenu: { name: 'ElSubMenu' },
  ElIcon: { name: 'ElIcon' },
  ElDropdown: { name: 'ElDropdown' },
  ElDropdownMenu: { name: 'ElDropdownMenu' },
  ElDropdownItem: { name: 'ElDropdownItem' },
  ElAvatar: { name: 'ElAvatar' },
  ElButton: { name: 'ElButton' },
  ElForm: { name: 'ElForm' },
  ElFormItem: { name: 'ElFormItem' },
  ElInput: { name: 'ElInput' },
  ElCard: { name: 'ElCard' },
  ElLink: { name: 'ElLink' },
  ElBreadcrumb: { name: 'ElBreadcrumb' },
  ElBreadcrumbItem: { name: 'ElBreadcrumbItem' },
  ElTooltip: { name: 'ElTooltip' }
}))

// Mock axios
vi.mock('axios', () => ({
  default: {
    create: vi.fn(() => ({
      interceptors: {
        request: {
          use: vi.fn()
        },
        response: {
          use: vi.fn()
        }
      },
      request: vi.fn()
    }))
  }
}))

// Mock Element Plus Icons
vi.mock('@element-plus/icons-vue', () => ({
  Menu: { name: 'Menu' },
  User: { name: 'User' },
  Setting: { name: 'Setting' },
  Logout: { name: 'Logout' },
  TrendCharts: { name: 'TrendCharts' },
  Expand: { name: 'Expand' },
  Fold: { name: 'Fold' },
  Odometer: { name: 'Odometer' },
  Wallet: { name: 'Wallet' },
  DataLine: { name: 'DataLine' },
  Warning: { name: 'Warning' },
  Sunny: { name: 'Sunny' },
  Moon: { name: 'Moon' },
  ArrowDown: { name: 'ArrowDown' },
  SwitchButton: { name: 'SwitchButton' },
  Lock: { name: 'Lock' }
}))

// Mock js-cookie
vi.mock('js-cookie', () => ({
  get: vi.fn(),
  set: vi.fn(),
  remove: vi.fn()
}))

// Mock nprogress
vi.mock('nprogress', () => ({
  start: vi.fn(),
  done: vi.fn(),
  configure: vi.fn()
}))

// Mock ECharts
vi.mock('echarts', () => ({
  init: vi.fn(() => ({
    setOption: vi.fn(),
    resize: vi.fn(),
    dispose: vi.fn()
  })),
  dispose: vi.fn()
}))

// Mock vue-echarts
vi.mock('vue-echarts', () => ({
  default: {
    name: 'VChart'
  }
}))

// Global test utilities
global.ResizeObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn()
}))

// Mock window.location
delete (window as any).location
window.location = {
  href: 'http://localhost:3000',
  assign: vi.fn(),
  replace: vi.fn(),
  reload: vi.fn()
} as any

// Mock Vue Router
vi.mock('vue-router', () => ({
  useRoute: () => ({
    path: '/',
    matched: []
  }),
  useRouter: () => ({
    push: vi.fn(),
    replace: vi.fn(),
    go: vi.fn(),
    back: vi.fn(),
    forward: vi.fn()
  }),
  createRouter: vi.fn(),
  createWebHistory: vi.fn()
}))

// Vue Test Utils global config
config.global.mocks = {
  $t: (key: string) => key
}
