#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from backend.db_connection import execute_update

def create_tables():

    # TODO: 未完成！这个建表和触发器设计只是一个示例（不一定对）
    raise NotImplementedError("TODO: This funciton has not yet been completed.")

    execute_update("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    execute_update("""
        CREATE TRIGGER IF NOT EXISTS after_order_insert
        AFTER INSERT ON orders
        FOR EACH ROW
        BEGIN
            INSERT INTO audit_log (message)
            VALUES (CONCAT('New order: ', NEW.id, ' for user ', NEW.user_id));
        END;
    """)

   
    
if __name__ == "__main__":
    create_tables()
    print("Creat table successfully.")