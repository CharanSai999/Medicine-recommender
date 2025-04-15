import streamlit as st
import sqlite3
import hashlib
import os

# Create a connection to SQLite database in memory
def get_connection():
    return sqlite3.connect('drug_recommendation.db', check_same_thread=False)

# Create a table for user authentication
def create_user_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    ''')
    conn.commit()
    conn.close()

# Hash the password for security
def make_hash(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# Register a new user
def register_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if username already exists
    cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    
    if result:
        conn.close()
        return "Username already exists"
    
    # Hash the password and store the user
    hashed_password = make_hash(password)
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", 
                      (username, hashed_password))
        conn.commit()
        conn.close()
        return "success"
    except Exception as e:
        conn.close()
        return f"Error: {str(e)}"

# Login verification
def login_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get stored password for the username
    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    
    if result:
        stored_password = result[0]
        hashed_password = make_hash(password)
        
        if stored_password == hashed_password:
            conn.close()
            return True
    
    conn.close()
    return False

# Authenticate middleware function
def authenticate(username, password):
    return login_user(username, password)
