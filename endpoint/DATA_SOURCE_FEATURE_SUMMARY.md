# 数据来源功能实现总结

## 概述

本次更新为量化交易系统添加了完整的数据来源管理功能，包括数据来源表、symbols和market_data表的数据来源标识，以及相关的API和服务。

## 主要功能

### 1. 数据库结构更新

#### 新增数据来源表 (data_sources)
- `id`: 主键
- `name`: 数据来源名称（唯一）
- `uri`: 数据来源URI
- `description`: 数据来源描述
- `provider_type`: 提供商类型（akshare/yahoo/alpha_vantage等）
- `is_active`: 是否激活
- `priority`: 优先级（数字越小优先级越高）
- `config`: JSON格式的配置信息
- `last_updated`: 最后更新时间
- `created_at`: 创建时间
- `updated_at`: 更新时间

#### 修改现有表
- **symbols表**: 添加 `data_source_id` 字段，关联到数据来源表
- **market_data表**: 添加 `data_source_id` 字段，关联到数据来源表

### 2. 模型更新

#### DataSource模型 (`models/data_source.py`)
- 完整的数据来源模型定义
- 支持配置信息的JSON存储和解析
- 提供 `to_dict()` 方法用于API响应

#### Symbol和MarketData模型更新
- 添加数据来源关联字段
- 更新 `to_dict()` 方法包含数据来源信息
- 建立与DataSource的外键关系

### 3. 数据库迁移

#### 迁移脚本 (`database/migrations/v1.3.0_add_data_source_support.sql`)
- 创建数据来源表
- 为symbols和market_data表添加数据来源字段
- 添加外键约束和索引
- 插入默认数据来源（AKShare、Yahoo Finance等）
- 创建数据来源统计视图

### 4. API接口

#### 数据来源管理API
- `GET /api/data-sources` - 获取数据来源列表（支持分页和筛选）
- `POST /api/data-sources` - 创建数据来源
- `GET /api/data-sources/<id>` - 获取数据来源详情
- `PUT /api/data-sources/<id>` - 更新数据来源
- `DELETE /api/data-sources/<id>` - 删除数据来源
- `GET /api/data-sources/<id>/statistics` - 获取数据来源统计信息
- `POST /api/data-sources/<id>/test` - 测试数据来源连接

### 5. 服务更新

#### MarketDataService更新
- 自动获取或创建数据来源记录
- 在同步symbols和market_data时自动关联数据来源
- 健康检查包含数据来源信息

### 6. 响应代码更新

#### 新增错误代码
- `DATA_SOURCE_EXISTS` (10014): 数据来源名称已存在
- `DATA_SOURCE_IN_USE` (10015): 数据来源正在使用中
- `CREATE_ERROR` (50010): 创建失败
- `UPDATE_ERROR` (50011): 更新失败
- `DELETE_ERROR` (50012): 删除失败
- `TEST_ERROR` (50013): 测试失败

## 使用示例

### 1. 创建数据来源
```python
data_source = DataSource(
    name="AKShare数据源",
    uri="https://akshare.akfamily.xyz/",
    description="AKShare开源财经数据接口库",
    provider_type="akshare",
    is_active=True,
    priority=1,
    config={"api_base": "https://akshare.akfamily.xyz/", "timeout": 30}
)
```

### 2. 查询带数据来源的Symbol
```python
symbols = Symbol.query.filter_by(data_source_id=data_source_id).all()
for symbol in symbols:
    print(f"股票: {symbol.symbol}, 数据来源: {symbol.data_source.name}")
```

### 3. 查询带数据来源的MarketData
```python
market_data = MarketData.query.filter_by(data_source_id=data_source_id).all()
for data in market_data:
    print(f"股票: {data.symbol}, 数据来源: {data.data_source.name}")
```

## 数据库视图

### data_source_statistics视图
提供数据来源的统计信息，包括：
- 关联的symbols数量
- 关联的market_data数量
- 最新数据时间

### data_source_performance视图
提供数据来源的性能统计，包括：
- 总记录数
- 唯一股票数
- 数据时间范围
- 平均每日记录数

## 测试

提供了完整的测试脚本 (`test_data_source.py`) 来验证：
- 数据来源创建和查询
- Symbol和MarketData的数据来源关联
- 关联查询功能
- to_dict方法的数据来源信息

## 迁移说明

1. 运行数据库迁移脚本：
   ```bash
   python database/migrate.py upgrade v1.3.0
   ```

2. 现有数据会自动关联到默认的AKShare数据源

3. 新的数据获取会自动关联到相应的数据来源

## 注意事项

1. 删除数据来源前会检查是否有关联的symbols或market_data
2. 数据来源的配置信息以JSON格式存储
3. 支持多个数据来源的优先级管理
4. 所有API都需要认证才能访问

## 后续扩展

1. 可以添加数据来源的健康检查功能
2. 可以添加数据来源的自动切换机制
3. 可以添加数据来源的性能监控
4. 可以添加数据来源的配置管理界面
