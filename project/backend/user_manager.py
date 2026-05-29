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
        logger.error("Failed to check for existing username during registration.")
        return {"success": False, "message": "Database error."}

    if len(existing_user) > 0:
        logger.info(f"Registration failed: Username '{username}' is already taken.")
        return {"success": False, "message": "Username already exists."}

    # --- Step 2: Insert the new user ---
    query = "INSERT INTO users (username, password) VALUES (%s, %s)"
    result = execute_update(query, (username, password))    
    
    if result > 0:  # 插入成功
        logger.info(f"New user registered: {username}")

        # 1. 编写查询语句，利用刚注册的 username 查出记录
        get_id_query = "SELECT user_id FROM users WHERE username = %s"
        # 2. 执行查询，得到一个包含字典的列表，例如：[{'user_id': 5}]
        new_user_record = execute_query(get_id_query, (username,))
        
        # 3. 提取具体的 ID 值。new_user_record[0] 取出第一行字典，['user_id'] 取出对应的值
        new_user_id = new_user_record[0]['user_id']
        
        # 4. 在最终返回的字典中，务必包含 'user_id' 键
        return {
            "success": True, 
            "message": "User registered successfully.", 
            "user_id": new_user_id
        }
    else:           # 插入失败
        logger.error(f"Failed to register user: {username}")
        return {"success": False, "message": "Failed to register user. Please try again."}
    
def login_user(username, password):
    """
    用户登录
    返回: {'success': True/False, 'message': '...', 'user_id': int, 'name': str}
    """
    query = "SELECT user_id, name FROM users WHERE username = %s AND password = %s"
    try:
        user_rows = execute_query(query, (username, password))
        if user_rows is None:
            return {"success": False, "message": "Database error."}
        
        if len(user_rows) > 0:
            # Assumes execute_query returns a list of dictionaries
            user = user_rows[0]
            logger.info(f"User logged in successfully: {username}")
            return {
                "success": True, 
                "message": "Login successfully.", 
                "user_id": user['user_id'], 
                "name": user.get('name')
            }
        else:
            logger.info(f"Failed login attempt for username: {username}")
            return {"success": False, "message": "Invalid username or password."}
    except Exception as e:
        logger.error(f"Error during login for {username}: {e}")
        return {"success": False, "message": "An error occurred during login."}

def get_user_profile(user_id):
    """
    获取用户个人信息
    返回: {'user_id': int, 'username': str, 'name': str, 'gender': str, 'birth_date': str, 'age': int}
    """
    # Directly query the UserProfileView to get the dynamically calculated age
    query = "SELECT * FROM UserProfileView WHERE user_id = %s"
    try:
        profile_rows = execute_query(query, (user_id,))
        if profile_rows and len(profile_rows) > 0:
            profile = profile_rows[0]
            # Convert birth_date to string format if it is a datetime.date object
            if profile.get('birth_date'):
                profile['birth_date'] = str(profile['birth_date'])
            return profile
        return {}
    except Exception as e:
        logger.error(f"Failed to get user profile for user_id {user_id}: {e}")
        return {}

def update_user_profile(user_id, name=None, gender=None, birth_date=None):
    """
    更新用户个人信息
    返回: {'success': True/False, 'message': '...'}
    """
    query = "UPDATE users SET name = %s, gender = %s, birth_date = %s WHERE user_id = %s"
    try:
        result = execute_update(query, (name, gender, birth_date, user_id))
        if result >= 0:
            logger.info(f"User profile updated successfully for user_id: {user_id}")
            return {"success": True, "message": "Profile updated successfully."}
        else:
            return {"success": False, "message": "Failed to update profile."}
    except Exception as e:
        logger.error(f"Error updating user profile for user_id {user_id}: {e}")
        return {"success": False, "message": "Database error during profile update."}

def search_users(keyword):
    """
    搜索用户（通过用户名或姓名模糊匹配）
    返回: [{'user_id': int, 'username': str, 'name': str}, ...]
    """
    query = "SELECT user_id, username, name FROM users WHERE username LIKE %s OR name LIKE %s"
    search_term = f"%{keyword}%"
    try:
        results = execute_query(query, (search_term, search_term))
        return results if results is not None else []
    except Exception as e:
        logger.error(f"Error searching users with keyword '{keyword}': {e}")
        return []

def add_friend(user_id, friend_id, group_name="默认分组"):
    """
    添加好友（双向，使用事务）
    返回: {'success': True/False, 'message': '...'}
    """
    if int(user_id) == int(friend_id):
        return {"success": False, "message": "You cannot add yourself as a friend."}
    
    # Check if friendship already exists
    check_query = "SELECT 1 FROM friendships WHERE user_id = %s AND friend_id = %s"
    existing = execute_query(check_query, (user_id, friend_id))
    if existing and len(existing) > 0:
        return {"success": False, "message": "You are already friends with this user."}

    # Prepare two operations for a mutual bidirectional friendship relationship
    sql = "INSERT INTO friendships (user_id, friend_id, group_name) VALUES (%s, %s, %s)"
    operations = [
        (sql, (user_id, friend_id, group_name)),
        (sql, (friend_id, user_id, "默认分组"))  # The friend puts you into their default group
    ]
    
    try:
        success = execute_transaction(operations)
        if success:
            logger.info(f"Mutual friendship established between user {user_id} and user {friend_id}")
            return {"success": True, "message": "Friend added successfully."}
        else:
            return {"success": False, "message": "Failed to add friend. Transaction rolled back."}
    except Exception as e:
        logger.error(f"Transaction error while adding friend (user {user_id}, friend {friend_id}): {e}")
        return {"success": False, "message": "Database error during mutual friend addition."}

def remove_friend(user_id, friend_id):
    """
    删除好友（双向，使用事务）
    返回: {'success': True/False, 'message': '...'}
    """
    # 检查好友关系是否存在
    check_query = "SELECT 1 FROM friendships WHERE user_id = %s AND friend_id = %s"
    existing = execute_query(check_query, (user_id, friend_id))
    
    if not existing or len(existing) == 0:
        logger.info(f"Failed to remove friend: user {user_id} and user {friend_id} are not friends.")
        return {"success": False, "message": "Friend not found. You are not friends with this user."}

    sql = "DELETE FROM friendships WHERE user_id = %s AND friend_id = %s"
    operations = [
        (sql, (user_id, friend_id)),
        (sql, (friend_id, user_id))
    ]
    
    try:
        success = execute_transaction(operations)
        if success:
            logger.info(f"Mutual friendship removed between user {user_id} and user {friend_id}")
            return {"success": True, "message": "Friend removed successfully."}
        else:
            return {"success": False, "message": "Failed to remove friend. Transaction rolled back."}
    except Exception as e:
        logger.error(f"Transaction error while removing friend (user {user_id}, friend {friend_id}): {e}")
        return {"success": False, "message": "Database error during mutual friend removal."}

def get_friends_list(user_id, group_name=None):
    """
    获取好友列表（可按分组筛选）
    返回: [{'friend_id': int, 'username': str, 'name': str, 'group_name': str}, ...]
    """
    if group_name:
        query = """
        SELECT 
            f.friend_id, 
            u.username, 
            IFNULL(u.name, 'N/A') AS name, 
            IFNULL(f.group_name, '默认分组') AS group_name 
        FROM friendships f 
        JOIN users u ON f.friend_id = u.user_id 
        WHERE f.user_id = %s AND f.group_name = %s
        """
        params = (user_id, group_name)
    else:
        query = """
        SELECT 
            f.friend_id, 
            u.username, 
            IFNULL(u.name, 'N/A') AS name, 
            IFNULL(f.group_name, '默认分组') AS group_name 
        FROM friendships f 
        JOIN users u ON f.friend_id = u.user_id 
        WHERE f.user_id = %s
        """
        params = (user_id,)
        
    try:
        results = execute_query(query, params)
        return results if results is not None else []
    except Exception as e:
        logger.error(f"Error fetching friends list for user {user_id}: {e}")
        return []

def update_friend_group(user_id, friend_id, new_group_name):
    """
    修改好友分组（单向修改用户自己对好友的分组归类）
    返回: {'success': True/False, 'message': '...'}
    """
    query = "UPDATE friendships SET group_name = %s WHERE user_id = %s AND friend_id = %s"
    try:
        result = execute_update(query, (new_group_name, user_id, friend_id))
        if result > 0:
            logger.info(f"User {user_id} changed friend {friend_id}'s group to '{new_group_name}'")
            return {"success": True, "message": "Friend group updated successfully."}
            
        return {"success": False, "message": "Friendship record not found or group unchanged."}
    except Exception as e:
        logger.error(f"Error updating friend group for user {user_id}, friend {friend_id}: {e}")
        return {"success": False, "message": "Database error during group modification."}
