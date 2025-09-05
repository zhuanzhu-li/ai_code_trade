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
    
    # 注册API蓝图
    from app.routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # 根路径重定向到API信息
    @app.route('/')
    def index():
        from flask import redirect, url_for
        return redirect('/api/info')
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
    
    return app
