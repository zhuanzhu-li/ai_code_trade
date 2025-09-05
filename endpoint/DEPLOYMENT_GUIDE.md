# 部署指南

本指南将帮助您在生产环境中部署量化交易系统。

## 系统要求

### 最低要求
- **CPU**: 2核心
- **内存**: 4GB RAM
- **存储**: 20GB 可用空间
- **操作系统**: Ubuntu 20.04 LTS 或 CentOS 8+

### 推荐配置
- **CPU**: 4核心或更多
- **内存**: 8GB RAM 或更多
- **存储**: 50GB SSD
- **操作系统**: Ubuntu 22.04 LTS

## 环境准备

### 1. 安装系统依赖

#### Ubuntu/Debian
```bash
# 更新系统包
sudo apt update && sudo apt upgrade -y

# 安装必要的包
sudo apt install -y python3 python3-pip python3-venv mysql-server nginx git

# 安装MySQL客户端开发包
sudo apt install -y libmysqlclient-dev pkg-config

# 安装TA-Lib依赖
sudo apt install -y build-essential wget
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make
sudo make install
cd ..
rm -rf ta-lib ta-lib-0.4.0-src.tar.gz
```

#### CentOS/RHEL
```bash
# 更新系统包
sudo yum update -y

# 安装必要的包
sudo yum install -y python3 python3-pip mysql-server nginx git

# 安装MySQL客户端开发包
sudo yum install -y mysql-devel pkgconfig

# 安装TA-Lib依赖
sudo yum groupinstall -y "Development Tools"
sudo yum install -y wget
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make
sudo make install
cd ..
rm -rf ta-lib ta-lib-0.4.0-src.tar.gz
```

### 2. 配置MySQL数据库

```bash
# 启动MySQL服务
sudo systemctl start mysql
sudo systemctl enable mysql

# 安全配置
sudo mysql_secure_installation

# 创建数据库和用户
sudo mysql -u root -p
```

在MySQL中执行以下SQL：

```sql
-- 创建数据库
CREATE DATABASE quant_trading CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE quant_trading_dev CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建用户
CREATE USER 'quant_user'@'localhost' IDENTIFIED BY 'your_secure_password';
CREATE USER 'quant_user'@'%' IDENTIFIED BY 'your_secure_password';

-- 授权
GRANT ALL PRIVILEGES ON quant_trading.* TO 'quant_user'@'localhost';
GRANT ALL PRIVILEGES ON quant_trading.* TO 'quant_user'@'%';
GRANT ALL PRIVILEGES ON quant_trading_dev.* TO 'quant_user'@'localhost';
GRANT ALL PRIVILEGES ON quant_trading_dev.* TO 'quant_user'@'%';

-- 刷新权限
FLUSH PRIVILEGES;

-- 退出
EXIT;
```

## 应用部署

### 1. 创建应用用户

```bash
# 创建专用用户
sudo useradd -m -s /bin/bash quant
sudo usermod -aG sudo quant

# 切换到应用用户
sudo su - quant
```

### 2. 部署应用代码

```bash
# 克隆代码
git clone <your-repository-url> /home/quant/quant-trading-system
cd /home/quant/quant-trading-system

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install --upgrade pip
pip install -r requirements.txt

# 安装Gunicorn
pip install gunicorn
```

### 3. 配置环境变量

```bash
# 创建环境配置文件
cp env.example .env
nano .env
```

配置`.env`文件：

```env
# 数据库配置
DATABASE_URL=mysql+pymysql://quant_user:your_secure_password@localhost/quant_trading
DEV_DATABASE_URL=mysql+pymysql://quant_user:your_secure_password@localhost/quant_trading_dev

# 安全配置
SECRET_KEY=your-very-secure-secret-key-here
FLASK_ENV=production

# 交易配置
TRADING_ENABLED=False
MAX_POSITION_SIZE=10000
MAX_DAILY_LOSS=1000

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=/home/quant/quant-trading-system/logs/trading.log

# 服务器配置
HOST=0.0.0.0
PORT=5000
```

### 4. 初始化数据库

```bash
# 设置环境变量
export FLASK_APP=app.py
export FLASK_ENV=production

# 初始化数据库迁移
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# 创建日志目录
mkdir -p logs
chmod 755 logs
```

### 5. 创建Gunicorn配置文件

```bash
# 创建Gunicorn配置
nano gunicorn.conf.py
```

`gunicorn.conf.py`内容：

```python
# Gunicorn配置文件

# 服务器socket
bind = "127.0.0.1:5000"
backlog = 2048

# Worker进程
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# 重启
max_requests = 1000
max_requests_jitter = 50
preload_app = True

# 日志
accesslog = "/home/quant/quant-trading-system/logs/gunicorn_access.log"
errorlog = "/home/quant/quant-trading-system/logs/gunicorn_error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# 进程管理
pidfile = "/home/quant/quant-trading-system/gunicorn.pid"
daemon = False
user = "quant"
group = "quant"

# 安全
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190
```

### 6. 创建Systemd服务

```bash
# 创建服务文件
sudo nano /etc/systemd/system/quant-trading.service
```

`/etc/systemd/system/quant-trading.service`内容：

```ini
[Unit]
Description=Quant Trading System
After=network.target mysql.service

[Service]
Type=notify
User=quant
Group=quant
WorkingDirectory=/home/quant/quant-trading-system
Environment=PATH=/home/quant/quant-trading-system/venv/bin
ExecStart=/home/quant/quant-trading-system/venv/bin/gunicorn --config gunicorn.conf.py app:app
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
# 重新加载systemd配置
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start quant-trading

# 设置开机自启
sudo systemctl enable quant-trading

# 检查状态
sudo systemctl status quant-trading
```

## Nginx配置

### 1. 安装和配置Nginx

```bash
# 安装Nginx
sudo apt install nginx -y

# 创建配置文件
sudo nano /etc/nginx/sites-available/quant-trading
```

`/etc/nginx/sites-available/quant-trading`内容：

```nginx
server {
    listen 80;
    server_name your-domain.com;  # 替换为您的域名

    # 静态文件
    location /static/ {
        alias /home/quant/quant-trading-system/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # API和动态内容
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # 缓冲设置
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }

    # 安全头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

    # 日志
    access_log /var/log/nginx/quant-trading_access.log;
    error_log /var/log/nginx/quant-trading_error.log;
}
```

### 2. 启用站点

```bash
# 启用站点
sudo ln -s /etc/nginx/sites-available/quant-trading /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启Nginx
sudo systemctl restart nginx
sudo systemctl enable nginx
```

## SSL证书配置（可选但推荐）

### 使用Let's Encrypt

```bash
# 安装Certbot
sudo apt install certbot python3-certbot-nginx -y

# 获取SSL证书
sudo certbot --nginx -d your-domain.com

# 设置自动续期
sudo crontab -e
# 添加以下行：
# 0 12 * * * /usr/bin/certbot renew --quiet
```

## 监控和日志

### 1. 日志管理

```bash
# 创建日志轮转配置
sudo nano /etc/logrotate.d/quant-trading
```

`/etc/logrotate.d/quant-trading`内容：

```
/home/quant/quant-trading-system/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 quant quant
    postrotate
        systemctl reload quant-trading
    endscript
}
```

### 2. 系统监控

```bash
# 安装监控工具
sudo apt install htop iotop nethogs -y

# 创建监控脚本
nano /home/quant/monitor.sh
```

`/home/quant/monitor.sh`内容：

```bash
#!/bin/bash

# 检查服务状态
echo "=== 服务状态 ==="
systemctl status quant-trading --no-pager
systemctl status nginx --no-pager
systemctl status mysql --no-pager

# 检查资源使用
echo "=== 资源使用 ==="
free -h
df -h
ps aux --sort=-%cpu | head -10

# 检查日志错误
echo "=== 最近错误 ==="
tail -20 /home/quant/quant-trading-system/logs/gunicorn_error.log
tail -20 /var/log/nginx/quant-trading_error.log
```

```bash
# 设置执行权限
chmod +x /home/quant/monitor.sh

# 添加到crontab
crontab -e
# 添加以下行（每5分钟检查一次）：
# */5 * * * * /home/quant/monitor.sh >> /home/quant/monitor.log 2>&1
```

## 备份策略

### 1. 数据库备份

```bash
# 创建备份脚本
nano /home/quant/backup_db.sh
```

`/home/quant/backup_db.sh`内容：

```bash
#!/bin/bash

# 配置
DB_NAME="quant_trading"
DB_USER="quant_user"
DB_PASS="your_secure_password"
BACKUP_DIR="/home/quant/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份数据库
mysqldump -u$DB_USER -p$DB_PASS $DB_NAME > $BACKUP_DIR/quant_trading_$DATE.sql

# 压缩备份
gzip $BACKUP_DIR/quant_trading_$DATE.sql

# 删除7天前的备份
find $BACKUP_DIR -name "quant_trading_*.sql.gz" -mtime +7 -delete

echo "数据库备份完成: quant_trading_$DATE.sql.gz"
```

```bash
# 设置执行权限
chmod +x /home/quant/backup_db.sh

# 添加到crontab（每天凌晨2点备份）
crontab -e
# 添加以下行：
# 0 2 * * * /home/quant/backup_db.sh >> /home/quant/backup.log 2>&1
```

### 2. 应用代码备份

```bash
# 创建代码备份脚本
nano /home/quant/backup_code.sh
```

`/home/quant/backup_code.sh`内容：

```bash
#!/bin/bash

# 配置
APP_DIR="/home/quant/quant-trading-system"
BACKUP_DIR="/home/quant/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份应用代码（排除虚拟环境和日志）
tar -czf $BACKUP_DIR/quant_trading_code_$DATE.tar.gz \
    --exclude='venv' \
    --exclude='logs' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    -C /home/quant quant-trading-system

# 删除30天前的备份
find $BACKUP_DIR -name "quant_trading_code_*.tar.gz" -mtime +30 -delete

echo "代码备份完成: quant_trading_code_$DATE.tar.gz"
```

## 安全配置

### 1. 防火墙配置

```bash
# 配置UFW防火墙
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 2. 数据库安全

```bash
# 编辑MySQL配置
sudo nano /etc/mysql/mysql.conf.d/mysqld.cnf

# 添加以下配置：
[mysqld]
bind-address = 127.0.0.1
max_connections = 100
innodb_buffer_pool_size = 1G
innodb_log_file_size = 256M
query_cache_size = 64M
query_cache_limit = 2M
```

### 3. 应用安全

```bash
# 设置文件权限
sudo chown -R quant:quant /home/quant/quant-trading-system
sudo chmod -R 755 /home/quant/quant-trading-system
sudo chmod 600 /home/quant/quant-trading-system/.env

# 限制SSH访问
sudo nano /etc/ssh/sshd_config
# 设置：
# PermitRootLogin no
# PasswordAuthentication no
# PubkeyAuthentication yes
```

## 性能优化

### 1. 数据库优化

```sql
-- 在MySQL中执行
-- 创建索引
CREATE INDEX idx_trades_portfolio_executed ON trades(portfolio_id, executed_at);
CREATE INDEX idx_market_data_symbol_timestamp ON market_data(symbol_id, timestamp);
CREATE INDEX idx_positions_portfolio_symbol ON positions(portfolio_id, symbol);

-- 分析表
ANALYZE TABLE trades;
ANALYZE TABLE market_data;
ANALYZE TABLE positions;
```

### 2. 应用优化

```bash
# 编辑Gunicorn配置
nano gunicorn.conf.py

# 调整worker数量（通常为CPU核心数的2倍）
workers = 8

# 调整超时时间
timeout = 60
```

### 3. Nginx优化

```bash
# 编辑Nginx配置
sudo nano /etc/nginx/nginx.conf

# 在http块中添加：
worker_processes auto;
worker_connections 1024;

# 启用gzip压缩
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
```

## 故障排除

### 1. 常见问题

**服务无法启动**
```bash
# 检查服务状态
sudo systemctl status quant-trading

# 查看日志
journalctl -u quant-trading -f

# 检查端口占用
sudo netstat -tlnp | grep :5000
```

**数据库连接失败**
```bash
# 检查MySQL状态
sudo systemctl status mysql

# 测试数据库连接
mysql -u quant_user -p -h localhost quant_trading

# 检查防火墙
sudo ufw status
```

**Nginx配置错误**
```bash
# 测试Nginx配置
sudo nginx -t

# 查看Nginx错误日志
sudo tail -f /var/log/nginx/error.log
```

### 2. 性能问题

**内存不足**
```bash
# 检查内存使用
free -h
ps aux --sort=-%mem | head -10

# 调整Gunicorn worker数量
# 编辑gunicorn.conf.py，减少workers数量
```

**数据库慢查询**
```sql
-- 查看慢查询
SHOW VARIABLES LIKE 'slow_query_log';
SHOW VARIABLES LIKE 'long_query_time';

-- 启用慢查询日志
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 2;
```

## 更新和维护

### 1. 应用更新

```bash
# 切换到应用目录
cd /home/quant/quant-trading-system

# 停止服务
sudo systemctl stop quant-trading

# 备份当前版本
cp -r . ../quant-trading-backup-$(date +%Y%m%d)

# 拉取最新代码
git pull origin main

# 更新依赖
source venv/bin/activate
pip install -r requirements.txt

# 数据库迁移
flask db upgrade

# 重启服务
sudo systemctl start quant-trading
```

### 2. 定期维护

```bash
# 创建维护脚本
nano /home/quant/maintenance.sh
```

`/home/quant/maintenance.sh`内容：

```bash
#!/bin/bash

echo "开始系统维护 - $(date)"

# 清理日志
find /home/quant/quant-trading-system/logs -name "*.log" -mtime +30 -delete

# 清理临时文件
find /tmp -name "quant_*" -mtime +7 -delete

# 更新系统包
sudo apt update && sudo apt upgrade -y

# 重启服务
sudo systemctl restart quant-trading
sudo systemctl restart nginx

echo "系统维护完成 - $(date)"
```

```bash
# 设置执行权限
chmod +x /home/quant/maintenance.sh

# 添加到crontab（每周日凌晨3点执行）
crontab -e
# 添加以下行：
# 0 3 * * 0 /home/quant/maintenance.sh >> /home/quant/maintenance.log 2>&1
```

## 总结

按照本指南，您应该能够成功部署量化交易系统到生产环境。记住：

1. 定期备份数据库和代码
2. 监控系统性能和日志
3. 保持系统和依赖包的更新
4. 定期检查安全配置
5. 测试灾难恢复流程

如有问题，请检查日志文件并参考故障排除部分。
