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
    query = "SELECT admin_id, name FROM admins WHERE admin_username = %s AND password = %s"
    try:
        admin_rows = execute_query(query, (admin_username, password))
        if admin_rows is None:
            return {"success": False, "message": "Database error."}
            
        if len(admin_rows) > 0:
            admin = admin_rows[0]
            logger.info(f"Admin logged in successfully: {admin_username}")
            return {
                "success": True,
                "message": "Admin login successfully.",
                "admin_id": admin['admin_id'],
                "name": admin.get('name')
            }
        else:
            logger.info(f"Failed admin login attempt for username: {admin_username}")
            return {"success": False, "message": "Invalid admin username or password."}
    except Exception as e:
        logger.error(f"Error during admin login for {admin_username}: {e}")
        return {"success": False, "message": "An error occurred during admin login."}

def get_admin_profile(admin_id):
    """
    获取管理员个人信息（计算年龄）
    返回: {'admin_id': int, 'admin_username': str, 'name': str, 'gender': str, 'birth_date': str, 'age': int}
    """
    # Dynamically calculate age using TIMESTAMPDIFF directly from the admins table
    query = """
        SELECT admin_id, admin_username, name, gender, birth_date,
               TIMESTAMPDIFF(YEAR, birth_date, CURDATE()) AS age
        FROM admins
        WHERE admin_id = %s
    """
    try:
        profile_rows = execute_query(query, (admin_id,))
        if profile_rows and len(profile_rows) > 0:
            profile = profile_rows[0]
            if profile.get('birth_date'):
                profile['birth_date'] = str(profile['birth_date'])
            return profile
        return {}
    except Exception as e:
        logger.error(f"Failed to get admin profile for admin_id {admin_id}: {e}")
        return {}

def update_admin_profile(admin_id, name=None, gender=None, birth_date=None):
    """
    更新管理员个人信息
    返回: {'success': True/False, 'message': '...'}
    """
    query = "UPDATE admins SET name = %s, gender = %s, birth_date = %s WHERE admin_id = %s"
    try:
        result = execute_update(query, (name, gender, birth_date, admin_id))
        if result >= 0:
            logger.info(f"Admin profile updated successfully for admin_id: {admin_id}")
            return {"success": True, "message": "Admin profile updated successfully."}
        else:
            return {"success": False, "message": "Failed to update admin profile."}
    except Exception as e:
        logger.error(f"Error updating admin profile for admin_id {admin_id}: {e}")
        return {"success": False, "message": "Database error during admin profile update."}

def get_all_users():
    """
    浏览所有用户列表（不包含敏感信息）
    返回: [{'user_id': int, 'username': str}, ...]
    """
    query = "SELECT user_id, username FROM users ORDER BY user_id ASC"
    try:
        results = execute_query(query)
        return results if results is not None else []
    except Exception as e:
        logger.error(f"Error fetching all users for admin review: {e}")
        return []

def delete_user_by_admin(admin_id, target_user_id):
    """
    管理员注销用户（删除用户及其所有相关数据）
    返回: {'success': True/False, 'message': '...'}
    """
    # Check if the acting admin exists first
    admin_check = execute_query("SELECT 1 FROM admins WHERE admin_id = %s", (admin_id,))
    if not admin_check:
        return {"success": False, "message": "Unauthorized. Action requires admin privileges."}

    query = "DELETE FROM users WHERE user_id = %s"
    try:
        # Thanks to ON DELETE CASCADE on friendships, moments, and comments tables,
        # deleting this user record will trigger MySQL to automatically and safely clean up everything.
        result = execute_update(query, (target_user_id,))
        if result > 0:
            logger.warning(f"Admin {admin_id} deleted user account {target_user_id} and all related data.")
            return {"success": True, "message": "User and all related records deleted successfully."}
        else:
            return {"success": False, "message": "Target user not found."}
    except Exception as e:
        logger.error(f"Error deleting user {target_user_id} by admin {admin_id}: {e}")
        return {"success": False, "message": "Database error during user erasure."}

def get_all_moments_for_review():
    """
    浏览所有朋友圈（用于审核，必须包含完整的评论列表结构）
    返回: [ {'moment_id': int, 'user_id': int, 'username': str, 'content': str, 'last_update_time': str, 'comments': [...]}, ... ]
    """
    moments_query = """
        SELECT m.moment_id, m.user_id, u.username, m.content, m.last_update_time
        FROM moments m
        JOIN users u ON m.user_id = u.user_id
        ORDER BY m.last_update_time DESC
    """
    try:
        moments = execute_query(moments_query)
        if not moments:
            return []

        # Pack comments dynamically for every single moment on the system
        for moment in moments:
            if moment.get('last_update_time'):
                moment['last_update_time'] = str(moment['last_update_time'])
                
            comments_query = """
                SELECT c.comment_id, c.user_id AS commenter_id, u.username AS commenter_name, c.content, c.comment_time
                FROM comments c
                JOIN users u ON c.user_id = u.user_id
                WHERE c.moment_id = %s
                ORDER BY c.comment_time ASC
            """
            comments = execute_query(comments_query, (moment['moment_id'],))
            
            if comments:
                for comment in comments:
                    if comment.get('comment_time'):
                        comment['comment_time'] = str(comment['comment_time'])
                moment['comments'] = comments
            else:
                moment['comments'] = []
                
        return moments
    except Exception as e:
        logger.error(f"Error fetching all timeline elements for audit: {e}")
        return []

def delete_moment_by_admin(admin_id, moment_id):
    """
    删除违规朋友圈（管理员权限）
    返回: {'success': True/False, 'message': '...'}
    """
    # Check if the acting admin exists first
    admin_check = execute_query("SELECT 1 FROM admins WHERE admin_id = %s", (admin_id,))
    if not admin_check:
        return {"success": False, "message": "Unauthorized. Action requires admin privileges."}

    query = "DELETE FROM moments WHERE moment_id = %s"
    try:
        # ON DELETE CASCADE automatically purges all child comments from the DB
        result = execute_update(query, (moment_id,))
        if result > 0:
            logger.warning(f"Admin {admin_id} force deleted non-compliant moment ID {moment_id}.")
            return {"success": True, "message": "Violation moment removed successfully."}
        else:
            return {"success": False, "message": "Target moment not found."}
    except Exception as e:
        logger.error(f"Error force deleting moment {moment_id} by admin {admin_id}: {e}")
        return {"success": False, "message": "Database error during forced moment deletion."}
