<template>
  <div class="settings">
    <Layout>
      <div class="settings-content">
        <!-- 页面头部 -->
        <div class="page-header">
          <div class="header-left">
            <h1 class="page-title">系统设置</h1>
            <p class="page-subtitle">管理您的账户和系统偏好</p>
          </div>
        </div>
        
        <!-- 设置内容 -->
        <div class="settings-container">
          <el-tabs v-model="activeTab" class="settings-tabs">
            <!-- 账户设置 -->
            <el-tab-pane label="账户设置" name="account">
              <el-card class="settings-card">
                <template #header>
                  <h3 class="card-title">个人信息</h3>
                </template>
                
                <el-form
                  ref="profileFormRef"
                  :model="profileForm"
                  :rules="profileFormRules"
                  label-width="100px"
                  class="settings-form"
                >
                  <el-form-item label="用户名" prop="username">
                    <el-input v-model="profileForm.username" disabled />
                  </el-form-item>
                  
                  <el-form-item label="邮箱" prop="email">
                    <el-input v-model="profileForm.email" />
                  </el-form-item>
                  
                  <el-form-item>
                    <el-button type="primary" :loading="profileLoading" @click="updateProfile">
                      更新个人信息
                    </el-button>
                  </el-form-item>
                </el-form>
              </el-card>
              
              <el-card class="settings-card">
                <template #header>
                  <h3 class="card-title">修改密码</h3>
                </template>
                
                <el-form
                  ref="passwordFormRef"
                  :model="passwordForm"
                  :rules="passwordFormRules"
                  label-width="100px"
                  class="settings-form"
                >
                  <el-form-item label="当前密码" prop="currentPassword">
                    <el-input
                      v-model="passwordForm.currentPassword"
                      type="password"
                      show-password
                    />
                  </el-form-item>
                  
                  <el-form-item label="新密码" prop="newPassword">
                    <el-input
                      v-model="passwordForm.newPassword"
                      type="password"
                      show-password
                    />
                  </el-form-item>
                  
                  <el-form-item label="确认密码" prop="confirmPassword">
                    <el-input
                      v-model="passwordForm.confirmPassword"
                      type="password"
                      show-password
                    />
                  </el-form-item>
                  
                  <el-form-item>
                    <el-button type="primary" :loading="passwordLoading" @click="updatePassword">
                      修改密码
                    </el-button>
                  </el-form-item>
                </el-form>
              </el-card>
            </el-tab-pane>
            
            <!-- 交易设置 -->
            <el-tab-pane label="交易设置" name="trading">
              <el-card class="settings-card">
                <template #header>
                  <h3 class="card-title">默认交易参数</h3>
                </template>
                
                <el-form
                  ref="tradingFormRef"
                  :model="tradingForm"
                  :rules="tradingFormRules"
                  label-width="120px"
                  class="settings-form"
                >
                  <el-form-item label="默认手续费率" prop="defaultFeeRate">
                    <el-input-number
                      v-model="tradingForm.defaultFeeRate"
                      :min="0"
                      :max="1"
                      :precision="4"
                      placeholder="手续费率"
                      style="width: 200px"
                    />
                    <span class="form-tip">（例如：0.001 表示 0.1%）</span>
                  </el-form-item>
                  
                  <el-form-item label="默认仓位比例" prop="defaultPositionSize">
                    <el-input-number
                      v-model="tradingForm.defaultPositionSize"
                      :min="0.01"
                      :max="1"
                      :precision="2"
                      placeholder="仓位比例"
                      style="width: 200px"
                    />
                    <span class="form-tip">（例如：0.1 表示 10%）</span>
                  </el-form-item>
                  
                  <el-form-item label="最大持仓数量" prop="maxPositions">
                    <el-input-number
                      v-model="tradingForm.maxPositions"
                      :min="1"
                      :max="50"
                      placeholder="最大持仓数量"
                      style="width: 200px"
                    />
                  </el-form-item>
                  
                  <el-form-item>
                    <el-button type="primary" :loading="tradingLoading" @click="updateTradingSettings">
                      保存交易设置
                    </el-button>
                  </el-form-item>
                </el-form>
              </el-card>
            </el-tab-pane>
            
            <!-- 通知设置 -->
            <el-tab-pane label="通知设置" name="notifications">
              <el-card class="settings-card">
                <template #header>
                  <h3 class="card-title">通知偏好</h3>
                </template>
                
                <el-form
                  ref="notificationFormRef"
                  :model="notificationForm"
                  label-width="150px"
                  class="settings-form"
                >
                  <el-form-item label="邮件通知">
                    <el-switch v-model="notificationForm.emailEnabled" />
                    <span class="form-tip">接收邮件通知</span>
                  </el-form-item>
                  
                  <el-form-item label="交易通知">
                    <el-switch v-model="notificationForm.tradeNotifications" />
                    <span class="form-tip">交易执行通知</span>
                  </el-form-item>
                  
                  <el-form-item label="风险警报">
                    <el-switch v-model="notificationForm.riskAlerts" />
                    <span class="form-tip">风险警报通知</span>
                  </el-form-item>
                  
                  <el-form-item label="策略通知">
                    <el-switch v-model="notificationForm.strategyNotifications" />
                    <span class="form-tip">策略执行通知</span>
                  </el-form-item>
                  
                  <el-form-item>
                    <el-button type="primary" :loading="notificationLoading" @click="updateNotificationSettings">
                      保存通知设置
                    </el-button>
                  </el-form-item>
                </el-form>
              </el-card>
            </el-tab-pane>
            
            <!-- 系统设置 -->
            <el-tab-pane label="系统设置" name="system">
              <el-card class="settings-card">
                <template #header>
                  <h3 class="card-title">界面设置</h3>
                </template>
                
                <el-form
                  ref="systemFormRef"
                  :model="systemForm"
                  label-width="120px"
                  class="settings-form"
                >
                  <el-form-item label="主题模式">
                    <el-radio-group v-model="systemForm.theme">
                      <el-radio label="light">浅色模式</el-radio>
                      <el-radio label="dark">深色模式</el-radio>
                      <el-radio label="auto">跟随系统</el-radio>
                    </el-radio-group>
                  </el-form-item>
                  
                  <el-form-item label="语言">
                    <el-select v-model="systemForm.language" style="width: 200px">
                      <el-option label="简体中文" value="zh-CN" />
                      <el-option label="English" value="en-US" />
                    </el-select>
                  </el-form-item>
                  
                  <el-form-item label="时区">
                    <el-select v-model="systemForm.timezone" style="width: 200px">
                      <el-option label="北京时间 (UTC+8)" value="Asia/Shanghai" />
                      <el-option label="纽约时间 (UTC-5)" value="America/New_York" />
                      <el-option label="伦敦时间 (UTC+0)" value="Europe/London" />
                    </el-select>
                  </el-form-item>
                  
                  <el-form-item>
                    <el-button type="primary" :loading="systemLoading" @click="updateSystemSettings">
                      保存系统设置
                    </el-button>
                  </el-form-item>
                </el-form>
              </el-card>
              
              <el-card class="settings-card">
                <template #header>
                  <h3 class="card-title">数据管理</h3>
                </template>
                
                <div class="data-management">
                  <div class="data-item">
                    <div class="data-info">
                      <h4>导出数据</h4>
                      <p>导出您的交易记录和投资组合数据</p>
                    </div>
                    <el-button @click="exportData">导出数据</el-button>
                  </div>
                  
                  <div class="data-item">
                    <div class="data-info">
                      <h4>清除缓存</h4>
                      <p>清除本地缓存数据，释放存储空间</p>
                    </div>
                    <el-button @click="clearCache">清除缓存</el-button>
                  </div>
                  
                  <div class="data-item danger">
                    <div class="data-info">
                      <h4>重置账户</h4>
                      <p>删除所有数据并重置账户（不可恢复）</p>
                    </div>
                    <el-button type="danger" @click="resetAccount">重置账户</el-button>
                  </div>
                </div>
              </el-card>
            </el-tab-pane>
          </el-tabs>
        </div>
      </div>
    </Layout>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import Layout from '@/components/Layout/index.vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

const activeTab = ref('account')
const profileLoading = ref(false)
const passwordLoading = ref(false)
const tradingLoading = ref(false)
const notificationLoading = ref(false)
const systemLoading = ref(false)

const profileFormRef = ref<FormInstance>()
const passwordFormRef = ref<FormInstance>()
const tradingFormRef = ref<FormInstance>()
const notificationFormRef = ref<FormInstance>()
const systemFormRef = ref<FormInstance>()

// 个人信息表单
const profileForm = reactive({
  username: '',
  email: ''
})

const profileFormRules: FormRules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ]
}

// 密码修改表单
const passwordForm = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const validateConfirmPassword = (_rule: any, value: any, callback: any) => {
  if (value !== passwordForm.newPassword) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const passwordFormRules: FormRules = {
  currentPassword: [
    { required: true, message: '请输入当前密码', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度在 6 到 20 个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

// 交易设置表单
const tradingForm = reactive({
  defaultFeeRate: 0.001,
  defaultPositionSize: 0.1,
  maxPositions: 10
})

const tradingFormRules: FormRules = {
  defaultFeeRate: [
    { required: true, message: '请输入默认手续费率', trigger: 'blur' },
    { type: 'number', min: 0, max: 1, message: '手续费率应在 0 到 1 之间', trigger: 'blur' }
  ],
  defaultPositionSize: [
    { required: true, message: '请输入默认仓位比例', trigger: 'blur' },
    { type: 'number', min: 0.01, max: 1, message: '仓位比例应在 0.01 到 1 之间', trigger: 'blur' }
  ]
}

// 通知设置表单
const notificationForm = reactive({
  emailEnabled: true,
  tradeNotifications: true,
  riskAlerts: true,
  strategyNotifications: false
})

// 系统设置表单
const systemForm = reactive({
  theme: 'light',
  language: 'zh-CN',
  timezone: 'Asia/Shanghai'
})

// 更新个人信息
const updateProfile = async () => {
  if (!profileFormRef.value) return
  
  try {
    await profileFormRef.value.validate()
    profileLoading.value = true
    
    // 这里应该调用API更新个人信息
    authStore.updateUser({ ...authStore.user!, ...profileForm })
    ElMessage.success('个人信息已更新')
  } catch (error) {
    console.error('更新个人信息失败:', error)
  } finally {
    profileLoading.value = false
  }
}

// 修改密码
const updatePassword = async () => {
  if (!passwordFormRef.value) return
  
  try {
    await passwordFormRef.value.validate()
    passwordLoading.value = true
    
    // 这里应该调用API修改密码
    ElMessage.success('密码修改成功')
    passwordForm.currentPassword = ''
    passwordForm.newPassword = ''
    passwordForm.confirmPassword = ''
    passwordFormRef.value.resetFields()
  } catch (error) {
    console.error('修改密码失败:', error)
  } finally {
    passwordLoading.value = false
  }
}

// 更新交易设置
const updateTradingSettings = async () => {
  if (!tradingFormRef.value) return
  
  try {
    await tradingFormRef.value.validate()
    tradingLoading.value = true
    
    // 这里应该调用API更新交易设置
    ElMessage.success('交易设置已保存')
  } catch (error) {
    console.error('更新交易设置失败:', error)
  } finally {
    tradingLoading.value = false
  }
}

// 更新通知设置
const updateNotificationSettings = async () => {
  try {
    notificationLoading.value = true
    
    // 这里应该调用API更新通知设置
    ElMessage.success('通知设置已保存')
  } catch (error) {
    console.error('更新通知设置失败:', error)
  } finally {
    notificationLoading.value = false
  }
}

// 更新系统设置
const updateSystemSettings = async () => {
  try {
    systemLoading.value = true
    
    // 这里应该调用API更新系统设置
    ElMessage.success('系统设置已保存')
  } catch (error) {
    console.error('更新系统设置失败:', error)
  } finally {
    systemLoading.value = false
  }
}

// 导出数据
const exportData = () => {
  ElMessage.info('导出功能开发中')
}

// 清除缓存
const clearCache = () => {
  ElMessage.success('缓存已清除')
}

// 重置账户
const resetAccount = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要重置账户吗？这将删除所有数据且不可恢复！',
      '确认重置',
      {
        confirmButtonText: '确定重置',
        cancelButtonText: '取消',
        type: 'error'
      }
    )
    
    // 这里应该调用API重置账户
    ElMessage.success('账户已重置')
  } catch (error) {
    // 用户取消重置
  }
}

// 初始化数据
onMounted(() => {
  if (authStore.user) {
    profileForm.username = authStore.user.username
    profileForm.email = authStore.user.email
  }
})
</script>

<style lang="scss" scoped>
.settings {
  height: 100vh;
  overflow: hidden;
}

.settings-content {
  height: 100%;
  overflow-y: auto;
}

.page-header {
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-light);
}

.header-left {
  .page-title {
    font-size: 24px;
    font-weight: 600;
    color: var(--text-primary);
    margin: 0 0 4px 0;
  }
  
  .page-subtitle {
    font-size: 14px;
    color: var(--text-secondary);
    margin: 0;
  }
}

.settings-container {
  .settings-tabs {
    .el-tabs__content {
      padding: 0;
    }
  }
  
  .settings-card {
    margin-bottom: 24px;
    
    .card-title {
      font-size: 16px;
      font-weight: 600;
      color: var(--text-primary);
      margin: 0;
    }
    
    .settings-form {
      max-width: 600px;
      
      .form-tip {
        margin-left: 8px;
        font-size: 12px;
        color: var(--text-secondary);
      }
    }
  }
  
  .data-management {
    .data-item {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 16px 0;
      border-bottom: 1px solid var(--border-light);
      
      &:last-child {
        border-bottom: none;
      }
      
      &.danger {
        .data-info h4 {
          color: var(--danger-color);
        }
      }
      
      .data-info {
        flex: 1;
        
        h4 {
          font-size: 16px;
          font-weight: 600;
          color: var(--text-primary);
          margin: 0 0 4px 0;
        }
        
        p {
          font-size: 14px;
          color: var(--text-secondary);
          margin: 0;
        }
      }
    }
  }
}

@media (max-width: 768px) {
  .settings-form {
    max-width: 100%;
  }
  
  .data-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
}
</style>
