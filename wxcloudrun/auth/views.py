from flask import Blueprint, request, jsonify
from wxcloudrun.auth.models import User
from wxcloudrun import db
from .. import config
import requests
import os

auth = Blueprint('auth', __name__)

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