from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from config import config
from models import db
import os

def create_app(config_name=None):
    """应用工厂函数"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # 初始化扩展
    db.init_app(app)
    migrate = Migrate(app, db)
    
    # 配置CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # 尝试注册API文档蓝图（Flask-RESTX）
    try:
        from app.api_docs import api_docs_bp
        app.register_blueprint(api_docs_bp, url_prefix='/api')
        
        # 注册RESTX路由
        from app.restx_routes import (
            auth_ns, users_ns, portfolios_ns, trades_ns, strategies_ns,
            market_data_ns, risk_ns, dashboard_ns, system_ns
        )
        print("✅ Flask-RESTX API文档已启用")
    except ImportError as e:
        print(f"⚠️  Flask-RESTX未安装，跳过API文档功能: {e}")
        print("   请运行: pip install flask-restx marshmallow")
    
    # 注册传统API蓝图（保持向后兼容）
    from app.routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api/legacy')
    
    # 根路径重定向到API文档
    @app.route('/')
    def index():
        from flask import redirect, url_for
        return redirect('/api/docs/')
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
    
    return app
