# API文档自动生成系统

## 概述

本项目已集成Flask-RESTX来自动生成API文档，替代手动维护的API文档方式。新系统提供以下优势：

- ✅ **自动同步**：文档与代码实时同步
- ✅ **交互式测试**：内置API测试界面
- ✅ **类型验证**：自动验证请求/响应格式
- ✅ **美观界面**：现代化的Swagger UI界面
- ✅ **完整覆盖**：100%的API端点覆盖

## 快速开始

### 1. 安装依赖

```bash
cd endpoint
pip install -r requirements.txt
```

### 2. 启动服务

```bash
python app.py
```

### 3. 访问API文档

打开浏览器访问：http://localhost:5000/api/docs/

## 文档结构

### 自动生成的文档

- **Swagger UI**: http://localhost:5000/api/docs/
- **OpenAPI JSON**: http://localhost:5000/api/swagger.json

### 传统文档（已弃用）

- **Markdown文档**: `API_DOCUMENTATION.md` (仅作参考)

## API端点分类

### 1. 用户认证 (`/api/auth/`)
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `GET /api/auth/me` - 获取当前用户信息

### 2. 用户管理 (`/api/users/`)
- `POST /api/users` - 创建用户
- `GET /api/users/{user_id}` - 获取用户信息

### 3. 投资组合管理 (`/api/portfolios/`)
- `GET /api/portfolios` - 获取投资组合列表
- `POST /api/portfolios` - 创建投资组合
- `GET /api/portfolios/{id}` - 获取投资组合详情
- `GET /api/portfolios/{id}/positions` - 获取持仓信息

### 4. 交易管理 (`/api/trades/`)
- `GET /api/trades` - 获取交易记录
- `POST /api/trades` - 创建交易

### 5. 策略管理 (`/api/strategies/`)
- `GET /api/strategies` - 获取策略列表
- `POST /api/strategies` - 创建策略
- `POST /api/strategies/{id}/execute` - 执行策略

### 6. 市场数据 (`/api/market-data/`)
- `GET /api/market-data/{symbol}/latest` - 获取最新价格
- `GET /api/market-data/{symbol}` - 获取历史数据
- `GET /api/market-data/symbols` - 获取股票列表

### 7. 风险管理 (`/api/risk/`)
- `GET /api/risk/rules` - 获取风险规则
- `POST /api/risk/rules` - 创建风险规则

### 8. 仪表板 (`/api/dashboard/`)
- `GET /api/dashboard/stats` - 获取统计数据

### 9. 系统 (`/api/system/`)
- `GET /api/system/health` - 健康检查
- `GET /api/system/info` - 系统信息

## 开发指南

### 添加新的API端点

1. **在 `restx_routes.py` 中添加新的Resource类**：

```python
@your_ns.route('/your-endpoint')
class YourEndpoint(Resource):
    @your_ns.expect(your_input_model)
    @your_ns.marshal_with(success_response_model, code=200)
    @token_required
    def post(self, current_user_id):
        """你的API端点描述"""
        # 实现逻辑
        return success_response(data, '操作成功')
```

2. **在 `api_docs.py` 中定义数据模型**：

```python
your_input_model = api.model('YourInput', {
    'field1': fields.String(required=True, description='字段1描述'),
    'field2': fields.Integer(description='字段2描述')
})
```

3. **注册到命名空间**：

```python
your_ns = api.namespace('your-module', description='你的模块描述')
```

### 数据模型定义

```python
# 输入模型
input_model = api.model('InputModel', {
    'required_field': fields.String(required=True, description='必填字段'),
    'optional_field': fields.Integer(description='可选字段'),
    'nested_field': fields.Nested(nested_model, description='嵌套字段')
})

# 输出模型
output_model = api.model('OutputModel', {
    'id': fields.Integer(description='ID'),
    'name': fields.String(description='名称'),
    'created_at': fields.DateTime(description='创建时间')
})
```

### 响应格式

所有API都使用统一的响应格式：

```json
{
    "code": 200,
    "msg": "成功！",
    "data": {
        // 实际数据
    }
}
```

## 工具和脚本

### 1. API同步检查

```bash
python scripts/check_api_docs.py
```

检查代码与文档的同步状态，生成报告。

### 2. API报告生成

脚本会自动生成 `api_report.json` 文件，包含：
- 所有API端点列表
- 按模块分组的统计
- 文档覆盖率

## 迁移指南

### 从传统API到RESTX API

1. **保持向后兼容**：传统API仍然可用，路径为 `/api/legacy/`
2. **逐步迁移**：可以逐步将API迁移到RESTX
3. **统一响应格式**：新API使用统一的响应格式

### 前端集成

```javascript
// 使用新的API端点
const response = await fetch('/api/portfolios', {
    method: 'GET',
    headers: {
        'Authorization': `Bearer ${token}`
    }
});

const data = await response.json();
// data.code, data.msg, data.data
```

## 最佳实践

### 1. 文档注释

```python
@your_ns.route('/endpoint')
class YourEndpoint(Resource):
    @your_ns.expect(input_model)
    @your_ns.marshal_with(output_model)
    def post(self):
        """
        详细的API描述
        
        参数说明：
        - param1: 参数1的详细说明
        - param2: 参数2的详细说明
        
        返回值：
        - 成功时返回数据对象
        - 失败时返回错误信息
        """
        pass
```

### 2. 错误处理

```python
try:
    # 业务逻辑
    result = process_data()
    return success_response(result, '操作成功')
except ValidationError as e:
    return business_error_response(ResponseCode.VALIDATION_ERROR, str(e))
except Exception as e:
    return system_error_response(ResponseCode.INTERNAL_ERROR, str(e))
```

### 3. 参数验证

```python
@your_ns.route('/endpoint')
class YourEndpoint(Resource):
    @your_ns.expect(input_model, validate=True)  # 启用验证
    def post(self):
        # 参数已自动验证
        pass
```

## 故障排除

### 常见问题

1. **Swagger UI无法访问**
   - 检查Flask-RESTX是否正确安装
   - 确认蓝图是否正确注册

2. **API端点不显示**
   - 检查Resource类是否正确继承
   - 确认命名空间是否正确注册

3. **数据模型验证失败**
   - 检查字段定义是否正确
   - 确认required字段是否提供

### 调试技巧

1. **查看Swagger JSON**：访问 `/api/swagger.json`
2. **检查控制台日志**：查看Flask应用日志
3. **使用API测试工具**：Postman、Insomnia等

## 更新日志

### v1.0.0 (2024-01-20)
- ✅ 集成Flask-RESTX
- ✅ 实现自动API文档生成
- ✅ 添加交互式测试界面
- ✅ 建立文档同步检查机制
- ✅ 提供完整的API覆盖

## 贡献指南

1. 添加新API时，请同时更新RESTX路由
2. 保持数据模型的一致性
3. 添加适当的文档注释
4. 运行同步检查脚本确保文档更新

## 联系方式

如有问题或建议，请通过以下方式联系：
- 邮箱: your-email@example.com
- GitHub: https://github.com/your-username/ai-code-trade
