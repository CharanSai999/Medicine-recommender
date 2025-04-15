import streamlit as st
import hashlib
import os
import sqlalchemy as sa
from sqlalchemy import create_engine, text
import psycopg2
import os

# Create a connection to PostgreSQL database
def get_connection():
    # Get the database URL from environment variables
    db_url = os.environ.get('DATABASE_URL')
    # Create and return the SQLAlchemy engine
    return create_engine(db_url)

# Create a table for user authentication
def create_user_table():
    engine = get_connection()
    with engine.connect() as conn:
        # Check if the table exists
        result = conn.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'users'
            );
        """))
        table_exists = result.scalar()
        
        if not table_exists:
            # Create the users table if it doesn't exist
            conn.execute(text("""
                CREATE TABLE users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(100) UNIQUE NOT NULL,
                    password VARCHAR(100) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))
            conn.commit()

# Hash the password for security
def make_hash(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# Register a new user
def register_user(username, password):
    engine = get_connection()
    
    # Hash the password
    hashed_password = make_hash(password)
    
    try:
        with engine.connect() as conn:
            # Check if username already exists
            result = conn.execute(text("SELECT username FROM users WHERE username = :username"), 
                                {"username": username})
            
            if result.fetchone():
                return "Username already exists"
            
            # Insert new user
            conn.execute(text("INSERT INTO users (username, password) VALUES (:username, :password)"), 
                      {"username": username, "password": hashed_password})
            conn.commit()
            return "success"
    except Exception as e:
        return f"Error: {str(e)}"

# Login verification
def login_user(username, password):
    engine = get_connection()
    
    # Hash the password
    hashed_password = make_hash(password)
    
    try:
        with engine.connect() as conn:
            # Get stored password for the username
            result = conn.execute(text("SELECT password FROM users WHERE username = :username"), 
                               {"username": username})
            user = result.fetchone()
            
            if user and user[0] == hashed_password:
                return True
    except Exception as e:
        st.error(f"Database error: {str(e)}")
    
    return False

# Authenticate middleware function
def authenticate(username, password):
    return login_user(username, password)
