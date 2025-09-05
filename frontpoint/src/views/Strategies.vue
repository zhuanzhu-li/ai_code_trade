<template>
  <div class="strategies">
    <Layout>
      <div class="strategies-content">
        <!-- 页面头部 -->
        <div class="page-header">
          <div class="header-left">
            <h1 class="page-title">策略管理</h1>
            <p class="page-subtitle">创建和管理您的交易策略</p>
          </div>
          <div class="header-right">
            <el-button type="primary" @click="showCreateDialog = true">
              <el-icon><Plus /></el-icon>
              创建策略
            </el-button>
          </div>
        </div>
        
        <!-- 策略统计 -->
        <div class="stats-grid">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon primary">
                <el-icon size="24"><Setting /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ strategyStore.totalStrategies }}</div>
                <div class="stat-label">总策略数</div>
              </div>
            </div>
          </el-card>
          
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon success">
                <el-icon size="24"><Check /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ strategyStore.activeStrategiesCount }}</div>
                <div class="stat-label">活跃策略</div>
              </div>
            </div>
          </el-card>
          
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon" :class="strategyStore.averageWinRate >= 50 ? 'success' : 'warning'">
                <el-icon size="24"><TrendCharts /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ strategyStore.averageWinRate.toFixed(1) }}%</div>
                <div class="stat-label">平均胜率</div>
              </div>
            </div>
          </el-card>
          
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon" :class="strategyStore.totalStrategyPnL >= 0 ? 'success' : 'danger'">
                <el-icon size="24"><Money /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value" :class="strategyStore.totalStrategyPnL >= 0 ? 'number-positive' : 'number-negative'">
                  ${{ strategyStore.totalStrategyPnL.toLocaleString() }}
                </div>
                <div class="stat-label">策略总盈亏</div>
              </div>
            </div>
          </el-card>
        </div>
        
        <!-- 策略列表 -->
        <div v-loading="strategyStore.loading" class="strategies-grid">
          <el-card
            v-for="strategy in strategyStore.strategies"
            :key="strategy.id"
            class="strategy-card"
            @click="viewStrategy(strategy)"
          >
            <div class="strategy-header">
              <div class="strategy-info">
                <h3 class="strategy-name">{{ strategy.name }}</h3>
                <p class="strategy-description">{{ strategy.description || '暂无描述' }}</p>
                <div class="strategy-meta">
                  <el-tag :type="getStrategyTypeColor(strategy.strategy_type)" size="small">
                    {{ getStrategyTypeName(strategy.strategy_type) }}
                  </el-tag>
                  <el-tag :type="strategy.is_active ? 'success' : 'info'" size="small">
                    {{ strategy.is_active ? '活跃' : '暂停' }}
                  </el-tag>
                </div>
              </div>
              <div class="strategy-actions">
                <el-button size="small" @click.stop="viewStrategy(strategy)">
                  查看
                </el-button>
                <el-button size="small" type="primary" @click.stop="editStrategy(strategy)">
                  编辑
                </el-button>
                <el-dropdown @command="(command) => handleStrategyAction(command, strategy)">
                  <el-button size="small">
                    更多<el-icon class="el-icon--right"><arrow-down /></el-icon>
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item v-if="strategy.is_active" command="stop">
                        停止策略
                      </el-dropdown-item>
                      <el-dropdown-item v-else command="start">
                        启动策略
                      </el-dropdown-item>
                      <el-dropdown-item command="execute">
                        执行策略
                      </el-dropdown-item>
                      <el-dropdown-item command="delete" divided>
                        删除
                      </el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
            </div>
            
            <div class="strategy-performance">
              <div class="performance-item">
                <div class="performance-label">总交易次数</div>
                <div class="performance-value">{{ strategy.performance.total_trades }}</div>
              </div>
              <div class="performance-item">
                <div class="performance-label">盈利交易</div>
                <div class="performance-value">{{ strategy.performance.winning_trades }}</div>
              </div>
              <div class="performance-item">
                <div class="performance-label">胜率</div>
                <div class="performance-value" :class="strategy.performance.win_rate >= 50 ? 'number-positive' : 'number-negative'">
                  {{ strategy.performance.win_rate.toFixed(1) }}%
                </div>
              </div>
              <div class="performance-item">
                <div class="performance-label">总盈亏</div>
                <div class="performance-value" :class="strategy.performance.total_pnl >= 0 ? 'number-positive' : 'number-negative'">
                  ${{ strategy.performance.total_pnl.toLocaleString() }}
                </div>
              </div>
            </div>
          </el-card>
        </div>
        
        <!-- 空状态 -->
        <div v-if="strategyStore.strategies.length === 0 && !strategyStore.loading" class="empty-state">
          <el-icon size="64" color="#c0c4cc">
            <Setting />
          </el-icon>
          <h3>暂无交易策略</h3>
          <p>创建您的第一个交易策略开始自动化交易</p>
          <el-button type="primary" @click="showCreateDialog = true">
            创建策略
          </el-button>
        </div>
      </div>
    </Layout>
    
    <!-- 创建/编辑策略对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingStrategy ? '编辑策略' : '创建策略'"
      width="600px"
      @close="resetForm"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="formRules"
        label-width="120px"
      >
        <el-form-item label="策略名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入策略名称" />
        </el-form-item>
        
        <el-form-item label="策略描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="请输入策略描述（可选）"
          />
        </el-form-item>
        
        <el-form-item label="策略类型" prop="strategy_type">
          <el-select v-model="form.strategy_type" placeholder="请选择策略类型" style="width: 100%">
            <el-option label="动量策略" value="momentum" />
            <el-option label="均值回归策略" value="mean_reversion" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="策略参数" prop="parameters">
          <div class="parameters-container">
            <div v-if="form.strategy_type === 'momentum'" class="parameter-group">
              <el-form-item label="回望周期" prop="parameters.lookback_period">
                <el-input-number
                  v-model="form.parameters?.lookback_period"
                  :min="5"
                  :max="100"
                  placeholder="回望周期"
                  style="width: 100%"
                />
              </el-form-item>
              <el-form-item label="RSI周期" prop="parameters.rsi_period">
                <el-input-number
                  v-model="form.parameters?.rsi_period"
                  :min="5"
                  :max="50"
                  placeholder="RSI周期"
                  style="width: 100%"
                />
              </el-form-item>
              <el-form-item label="仓位比例" prop="parameters.position_size_percentage">
                <el-input-number
                  v-model="form.parameters?.position_size_percentage"
                  :min="0.01"
                  :max="1"
                  :precision="2"
                  placeholder="仓位比例"
                  style="width: 100%"
                />
              </el-form-item>
            </div>
            
            <div v-else-if="form.strategy_type === 'mean_reversion'" class="parameter-group">
              <el-form-item label="布林带周期" prop="parameters.bb_period">
                <el-input-number
                  v-model="form.parameters?.bb_period"
                  :min="10"
                  :max="50"
                  placeholder="布林带周期"
                  style="width: 100%"
                />
              </el-form-item>
              <el-form-item label="布林带标准差" prop="parameters.bb_std">
                <el-input-number
                  v-model="form.parameters?.bb_std"
                  :min="1"
                  :max="3"
                  :precision="1"
                  placeholder="布林带标准差"
                  style="width: 100%"
                />
              </el-form-item>
              <el-form-item label="RSI周期" prop="parameters.rsi_period">
                <el-input-number
                  v-model="form.parameters?.rsi_period"
                  :min="5"
                  :max="50"
                  placeholder="RSI周期"
                  style="width: 100%"
                />
              </el-form-item>
              <el-form-item label="仓位比例" prop="parameters.position_size_percentage">
                <el-input-number
                  v-model="form.parameters?.position_size_percentage"
                  :min="0.01"
                  :max="1"
                  :precision="2"
                  placeholder="仓位比例"
                  style="width: 100%"
                />
              </el-form-item>
            </div>
          </div>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showCreateDialog = false">取消</el-button>
          <el-button type="primary" :loading="formLoading" @click="handleSubmit">
            {{ editingStrategy ? '更新' : '创建' }}
          </el-button>
        </div>
      </template>
    </el-dialog>
    
    <!-- 执行策略对话框 -->
    <el-dialog
      v-model="showExecuteDialog"
      title="执行策略"
      width="400px"
    >
      <el-form
        ref="executeFormRef"
        :model="executeForm"
        :rules="executeFormRules"
        label-width="100px"
      >
        <el-form-item label="投资组合" prop="portfolio_id">
          <el-select v-model="executeForm.portfolio_id" placeholder="请选择投资组合" style="width: 100%">
            <el-option
              v-for="portfolio in portfolioStore.portfolios"
              :key="portfolio.id"
              :label="portfolio.name"
              :value="portfolio.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="初始资金" prop="initial_capital">
          <el-input-number
            v-model="executeForm.initial_capital"
            :min="1000"
            :precision="2"
            placeholder="请输入初始资金"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showExecuteDialog = false">取消</el-button>
          <el-button type="primary" :loading="executeLoading" @click="handleExecute">
            开始执行
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import {
  Plus,
  Setting,
  Check,
  TrendCharts,
  Money,
  ArrowDown
} from '@element-plus/icons-vue'
import Layout from '@/components/Layout/index.vue'
import { useStrategyStore } from '@/stores/strategy'
import { usePortfolioStore } from '@/stores/portfolio'
import { useAuthStore } from '@/stores/auth'
import type { Strategy, CreateStrategyRequest, ExecuteStrategyRequest } from '@/types'

const router = useRouter()
const strategyStore = useStrategyStore()
const portfolioStore = usePortfolioStore()
const authStore = useAuthStore()

const showCreateDialog = ref(false)
const showExecuteDialog = ref(false)
const editingStrategy = ref<Strategy | null>(null)
const executingStrategy = ref<Strategy | null>(null)
const formLoading = ref(false)
const executeLoading = ref(false)
const formRef = ref<FormInstance>()
const executeFormRef = ref<FormInstance>()

const form = reactive<CreateStrategyRequest>({
  name: '',
  description: '',
  user_id: 0,
  strategy_type: 'momentum',
  parameters: {
    lookback_period: 20,
    rsi_period: 14,
    position_size_percentage: 0.1
  }
})

const executeForm = reactive<ExecuteStrategyRequest>({
  portfolio_id: 0,
  initial_capital: 10000
})

const formRules: FormRules = {
  name: [
    { required: true, message: '请输入策略名称', trigger: 'blur' },
    { min: 2, max: 50, message: '名称长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  strategy_type: [
    { required: true, message: '请选择策略类型', trigger: 'change' }
  ]
}

const executeFormRules: FormRules = {
  portfolio_id: [
    { required: true, message: '请选择投资组合', trigger: 'change' }
  ],
  initial_capital: [
    { required: true, message: '请输入初始资金', trigger: 'blur' },
    { type: 'number', min: 1000, message: '初始资金不能少于1000', trigger: 'blur' }
  ]
}

// 获取策略类型颜色
const getStrategyTypeColor = (type: string): 'primary' | 'success' | 'warning' | 'info' | 'danger' => {
  const colorMap: Record<string, 'primary' | 'success' | 'warning' | 'info' | 'danger'> = {
    'momentum': 'primary',
    'mean_reversion': 'success'
  }
  return colorMap[type] || 'info'
}

// 获取策略类型名称
const getStrategyTypeName = (type: string) => {
  const nameMap: Record<string, string> = {
    'momentum': '动量策略',
    'mean_reversion': '均值回归策略'
  }
  return nameMap[type] || type
}

// 查看策略详情
const viewStrategy = (strategy: Strategy) => {
  router.push(`/strategies/${strategy.id}`)
}

// 编辑策略
const editStrategy = (strategy: Strategy) => {
  editingStrategy.value = strategy
  form.name = strategy.name
  form.description = strategy.description || ''
  form.strategy_type = strategy.strategy_type
  form.parameters = { ...strategy.parameters }
  showCreateDialog.value = true
}

// 处理策略操作
const handleStrategyAction = async (command: string, strategy: Strategy) => {
  switch (command) {
    case 'start':
      await startStrategy(strategy)
      break
    case 'stop':
      await stopStrategy(strategy)
      break
    case 'execute':
      await executeStrategy(strategy)
      break
    case 'delete':
      await deleteStrategy(strategy)
      break
  }
}

// 启动策略
const startStrategy = async (strategy: Strategy) => {
  try {
    strategy.is_active = true
    strategyStore.updateStrategy(strategy)
    ElMessage.success('策略已启动')
  } catch (error) {
    ElMessage.error('启动失败')
  }
}

// 停止策略
const stopStrategy = async (strategy: Strategy) => {
  try {
    await ElMessageBox.confirm('确定要停止这个策略吗？', '确认停止', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await strategyStore.stopStrategy(strategy.id)
    ElMessage.success('策略已停止')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('停止失败')
    }
  }
}

// 执行策略
const executeStrategy = (strategy: Strategy) => {
  executingStrategy.value = strategy
  executeForm.portfolio_id = 0
  executeForm.initial_capital = 10000
  showExecuteDialog.value = true
}

// 删除策略
const deleteStrategy = async (strategy: Strategy) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除策略"${strategy.name}"吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 这里应该调用API删除策略
    const index = strategyStore.strategies.findIndex(s => s.id === strategy.id)
    if (index !== -1) {
      strategyStore.strategies.splice(index, 1)
    }
    ElMessage.success('策略已删除')
  } catch (error) {
    // 用户取消删除
  }
}

// 重置表单
const resetForm = () => {
  editingStrategy.value = null
  form.name = ''
  form.description = ''
  form.strategy_type = 'momentum'
  form.parameters = {
    lookback_period: 20,
    rsi_period: 14,
    position_size_percentage: 0.1
  }
  formRef.value?.clearValidate()
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    formLoading.value = true
    
    if (editingStrategy.value) {
      // 更新策略
      const strategy = { ...editingStrategy.value, ...form }
      strategyStore.updateStrategy(strategy)
      ElMessage.success('策略已更新')
    } else {
      // 创建策略
      form.user_id = authStore.user?.id || 0
      await strategyStore.createStrategy(form)
      ElMessage.success('策略创建成功')
    }
    
    showCreateDialog.value = false
    resetForm()
  } catch (error) {
    console.error('操作失败:', error)
  } finally {
    formLoading.value = false
  }
}

// 执行策略
const handleExecute = async () => {
  if (!executeFormRef.value || !executingStrategy.value) return
  
  try {
    await executeFormRef.value.validate()
    executeLoading.value = true
    
    await strategyStore.executeStrategy(executingStrategy.value.id, executeForm)
    ElMessage.success('策略开始执行')
    showExecuteDialog.value = false
  } catch (error) {
    console.error('执行策略失败:', error)
  } finally {
    executeLoading.value = false
  }
}

// 初始化数据
onMounted(async () => {
  try {
    const userId = authStore.user?.id
    if (userId) {
      await Promise.all([
        strategyStore.fetchStrategies(userId),
        portfolioStore.fetchPortfolios(userId)
      ])
    }
  } catch (error) {
    console.error('初始化数据失败:', error)
  }
})
</script>

<style lang="scss" scoped>
.strategies {
  height: 100vh;
  overflow: hidden;
}

.strategies-content {
  height: 100%;
  overflow-y: auto;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
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

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  .stat-content {
    display: flex;
    align-items: center;
    gap: 16px;
  }
  
  .stat-icon {
    width: 48px;
    height: 48px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    
    &.primary {
      background: #e6f7ff;
      color: #409eff;
    }
    
    &.success {
      background: #f6ffed;
      color: #67c23a;
    }
    
    &.warning {
      background: #fffbe6;
      color: #e6a23c;
    }
    
    &.danger {
      background: #fff2f0;
      color: #f56c6c;
    }
  }
  
  .stat-info {
    flex: 1;
  }
  
  .stat-value {
    font-size: 20px;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 4px;
  }
  
  .stat-label {
    font-size: 12px;
    color: var(--text-secondary);
  }
}

.strategies-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.strategy-card {
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid var(--border-light);
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-base);
    border-color: var(--primary-color);
  }
  
  .strategy-header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    margin-bottom: 16px;
  }
  
  .strategy-info {
    flex: 1;
    
    .strategy-name {
      font-size: 18px;
      font-weight: 600;
      color: var(--text-primary);
      margin: 0 0 4px 0;
    }
    
    .strategy-description {
      font-size: 14px;
      color: var(--text-secondary);
      margin: 0 0 8px 0;
      line-height: 1.4;
    }
    
    .strategy-meta {
      display: flex;
      gap: 8px;
    }
  }
  
  .strategy-actions {
    display: flex;
    gap: 8px;
  }
  
  .strategy-performance {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }
  
  .performance-item {
    .performance-label {
      font-size: 12px;
      color: var(--text-secondary);
      margin-bottom: 4px;
    }
    
    .performance-value {
      font-size: 16px;
      font-weight: 600;
      color: var(--text-primary);
    }
  }
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-secondary);
  
  .el-icon {
    margin-bottom: 16px;
  }
  
  h3 {
    font-size: 18px;
    margin: 0 0 8px 0;
    color: var(--text-primary);
  }
  
  p {
    margin: 0 0 24px 0;
  }
}

.parameters-container {
  .parameter-group {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
  }
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

@media (max-width: 768px) {
  .strategies-grid {
    grid-template-columns: 1fr;
  }
  
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .strategy-performance {
    grid-template-columns: 1fr;
  }
  
  .parameter-group {
    grid-template-columns: 1fr;
  }
}
</style>
