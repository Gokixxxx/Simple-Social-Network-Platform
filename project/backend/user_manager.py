#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
用户管理模块
"""

import logging
from .db_connection import execute_query, execute_update, execute_transaction

logger = logging.getLogger(__name__)

def register_user(username, password):
    """
    用户注册
    返回: {'success': True/False, 'message': '...', 'user_id': int}
    """
    # --- Step 1: Check for existing username ---
    check_query = "SELECT user_id FROM users WHERE username = %s" 
    existing_user = execute_query(check_query, (username,))

    if existing_user is None:
        # Database query failed
        logger.error("Failed to check for existing username during registration.")
        return {"success": False, "message": "Database error."}

    if len(existing_user) > 0:
        # Username is already taken
        logger.info(f"Registration failed: Username '{username}' is already taken.")
        return {"success": False, "message": "Username already exists."}

    # --- Step 2: Insert the new user ---
    query = "INSERT INTO users (username, password) VALUES (%s, %s)"
    result = execute_update(query, (username, password))    
    if result > 0:  # 成功
        logger.info(f"New user registered: {username}")
        return {"success": True, "message": "User registered successfully."}
    else:           # 失败
        logger.error(f"Failed to register user: {username}")
        return {"success": False, "message": "Failed to register user. Please try again."}

def login_user(username, password):
    """
    用户登录
    返回: {'success': True/False, 'message': '...', 'user_id': int, 'name': str}
    """
    pass

def get_user_profile(user_id):
    """
    获取用户个人信息
    返回: {'user_id': int, 'username': str, 'name': str, 'gender': str, 'birth_date': str, 'age': int}
    """
    pass

def update_user_profile(user_id, name=None, gender=None, birth_date=None):
    """
    更新用户个人信息
    返回: {'success': True/False, 'message': '...'}
    """
    pass

def search_users(keyword):
    """
    搜索用户（通过用户名）
    返回: [{'user_id': int, 'username': str}, ...]
    """
    pass

def add_friend(user_id, friend_id, group_name="默认分组"):
    """
    添加好友（双向，使用事务）
    返回: {'success': True/False, 'message': '...'}
    """
    pass

def remove_friend(user_id, friend_id):
    """
    删除好友（双向）
    返回: {'success': True/False, 'message': '...'}
    """
    pass

def get_friends_list(user_id, group_name=None):
    """
    获取好友列表（可按分组筛选）
    返回: [{'friend_id': int, 'username': str, 'group_name': str}, ...]
    """
    pass

def update_friend_group(user_id, friend_id, new_group_name):
    """
    修改好友分组
    返回: {'success': True/False, 'message': '...'}
    """
    pass