from flask import Blueprint, request, jsonify
from .models import Activity, ActivityParticipant
from wxcloudrun import db
from datetime import datetime

activity = Blueprint('activity', __name__)

@activity.route('/create', methods=['POST'])
def create_activity():
    data = request.get_json()
    
    # 验证必填字段
    if not all(key in data for key in ['title', 'activity_date']):
        return jsonify({'code': -1, 'msg': '缺少必填字段'})
        
    try:
        activity = Activity(
            title=data['title'],
            description=data.get('description'),
            activity_date=datetime.strptime(data['activity_date'], '%Y-%m-%d').date(),
            location_name=data.get('location_name'),
            location_latitude=data.get('location_latitude'),
            location_longitude=data.get('location_longitude'),
            organizer_id=data['user_id']
        )
        
        db.session.add(activity)
        db.session.commit()
        
        # 添加发起人作为参与者
        participant = ActivityParticipant(
            activity_id=activity.id,
            person_id=data['user_id'],
            role='organizer',
            status='confirmed'
        )
        db.session.add(participant)
        db.session.commit()
        
        return jsonify({'code': 0, 'msg': '创建成功', 'data': {'activity_id': activity.id}})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': -1, 'msg': f'创建失败: {str(e)}'})

@activity.route('/list', methods=['GET'])
def list_activities():
    # 获取查询参数
    user_id = request.args.get('user_id')
    status = request.args.get('status')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = Activity.query
    
    # 应用过滤条件
    if user_id:
        query = query.join(ActivityParticipant).filter(ActivityParticipant.person_id == user_id)
    if status:
        query = query.filter(Activity.status == status)
    if start_date:
        query = query.filter(Activity.activity_date >= datetime.strptime(start_date, '%Y-%m-%d').date())
    if end_date:
        query = query.filter(Activity.activity_date <= datetime.strptime(end_date, '%Y-%m-%d').date())
        
    # 按日期降序排序
    activities_list = query.order_by(Activity.activity_date.desc()).all()
    
    activities = [{
        'id': item.id,
        'title': item.title,
        'description': item.description,
        'activity_date': item.activity_date.strftime('%Y-%m-%d'),
        'location_name': item.location_name,
        'location_address': item.location_address if hasattr(item, 'location_address') else None,
        'status': item.status,
        'organizer_id': item.organizer_id
    } for item in activities_list]
    
    return jsonify({
        'code': 0,
        'data': {
            'activities': activities
        }
    })

@activity.route('/join', methods=['POST'])
def join_activity():
    data = request.get_json()
    
    # 验证必填字段
    if not all(key in data for key in ['activity_id', 'user_id']):
        return jsonify({'code': -1, 'msg': '缺少必填字段'})
        
    try:
        # 检查是否已经参与
        existing = ActivityParticipant.query.filter_by(
            activity_id=data['activity_id'],
            person_id=data['user_id']
        ).first()
        
        if existing:
            return jsonify({'code': -1, 'msg': '您已参与该活动'})
            
        # 检查活动是否存在且状态正常
        activity = Activity.query.get(data['activity_id'])
        if not activity:
            return jsonify({'code': -1, 'msg': '活动不存在'})
        if activity.status not in ['planning', 'confirmed']:
            return jsonify({'code': -1, 'msg': '活动状态不允许加入'})
            
        # 创建参与记录
        participant = ActivityParticipant(
            activity_id=data['activity_id'],
            person_id=data['user_id'],
            role='participant',
            status='pending'  # 如果需要发起人审核,状态为pending
        )
        
        db.session.add(participant)
        db.session.commit()
        
        return jsonify({'code': 0, 'msg': '加入成功'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': -1, 'msg': f'加入失败: {str(e)}'})

@activity.route('/leave', methods=['POST'])
def leave_activity():
    data = request.get_json()
    
    # 验证必填字段
    if not all(key in data for key in ['activity_id', 'user_id']):
        return jsonify({'code': -1, 'msg': '缺少必填字段'})
        
    try:
        # 查找参与记录
        participant = ActivityParticipant.query.filter_by(
            activity_id=data['activity_id'],
            person_id=data['user_id']
        ).first()
        
        if not participant:
            return jsonify({'code': -1, 'msg': '您未参与该活动'})
            
        # 检查是否为发起人
        if participant.role == 'organizer':
            return jsonify({'code': -1, 'msg': '发起人不能退出活动'})
            
        # 删除参与记录
        db.session.delete(participant)
        db.session.commit()
        
        return jsonify({'code': 0, 'msg': '退出成功'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': -1, 'msg': f'退出失败: {str(e)}'})

@activity.route('/participants', methods=['GET'])
def get_participants():
    # 获取活动ID
    activity_id = request.args.get('activity_id')
    if not activity_id:
        return jsonify({'code': -1, 'msg': '缺少活动ID'})
        
    try:
        # 查询参与者列表
        participants = ActivityParticipant.query.filter_by(
            activity_id=activity_id
        ).all()
        
        # 获取用户信息
        from wxcloudrun.auth.models import User
        result = []
        for p in participants:
            user = User.query.get(p.person_id)
            if user:
                result.append({
                    'user_id': user.id,
                    'nickname': user.nickname,
                    'avatar_url': user.avatar_url,
                    'role': p.role,
                    'status': p.status,
                    'joined_at': p.joined_at.strftime('%Y-%m-%d %H:%M:%S')
                })
        
        return jsonify({
            'code': 0,
            'data': {
                'participants': result
            }
        })
        
    except Exception as e:
        return jsonify({'code': -1, 'msg': f'查询失败: {str(e)}'})

@activity.route('/detail', methods=['GET'])
def get_activity_detail():
    activity_id = request.args.get('id')
    if not activity_id:
        return jsonify({'code': -1, 'msg': '缺少活动ID'})
        
    try:
        activity = Activity.query.get(activity_id)
        if not activity:
            return jsonify({'code': -1, 'msg': '活动不存在'})
            
        # 获取参与者列表
        from wxcloudrun.auth.models import User
        participants = ActivityParticipant.query.filter_by(
            activity_id=activity_id
        ).all()
        
        participant_list = []
        for p in participants:
            user = User.query.get(p.person_id)
            if user:
                participant_list.append({
                    'user_id': user.id,
                    'nickname': user.nickname,
                    'avatar_url': user.avatar_url,
                    'role': p.role,
                    'status': p.status
                })
        
        return jsonify({
            'code': 0,
            'data': {
                'id': activity.id,
                'title': activity.title,
                'description': activity.description,
                'activity_date': activity.activity_date.strftime('%Y-%m-%d'),
                'location_name': activity.location_name,
                'location_address': activity.location_address if hasattr(activity, 'location_address') else None,
                'status': activity.status,
                'organizer_id': activity.organizer_id,
                'participants': participant_list
            }
        })
        
    except Exception as e:
        return jsonify({'code': -1, 'msg': f'查询失败: {str(e)}'}) 