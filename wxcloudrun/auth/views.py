from flask import Blueprint, request, jsonify
from wxcloudrun.auth.models import User
from wxcloudrun import db
from .. import config
import requests
import os

auth = Blueprint('auth', __name__)

@auth.route('/', methods=['GET'])
def index():
    """认证模块根路由"""
    return jsonify({
        'code': 0,
        'msg': 'Auth service is running'
    })

@auth.route('/login', methods=['POST'])
def login():
    """微信登录接口"""
    data = request.get_json()
    code = data.get('code')
    
    # 通过code获取openid
    appid = config.WECHAT_APPID
    secret = config.WECHAT_SECRET
    url = f'https://api.weixin.qq.com/sns/jscode2session?appid={appid}&secret={secret}&js_code={code}&grant_type=authorization_code'
    
    resp = requests.get(url)
    result = resp.json()
    openid = result.get('openid')
    
    if not openid:
        return jsonify({'code': -1, 'msg': '登录失败'})
    
    # 查找用户
    user = User.query.filter_by(openid=openid).first()
    
    if not user:
        return jsonify({'code': 1, 'msg': '用户未授权'})
    
    if not user.is_authorized:
        return jsonify({'code': 1, 'msg': '用户未授权'})
    
    return jsonify({
        'code': 0,
        'data': {
            'userInfo': {
                'id': user.id,
                'nickname': user.nickname,
                'avatarUrl': user.avatar_url
            }
        }
    })

@auth.route('/authorize', methods=['POST'])
def authorize():
    """通过分享链接授权"""
    data = request.get_json()
    code = data.get('code')
    
    # 通过code获取openid
    appid = config.WECHAT_APPID
    secret = config.WECHAT_SECRET
    url = f'https://api.weixin.qq.com/sns/jscode2session?appid={appid}&secret={secret}&js_code={code}&grant_type=authorization_code'
    
    resp = requests.get(url)
    result = resp.json()
    openid = result.get('openid')
    
    if not openid:
        return jsonify({'code': -1, 'msg': '授权失败'})
    
    # 查找或创建用户
    user = User.query.filter_by(openid=openid).first()
    if user and user.is_authorized:
        # 如果用户已授权,返回用户信息
        return jsonify({
            'code': 0,
            'data': {
                'userInfo': {
                    'id': user.id,
                    'nickname': user.nickname,
                    'avatarUrl': user.avatar_url
                }
            }
        })
    
    # 未授权用户或新用户,只需要设置授权标记
    if not user:
        user = User(openid=openid, is_authorized=True)
        db.session.add(user)
    else:
        user.is_authorized = True
    
    db.session.commit()
    
    return jsonify({
        'code': 0,
        'msg': '授权成功'
    })

@auth.route('/update_user', methods=['POST'])
def update_user():
    """更新用户信息"""
    data = request.get_json()
    code = data.get('code')
    nickname = data.get('nickname')
    avatar_url = data.get('avatarUrl')
    
    # 通过code获取openid
    appid = config.WECHAT_APPID
    secret = config.WECHAT_SECRET
    url = f'https://api.weixin.qq.com/sns/jscode2session?appid={appid}&secret={secret}&js_code={code}&grant_type=authorization_code'
    
    resp = requests.get(url)
    result = resp.json()
    openid = result.get('openid')
    
    if not openid:
        return jsonify({'code': -1, 'msg': '更新失败'})
    
    # 更新用户信息
    user = User.query.filter_by(openid=openid).first()
    if user:
        user.nickname = nickname
        user.avatar_url = avatar_url
        user.is_authorized = True
        db.session.commit()
        
        return jsonify({
            'code': 0,
            'data': {
                'userInfo': {
                    'id': user.id,
                    'nickname': user.nickname,
                    'avatarUrl': user.avatar_url
                }
            },
            'msg': '更新成功'
        })
    
    return jsonify({'code': -1, 'msg': '用户不存在'})

@auth.route('/list', methods=['GET'])
def list_users():
    """获取用户列表"""
    try:
        # 只获取已授权的用户
        users = User.query.filter_by(is_authorized=True).all()
        
        return jsonify({
            'code': 0,
            'data': {
                'users': [{
                    'user_id': user.id,
                    'nickname': user.nickname,
                    'avatar_url': user.avatar_url,
                    'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S')
                } for user in users]
            }
        })
        
    except Exception as e:
        return jsonify({
            'code': -1,
            'msg': f'获取用户列表失败: {str(e)}'
        })

@auth.route('/detail', methods=['GET'])
def get_user_detail():
    """获取用户详情"""
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'code': -1, 'msg': '缺少用户ID'})
        
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'code': -1, 'msg': '用户不存在'})
            
        return jsonify({
            'code': 0,
            'data': {
                'user': {
                    'id': user.id,
                    'nickname': user.nickname,
                    'avatar_url': user.avatar_url,
                    'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S')
                }
            }
        })
        
    except Exception as e:
        return jsonify({
            'code': -1,
            'msg': f'获取用户详情失败: {str(e)}'
        })