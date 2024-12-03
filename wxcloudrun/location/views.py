from flask import Blueprint, request, jsonify
from .models import Location
from wxcloudrun import db

location = Blueprint('location', __name__)

@location.route('/list', methods=['GET'])
def get_locations():
    """获取用户的活动范围列表"""
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'code': -1, 'msg': '缺少用户ID'})
    
    try:
        locations = Location.query.filter_by(user_id=user_id).all()
        return jsonify({
            'code': 0,
            'data': {
                'locations': [{
                    'id': loc.id,
                    'name': loc.name,
                    'address': loc.address,
                    'latitude': float(loc.latitude),  # 确保返回数字类型
                    'longitude': float(loc.longitude),
                    'created_at': loc.created_at.strftime('%Y-%m-%d %H:%M:%S')
                } for loc in locations]
            }
        })
    except Exception as e:
        return jsonify({
            'code': -1,
            'msg': f'获取位置列表失败: {str(e)}'
        })

@location.route('/add', methods=['POST'])
def add_location():
    data = request.get_json()
    user_id = data.get('user_id')
    if not user_id:
        return jsonify({'code': -1, 'msg': '缺少用户ID'})
    
    location = Location(
        user_id=user_id,
        name=data.get('name'),
        address=data.get('address'),
        latitude=data.get('latitude'),
        longitude=data.get('longitude')
    )
    db.session.add(location)
    db.session.commit()
    
    return jsonify({'code': 0, 'msg': '添加成功'})

@location.route('/delete', methods=['POST'])
def delete_location():
    data = request.get_json()
    user_id = data.get('user_id')
    if not user_id:
        return jsonify({'code': -1, 'msg': '缺少用户ID'})
    
    location = Location.query.filter_by(id=data.get('id'), user_id=user_id).first()
    if location:
        db.session.delete(location)
        db.session.commit()
        return jsonify({'code': 0, 'msg': '删除成功'})
    
    return jsonify({'code': -1, 'msg': '位置不存在'}) 