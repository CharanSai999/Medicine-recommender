import pandas as pd
import numpy as np
import pickle
import os
from sklearn.feature_extraction.text import TfidfVectorizer

def train_model():
    # Create data directory if it doesn't exist
    if not os.path.exists('data'):
        os.makedirs('data')
    
    # Generate a synthetic dataset for medicine recommendations
    # In a real application, you would use a real medical dataset
    create_synthetic_data()
    
    # Load the dataset
    df = pd.read_csv('data/medicine_dataset.csv')
    
    # Preprocess the data
    # Convert symptom lists to space-separated strings for vectorization
    df['symptom_string'] = df['symptoms'].apply(lambda x: ' '.join(eval(x)) if isinstance(x, str) else ' '.join(x))
    
    # Extract all unique symptoms
    all_symptoms = set()
    for symptom_list in df['symptoms']:
        if isinstance(symptom_list, str):
            symptoms = eval(symptom_list)
        else:
            symptoms = symptom_list
        all_symptoms.update(symptoms)
    all_symptoms = sorted(list(all_symptoms))
    
    # Create a TF-IDF vectorizer
    vectorizer = TfidfVectorizer()
    symptom_matrix = vectorizer.fit_transform(df['symptom_string'])
    
    # Save the model, vectorizer, and other necessary data
    model_data = {
        'vectorizer': vectorizer,
        'similarity_matrix': symptom_matrix,
        'symptoms': all_symptoms,
        'drug_names': df['drug_name'].tolist()
    }
    
    # Create models directory if it doesn't exist
    if not os.path.exists('models'):
        os.makedirs('models')
    
    # Save the model data
    with open('models/drug_recommendation_model.pkl', 'wb') as f:
        pickle.dump(model_data, f)
    
    print("Model trained and saved successfully.")

def create_synthetic_data():
    """
    Create a synthetic dataset for medicine recommendations.
    This is only used for demonstration purposes.
    """
    # Define common symptoms and medications
    symptoms_list = [
        "fever", "headache", "cough", "runny nose", "sore throat", "fatigue",
        "body ache", "nausea", "vomiting", "diarrhea", "constipation", "dizziness",
        "chest pain", "shortness of breath", "abdominal pain", "rash", "joint pain",
        "back pain", "ear pain", "eye irritation", "swelling", "high blood pressure",
        "low blood pressure", "high blood sugar", "low blood sugar", "anxiety",
        "depression", "insomnia", "loss of appetite", "weight loss", "weight gain"
    ]
    
    medications = [
        "Acetaminophen", "Ibuprofen", "Aspirin", "Amoxicillin", "Azithromycin",
        "Loratadine", "Cetirizine", "Diphenhydramine", "Pseudoephedrine", "Guaifenesin",
        "Dextromethorphan", "Phenylephrine", "Omeprazole", "Ranitidine", "Famotidine",
        "Simvastatin", "Atorvastatin", "Lisinopril", "Amlodipine", "Metformin",
        "Albuterol", "Fluticasone", "Montelukast", "Prednisone", "Metoprolol",
        "Losartan", "Hydrochlorothiazide", "Sertraline", "Fluoxetine", "Escitalopram",
        "Levothyroxine", "Gabapentin", "Tramadol", "Cyclobenzaprine", "Meloxicam",
        "Naproxen", "Ciprofloxacin", "Metronidazole", "Fluconazole", "Amoxicillin-Clavulanate"
    ]
    
    # Create a list to store data
    data = []
    
    # Generate 40 entries with 1-4 symptoms mapped to a medication
    np.random.seed(42)  # For reproducibility
    for i in range(len(medications)):
        # Randomly select 1-4 symptoms for each medication
        num_symptoms = np.random.randint(1, 5)
        med_symptoms = np.random.choice(symptoms_list, num_symptoms, replace=False).tolist()
        
        # Add to data
        data.append({
            'drug_name': medications[i],
            'symptoms': str(med_symptoms),
            'description': f"Medication for treating {', '.join(med_symptoms)}"
        })
    
    # Create a DataFrame and save to CSV
    df = pd.DataFrame(data)
    df.to_csv('data/medicine_dataset.csv', index=False)
    
    print("Synthetic dataset created successfully.")

if __name__ == "__main__":
    train_model()
