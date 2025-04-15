import streamlit as st
import pandas as pd
import numpy as np
import pickle
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Function to load the model (or train if not available)
@st.cache_resource
def load_model():
    model_path = "models/drug_recommendation_model.pkl"
    
    # Check if model exists, if not train it first
    if not os.path.exists(model_path):
        # If the models directory doesn't exist, create it
        if not os.path.exists("models"):
            os.makedirs("models")
        
        from model_training import train_model
        train_model()
    
    # Load the saved model
    with open(model_path, 'rb') as f:
        model_data = pickle.load(f)
    
    # Extract components from the model data
    vectorizer = model_data['vectorizer']
    similarity_matrix = model_data['similarity_matrix']
    all_symptoms = model_data['symptoms']
    drug_names = model_data['drug_names']
    
    return similarity_matrix, vectorizer, all_symptoms, drug_names

# Function to get recommendations based on symptoms
def get_recommendations(user_symptoms, vectorizer, similarity_matrix, drug_names, top_n=10):
    # Combine the user's symptoms into a single string
    user_input = ' '.join(user_symptoms)
    
    # Transform the user input using the TF-IDF vectorizer
    user_vector = vectorizer.transform([user_input])
    
    # Calculate similarity scores
    similarity_scores = cosine_similarity(user_vector, similarity_matrix)
    
    # Get indices of top recommendations
    top_indices = np.argsort(similarity_scores[0])[-top_n:][::-1]
    
    # Return the drug names for the top indices
    return [drug_names[idx] for idx in top_indices]
