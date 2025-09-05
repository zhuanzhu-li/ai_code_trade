import os
from dotenv import load_dotenv

# 加载环境变量 - 必须在导入其他模块之前
load_dotenv()

from app import create_app

# 创建应用实例
app = create_app()

if __name__ == '__main__':
    # 确保日志目录存在
    os.makedirs('logs', exist_ok=True)
    
    # 运行应用
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=os.environ.get('FLASK_ENV') == 'development'
    )
