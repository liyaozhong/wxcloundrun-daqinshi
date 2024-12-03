from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import pymysql
import config

# 因MySQLDB不支持Python3，使用pymysql扩展库代替MySQLDB库
pymysql.install_as_MySQLdb()

# 初始化web应用
app = Flask(__name__, instance_relative_config=True)
app.config['DEBUG'] = config.DEBUG

# 设定数据库链接
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://{}:{}@{}/daqinshi'.format(config.username, config.password,
                                                                             config.db_address)

# 初始化DB操作对象
db = SQLAlchemy(app)

# 注册蓝图 - 使用url_prefix指定访问前缀
from wxcloudrun.auth.views import auth
from wxcloudrun.location.views import location
from wxcloudrun.activity.views import activity
from wxcloudrun.media.views import media

app.register_blueprint(auth, url_prefix='/api/auth')
app.register_blueprint(location, url_prefix='/api/location')
app.register_blueprint(activity, url_prefix='/api/activity')
app.register_blueprint(media, url_prefix='/api/media')

# 加载配置
app.config.from_object('config')