import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
import os
from datetime import datetime

# Create a connection to PostgreSQL database
def get_connection():
    # Get the database URL from environment variables
    db_url = os.environ.get('DATABASE_URL')
    # Create and return the SQLAlchemy engine
    return create_engine(db_url)

# Create a table for user history
def create_history_table():
    engine = get_connection()
    with engine.connect() as conn:
        # Check if the table exists
        result = conn.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'recommendation_history'
            );
        """))
        table_exists = result.scalar()
        
        if not table_exists:
            # Create the recommendation_history table if it doesn't exist
            conn.execute(text("""
                CREATE TABLE recommendation_history (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(100) NOT NULL,
                    symptoms TEXT NOT NULL,
                    severity INTEGER NOT NULL,
                    duration VARCHAR(50) NOT NULL,
                    recommendations TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))
            conn.commit()

# Save a recommendation to history
def save_recommendation(username, symptoms, severity, duration, recommendations):
    engine = get_connection()
    
    try:
        with engine.connect() as conn:
            # Convert symptoms list to string
            symptoms_str = ','.join(symptoms)
            # Convert recommendations list to string
            recommendations_str = ','.join(recommendations)
            
            # Insert recommendation history
            conn.execute(text("""
                INSERT INTO recommendation_history 
                (username, symptoms, severity, duration, recommendations) 
                VALUES (:username, :symptoms, :severity, :duration, :recommendations)
            """), {
                "username": username,
                "symptoms": symptoms_str,
                "severity": severity,
                "duration": duration,
                "recommendations": recommendations_str
            })
            conn.commit()
            return True
    except Exception as e:
        st.error(f"Database error: {str(e)}")
        return False

# Get user's recommendation history
def get_user_history(username):
    engine = get_connection()
    
    try:
        with engine.connect() as conn:
            # Get recommendation history for the user
            result = conn.execute(text("""
                SELECT id, symptoms, severity, duration, recommendations, created_at 
                FROM recommendation_history 
                WHERE username = :username
                ORDER BY created_at DESC
            """), {"username": username})
            
            history = []
            for row in result:
                history.append({
                    "id": row[0],
                    "symptoms": row[1].split(','),
                    "severity": row[2],
                    "duration": row[3],
                    "recommendations": row[4].split(','),
                    "timestamp": row[5].strftime("%Y-%m-%d %H:%M:%S")
                })
            
            return history
    except Exception as e:
        st.error(f"Database error: {str(e)}")
        return []