from django.db.models import Q
from items.models import Item
from matcher.utils.image_matcher import extract_features, compute_similarity, find_matches
from matcher.utils.location_utils import haversine
import numpy as np
import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing import image
from matcher.models import FeatureVector
from verification.models import VerificationQuestion
import pickle

# Initialize the model with explicit input shape
model = MobileNetV2(
    weights='imagenet',
    include_top=False,
    pooling='avg',
    input_shape=(224, 224, 3)
)

def extract_features(img_path):
    """Extract features from an image using MobileNetV2."""
    img = image.load_img(img_path, target_size=(224, 224))
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    features = model.predict(x)
    return features.flatten()

def compute_similarity(vector1, vector2):
    """Compute cosine similarity between two feature vectors."""
    return np.dot(vector1, vector2) / (np.linalg.norm(vector1) * np.linalg.norm(vector2))

def find_matches_for_item(item):
    """Find potential matches for a given item."""
    # Extract features for the new item
    features = extract_features(item.image.path)
    
    # Store the feature vector
    feature_vector = FeatureVector.objects.create(
        item=item,
        vector=pickle.dumps(features)
    )
    
    # Find potential matches
    matches = []
    opposite_type = 'FOUND' if item.item_type == 'LOST' else 'LOST'
    potential_matches = Item.objects.filter(
        item_type=opposite_type,
        status='ACTIVE'
    ).exclude(id=item.id)
    
    for potential_match in potential_matches:
        try:
            match_features = pickle.loads(potential_match.feature_vector.vector)
            similarity = compute_similarity(features, match_features)
            
            if similarity > 0.8:  # Threshold for considering a match
                match = Match.objects.create(
                    lost_item=item if item.item_type == 'LOST' else potential_match,
                    found_item=potential_match if item.item_type == 'LOST' else item,
                    similarity_score=float(similarity)
                )
                
                # Generate verification questions
                questions = [
                    "What color is the item?",
                    "What brand is the item?",
                    "When did you lose/find the item?",
                    "Are there any unique identifying marks or features?",
                ]
                
                for question in questions:
                    VerificationQuestion.objects.create(
                        match=match,
                        question=question,
                        expected_answer=""  # To be filled by the item owner
                    )
                
                matches.append(match)
        except Exception as e:
            print(f"Error processing match for item {potential_match.id}: {str(e)}")
    
    return matches

def verify_match(match, is_match, answers):
    """Verify a match based on user responses."""
    if is_match:
        # Check if answers match
        correct_answers = 0
        total_questions = match.verification_questions.count()
        
        for question in match.verification_questions.all():
            if str(question.id) in answers:
                user_answer = answers[str(question.id)]
                if question.expected_answer and user_answer.lower() == question.expected_answer.lower():
                    correct_answers += 1
        
        # If more than 70% answers are correct, consider it a verified match
        if total_questions > 0 and (correct_answers / total_questions) >= 0.7:
            match.status = 'VERIFIED'
            match.save()
            return True
    else:
        match.status = 'REJECTED'
        match.save()
        return True
    
    return False

def find_matches_for_item_old(item):
    # Find opposite-type items
    target_type = 'FOUND' if item.item_type == 'LOST' else 'LOST'
    candidates = Item.objects.filter(item_type=target_type)

    matches = []

    source_embedding = get_embedding(item.photo.path)

    for candidate in candidates:
        distance = haversine(
            item.latitude, item.longitude,
            candidate.latitude, candidate.longitude
        )
        if distance > 5:
            continue  # Skip far items

        try:
            target_embedding = get_embedding(candidate.photo.path)
            similarity = cosine_similarity(source_embedding, target_embedding)
            if similarity > 0.85:  # You can adjust this threshold
                matches.append({
                    'item': candidate,
                    'similarity': similarity,
                    'distance': distance
                })
        except:
            continue

    # Sort matches by similarity descending
    return sorted(matches, key=lambda x: x['similarity'], reverse=True) 