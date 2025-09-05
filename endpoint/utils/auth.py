from functools import wraps
from flask import request, jsonify
import jwt
import os
from datetime import datetime, timedelta

def token_required(f):
    """JWT token验证装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # 从请求头获取token
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]  # Bearer <token>
            except IndexError:
                return jsonify({'error': 'Token格式错误'}), 401
        
        if not token:
            return jsonify({'error': '缺少认证token'}), 401
        
        try:
            # 验证token
            data = jwt.decode(token, os.environ.get('SECRET_KEY', 'dev-secret-key'), algorithms=['HS256'])
            current_user_id = data['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token已过期'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': '无效的token'}), 401
        
        return f(current_user_id, *args, **kwargs)
    
    return decorated

def generate_token(user_id):
    """生成JWT token"""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=24)
    }
    
    token = jwt.encode(payload, os.environ.get('SECRET_KEY', 'dev-secret-key'), algorithm='HS256')
    return token

def verify_password(password, password_hash):
    """验证密码"""
    from werkzeug.security import check_password_hash
    return check_password_hash(password_hash, password)
