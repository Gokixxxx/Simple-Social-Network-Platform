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
    if len(content) > 500:
        return {"success": False, "message": "Content exceeds the maximum length."}
        
    query = "INSERT INTO moments (user_id, content) VALUES (%s, %s)"
    try:
        result = execute_update(query, (user_id, content))
        if result > 0:
            logger.info(f"User {user_id} posted a new moment successfully.")
            

            get_id_query = "SELECT moment_id FROM moments WHERE user_id = %s ORDER BY moment_id DESC LIMIT 1"
            new_moment_record = execute_query(get_id_query, (user_id,))

            new_moment_id = new_moment_record[0]['moment_id']
 
            return {
                "success": True, 
                "message": "Moment posted successfully.", 
                "moment_id": new_moment_id
            }
            # ============================================
            
        else:
            logger.error(f"User {user_id} failed to post moment.")
            return {"success": False, "message": "Failed to post moment. Please try again."}
    except Exception as e:
        logger.error(f"Error posting moment for user {user_id}: {e}")
        return {"success": False, "message": "Database error while posting moment."}

def update_moment(moment_id, user_id, new_content):
    """
    修改朋友圈
    返回: {'success': True/False, 'message': '...'}
    """
    # 确认这条朋友圈存在，且是这个用户发的
    check_query = "SELECT 1 FROM moments WHERE moment_id = %s AND user_id = %s"
    existing_moment = execute_query(check_query, (moment_id, user_id))
    
    if not existing_moment or len(existing_moment) == 0:
        return {"success": False, "message": "Moment not found or you do not have permission to edit it."}
    # 显式追加 last_update_time = NOW()，强迫 MySQL 刷新时间戳
    query = "UPDATE moments SET content = %s, last_update_time = NOW() WHERE moment_id = %s AND user_id = %s"
    try:
        result = execute_update(query, (new_content, moment_id, user_id))
        if result >= 0:
            logger.info(f"Moment ID {moment_id} updated successfully by user {user_id}.")
            return {"success": True, "message": "Moment updated successfully."}
        else:
            logger.info(f"Update canceled or unauthorized for moment ID {moment_id} by user {user_id}.")
            return {"success": False, "message": "Failed to update moment. Please try again."}
    except Exception as e:
        logger.error(f"Error updating moment {moment_id} for user {user_id}: {e}")
        return {"success": False, "message": "Database error during moment update."}

def delete_moment(moment_id, user_id):
    """
    删除朋友圈（会触发删除相关评论）
    返回: {'success': True/False, 'message': '...'}
    """
    query = "DELETE FROM moments WHERE moment_id = %s AND user_id = %s"
    try:
        # Thanks to 'ON DELETE CASCADE' constraint on comments table, 
        # deleting the moment will automatically clean up all associated comments safely.
        result = execute_update(query, (moment_id, user_id))
        if result > 0:
            logger.info(f"Moment ID {moment_id} and its comments deleted successfully by user {user_id}.")
            return {"success": True, "message": "Moment deleted successfully."}
        else:
            logger.info(f"Delete failed or unauthorized for moment ID {moment_id} by user {user_id}.")
            return {"success": False, "message": "Moment not found or you do not have permission to delete it."}
    except Exception as e:
        logger.error(f"Error deleting moment {moment_id} for user {user_id}: {e}")
        return {"success": False, "message": "Database error during moment deletion."}

def get_my_moments(user_id):
    """
    查看我的朋友圈
    返回: [{'moment_id': int, 'content': str, 'last_update_time': str, 'comment_count': int}, ... ]
    """
    query = """
        SELECT moment_id, content, last_update_time, comment_count
        FROM moments
        WHERE user_id = %s
        ORDER BY last_update_time DESC
    """
    try:
        results = execute_query(query, (user_id,))
        if results is None:
            return []
        
        # Convert datetime objects to string format for safety
        for row in results:
            if row.get('last_update_time'):
                row['last_update_time'] = str(row['last_update_time'])
        return results
    except Exception as e:
        logger.error(f"Error fetching moments for user {user_id}: {e}")
        return []

def get_friends_moments(user_id):
    """
    查看好友朋友圈（包含评论）
    返回: [ {'moment_id': int, 'user_id': int, 'username': str, 'content': str, 'last_update_time': str, 'comments': [...]}, ... ]
    """
    # Step 1: Query moments from the user's friends list
    moments_query = """
        SELECT m.moment_id, m.user_id, u.username, m.content, m.last_update_time
        FROM moments m
        JOIN users u ON m.user_id = u.user_id
        JOIN friendships f ON m.user_id = f.friend_id
        WHERE f.user_id = %s
        ORDER BY m.last_update_time DESC
    """
    
    try:
        moments = execute_query(moments_query, (user_id,))
        if not moments:
            return []

        # Step 2: Fetch and bundle comments for each timeline row
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
            
            # Format comment timestamps
            if comments:
                for comment in comments:
                    if comment.get('comment_time'):
                        comment['comment_time'] = str(comment['comment_time'])
                moment['comments'] = comments
            else:
                moment['comments'] = []
                
        return moments
    except Exception as e:
        logger.error(f"Error fetching friends timeline for user {user_id}: {e}")
        return []

def add_comment(moment_id, user_id, content):
    """
    评论朋友圈
    返回: {'success': True/False, 'message': '...', 'comment_id': int}
    """

    if len(content) > 255:
        return {"success": False, "message": "Content exceeds the maximum length of 255 characters."}

    query = "INSERT INTO comments (moment_id, user_id, content) VALUES (%s, %s, %s)"
    try:
        result = execute_update(query, (moment_id, user_id, content))
        if result > 0:
            logger.info(f"User {user_id} commented on moment ID {moment_id} successfully.")
            
            # 获取该用户刚刚生成的 comment_id 
            # 同样使用 ORDER BY comment_id DESC LIMIT 1 来确保拿到最新的一条
            get_id_query = "SELECT comment_id FROM comments WHERE user_id = %s ORDER BY comment_id DESC LIMIT 1"
            new_comment_record = execute_query(get_id_query, (user_id,))
            
            # 提取刚刚生成的 ID
            new_comment_id = new_comment_record[0]['comment_id']
            
            return {
                "success": True, 
                "message": "Comment added successfully.",
                "comment_id": new_comment_id 
            }
            # ============================================
            
        else:
            return {"success": False, "message": "Failed to add comment. Target moment may not exist."}
    except Exception as e:
        logger.error(f"Error adding comment on moment {moment_id} by user {user_id}: {e}")
        return {"success": False, "message": "Database error while adding comment."}

def delete_comment(comment_id, user_id):
    """
    删除评论（只能删除自己的评论）
    返回: {'success': True/False, 'message': '...'}
    """
    query = "DELETE FROM comments WHERE comment_id = %s AND user_id = %s"
    try:
        result = execute_update(query, (comment_id, user_id))
        if result > 0:
            logger.info(f"Comment ID {comment_id} deleted successfully by owner {user_id}.")
            return {"success": True, "message": "Comment deleted successfully."}
        else:
            logger.info(f"Delete failed or unauthorized for comment ID {comment_id} by user {user_id}.")
            return {"success": False, "message": "Comment not found or you do not have permission to delete it."}
    except Exception as e:
        logger.error(f"Error deleting comment {comment_id} for user {user_id}: {e}")
        return {"success": False, "message": "Database error during comment deletion."}
