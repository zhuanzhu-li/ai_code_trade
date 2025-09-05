<template>
  <div class="portfolios">
    <Layout>
      <div class="portfolios-content">
        <!-- 页面头部 -->
        <div class="page-header">
          <div class="header-left">
            <h1 class="page-title">投资组合管理</h1>
            <p class="page-subtitle">管理您的投资组合和资产配置</p>
          </div>
          <div class="header-right">
            <el-button type="primary" @click="showCreateDialog = true">
              <el-icon><Plus /></el-icon>
              创建投资组合
            </el-button>
          </div>
        </div>
        
        <!-- 投资组合列表 -->
        <div v-loading="portfolioStore.loading" class="portfolios-grid">
          <el-card
            v-for="portfolio in portfolioStore.portfolios"
            :key="portfolio.id"
            class="portfolio-card"
            @click="selectPortfolio(portfolio)"
          >
            <div class="portfolio-header">
              <div class="portfolio-info">
                <h3 class="portfolio-name">{{ portfolio.name }}</h3>
                <p class="portfolio-description">{{ portfolio.description || '暂无描述' }}</p>
              </div>
              <div class="portfolio-status">
                <el-tag :type="portfolio.is_active ? 'success' : 'info'" size="small">
                  {{ portfolio.is_active ? '活跃' : '暂停' }}
                </el-tag>
              </div>
            </div>
            
            <div class="portfolio-stats">
              <div class="stat-item">
                <div class="stat-label">总价值</div>
                <div class="stat-value">${{ portfolio.current_value.toLocaleString() }}</div>
              </div>
              <div class="stat-item">
                <div class="stat-label">现金余额</div>
                <div class="stat-value">${{ portfolio.cash_balance.toLocaleString() }}</div>
              </div>
              <div class="stat-item">
                <div class="stat-label">总盈亏</div>
                <div class="stat-value" :class="portfolio.total_pnl >= 0 ? 'number-positive' : 'number-negative'">
                  ${{ portfolio.total_pnl.toLocaleString() }}
                </div>
              </div>
              <div class="stat-item">
                <div class="stat-label">盈亏率</div>
                <div class="stat-value" :class="portfolio.total_pnl_percentage >= 0 ? 'number-positive' : 'number-negative'">
                  {{ portfolio.total_pnl_percentage.toFixed(2) }}%
                </div>
              </div>
            </div>
            
            <div class="portfolio-actions">
              <el-button size="small" @click.stop="viewPortfolio(portfolio)">
                查看详情
              </el-button>
              <el-button size="small" type="primary" @click.stop="editPortfolio(portfolio)">
                编辑
              </el-button>
              <el-dropdown @command="(command) => handlePortfolioAction(command, portfolio)">
                <el-button size="small">
                  更多<el-icon class="el-icon--right"><arrow-down /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="toggle">
                      {{ portfolio.is_active ? '暂停' : '激活' }}
                    </el-dropdown-item>
                    <el-dropdown-item command="delete" divided>
                      删除
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </el-card>
        </div>
        
        <!-- 空状态 -->
        <div v-if="portfolioStore.portfolios.length === 0 && !portfolioStore.loading" class="empty-state">
          <el-icon size="64" color="#c0c4cc">
            <Wallet />
          </el-icon>
          <h3>暂无投资组合</h3>
          <p>创建您的第一个投资组合开始交易</p>
          <el-button type="primary" @click="showCreateDialog = true">
            创建投资组合
          </el-button>
        </div>
      </div>
    </Layout>
    
    <!-- 创建/编辑投资组合对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingPortfolio ? '编辑投资组合' : '创建投资组合'"
      width="500px"
      @close="resetForm"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="组合名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入投资组合名称" />
        </el-form-item>
        
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="请输入投资组合描述（可选）"
          />
        </el-form-item>
        
        <el-form-item label="初始资金" prop="initial_capital">
          <el-input-number
            v-model="form.initial_capital"
            :min="0"
            :precision="2"
            placeholder="请输入初始资金"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showCreateDialog = false">取消</el-button>
          <el-button type="primary" :loading="formLoading" @click="handleSubmit">
            {{ editingPortfolio ? '更新' : '创建' }}
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
import { Plus, Wallet, ArrowDown } from '@element-plus/icons-vue'
import Layout from '@/components/Layout/index.vue'
import { usePortfolioStore } from '@/stores/portfolio'
import { useAuthStore } from '@/stores/auth'
import type { Portfolio, CreatePortfolioRequest } from '@/types'

const router = useRouter()
const portfolioStore = usePortfolioStore()
const authStore = useAuthStore()

const showCreateDialog = ref(false)
const editingPortfolio = ref<Portfolio | null>(null)
const formLoading = ref(false)
const formRef = ref<FormInstance>()

const form = reactive<CreatePortfolioRequest>({
  name: '',
  description: '',
  user_id: 0,
  initial_capital: 10000
})

const formRules: FormRules = {
  name: [
    { required: true, message: '请输入投资组合名称', trigger: 'blur' },
    { min: 2, max: 50, message: '名称长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  initial_capital: [
    { required: true, message: '请输入初始资金', trigger: 'blur' },
    { type: 'number', min: 0, message: '初始资金不能小于0', trigger: 'blur' }
  ]
}

// 选择投资组合
const selectPortfolio = (portfolio: Portfolio) => {
  portfolioStore.currentPortfolio = portfolio
  router.push(`/portfolios/${portfolio.id}`)
}

// 查看投资组合详情
const viewPortfolio = (portfolio: Portfolio) => {
  router.push(`/portfolios/${portfolio.id}`)
}

// 编辑投资组合
const editPortfolio = (portfolio: Portfolio) => {
  editingPortfolio.value = portfolio
  form.name = portfolio.name
  form.description = portfolio.description || ''
  form.initial_capital = portfolio.initial_capital
  showCreateDialog.value = true
}

// 处理投资组合操作
const handlePortfolioAction = async (command: string, portfolio: Portfolio) => {
  switch (command) {
    case 'toggle':
      await togglePortfolio(portfolio)
      break
    case 'delete':
      await deletePortfolio(portfolio)
      break
  }
}

// 切换投资组合状态
const togglePortfolio = async (portfolio: Portfolio) => {
  try {
    // 这里应该调用API更新投资组合状态
    portfolio.is_active = !portfolio.is_active
    portfolioStore.updatePortfolio(portfolio)
    ElMessage.success(`投资组合已${portfolio.is_active ? '激活' : '暂停'}`)
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

// 删除投资组合
const deletePortfolio = async (portfolio: Portfolio) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除投资组合"${portfolio.name}"吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 这里应该调用API删除投资组合
    const index = portfolioStore.portfolios.findIndex(p => p.id === portfolio.id)
    if (index !== -1) {
      portfolioStore.portfolios.splice(index, 1)
    }
    ElMessage.success('投资组合已删除')
  } catch (error) {
    // 用户取消删除
  }
}

// 重置表单
const resetForm = () => {
  editingPortfolio.value = null
  form.name = ''
  form.description = ''
  form.initial_capital = 10000
  formRef.value?.clearValidate()
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    formLoading.value = true
    
    if (editingPortfolio.value) {
      // 更新投资组合
      // 这里应该调用API更新投资组合
      const portfolio = { ...editingPortfolio.value, ...form }
      portfolioStore.updatePortfolio(portfolio)
      ElMessage.success('投资组合已更新')
    } else {
      // 创建投资组合
      form.user_id = authStore.user?.id || 0
      await portfolioStore.createPortfolio(form)
      ElMessage.success('投资组合创建成功')
    }
    
    showCreateDialog.value = false
    resetForm()
  } catch (error) {
    console.error('操作失败:', error)
  } finally {
    formLoading.value = false
  }
}

// 初始化数据
onMounted(async () => {
  try {
    const userId = authStore.user?.id
    if (userId) {
      await portfolioStore.fetchPortfolios(userId)
    }
  } catch (error) {
    console.error('获取投资组合列表失败:', error)
  }
})
</script>

<style lang="scss" scoped>
.portfolios {
  height: 100vh;
  overflow: hidden;
}

.portfolios-content {
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

.portfolios-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.portfolio-card {
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid var(--border-light);
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-base);
    border-color: var(--primary-color);
  }
  
  .portfolio-header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    margin-bottom: 16px;
  }
  
  .portfolio-info {
    flex: 1;
    
    .portfolio-name {
      font-size: 18px;
      font-weight: 600;
      color: var(--text-primary);
      margin: 0 0 4px 0;
    }
    
    .portfolio-description {
      font-size: 14px;
      color: var(--text-secondary);
      margin: 0;
      line-height: 1.4;
    }
  }
  
  .portfolio-stats {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    margin-bottom: 16px;
  }
  
  .stat-item {
    .stat-label {
      font-size: 12px;
      color: var(--text-secondary);
      margin-bottom: 4px;
    }
    
    .stat-value {
      font-size: 16px;
      font-weight: 600;
      color: var(--text-primary);
    }
  }
  
  .portfolio-actions {
    display: flex;
    gap: 8px;
    justify-content: flex-end;
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

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

@media (max-width: 768px) {
  .portfolios-grid {
    grid-template-columns: 1fr;
  }
  
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .portfolio-stats {
    grid-template-columns: 1fr;
  }
  
  .portfolio-actions {
    flex-wrap: wrap;
  }
}
</style>
