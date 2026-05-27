#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from backend.db_connection import execute_update, execute_query

def init_admins():
    admins = [
        ("Admin1", "111111", "Test Admin A"),
        ("Admin2", "222222", "Test Admin B")
    ]
    
    for username, password, name in admins:
        existing = execute_query(
            "SELECT admin_id FROM admins WHERE admin_username = %s", 
            (username,)
        )
        
        if existing:
            print(f">: Admin '{username}' exists.")
            continue
            
        rows = execute_update(
            "INSERT INTO admins (admin_username, password, name) VALUES (%s, %s, %s)",
            (username, password, name)
        )
        
        if rows > 0:
            print(f"Created: {username}")
        else:
            print(f"Failed to create: {username}")

if __name__ == "__main__":
    init_admins()