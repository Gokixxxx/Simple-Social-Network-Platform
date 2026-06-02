#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
管理员管理模块
"""

import logging
from .db_connection import execute_query, execute_update

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
    获取管理员个人信息
    """
    query = "SELECT admin_id, admin_username, name, gender, birth_date FROM admins WHERE admin_id = %s"
    try:
        rows = execute_query(query, (admin_id,))
        return rows[0] if rows else None
    except Exception as e:
        logger.error(f"Error fetching admin profile for ID {admin_id}: {e}")
        return None

def update_admin_profile(admin_id, name, gender, birth_date):
    """
    更新管理员个人信息
    """
    query = "UPDATE admins SET name = %s, gender = %s, birth_date = %s WHERE admin_id = %s"
    try:
        result = execute_update(query, (name, gender, birth_date, admin_id))
        if result >= 0:
            return {"success": True, "message": "Admin profile updated successfully."}
        return {"success": False, "message": "Profile update failed."}
    except Exception as e:
        logger.error(f"Error updating admin profile for ID {admin_id}: {e}")
        return {"success": False, "message": "Database error."}

def get_all_users():
    """
    获取所有有效用户列表（供管理员审查）
    接入视图：用 UserProfileView 视图来直接获取包含动态年龄的信息
    """
    query = "SELECT user_id, username, name, gender, birth_date, age FROM UserProfileView"
    try:
        results = execute_query(query)
        return results if results is not None else []
    except Exception as e:
        logger.error(f"Error fetching all users for admin: {e}")
        return []

def delete_user_by_admin(admin_id, target_user_id):
    """
    删除用户（管理员权限）
    """
    admin_check = execute_query("SELECT 1 FROM admins WHERE admin_id = %s", (admin_id,))
    if not admin_check:
        return {"success": False, "message": "Unauthorized. Action requires admin privileges."}

    query = "DELETE FROM users WHERE user_id = %s"
    try:
        result = execute_update(query, (target_user_id,))
        if result > 0:
            logger.warning(f"Admin {admin_id} deleted user ID {target_user_id}.")
            return {"success": True, "message": "User removed successfully."}
        return {"success": False, "message": "Target user not found."}
    except Exception as e:
        logger.error(f"Error deleting user {target_user_id} by admin {admin_id}: {e}")
        return {"success": False, "message": "Database error."}

def get_all_moments_for_review(admin_id=None):
    """
    获取全网朋友圈动态以供管理员审查
    用 MomentsTimelineView 视图，消除了底层的硬编码 JOIN 树
    """
    query = """
    SELECT 
        moment_id, 
        author_id AS user_id, 
        author_username AS username, 
        author_name AS name,
        content, 
        last_update_time, 
        comment_count 
    FROM MomentsTimelineView 
    ORDER BY last_update_time DESC
    """
    try:
        moments = execute_query(query)
        if moments is None:
            return []

        for moment in moments:
            mid = moment['moment_id']
            comment_query = """
            SELECT 
                c.comment_id, 
                c.user_id AS commenter_id, 
                u.username AS commenter_username,
                IFNULL(u.name, u.username) AS commenter_name, 
                c.content, 
                c.comment_time 
            FROM comments c
            JOIN users u ON c.user_id = u.user_id
            WHERE c.moment_id = %s
            ORDER BY c.comment_time ASC
            """
            comments = execute_query(comment_query, (mid,))
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
    admin_check = execute_query("SELECT 1 FROM admins WHERE admin_id = %s", (admin_id,))
    if not admin_check:
        return {"success": False, "message": "Unauthorized. Action requires admin privileges."}

    query = "DELETE FROM moments WHERE moment_id = %s"
    try:
        result = execute_update(query, (moment_id,))
        if result > 0:
            logger.warning(f"Admin {admin_id} force deleted non-compliant moment ID {moment_id}.")
            return {"success": True, "message": "Violation moment removed successfully."}
        else:
            return {"success": False, "message": "Target moment not found."}
    except Exception as e:
        logger.error(f"Error force deleting moment {moment_id} by admin {admin_id}: {e}")
        return {"success": False, "message": "Database error during forced moment deletion."}
