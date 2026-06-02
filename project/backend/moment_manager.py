#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
朋友圈管理模块
"""

import logging
from .db_connection import execute_query, execute_update

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
        else:
            logger.error(f"User {user_id} failed to post moment.")
            return {"success": False, "message": "Failed to post moment. Please try again."}
    except Exception as e:
        logger.error(f"Error posting moment for user {user_id}: {e}")
        return {"success": False, "message": "Database error while posting moment."}

def update_moment(moment_id, user_id, content):
    """
    修改朋友圈内容（严格限制只能修改自己的）
    """
    if len(content) > 500:
        return {"success": False, "message": "Content exceeds the maximum length."}
        
    query = "UPDATE moments SET content = %s WHERE moment_id = %s AND user_id = %s"
    try:
        result = execute_update(query, (content, moment_id, user_id))
        if result > 0:
            return {"success": True, "message": "Moment updated successfully."}
        return {"success": False, "message": "Moment not found or you do not have permission to edit it."}
    except Exception as e:
        logger.error(f"Error updating moment {moment_id} for user {user_id}: {e}")
        return {"success": False, "message": "Database error while updating moment."}

def delete_moment(moment_id, user_id):
    """
    删除朋友圈（严格限制只能删除自己的，依靠 ON DELETE CASCADE 自动级联删除评论）
    """
    query = "DELETE FROM moments WHERE moment_id = %s AND user_id = %s"
    try:
        result = execute_update(query, (moment_id, user_id))
        if result > 0:
            return {"success": True, "message": "Moment deleted successfully."}
        return {"success": False, "message": "Moment not found or you do not have permission to delete it."}
    except Exception as e:
        logger.error(f"Error deleting moment {moment_id} for user {user_id}: {e}")
        return {"success": False, "message": "Database error while deleting moment."}

def get_my_moments(user_id):
    """
    获取当前用户自己的朋友圈列表
    用 MomentsTimelineView 视图简化单表过滤
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
    WHERE author_id = %s
    ORDER BY last_update_time DESC
    """
    try:
        moments = execute_query(query, (user_id,))
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
        logger.error(f"Error fetching my moments for user {user_id}: {e}")
        return []

def get_friends_moments(user_id):
    """
    获取好友朋友圈动态流（含最后更新时间、发布者名称及评论详情）
    """
    query = """
    SELECT 
        t.moment_id, 
        t.author_id AS user_id, 
        t.author_username AS username, 
        t.author_name AS name,
        t.content, 
        t.last_update_time, 
        t.comment_count
    FROM MomentsTimelineView t
    JOIN friendships f ON t.author_id = f.friend_id
    WHERE f.user_id = %s
    ORDER BY t.last_update_time DESC
    """
    try:
        moments = execute_query(query, (user_id,))
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
        logger.error(f"Error fetching friends moments for user {user_id}: {e}")
        return []

def add_comment(moment_id, user_id, content):
    """
    对朋友圈添加评论
    """
    query = "INSERT INTO comments (moment_id, user_id, content) VALUES (%s, %s, %s)"
    try:
        result = execute_update(query, (moment_id, user_id, content))
        if result > 0:
            get_id_query = "SELECT comment_id FROM comments WHERE moment_id = %s AND user_id = %s ORDER BY comment_id DESC LIMIT 1"
            new_comment_record = execute_query(get_id_query, (moment_id, user_id))
            new_comment_id = new_comment_record[0]['comment_id']
            
            return {
                "success": True, 
                "message": "Comment added successfully.",
                "comment_id": new_comment_id 
            }
        else:
            return {"success": False, "message": "Failed to add comment. Target moment may not exist."}
    except Exception as e:
        logger.error(f"Error adding comment on moment {moment_id} by user {user_id}: {e}")
        return {"success": False, "message": "Database error while adding comment."}

def delete_comment(comment_id, user_id):
    """
    删除评论（严格限制只能删除自己发布的评论）
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
