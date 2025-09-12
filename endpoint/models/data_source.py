from . import db
from datetime import datetime

class DataSource(db.Model):
    """数据来源模型"""
    __tablename__ = 'data_sources'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)  # 数据来源名称
    uri = db.Column(db.String(500), nullable=False)  # 数据来源URI
    description = db.Column(db.Text)  # 数据来源描述
    provider_type = db.Column(db.String(50), nullable=False)  # 提供商类型：akshare, yahoo, alpha_vantage等
    is_active = db.Column(db.Boolean, default=True)  # 是否激活
    priority = db.Column(db.Integer, default=1)  # 优先级（数字越小优先级越高）
    config = db.Column(db.Text)  # JSON格式的配置信息
    last_updated = db.Column(db.DateTime)  # 最后更新时间
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 索引
    __table_args__ = (
        db.Index('idx_provider_type', 'provider_type'),
        db.Index('idx_is_active', 'is_active'),
        db.Index('idx_priority', 'priority'),
    )
    
    def get_config(self):
        """获取配置信息"""
        import json
        if self.config:
            return json.loads(self.config)
        return {}
    
    def set_config(self, config_dict):
        """设置配置信息"""
        import json
        self.config = json.dumps(config_dict)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'uri': self.uri,
            'description': self.description,
            'provider_type': self.provider_type,
            'is_active': self.is_active,
            'priority': self.priority,
            'config': self.get_config(),
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<DataSource {self.name}>'
