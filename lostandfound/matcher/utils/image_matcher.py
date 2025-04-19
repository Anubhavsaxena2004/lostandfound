import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress TensorFlow logging
os.environ['TF_CPP_MIN_VLOG_LEVEL'] = '3'  # Suppress verbose logging
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'  # Force CPU usage

import tensorflow as tf
import numpy as np
from tensorflow.keras.applications import MobileNet
from tensorflow.keras.applications.mobilenet import preprocess_input
from tensorflow.keras.preprocessing import image

def initialize_model():
    """Initialize the MobileNet model with proper input shape."""
    try:
        input_shape = (224, 224, 3)  # Standard input shape for MobileNet
        model = MobileNet(
            weights='imagenet',
            include_top=False,
            pooling='avg',
            input_shape=input_shape
        )
        return model
    except Exception as e:
        print(f"Error initializing model: {str(e)}")
        return None

# Initialize model once at module level
model = initialize_model()

def extract_features(img_path):
    """Extract features from an image using MobileNet."""
    if model is None:
        print("Model not initialized")
        return None
        
    try:
        # Load and preprocess the image
        img = image.load_img(img_path, target_size=(224, 224))
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        x = preprocess_input(x)

        # Extract features
        features = model.predict(x, verbose=0)  # Suppress prediction output
        return features.flatten()
    except Exception as e:
        print(f"Error extracting features from image {img_path}: {str(e)}")
        return None

def compute_similarity(features1, features2):
    """Compute cosine similarity between two feature vectors."""
    if features1 is None or features2 is None:
        return 0.0
    
    try:
        norm1 = np.linalg.norm(features1)
        norm2 = np.linalg.norm(features2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
            
        return np.dot(features1, features2) / (norm1 * norm2)
    except Exception as e:
        print(f"Error computing similarity: {str(e)}")
        return 0.0

def find_matches(target_features, candidate_features, threshold=0.8):
    """Find matches among candidate features that exceed the similarity threshold."""
    if target_features is None or not candidate_features:
        return []
        
    try:
        matches = []
        for idx, features in enumerate(candidate_features):
            similarity = compute_similarity(target_features, features)
            if similarity > threshold:
                matches.append((idx, similarity))
        return sorted(matches, key=lambda x: x[1], reverse=True)
    except Exception as e:
        print(f"Error finding matches: {str(e)}")
        return [] 