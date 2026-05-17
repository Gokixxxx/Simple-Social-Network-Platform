#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
朋友圈管理模块
"""

import logging
from .db_connection import execute_query, execute_update, execute_transaction

logger = logging.getLogger(__name__)

def post_moment(user_id, content):
    """
    发表朋友圈
    返回: {'success': True/False, 'message': '...', 'moment_id': int}
    """
    pass

def update_moment(moment_id, user_id, new_content):
    """
    修改朋友圈
    返回: {'success': True/False, 'message': '...'}
    """
    pass

def delete_moment(moment_id, user_id):
    """
    删除朋友圈（会触发删除相关评论）
    返回: {'success': True/False, 'message': '...'}
    """
    pass

def get_my_moments(user_id):
    """
    查看我的朋友圈
    返回: [{'moment_id': int, 'content': str, 'last_update_time': str, 'comment_count': int}, ...]
    """
    pass

def get_friends_moments(user_id):
    """
    查看好友朋友圈（包含评论）
    返回: [
        {
            'moment_id': int,
            'user_id': int,
            'username': str,
            'content': str,
            'last_update_time': str,
            'comments': [
                {'comment_id': int, 'commenter_id': int, 'commenter_name': str, 'content': str, 'comment_time': str},
                ...
            ]
        },
        ...
    ]
    """
    pass

def add_comment(moment_id, user_id, content):
    """
    评论朋友圈
    返回: {'success': True/False, 'message': '...', 'comment_id': int}
    """
    pass

def delete_comment(comment_id, user_id):
    """
    删除评论（只能删除自己的评论）
    返回: {'success': True/False, 'message': '...'}
    """
    pass