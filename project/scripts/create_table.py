#!/usr/bin/env python3
# -*- coding: utf-8 -*-


def create_tables():

    from backend.db_connection import execute_transaction
    # Define all SQL operations in chronological order
    statements = [
        # 1. Drop existing tables/views/triggers (in reverse order of dependencies)
        "DROP VIEW IF EXISTS UserProfileView",
        "DROP TRIGGER IF EXISTS before_friendship_insert",  # 清理旧触发器
        "DROP TABLE IF EXISTS comments",
        "DROP TABLE IF EXISTS moments",
        "DROP TABLE IF EXISTS friendships",
        "DROP TABLE IF EXISTS admins",
        "DROP TABLE IF EXISTS users",
        
        # 2. Create users table
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
        
        # 3. Create admins table
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
        
        # 4. Create friendships table (with Cascade Delete)
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
        
        # 【触发器】防止自己加自己好友
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
        
        # 5. Create moments table (with Cascade Delete)
        """
        CREATE TABLE moments (
            moment_id INT PRIMARY KEY AUTO_INCREMENT,
            user_id INT,
            content VARCHAR(500) NOT NULL,
            last_update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
        """,
        
       # 6. Create comments table (with Double Cascade Delete)
        """
        CREATE TABLE comments (
            comment_id INT PRIMARY KEY AUTO_INCREMENT,
            moment_id INT,
            user_id INT,
            content VARCHAR(255) NOT NULL,
            comment_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (moment_id) REFERENCES moments(moment_id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
        """,
        "DROP TRIGGER IF EXISTS after_comment_insert",
        "DROP TRIGGER IF EXISTS after_comment_delete",
        # 触发器：新增评论时，朋友圈评论数 + 1
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
        # 触发器：删除评论时，朋友圈评论数 - 1
        """
        CREATE TRIGGER after_comment_delete
        AFTER DELETE ON comments
        FOR EACH ROW
        BEGIN
            UPDATE moments 
            SET comment_count = GREATEST(0, comment_count - 1)  -- 使用 GREATEST 确保不会出现负数，增加安全性
            WHERE moment_id = OLD.moment_id;
        END
        """,
        
        # 7. Create view to calculate age dynamically
        """
        CREATE VIEW UserProfileView AS
        SELECT 
            user_id, username, name, gender, birth_date,
            TIMESTAMPDIFF(YEAR, birth_date, CURDATE()) AS age
        FROM users
        """,
        
        # 8. Initialize default admin user
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
