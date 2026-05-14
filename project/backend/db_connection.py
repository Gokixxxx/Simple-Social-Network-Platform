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

def create_connection():
    """
    create database connection

    Return: 
        - connection object[success] or None[failure]
    """
    pass

def close_connection(connection):
    """
    close database connection

    Args: 
        - connection: connection object
    """
    pass

def execute_query(query: str, params: tuple = None) -> list[tuple] | None:
    """
    execute SELECT operation

    Args:
        - query: the SELECT clause, using '%s' as a data placeholder
        - params: the data corresponding to those %s placeholders mentioned above
    Returns:
        - a tuple list, representing the result of SELECT clause 
    """
    pass

def execute_update(query: str, params: tuple = None) -> int:
    """
    execute UPDATE/INSERT/DELETE operation
    
    Args:
        - query: the UPDATE/INSERT/DELETE clause, using '%s' as a data placeholder
        - params: the data corresponding to those %s placeholders mentioned above
    Returns:
        - an integer, representing the line number of affected rows[success] or -1[failure]
    """
    pass