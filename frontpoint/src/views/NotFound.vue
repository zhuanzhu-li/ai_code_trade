<template>
  <div class="not-found-container">
    <div class="not-found-content">
      <div class="not-found-icon">
        <el-icon size="120" color="#e6a23c">
          <Warning />
        </el-icon>
      </div>
      <h1 class="not-found-title">404</h1>
      <p class="not-found-description">抱歉，您访问的页面不存在</p>
      <div class="not-found-actions">
        <el-button type="primary" @click="goHome">
          返回首页
        </el-button>
        <el-button @click="goBack">
          返回上页
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { Warning } from '@element-plus/icons-vue'

const router = useRouter()

const goHome = () => {
  router.push('/dashboard')
}

const goBack = () => {
  router.go(-1)
}
</script>

<style lang="scss" scoped>
.not-found-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: #f5f7fa;
}

.not-found-content {
  text-align: center;
  padding: 40px;
}

.not-found-icon {
  margin-bottom: 24px;
}

.not-found-title {
  font-size: 72px;
  font-weight: 700;
  color: #e6a23c;
  margin: 0 0 16px 0;
}

.not-found-description {
  font-size: 18px;
  color: #606266;
  margin: 0 0 32px 0;
}

.not-found-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
}

@media (max-width: 480px) {
  .not-found-content {
    padding: 20px;
  }
  
  .not-found-title {
    font-size: 48px;
  }
  
  .not-found-actions {
    flex-direction: column;
    align-items: center;
  }
}
</style>
