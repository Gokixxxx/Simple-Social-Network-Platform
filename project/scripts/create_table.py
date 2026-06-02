#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def create_tables():
    from backend.db_connection import execute_transaction

    statements = [
        # 1. 清理旧的视图、触发器和表
        "DROP VIEW IF EXISTS UserProfileView",
        "DROP VIEW IF EXISTS DetailedFriendshipView",
        "DROP VIEW IF EXISTS MomentsTimelineView",
        "DROP TRIGGER IF EXISTS before_friendship_insert",
        "DROP TRIGGER IF EXISTS after_comment_insert",
        "DROP TRIGGER IF EXISTS after_comment_delete",
        "DROP TABLE IF EXISTS comments",
        "DROP TABLE IF EXISTS moments",
        "DROP TABLE IF EXISTS friendships",
        "DROP TABLE IF EXISTS admins",
        "DROP TABLE IF EXISTS users",
        
        # 2. 创建用户表 (users)
        """
        CREATE TABLE users (
            user_id INT PRIMARY KEY AUTO_INCREMENT,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            name VARCHAR(50),
            gender ENUM('M', 'F', 'Other'),
            birth_date DATE
        )
        """,
        
        # 3. 创建管理员表 (admins)
        """
        CREATE TABLE admins (
            admin_id INT PRIMARY KEY AUTO_INCREMENT,
            admin_username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            name VARCHAR(50),
            gender ENUM('M', 'F', 'Other'),
            birth_date DATE
        )
        """,
        
        # 4. 创建好友关系表 (friendships)
        """
        CREATE TABLE friendships (
            user_id INT,
            friend_id INT,
            group_name VARCHAR(50) DEFAULT '默认分组',
            PRIMARY KEY (user_id, friend_id),
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (friend_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
        """,
        
        # 5. 创建朋友圈动态表 (moments)
        """
        CREATE TABLE moments (
            moment_id INT PRIMARY KEY AUTO_INCREMENT,
            user_id INT,
            content TEXT NOT NULL,
            last_update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            comment_count INT DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
        """,
        
        # 6. 创建评论表 (comments)
        """
        CREATE TABLE comments (
            comment_id INT PRIMARY KEY AUTO_INCREMENT,
            moment_id INT,
            user_id INT,
            content TEXT NOT NULL,
            comment_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (moment_id) REFERENCES moments(moment_id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
        """,
        
        # 7. 创建触发器：防止自己加自己为好友
        """
        CREATE TRIGGER before_friendship_insert
        BEFORE INSERT ON friendships
        FOR EACH ROW
        BEGIN
            IF NEW.user_id = NEW.friend_id THEN
                SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'You cannot add yourself as a friend.';
            END IF;
        END
        """,
        
        # 8. 创建触发器：维护朋友圈评论数自增
        """
        CREATE TRIGGER after_comment_insert
        AFTER INSERT ON comments
        FOR EACH ROW
        BEGIN
            UPDATE moments 
            SET comment_count = comment_count + 1 
            WHERE moment_id = NEW.moment_id;
        END
        """,
        
        # 9. 创建触发器：维护朋友圈评论数自减
        """
        CREATE TRIGGER after_comment_delete
        AFTER DELETE ON comments
        FOR EACH ROW
        BEGIN
            UPDATE moments 
            SET comment_count = GREATEST(0, comment_count - 1)
            WHERE moment_id = OLD.moment_id;
        END
        """,
        
        # 10. 【视图 1】用户个人公开信息视图，脱敏密码，动态计算年龄
        """
        CREATE VIEW UserProfileView AS
        SELECT 
            user_id, username, name, gender, birth_date,
            TIMESTAMPDIFF(YEAR, birth_date, CURDATE()) AS age
        FROM users
        """,
        
        # 11. 【视图 2】好友详细关系看板视图，封装 JOIN，统一处理空姓名与默认分组
        """
        CREATE VIEW DetailedFriendshipView AS
        SELECT 
            f.user_id AS user_id, 
            f.friend_id AS friend_id, 
            u.username AS username, 
            IFNULL(u.name, 'N/A') AS name, 
            IFNULL(f.group_name, '默认分组') AS group_name
        FROM friendships f
        JOIN users u ON f.friend_id = u.user_id
        """,
        
        # 12. 【视图 3】朋友圈动态流看板视图，融合发布者信息，解耦上层流媒体逻辑
        """
        CREATE VIEW MomentsTimelineView AS
        SELECT 
            m.moment_id AS moment_id,
            m.user_id AS author_id,
            u.username AS author_username,
            IFNULL(u.name, 'N/A') AS author_name,
            m.content AS content,
            m.last_update_time AS last_update_time,
            m.comment_count AS comment_count
        FROM moments m
        JOIN users u ON m.user_id = u.user_id
        """,
        
        # 13. 初始化默认超级管理员
        "INSERT INTO admins (admin_username, password, name) VALUES ('admin', 'admin123', 'Super Admin')"
    ]
    
    # Map statements to the tuple format required by execute_transaction: (sql, params)
    operations = [(sql, None) for sql in statements]
    
    print("Initializing database: creating tables, views, triggers and default data...")
    
    # Execute all operations within a single transaction
    success = execute_transaction(operations)
    
    if success:
        print("Create table and triggers successfully.")
    else:
        print("Database initialization failed. Transaction has been rolled back safely.")

if __name__ == "__main__":
    create_tables()
