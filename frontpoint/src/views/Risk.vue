<template>
  <div class="risk">
    <Layout>
      <div class="risk-content">
        <!-- 页面头部 -->
        <div class="page-header">
          <div class="header-left">
            <h1 class="page-title">风险管理</h1>
            <p class="page-subtitle">监控和管理交易风险</p>
          </div>
          <div class="header-right">
            <el-button type="primary" @click="showCreateRuleDialog = true">
              <el-icon><Plus /></el-icon>
              创建风险规则
            </el-button>
          </div>
        </div>
        
        <!-- 风险概览 -->
        <div class="risk-overview">
          <el-card class="overview-card">
            <div class="overview-content">
              <div class="risk-metrics">
                <div class="metric-item">
                  <div class="metric-icon warning">
                    <el-icon size="24"><Warning /></el-icon>
                  </div>
                  <div class="metric-info">
                    <div class="metric-value">{{ riskAlerts.length }}</div>
                    <div class="metric-label">活跃警报</div>
                  </div>
                </div>
                
                <div class="metric-item">
                  <div class="metric-icon success">
                    <el-icon size="24"><Check /></el-icon>
                  </div>
                  <div class="metric-info">
                    <div class="metric-value">{{ riskRules.length }}</div>
                    <div class="metric-label">风险规则</div>
                  </div>
                </div>
                
                <div class="metric-item">
                  <div class="metric-icon info">
                    <el-icon size="24"><TrendCharts /></el-icon>
                  </div>
                  <div class="metric-info">
                    <div class="metric-value">{{ activeRulesCount }}</div>
                    <div class="metric-label">活跃规则</div>
                  </div>
                </div>
                
                <div class="metric-item">
                  <div class="metric-icon" :class="overallRiskLevel">
                    <el-icon size="24"><CircleCheck /></el-icon>
                  </div>
                  <div class="metric-info">
                    <div class="metric-value">{{ getRiskLevelText(overallRiskLevel) }}</div>
                    <div class="metric-label">整体风险等级</div>
                  </div>
                </div>
              </div>
            </div>
          </el-card>
        </div>
        
        <!-- 风险警报 -->
        <el-card class="alerts-card">
          <template #header>
            <div class="card-header">
              <h3 class="card-title">风险警报</h3>
              <div class="card-actions">
                <el-button size="small" @click="refreshAlerts">
                  <el-icon><Refresh /></el-icon>
                  刷新
                </el-button>
                <el-button size="small" @click="markAllResolved">
                  全部标记为已解决
                </el-button>
              </div>
            </div>
          </template>
          
          <div v-if="riskAlerts.length === 0" class="empty-container">
            <el-icon size="48" color="#c0c4cc">
              <Check />
            </el-icon>
            <p>暂无风险警报</p>
          </div>
          
          <div v-else class="alerts-list">
            <div
              v-for="alert in riskAlerts"
              :key="alert.id"
              class="alert-item"
              :class="alert.alert_type"
            >
              <div class="alert-icon">
                <el-icon>
                  <Warning v-if="alert.alert_type === 'warning'" />
                  <CircleClose v-else-if="alert.alert_type === 'error'" />
                  <InfoFilled v-else />
                </el-icon>
              </div>
              <div class="alert-content">
                <div class="alert-message">{{ alert.message }}</div>
                <div class="alert-meta">
                  <span class="alert-time">{{ formatTime(alert.created_at) }}</span>
                  <el-tag :type="alert.is_resolved ? 'success' : 'warning'" size="small">
                    {{ alert.is_resolved ? '已解决' : '未解决' }}
                  </el-tag>
                </div>
              </div>
              <div v-if="!alert.is_resolved" class="alert-actions">
                <el-button size="small" type="primary" @click="resolveAlert(alert)">
                  标记为已解决
                </el-button>
              </div>
            </div>
          </div>
        </el-card>
        
        <!-- 风险规则 -->
        <el-card class="rules-card">
          <template #header>
            <div class="card-header">
              <h3 class="card-title">风险规则</h3>
              <div class="card-actions">
                <el-button size="small" @click="refreshRules">
                  <el-icon><Refresh /></el-icon>
                  刷新
                </el-button>
              </div>
            </div>
          </template>
          
          <el-table :data="riskRules" style="width: 100%">
            <el-table-column prop="name" label="规则名称" width="200" />
            <el-table-column prop="description" label="描述" min-width="200" />
            <el-table-column prop="rule_type" label="规则类型" width="120">
              <template #default="{ row }">
                <el-tag :type="getRuleTypeColor(row.rule_type)" size="small">
                  {{ getRuleTypeName(row.rule_type) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="parameters" label="参数" width="200">
              <template #default="{ row }">
                <div class="parameters-display">
                  <div v-for="(value, key) in row.parameters" :key="key" class="parameter-item">
                    <span class="parameter-key">{{ key }}:</span>
                    <span class="parameter-value">{{ value }}</span>
                  </div>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="is_active" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
                  {{ row.is_active ? '活跃' : '暂停' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="160">
              <template #default="{ row }">
                {{ formatTime(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150" fixed="right">
              <template #default="{ row }">
                <el-button size="small" type="text" @click="editRule(row)">
                  编辑
                </el-button>
                <el-button
                  size="small"
                  type="text"
                  @click="toggleRule(row)"
                >
                  {{ row.is_active ? '暂停' : '激活' }}
                </el-button>
                <el-button
                  size="small"
                  type="text"
                  class="danger-text"
                  @click="deleteRule(row)"
                >
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </div>
    </Layout>
    
    <!-- 创建/编辑风险规则对话框 -->
    <el-dialog
      v-model="showCreateRuleDialog"
      :title="editingRule ? '编辑风险规则' : '创建风险规则'"
      width="600px"
      @close="resetRuleForm"
    >
      <el-form
        ref="ruleFormRef"
        :model="ruleForm"
        :rules="ruleFormRules"
        label-width="120px"
      >
        <el-form-item label="规则名称" prop="name">
          <el-input v-model="ruleForm.name" placeholder="请输入规则名称" />
        </el-form-item>
        
        <el-form-item label="规则描述" prop="description">
          <el-input
            v-model="ruleForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入规则描述（可选）"
          />
        </el-form-item>
        
        <el-form-item label="规则类型" prop="rule_type">
          <el-select v-model="ruleForm.rule_type" placeholder="请选择规则类型" style="width: 100%">
            <el-option label="持仓大小限制" value="position_size" />
            <el-option label="日损失限制" value="daily_loss" />
            <el-option label="最大回撤控制" value="max_drawdown" />
            <el-option label="交易频率限制" value="trading_frequency" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="规则参数" prop="parameters">
          <div class="parameters-container">
            <div v-if="ruleForm.rule_type === 'position_size'" class="parameter-group">
              <el-form-item label="最大持仓金额" prop="parameters.max_position_size">
                <el-input-number
                  v-model="ruleForm.parameters?.max_position_size"
                  :min="0"
                  :precision="2"
                  placeholder="最大持仓金额"
                  style="width: 100%"
                />
              </el-form-item>
              <el-form-item label="最大持仓比例" prop="parameters.max_position_percentage">
                <el-input-number
                  v-model="ruleForm.parameters?.max_position_percentage"
                  :min="0"
                  :max="100"
                  :precision="2"
                  placeholder="最大持仓比例(%)"
                  style="width: 100%"
                />
              </el-form-item>
            </div>
            
            <div v-else-if="ruleForm.rule_type === 'daily_loss'" class="parameter-group">
              <el-form-item label="最大日损失" prop="parameters.max_daily_loss">
                <el-input-number
                  v-model="ruleForm.parameters?.max_daily_loss"
                  :min="0"
                  :precision="2"
                  placeholder="最大日损失"
                  style="width: 100%"
                />
              </el-form-item>
            </div>
            
            <div v-else-if="ruleForm.rule_type === 'max_drawdown'" class="parameter-group">
              <el-form-item label="最大回撤比例" prop="parameters.max_drawdown_percentage">
                <el-input-number
                  v-model="ruleForm.parameters?.max_drawdown_percentage"
                  :min="0"
                  :max="100"
                  :precision="2"
                  placeholder="最大回撤比例(%)"
                  style="width: 100%"
                />
              </el-form-item>
            </div>
            
            <div v-else-if="ruleForm.rule_type === 'trading_frequency'" class="parameter-group">
              <el-form-item label="最大交易次数" prop="parameters.max_trades_per_day">
                <el-input-number
                  v-model="ruleForm.parameters?.max_trades_per_day"
                  :min="1"
                  placeholder="每日最大交易次数"
                  style="width: 100%"
                />
              </el-form-item>
            </div>
          </div>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showCreateRuleDialog = false">取消</el-button>
          <el-button type="primary" :loading="ruleFormLoading" @click="handleRuleSubmit">
            {{ editingRule ? '更新' : '创建' }}
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import {
  Plus,
  Warning,
  Check,
  TrendCharts,
  CircleCheck,
  CircleClose,
  InfoFilled,
  Refresh
} from '@element-plus/icons-vue'
import Layout from '@/components/Layout/index.vue'
import { apiClient } from '@/api'
import type { RiskRule, RiskAlert, CreateRiskRuleRequest } from '@/types'
import dayjs from 'dayjs'

const showCreateRuleDialog = ref(false)
const editingRule = ref<RiskRule | null>(null)
const ruleFormLoading = ref(false)
const ruleFormRef = ref<FormInstance>()

// 风险规则和警报数据
const riskRules = ref<RiskRule[]>([])
const riskAlerts = ref<RiskAlert[]>([])

// 风险规则表单
const ruleForm = reactive<CreateRiskRuleRequest>({
  name: '',
  description: '',
  rule_type: 'position_size',
  parameters: {
    max_position_size: 10000,
    max_position_percentage: 20
  }
})

const ruleFormRules: FormRules = {
  name: [
    { required: true, message: '请输入规则名称', trigger: 'blur' },
    { min: 2, max: 50, message: '名称长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  rule_type: [
    { required: true, message: '请选择规则类型', trigger: 'change' }
  ]
}

// 活跃规则数量
const activeRulesCount = computed(() => 
  riskRules.value.filter(rule => rule.is_active).length
)

// 整体风险等级
const overallRiskLevel = computed(() => {
  const alertCount = riskAlerts.value.filter(alert => !alert.is_resolved).length
  if (alertCount === 0) return 'success'
  if (alertCount <= 2) return 'warning'
  return 'danger'
})

// 获取风险等级文本
const getRiskLevelText = (level: string) => {
  const levelMap: Record<string, string> = {
    'success': '低风险',
    'warning': '中风险',
    'danger': '高风险'
  }
  return levelMap[level] || '未知'
}

// 获取规则类型颜色
const getRuleTypeColor = (type: string): 'primary' | 'success' | 'warning' | 'info' | 'danger' => {
  const colorMap: Record<string, 'primary' | 'success' | 'warning' | 'info' | 'danger'> = {
    'position_size': 'primary',
    'daily_loss': 'danger',
    'max_drawdown': 'warning',
    'trading_frequency': 'info'
  }
  return colorMap[type] || 'info'
}

// 获取规则类型名称
const getRuleTypeName = (type: string) => {
  const nameMap: Record<string, string> = {
    'position_size': '持仓大小限制',
    'daily_loss': '日损失限制',
    'max_drawdown': '最大回撤控制',
    'trading_frequency': '交易频率限制'
  }
  return nameMap[type] || type
}

// 刷新警报
const refreshAlerts = async () => {
  try {
    riskAlerts.value = await apiClient.getRiskAlerts()
    ElMessage.success('警报数据已刷新')
  } catch (error) {
    ElMessage.error('刷新失败')
  }
}

// 刷新规则
const refreshRules = async () => {
  try {
    riskRules.value = await apiClient.getRiskRules()
    ElMessage.success('规则数据已刷新')
  } catch (error) {
    ElMessage.error('刷新失败')
  }
}

// 标记所有警报为已解决
const markAllResolved = async () => {
  try {
    await ElMessageBox.confirm('确定要标记所有警报为已解决吗？', '确认操作', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    // 这里应该调用API标记所有警报为已解决
    riskAlerts.value.forEach(alert => {
      alert.is_resolved = true
      alert.resolved_at = new Date().toISOString()
    })
    ElMessage.success('所有警报已标记为已解决')
  } catch (error) {
    // 用户取消
  }
}

// 解决警报
const resolveAlert = async (alert: RiskAlert) => {
  try {
    // 这里应该调用API解决警报
    alert.is_resolved = true
    alert.resolved_at = new Date().toISOString()
    ElMessage.success('警报已标记为已解决')
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

// 编辑规则
const editRule = (rule: RiskRule) => {
  editingRule.value = rule
  ruleForm.name = rule.name
  ruleForm.description = rule.description || ''
  ruleForm.rule_type = rule.rule_type
  ruleForm.parameters = { ...rule.parameters }
  showCreateRuleDialog.value = true
}

// 切换规则状态
const toggleRule = async (rule: RiskRule) => {
  try {
    rule.is_active = !rule.is_active
    // 这里应该调用API更新规则状态
    ElMessage.success(`规则已${rule.is_active ? '激活' : '暂停'}`)
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

// 删除规则
const deleteRule = async (rule: RiskRule) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除规则"${rule.name}"吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 这里应该调用API删除规则
    const index = riskRules.value.findIndex(r => r.id === rule.id)
    if (index !== -1) {
      riskRules.value.splice(index, 1)
    }
    ElMessage.success('规则已删除')
  } catch (error) {
    // 用户取消删除
  }
}

// 重置规则表单
const resetRuleForm = () => {
  editingRule.value = null
  ruleForm.name = ''
  ruleForm.description = ''
  ruleForm.rule_type = 'position_size'
  ruleForm.parameters = {
    max_position_size: 10000,
    max_position_percentage: 20
  }
  ruleFormRef.value?.clearValidate()
}

// 提交规则表单
const handleRuleSubmit = async () => {
  if (!ruleFormRef.value) return
  
  try {
    await ruleFormRef.value.validate()
    ruleFormLoading.value = true
    
    if (editingRule.value) {
      // 更新规则
      const rule = { ...editingRule.value, ...ruleForm }
      const index = riskRules.value.findIndex(r => r.id === rule.id)
      if (index !== -1) {
        riskRules.value[index] = rule
      }
      ElMessage.success('规则已更新')
    } else {
      // 创建规则
      const newRule = await apiClient.createRiskRule(ruleForm)
      riskRules.value.push(newRule)
      ElMessage.success('规则创建成功')
    }
    
    showCreateRuleDialog.value = false
    resetRuleForm()
  } catch (error) {
    console.error('操作失败:', error)
  } finally {
    ruleFormLoading.value = false
  }
}

// 格式化时间
const formatTime = (time: string) => {
  return dayjs(time).format('MM-DD HH:mm')
}

// 初始化数据
onMounted(async () => {
  try {
    await Promise.all([
      refreshRules(),
      refreshAlerts()
    ])
  } catch (error) {
    console.error('初始化风险管理数据失败:', error)
  }
})
</script>

<style lang="scss" scoped>
.risk {
  height: 100vh;
  overflow: hidden;
}

.risk-content {
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

.risk-overview {
  margin-bottom: 24px;
}

.overview-card {
  .overview-content {
    .risk-metrics {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 24px;
    }
    
    .metric-item {
      display: flex;
      align-items: center;
      gap: 16px;
    }
    
    .metric-icon {
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
      
      &.info {
        background: #f4f4f5;
        color: #909399;
      }
    }
    
    .metric-info {
      .metric-value {
        font-size: 24px;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 4px;
      }
      
      .metric-label {
        font-size: 14px;
        color: var(--text-secondary);
      }
    }
  }
}

.alerts-card {
  margin-bottom: 24px;
  
  .card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  
  .card-actions {
    display: flex;
    gap: 8px;
  }
  
  .empty-container {
    text-align: center;
    padding: 40px;
    color: var(--text-secondary);
  }
  
  .alerts-list {
    .alert-item {
      display: flex;
      align-items: center;
      gap: 16px;
      padding: 16px;
      border-radius: 8px;
      margin-bottom: 12px;
      border-left: 4px solid;
      
      &.warning {
        background: #fff7e6;
        border-left-color: #e6a23c;
      }
      
      &.error {
        background: #fff2f0;
        border-left-color: #f56c6c;
      }
      
      &.info {
        background: #f0f9ff;
        border-left-color: #409eff;
      }
      
      .alert-icon {
        font-size: 20px;
        color: var(--text-primary);
      }
      
      .alert-content {
        flex: 1;
        
        .alert-message {
          font-size: 14px;
          color: var(--text-primary);
          margin-bottom: 4px;
        }
        
        .alert-meta {
          display: flex;
          align-items: center;
          gap: 12px;
          
          .alert-time {
            font-size: 12px;
            color: var(--text-secondary);
          }
        }
      }
      
      .alert-actions {
        display: flex;
        gap: 8px;
      }
    }
  }
}

.rules-card {
  .card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  
  .card-actions {
    display: flex;
    gap: 8px;
  }
  
  .parameters-display {
    .parameter-item {
      display: flex;
      gap: 8px;
      margin-bottom: 4px;
      
      .parameter-key {
        font-size: 12px;
        color: var(--text-secondary);
        min-width: 80px;
      }
      
      .parameter-value {
        font-size: 12px;
        color: var(--text-primary);
      }
    }
  }
  
  .danger-text {
    color: var(--danger-color);
  }
}

.parameters-container {
  .parameter-group {
    display: grid;
    grid-template-columns: 1fr;
    gap: 16px;
  }
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .risk-metrics {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .alert-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .alert-actions {
    width: 100%;
    justify-content: flex-end;
  }
}
</style>
