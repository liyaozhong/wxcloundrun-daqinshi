from flask import Blueprint, request, jsonify
from .models import Location
from wxcloudrun import db

location = Blueprint('location', __name__)

@location.route('/list', methods=['GET'])
def get_locations():
    # 从请求参数获取用户ID
    data = request.args
    user_id = data.get('user_id')
    if not user_id:
        return jsonify({'code': -1, 'msg': '缺少用户ID'})
    
    locations = Location.query.filter_by(user_id=user_id).all()
    return jsonify({
        'code': 0,
        'data': {
            'locations': [{
                'id': loc.id,
                'name': loc.name,
                'address': loc.address,
                'latitude': loc.latitude,
                'longitude': loc.longitude
            } for loc in locations]
        }
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