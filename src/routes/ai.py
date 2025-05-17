from flask import Blueprint, request, jsonify, session, redirect, url_for
from src.models.user import db, User, Song, UserPreference, Recommendation
from src.models.recommendation import recommendation_engine, SpotifyClient
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ai_bp = Blueprint('ai', __name__)

@ai_bp.route('/recommendations/generate', methods=['POST'])
def generate_recommendations():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    user_id = session['user_id']
    
    # Generate recommendations
    success = recommendation_engine.generate_recommendations(user_id)
    
    if not success:
        return jsonify({'error': 'Failed to generate recommendations'}), 500
    
    return jsonify({'message': 'Recommendations generated successfully'}), 200

@ai_bp.route('/recommendations/spotify', methods=['POST'])
def spotify_recommendations():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    user_id = session['user_id']
    user = User.query.get(user_id)
    
    if not user or not user.spotify_access_token:
        return jsonify({'error': 'No Spotify access token available'}), 400
    
    # Fetch and store recommendations from Spotify
    success = recommendation_engine.fetch_and_store_spotify_recommendations(
        user_id=user_id,
        access_token=user.spotify_access_token
    )
    
    if not success:
        return jsonify({'error': 'Failed to get Spotify recommendations'}), 500
    
    return jsonify({'message': 'Spotify recommendations generated successfully'}), 200

@ai_bp.route('/recommendations/train', methods=['POST'])
def train_model():
    # This endpoint would typically be admin-only or triggered by a scheduled task
    success = recommendation_engine.train()
    
    if not success:
        return jsonify({'error': 'Failed to train model'}), 500
    
    return jsonify({'message': 'Model trained successfully'}), 200

@ai_bp.route('/feedback/process', methods=['POST'])
def process_feedback():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    user_id = session['user_id']
    data = request.get_json()
    
    if not data or 'song_id' not in data or 'rating' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Get song
    song = Song.query.filter_by(spotify_id=data['song_id']).first()
    
    if not song:
        return jsonify({'error': 'Song not found'}), 404
    
    # Process feedback
    rating_bool = data['rating'] == 'like'
    success = recommendation_engine.process_feedback(user_id, song.id, rating_bool)
    
    if not success:
        return jsonify({'error': 'Failed to process feedback'}), 500
    
    # Generate new recommendations if needed
    recommendation_engine.generate_recommendations(user_id)
    
    return jsonify({'message': 'Feedback processed successfully'}), 200
