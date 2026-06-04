#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Database connector
"""

import os
import logging
from contextlib import contextmanager
import mysql.connector
from typing import Optional, List, Tuple, Any
from mysql.connector import connect, Error as MySQLError, MySQLConnection

from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
load_dotenv(dotenv_path)

required_vars = ["DB_HOST", "DB_PORT", "DB_USER", "DB_PASSWORD", "DB_NAME"]
for var in required_vars:
    if not os.getenv(var):
        raise EnvironmentError(f"Missing: {var}")
    
logger = logging.getLogger(__name__)

def create_connection():
    """
    Internal function to create a database connection.

    Return: 
        - connection object[success] or None[failure]
    """
    try:
        connection = mysql.connector.connect(
            host = os.getenv("DB_HOST"),
            port = os.getenv("DB_PORT"),
            user = os.getenv("DB_USER"),
            password = os.getenv("DB_PASSWORD"),
            database = os.getenv("DB_NAME")
        )
        if connection.is_connected():
            logger.info("Successfully connected to the database.")
            return connection
        
    except MySQLError as e:
        logger.error(f"Error while connecting to MySQL: {e}")
        return None

def close_connection(connection):
    """
    Internal function to close a database connection.

    Args: 
        - connection: connection object
    """
    if connection and connection.is_connected():
        try:
            connection.close()
            logger.info("MySQL connection is closed.")

        except MySQLError as e:
            logger.error(f"Error while closing the connection: {e}")

def execute_query(query: str, params: tuple = None) -> list[dict] | None:
    """
    Manager call: executing SELECT operation.
    ...
    """
    connection = create_connection()
    if not connection:
        return None

    cursor = None
    try:
        cursor = connection.cursor(dictionary=True) 
        
        cursor.execute(query, params)
        result = cursor.fetchall()
        logger.debug(f"Executed query: {query}, with params: {params}. Fetched {len(result)} rows.")
        return result
    
    except MySQLError as e:
        logger.error(f"Error while executing query: {query}, with params: {params}. Error: {e}")
        return None
    
    finally:
        if cursor:
            cursor.close()
        close_connection(connection)

def execute_update(query: str, params: tuple = None) -> int:
    """
    Manager call: executing UPDATE/INSERT/DELETE operation.
    
    Args:
        - query: the UPDATE/INSERT/DELETE clause, using '%s' as a data placeholder
        - params: the data corresponding to those %s placeholders mentioned above
    Returns:
        - an integer, representing the line number of affected rows[success] or -1[failure]
    """
    connection = create_connection()
    if not connection:
        return -1

    cursor = None
    try:
        cursor = connection.cursor()
        cursor.execute(query, params)
        connection.commit()  # Commit the transaction
        affected_rows = cursor.rowcount
        logger.debug(f"Executed update: {query}, with params: {params}. Affected {affected_rows} rows.")
        return affected_rows
    
    except MySQLError as e:
        logger.error(f"Error while executing update: {query}, with params: {params}. Error: {e}")
        connection.rollback()  # Rollback in case of error
        return -1
    
    finally:
        if cursor:
            cursor.close()
        close_connection(connection)

def begin_transaction() -> Optional[MySQLConnection]:
    """
    Starts a new database transaction.
    
    Returns:
        - connection object[success] or None[failure]
        
    Usage:
        conn = begin_transaction()
        if conn:
            try:
                execute_update_in_transaction(conn, "INSERT ...", params)
                execute_update_in_transaction(conn, "UPDATE ...", params)
                commit_transaction(conn)
            except Exception as e:
                rollback_transaction(conn)
                raise e
    """
    conn = create_connection()
    if conn:
        conn.autocommit = False # auto commit is banned
        logger.debug("Transaction started.")
    return conn

def commit_transaction(connection: MySQLConnection) -> bool:
    """
    Commits the current transaction.

    Args:
        - connection: the connection to commit
    Returns:
        - a bool variable to describe whether the commit operation was successful or not.

    """
    try:
        connection.commit()
        logger.debug("Transaction committed.")
        return True
    
    except MySQLError as e:
        logger.error(f"Error committing transaction: {e}")
        return False
    
    finally:
        if connection.is_connected():
            connection.close()
            logger.debug("Database connection closed after commit.")

def rollback_transaction(connection: MySQLConnection) -> bool:
    """
    Rolls back the current transaction.

    Args:
        - connection: the connection to rollback
    Returns:
        - a bool variable to describe whether the rollback operation was successful or not.
    """
    try:
        connection.rollback()
        logger.debug("Transaction rolled back.")
        return True
    except MySQLError as e:
        logger.error(f"Error rolling back transaction: {e}")
        return False
    finally:
        if connection.is_connected():
            connection.close()
            logger.debug("Database connection closed after rollback.")

def execute_transaction(operations: List[Tuple[str, Optional[Tuple]]]) -> bool:
    """
    批量执行多个SQL操作的事务函数（兼容原有代码调用）
    Args:
        operations: 操作列表，每个元素为 (sql语句, 参数元组)
    Returns:
        事务执行成功返回True，失败返回False并自动回滚
    """
    conn = begin_transaction()
    if not conn:
        logger.error("Failed to start transaction")
        return False
    
    try:
        for sql, params in operations:
            result = execute_update_in_transaction(conn, sql, params)
            if result == -1:
                raise Exception(f"SQL execution failed: {sql[:100]}")
        
        return commit_transaction(conn)
    
    except Exception as e:
        logger.error(f"Transaction failed: {str(e)}")
        rollback_transaction(conn)
        return False

def execute_query_in_transaction(connection: MySQLConnection, query: str, params: Optional[Tuple] = None) -> list[tuple] | None:
    """
    Executes a SELECT query within an existing transaction.

    Args:
        - connection: the connection in transaction
        - query: the SELECT clause, using '%s' as a data placeholder
        - params: the data corresponding to those %s placeholders mentioned above
    Returns:
        - a tuple list, representing the result of SELECT clause or None for failure

    """
    cursor = None
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params or ())
        result = cursor.fetchall()
        return result
    except MySQLError as e:
        logger.error(f"Query execution error in transaction: {e}")
        return None
    finally:
        if cursor:
            cursor.close()

def execute_update_in_transaction(connection: MySQLConnection, query: str, params: Optional[Tuple] = None) -> int:
    """
    Executes an INSERT, UPDATE, or DELETE statement within an existing transaction.

    Args:
        - connection: the connection in transaction
        - query: the INSERT, UPDATE, or DELETE clause, using '%s' as a data placeholder
        - params: the data corresponding to those %s placeholders mentioned above
    Returns:
        - an integer, representing the line number of affected rows[success] or -1[failure]
    """
    cursor = None
    try:
        cursor = connection.cursor()
        cursor.execute(query, params or ())
        return cursor.rowcount
    except MySQLError as e:
        logger.error(f"Update execution error in transaction: {e}")
        return -1
    finally:
        if cursor:
            cursor.close()
