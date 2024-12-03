from flask import Blueprint, request, jsonify
from .models import Media
from wxcloudrun import db

media = Blueprint('media', __name__)

@media.route('/upload', methods=['POST'])
def upload_media():
    data = request.get_json()
    
    if not all(key in data for key in ['file_id', 'type']):
        return jsonify({'code': -1, 'msg': '缺少必填字段'})
        
    try:
        media = Media(
            file_id=data['file_id'],
            type=data['type'],
            tags=data.get('tags', [])
        )
        
        db.session.add(media)
        db.session.commit()
        
        return jsonify({
            'code': 0, 
            'msg': '上传成功',
            'data': {'media_id': media.id}
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': -1, 'msg': f'上传失败: {str(e)}'})

@media.route('/list', methods=['GET'])
def list_media():
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)
    tag = request.args.get('tag')
    
    try:
        query = Media.query
        if tag:
            query = query.filter(Media.tags.contains([tag]))
            
        total = query.count()
        media_list = query.order_by(Media.created_at.desc())\
            .offset((page - 1) * page_size)\
            .limit(page_size)\
            .all()
        
        return jsonify({
            'code': 0,
            'data': {
                'total': total,
                'media': [{
                    'id': m.id,
                    'file_id': m.file_id,
                    'type': m.type,
                    'tags': m.tags,
                    'favorites': m.favorites,
                    'created_at': m.created_at.strftime('%Y-%m-%d %H:%M:%S')
                } for m in media_list]
            }
        })
        
    except Exception as e:
        return jsonify({'code': -1, 'msg': f'获取失败: {str(e)}'})