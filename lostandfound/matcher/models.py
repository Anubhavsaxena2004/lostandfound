import tensorflow as tf
from tensorflow import MobileNetV2
from tensorflow import image
import numpy as np
from geopy.distance import geodesic
import re
from transformers import pipeline
from datetime import datetime, timedelta

class ItemMatcher:
    def __init__(self):
        # Image models
        self.image_model = MobileNetV2(weights='imagenet', include_top=False, pooling='avg')
        self.object_detector = pipeline("object-detection", model="facebook/detr-resnet-50")
        
        # Text models
        self.sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
        
    # Image processing methods
    def preprocess_image(self, img_path):
        img = image.load_img(img_path, target_size=(224, 224))
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        x = tf.keras.applications.mobilenet_v2.preprocess_input(x)
        return x

    def get_image_features(self, img_path):
        processed_image = self.preprocess_image(img_path)
        features = self.image_model.predict(processed_image)
        return features.flatten()

    # Text processing methods
    def get_text_features(self, description):
        return self.text_model.encode(description)
    
    # Location processing methods
    def extract_coordinates(self, location_str):
        """Extract lat/long from location string"""
        match = re.search(r'(-?\d+\.\d+),\s*(-?\d+\.\d+)', location_str)
        if match:
            return float(match.group(1)), float(match.group(2))
        return None
    
    def calculate_location_similarity(self, loc1, loc2):
        """Calculate distance between two locations in km"""
        if not loc1 or not loc2:
            return 0
        coords1 = self.extract_coordinates(loc1)
        coords2 = self.extract_coordinates(loc2)
        if not coords1 or not coords2:
            return 0
        distance = geodesic(coords1, coords2).km
        # Convert distance to similarity score (0-1)
        return max(0, 1 - (distance / 100))  # 100km max distance for full similarity

    # Combined matching
    def calculate_combined_similarity(self, item1, item2):
        """Calculate weighted similarity score (0-1) considering all factors"""
        weights = {
            'image': 0.35,
            'objects': 0.15,
            'text': 0.25,
            'sentiment': 0.05,
            'location': 0.15,
            'time': 0.05
        }
        
        similarities = {
            'image': 0,
            'objects': 0,
            'text': 0,
            'sentiment': 0,
            'location': 0,
            'time': 0
        }
        
        # Image processing
        if item1.image and item2.image:
            # Visual similarity
            img1_features = self.get_image_features(item1.image.path)
            img2_features = self.get_image_features(item2.image.path)
            similarities['image'] = self.calculate_cosine_similarity(img1_features, img2_features)
            
            # Object detection
            objects1 = self.object_detector(item1.image.path)
            objects2 = self.object_detector(item2.image.path)
            similarities['objects'] = self.compare_objects(objects1, objects2)
        
        # Text processing
        if item1.description and item2.description:
            # Semantic similarity
            text1_features = self.get_text_features(item1.description)
            text2_features = self.get_text_features(item2.description)
            similarities['text'] = self.calculate_cosine_similarity(text1_features, text2_features)
            
            # Sentiment analysis
            sentiment1 = self.sentiment_analyzer(item1.description)[0]
            sentiment2 = self.sentiment_analyzer(item2.description)[0]
            if sentiment1['label'] == sentiment2['label']:
                similarities['sentiment'] = 1 - abs(sentiment1['score'] - sentiment2['score'])
        
        # Location similarity
        if item1.location and item2.location:
            similarities['location'] = self.calculate_location_similarity(item1.location, item2.location)
            
        # Time decay (prioritize recent items)
        time_diff = abs((item1.created_at - item2.created_at).days)
        similarities['time'] = max(0, 1 - (time_diff / 30))  # 30-day decay
        
        # Calculate weighted sum
        total_score = sum(weight * similarities[factor] 
                         for factor, weight in weights.items())
        
        return total_score

    def compare_objects(self, objects1, objects2):
        """Compare detected objects between images"""
        labels1 = {obj['label'] for obj in objects1}
        labels2 = {obj['label'] for obj in objects2}
        common = labels1 & labels2
        return len(common) / max(len(labels1), len(labels2))
        
    def calculate_cosine_similarity(self, vec1, vec2):
        """Generic cosine similarity calculation"""
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

    def find_best_matches(self, item, candidate_items, threshold=0.6):
        """Find all matches above similarity threshold"""
        matches = []
        for candidate in candidate_items:
            similarity = self.calculate_combined_similarity(item, candidate)
            if similarity > threshold:
                matches.append({
                    'item': candidate,
                    'similarity': similarity,
                    'type': candidate.status.lower()
                })
        return sorted(matches, key=lambda x: x['similarity'], reverse=True)
