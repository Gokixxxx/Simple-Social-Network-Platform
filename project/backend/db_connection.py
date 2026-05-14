#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Database connector
"""

import os
import logging
from contextlib import contextmanager
import mysql.connector
from mysql.connector import Error

from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
load_dotenv(dotenv_path)

required_vars = ["DB_HOST", "DB_USER", "DB_PASSWORD", "DB_NAME"]
for var in required_vars:
    if not os.getenv(var):
        raise EnvironmentError(f"Missing: {var}")
    
logger = logging.getLogger(__name__)

def get_connection():
    """
    获取数据库连接
    返回: connection对象 或 None（失败时）
    """
    pass

def execute_query(query, params=None, fetch='all'):
    """
    执行查询语句（SELECT）
    参数:
        query: SQL查询语句
        params: 参数元组（防止SQL注入）
        fetch: 'all'（返回所有结果）或 'one'（返回单条）
    返回: 查询结果列表 或 None
    """
    pass

def execute_update(query, params=None):
    """
    执行更新语句（INSERT/UPDATE/DELETE）
    参数:
        query: SQL更新语句
        params: 参数元组
    返回: {'success': True/False, 'message': '...', 'last_id': int}
    """
    pass

def execute_transaction(queries):
    """
    执行事务（多个SQL语句）
    参数:
        queries: 列表，每个元素是 (query, params) 元组
    返回: {'success': True/False, 'message': '...'}
    """
    pass