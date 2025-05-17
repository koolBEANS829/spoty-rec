from flask import Blueprint, request, jsonify, redirect, session, current_app, url_for
import requests
import base64
import json
import os
from src.models.user import db, User, Song
from datetime import datetime, timedelta

spotify_bp = Blueprint('spotify', __name__)

# Spotify API credentials
# These would typically be stored in environment variables
SPOTIFY_CLIENT_ID = "d7753592ca324b718d50aa4dbeacdb87"
SPOTIFY_CLIENT_SECRET = "03ae86e4fd494378a9fa01d83ed1d3e9"
REDIRECT_URI = "http://localhost:5000/api/auth/spotify/callback"

@spotify_bp.route('/auth/spotify', methods=['GET'])
def spotify_auth():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    # Spotify authorization URL
    scope = "user-read-private user-read-email user-top-read user-read-recently-played streaming"
    auth_url = f"https://accounts.spotify.com/authorize?client_id={SPOTIFY_CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URI}&scope={scope}&show_dialog=true"
    
    return jsonify({'auth_url': auth_url}), 200

@spotify_bp.route('/auth/spotify/callback', methods=['GET'])
def spotify_callback():
    if 'user_id' not in session:
        return "Not logged in", 401
    
    code = request.args.get('code')
    if not code:
        return "Authorization failed", 400
    
    # Exchange code for tokens
    auth_header = base64.b64encode(f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}".encode()).decode()
    headers = {
        'Authorization': f'Basic {auth_header}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI
    }
    
    response = requests.post('https://accounts.spotify.com/api/token', headers=headers, data=data)
    
    if response.status_code != 200:
        return "Token exchange failed", 400
    
    tokens = response.json()
    
    # Save tokens to user
    user = User.query.get(session['user_id'])
    user.spotify_access_token = tokens['access_token']
    user.spotify_refresh_token = tokens['refresh_token']
    db.session.commit()
    
    return redirect('/')

@spotify_bp.route('/spotify/refresh_token', methods=['GET'])
def refresh_token():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    user = User.query.get(session['user_id'])
    if not user or not user.spotify_refresh_token:
        return jsonify({'error': 'No refresh token available'}), 400
    
    # Exchange refresh token for new access token
    auth_header = base64.b64encode(f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}".encode()).decode()
    headers = {
        'Authorization': f'Basic {auth_header}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': user.spotify_refresh_token
    }
    
    response = requests.post('https://accounts.spotify.com/api/token', headers=headers, data=data)
    
    if response.status_code != 200:
        return jsonify({'error': 'Token refresh failed'}), 400
    
    tokens = response.json()
    
    # Update access token
    user.spotify_access_token = tokens['access_token']
    if 'refresh_token' in tokens:
        user.spotify_refresh_token = tokens['refresh_token']
    db.session.commit()
    
    return jsonify({'message': 'Token refreshed successfully'}), 200

@spotify_bp.route('/spotify/search', methods=['GET'])
def search_songs():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    query = request.args.get('q')
    if not query:
        return jsonify({'error': 'No search query provided'}), 400
    
    user = User.query.get(session['user_id'])
    if not user or not user.spotify_access_token:
        return jsonify({'error': 'No Spotify access token available'}), 400
    
    # Search Spotify
    headers = {
        'Authorization': f'Bearer {user.spotify_access_token}'
    }
    params = {
        'q': query,
        'type': 'track',
        'limit': 10
    }
    
    response = requests.get('https://api.spotify.com/v1/search', headers=headers, params=params)
    
    # Handle token expiration
    if response.status_code == 401:
        # Try to refresh token
        refresh_response = requests.get(url_for('spotify.refresh_token', _external=True))
        if refresh_response.status_code != 200:
            return jsonify({'error': 'Spotify authentication expired'}), 401
        
        # Retry with new token
        user = User.query.get(session['user_id'])
        headers = {
            'Authorization': f'Bearer {user.spotify_access_token}'
        }
        response = requests.get('https://api.spotify.com/v1/search', headers=headers, params=params)
    
    if response.status_code != 200:
        return jsonify({'error': 'Spotify API error'}), response.status_code
    
    data = response.json()
    
    # Process and return results
    results = []
    for item in data['tracks']['items']:
        # Check if song exists in our database
        song = Song.query.filter_by(spotify_id=item['id']).first()
        
        # If not, create it
        if not song:
            song = Song(
                spotify_id=item['id'],
                title=item['name'],
                artist=item['artists'][0]['name'],
                album=item['album']['name'],
                popularity=item['popularity'],
                preview_url=item['preview_url']
            )
            db.session.add(song)
            db.session.commit()
        
        results.append({
            'id': song.id,
            'spotify_id': song.spotify_id,
            'title': song.title,
            'artist': song.artist,
            'album': song.album,
            'popularity': song.popularity,
            'preview_url': song.preview_url,
            'image_url': item['album']['images'][0]['url'] if item['album']['images'] else None
        })
    
    return jsonify(results), 200

@spotify_bp.route('/spotify/features/<spotify_id>', methods=['GET'])
def get_audio_features(spotify_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    user = User.query.get(session['user_id'])
    if not user or not user.spotify_access_token:
        return jsonify({'error': 'No Spotify access token available'}), 400
    
    # Get audio features from Spotify
    headers = {
        'Authorization': f'Bearer {user.spotify_access_token}'
    }
    
    response = requests.get(f'https://api.spotify.com/v1/audio-features/{spotify_id}', headers=headers)
    
    # Handle token expiration
    if response.status_code == 401:
        # Try to refresh token
        refresh_response = requests.get(url_for('spotify.refresh_token', _external=True))
        if refresh_response.status_code != 200:
            return jsonify({'error': 'Spotify authentication expired'}), 401
        
        # Retry with new token
        user = User.query.get(session['user_id'])
        headers = {
            'Authorization': f'Bearer {user.spotify_access_token}'
        }
        response = requests.get(f'https://api.spotify.com/v1/audio-features/{spotify_id}', headers=headers)
    
    if response.status_code != 200:
        return jsonify({'error': 'Spotify API error'}), response.status_code
    
    features = response.json()
    
    # Update song in database with features
    song = Song.query.filter_by(spotify_id=spotify_id).first()
    if song:
        song.set_features(features)
        db.session.commit()
    
    return jsonify(features), 200
