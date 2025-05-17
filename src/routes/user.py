from flask import Blueprint, request, jsonify, session, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from src.models.user import db, User, Song, UserPreference, Recommendation
from datetime import datetime
import json

user_bp = Blueprint('user', __name__)

@user_bp.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Validate input
    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Check if user already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    # Create new user
    hashed_password = generate_password_hash(data['password'])
    new_user = User(
        username=data['username'],
        email=data['email'],
        password_hash=hashed_password,
        created_at=datetime.utcnow()
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'message': 'User registered successfully', 'user_id': new_user.id}), 201

@user_bp.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    
    # Validate input
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Missing username or password'}), 400
    
    # Find user
    user = User.query.filter_by(username=data['username']).first()
    
    # Check password
    if not user or not check_password_hash(user.password_hash, data['password']):
        return jsonify({'error': 'Invalid username or password'}), 401
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    # Set session
    session['user_id'] = user.id
    
    return jsonify({
        'message': 'Login successful',
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email
        }
    }), 200

@user_bp.route('/auth/logout', methods=['GET'])
def logout():
    session.pop('user_id', None)
    return jsonify({'message': 'Logout successful'}), 200

@user_bp.route('/user/profile', methods=['GET'])
def get_profile():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'created_at': user.created_at,
        'last_login': user.last_login,
        'has_spotify': bool(user.spotify_access_token)
    }), 200

@user_bp.route('/user/preferences', methods=['GET'])
def get_preferences():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    preferences = UserPreference.query.filter_by(user_id=session['user_id']).all()
    result = []
    
    for pref in preferences:
        song = Song.query.get(pref.song_id)
        if song:
            result.append({
                'id': pref.id,
                'song': {
                    'id': song.id,
                    'spotify_id': song.spotify_id,
                    'title': song.title,
                    'artist': song.artist,
                    'album': song.album
                },
                'rating': 'like' if pref.rating else 'dislike',
                'timestamp': pref.timestamp
            })
    
    return jsonify(result), 200

@user_bp.route('/feedback', methods=['POST'])
def submit_feedback():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    data = request.get_json()
    
    # Validate input
    if not data or 'song_id' not in data or 'rating' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    
    song = Song.query.filter_by(spotify_id=data['song_id']).first()
    
    # If song doesn't exist in our database yet, we need more info
    if not song and not (data.get('title') and data.get('artist')):
        return jsonify({'error': 'Song not found, need title and artist'}), 400
    
    # Create song if it doesn't exist
    if not song:
        song = Song(
            spotify_id=data['song_id'],
            title=data['title'],
            artist=data['artist'],
            album=data.get('album'),
            genre=data.get('genre'),
            popularity=data.get('popularity'),
            preview_url=data.get('preview_url')
        )
        
        if data.get('features'):
            song.set_features(data['features'])
            
        db.session.add(song)
        db.session.commit()
    
    # Check if preference already exists
    existing_pref = UserPreference.query.filter_by(
        user_id=session['user_id'],
        song_id=song.id
    ).first()
    
    if existing_pref:
        # Update existing preference
        existing_pref.rating = data['rating'] == 'like'
        existing_pref.timestamp = datetime.utcnow()
    else:
        # Create new preference
        new_pref = UserPreference(
            user_id=session['user_id'],
            song_id=song.id,
            rating=data['rating'] == 'like'
        )
        db.session.add(new_pref)
    
    db.session.commit()
    
    # Update recommendation model (this would trigger the AI to learn)
    # This is a placeholder - actual implementation would be in the AI module
    
    return jsonify({'message': 'Feedback submitted successfully'}), 200

@user_bp.route('/recommendations', methods=['GET'])
def get_recommendations():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    # This is a placeholder - actual implementation would query the AI model
    # For now, return some mock recommendations
    
    # Mark recommendations as shown
    recommendations = Recommendation.query.filter_by(
        user_id=session['user_id'],
        is_shown=False
    ).order_by(Recommendation.recommendation_score.desc()).limit(10).all()
    
    result = []
    for rec in recommendations:
        song = Song.query.get(rec.song_id)
        if song:
            result.append({
                'id': rec.id,
                'song': {
                    'id': song.id,
                    'spotify_id': song.spotify_id,
                    'title': song.title,
                    'artist': song.artist,
                    'album': song.album,
                    'preview_url': song.preview_url
                },
                'score': rec.recommendation_score
            })
            rec.is_shown = True
    
    db.session.commit()
    
    return jsonify(result), 200
