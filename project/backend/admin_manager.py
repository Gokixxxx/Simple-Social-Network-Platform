#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
管理员管理模块
"""

import logging
from .db_connection import execute_query, execute_update, execute_transaction

logger = logging.getLogger(__name__)

def login_admin(admin_username, password):
    """
    管理员登录
    返回: {'success': True/False, 'message': '...', 'admin_id': int, 'name': str}
    """
    pass

def get_admin_profile(admin_id):
    """
    获取管理员个人信息
    返回: {'admin_id': int, 'admin_username': str, 'name': str, 'gender': str, 'birth_date': str, 'age': int}
    """
    pass

def update_admin_profile(admin_id, name=None, gender=None, birth_date=None):
    """
    更新管理员个人信息
    返回: {'success': True/False, 'message': '...'}
    """
    pass

def get_all_users():
    """
    浏览所有用户列表（不包含敏感信息）
    返回: [{'user_id': int, 'username': str}, ...]
    """
    pass

def delete_user_by_admin(admin_id, target_user_id):
    """
    管理员注销用户（删除用户及其所有相关数据）
    返回: {'success': True/False, 'message': '...'}
    """
    pass

def get_all_moments_for_review():
    """
    浏览所有朋友圈（用于审核）
    返回: [
        {
            'moment_id': int,
            'user_id': int,
            'username': str,
            'content': str,
            'last_update_time': str,
            'comments': [...]
        },
        ...
    ]
    """
    pass

def delete_moment_by_admin(admin_id, moment_id):
    """
    删除违规朋友圈（管理员权限）
    返回: {'success': True/False, 'message': '...'}
    """
    pass