import os

# 是否开启debug模式
DEBUG = True

# 读取数据库环境变量
username = os.environ.get("MYSQL_USERNAME", 'root')
password = os.environ.get("MYSQL_PASSWORD", 'root')
db_address = os.environ.get("MYSQL_ADDRESS", '127.0.0.1:3306')

# 读取微信小程序配置
WECHAT_APPID = os.environ.get("WECHAT_APPID", '')
WECHAT_SECRET = os.environ.get("WECHAT_SECRET", '')
