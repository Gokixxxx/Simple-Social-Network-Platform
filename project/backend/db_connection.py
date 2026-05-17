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

required_vars = ["DB_HOST", "DB_PORT", "DB_USER", "DB_PASSWORD", "DB_NAME"]
for var in required_vars:
    if not os.getenv(var):
        raise EnvironmentError(f"Missing: {var}")
    
logger = logging.getLogger(__name__)

def create_connection():
    """
    create database connection

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
        else:
            logger.info("Unknown Error while connecting to MySQL.")
            return None
        
    except Error as e:
        logger.error(f"Error while connecting to MySQL: {e}")
        return None

def close_connection(connection):
    """
    close database connection

    Args: 
        - connection: connection object
    """
    if connection and connection.is_connected():
        try:
            connection.close()
            logger.info("MySQL connection is closed.")

        except Error as e:
            logger.error(f"Error while closing the connection: {e}")

def execute_query(query: str, params: tuple = None) -> list[tuple] | None:
    """
    execute SELECT operation

    Args:
        - query: the SELECT clause, using '%s' as a data placeholder
        - params: the data corresponding to those %s placeholders mentioned above
    Returns:
        - a tuple list, representing the result of SELECT clause 
    """
    connection = create_connection()
    if not connection:
        return None

    cursor = None
    try:
        cursor = connection.cursor()
        cursor.execute(query, params)
        result = cursor.fetchall()
        logger.debug(f"Executed query: {query}, with params: {params}. Fetched {len(result)} rows.")
        return result
    
    except Error as e:
        logger.error(f"Error while executing query: {query}, with params: {params}. Error: {e}")
        return None
    
    finally:
        if cursor:
            cursor.close()
        close_connection(connection)

def execute_update(query: str, params: tuple = None) -> int:
    """
    execute UPDATE/INSERT/DELETE operation
    
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
    
    except Error as e:
        logger.error(f"Error while executing update: {query}, with params: {params}. Error: {e}")
        connection.rollback()  # Rollback in case of error
        return -1
    
    finally:
        if cursor:
            cursor.close()
        close_connection(connection)