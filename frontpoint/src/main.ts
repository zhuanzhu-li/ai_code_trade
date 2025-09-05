import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'

// Element Plus
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import 'element-plus/theme-chalk/dark/css-vars.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

// 全局样式
import './styles/index.scss'

// 进度条
import NProgress from 'nprogress'
import 'nprogress/nprogress.css'

// 配置进度条
NProgress.configure({ showSpinner: false })

const app = createApp(App)

// 注册Element Plus图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(createPinia())
app.use(router)
app.use(ElementPlus)

// 全局错误处理
app.config.errorHandler = (err, _vm, info) => {
  console.error('全局错误:', err, info)
}

app.mount('#app')
