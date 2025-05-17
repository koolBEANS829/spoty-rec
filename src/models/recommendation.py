import requests
import numpy as np
from sklearn.neighbors import NearestNeighbors
from src.models.user import db, User, Song, UserPreference, Recommendation
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SpotifyClient:
    """Client for interacting with Spotify API"""
    
    BASE_URL = "https://api.spotify.com/v1"
    
    @staticmethod
    def get_headers(access_token):
        """Get headers for Spotify API requests"""
        return {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
    
    @staticmethod
    def get_audio_features(access_token, track_id):
        """Get audio features for a track"""
        url = f"{SpotifyClient.BASE_URL}/audio-features/{track_id}"
        headers = SpotifyClient.get_headers(access_token)
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting audio features: {e}")
            return None
    
    @staticmethod
    def get_recommendations(access_token, seed_tracks=None, seed_genres=None, seed_artists=None, limit=10):
        """Get recommendations from Spotify"""
        url = f"{SpotifyClient.BASE_URL}/recommendations"
        headers = SpotifyClient.get_headers(access_token)
        
        params = {'limit': limit}
        
        if seed_tracks:
            params['seed_tracks'] = ','.join(seed_tracks[:5])  # Max 5 seed tracks
        elif seed_genres:
            params['seed_genres'] = ','.join(seed_genres[:5])  # Max 5 seed genres
        elif seed_artists:
            params['seed_artists'] = ','.join(seed_artists[:5])  # Max 5 seed artists
        else:
            # Default to some popular genres if no seeds provided
            params['seed_genres'] = 'pop,rock,hip-hop,electronic,r-n-b'
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting recommendations: {e}")
            return None
    
    @staticmethod
    def search_tracks(access_token, query, limit=10):
        """Search for tracks on Spotify"""
        url = f"{SpotifyClient.BASE_URL}/search"
        headers = SpotifyClient.get_headers(access_token)
        params = {
            'q': query,
            'type': 'track',
            'limit': limit
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error searching tracks: {e}")
            return None
    
    @staticmethod
    def get_track(access_token, track_id):
        """Get track details"""
        url = f"{SpotifyClient.BASE_URL}/tracks/{track_id}"
        headers = SpotifyClient.get_headers(access_token)
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting track: {e}")
            return None

class RecommendationEngine:
    """AI-based recommendation engine that learns from user feedback"""
    
    def __init__(self):
        self.model = NearestNeighbors(n_neighbors=10, algorithm='ball_tree')
        self.song_features = []
        self.song_ids = []
        self.is_trained = False
    
    def extract_features(self, song):
        """Extract relevant features from a song"""
        features = song.get_features()
        if not features:
            return None
        
        # Extract relevant audio features
        relevant_features = [
            features.get('danceability', 0),
            features.get('energy', 0),
            features.get('key', 0) / 11.0,  # Normalize key
            features.get('loudness', 0) / -60.0,  # Normalize loudness
            features.get('mode', 0),
            features.get('speechiness', 0),
            features.get('acousticness', 0),
            features.get('instrumentalness', 0),
            features.get('liveness', 0),
            features.get('valence', 0),
            features.get('tempo', 0) / 250.0,  # Normalize tempo
        ]
        
        return relevant_features
    
    def train(self, user_id=None):
        """Train the recommendation model"""
        # Get all songs with features
        songs = Song.query.all()
        
        self.song_features = []
        self.song_ids = []
        
        for song in songs:
            features = self.extract_features(song)
            if features:
                self.song_features.append(features)
                self.song_ids.append(song.id)
        
        if not self.song_features:
            logger.warning("No song features available for training")
            return False
        
        # Train the model
        self.model.fit(self.song_features)
        self.is_trained = True
        logger.info(f"Model trained with {len(self.song_features)} songs")
        
        # If user_id is provided, generate recommendations for that user
        if user_id:
            self.generate_recommendations(user_id)
        
        return True
    
    def get_user_profile(self, user_id):
        """Create a user profile based on liked songs"""
        # Get user's liked songs
        preferences = UserPreference.query.filter_by(user_id=user_id, rating=True).all()
        
        if not preferences:
            logger.info(f"User {user_id} has no liked songs")
            return None
        
        # Extract features from liked songs
        liked_features = []
        for pref in preferences:
            song = Song.query.get(pref.song_id)
            if song:
                features = self.extract_features(song)
                if features:
                    liked_features.append(features)
        
        if not liked_features:
            logger.info(f"No features available for user {user_id}'s liked songs")
            return None
        
        # Create user profile by averaging features
        user_profile = np.mean(liked_features, axis=0)
        logger.info(f"Created user profile for user {user_id} based on {len(liked_features)} songs")
        return user_profile
    
    def generate_recommendations(self, user_id, n_recommendations=10):
        """Generate recommendations for a user"""
        if not self.is_trained:
            success = self.train()
            if not success:
                logger.warning("Failed to train model for recommendations")
                return False
        
        # Get user profile
        user_profile = self.get_user_profile(user_id)
        
        # If user has no profile, use popularity-based recommendations
        if user_profile is None:
            logger.info(f"Using popularity-based recommendations for user {user_id}")
            return self.popularity_recommendations(user_id, n_recommendations)
        
        # Find nearest neighbors to user profile
        distances, indices = self.model.kneighbors([user_profile], n_neighbors=n_recommendations*2)
        
        # Get recommended song IDs
        recommended_song_ids = [self.song_ids[idx] for idx in indices[0]]
        
        # Filter out songs the user has already rated
        user_rated_songs = UserPreference.query.filter_by(user_id=user_id).with_entities(UserPreference.song_id).all()
        user_rated_song_ids = [song.song_id for song in user_rated_songs]
        
        recommended_song_ids = [song_id for song_id in recommended_song_ids if song_id not in user_rated_song_ids]
        
        # Limit to requested number
        recommended_song_ids = recommended_song_ids[:n_recommendations]
        
        # Store recommendations in database
        self.store_recommendations(user_id, recommended_song_ids, distances[0])
        
        logger.info(f"Generated {len(recommended_song_ids)} recommendations for user {user_id}")
        return True
    
    def popularity_recommendations(self, user_id, n_recommendations=10):
        """Generate recommendations based on popularity for new users"""
        # Get popular songs
        popular_songs = Song.query.order_by(Song.popularity.desc()).limit(n_recommendations*2).all()
        
        # Filter out songs the user has already rated
        user_rated_songs = UserPreference.query.filter_by(user_id=user_id).with_entities(UserPreference.song_id).all()
        user_rated_song_ids = [song.song_id for song in user_rated_songs]
        
        recommended_song_ids = []
        for song in popular_songs:
            if song.id not in user_rated_song_ids:
                recommended_song_ids.append(song.id)
                if len(recommended_song_ids) >= n_recommendations:
                    break
        
        # Store recommendations in database
        self.store_recommendations(user_id, recommended_song_ids)
        
        logger.info(f"Generated {len(recommended_song_ids)} popularity-based recommendations for user {user_id}")
        return True
    
    def store_recommendations(self, user_id, song_ids, distances=None):
        """Store recommendations in the database"""
        # Clear existing unshown recommendations
        Recommendation.query.filter_by(user_id=user_id, is_shown=False).delete()
        
        # Add new recommendations
        for i, song_id in enumerate(song_ids):
            # Calculate score (inverse of distance, or 1.0 for popularity-based)
            score = 1.0 / (1.0 + distances[i]) if distances is not None else 1.0 - (i * 0.05)
            
            recommendation = Recommendation(
                user_id=user_id,
                song_id=song_id,
                recommendation_score=float(score),
                is_shown=False
            )
            db.session.add(recommendation)
        
        db.session.commit()
        logger.info(f"Stored {len(song_ids)} recommendations for user {user_id}")
    
    def process_feedback(self, user_id, song_id, rating):
        """Process user feedback and update recommendations"""
        # Check if we have enough feedback to generate new recommendations
        feedback_count = UserPreference.query.filter_by(user_id=user_id).count()
        
        # Store the feedback
        existing_pref = UserPreference.query.filter_by(
            user_id=user_id,
            song_id=song_id
        ).first()
        
        if existing_pref:
            # Update existing preference
            existing_pref.rating = rating
            db.session.commit()
            logger.info(f"Updated feedback for user {user_id}, song {song_id}, rating {rating}")
        else:
            # Create new preference
            new_pref = UserPreference(
                user_id=user_id,
                song_id=song_id,
                rating=rating
            )
            db.session.add(new_pref)
            db.session.commit()
            logger.info(f"Added new feedback for user {user_id}, song {song_id}, rating {rating}")
        
        # Generate new recommendations if we have enough feedback
        if feedback_count >= 5:  # Arbitrary threshold
            self.generate_recommendations(user_id)
        
        return True
    
    def fetch_and_store_spotify_recommendations(self, user_id, access_token):
        """Fetch recommendations from Spotify API and store them"""
        # Get user's top liked songs as seed tracks
        top_preferences = UserPreference.query.filter_by(
            user_id=user_id, 
            rating=True
        ).order_by(UserPreference.timestamp.desc()).limit(5).all()
        
        seed_tracks = []
        for pref in top_preferences:
            song = Song.query.get(pref.song_id)
            if song:
                seed_tracks.append(song.spotify_id)
        
        # If user has no liked songs, use popularity-based recommendations
        if not seed_tracks:
            return self.popularity_recommendations(user_id)
        
        # Get recommendations from Spotify
        spotify_recommendations = SpotifyClient.get_recommendations(
            access_token=access_token,
            seed_tracks=seed_tracks,
            limit=20
        )
        
        if not spotify_recommendations or 'tracks' not in spotify_recommendations:
            logger.error("Failed to get recommendations from Spotify")
            return False
        
        # Process and store recommendations
        for track in spotify_recommendations['tracks']:
            # Check if song exists in our database
            song = Song.query.filter_by(spotify_id=track['id']).first()
            
            # If not, create it
            if not song:
                song = Song(
                    spotify_id=track['id'],
                    title=track['name'],
                    artist=track['artists'][0]['name'],
                    album=track['album']['name'],
                    popularity=track['popularity'],
                    preview_url=track['preview_url']
                )
                db.session.add(song)
                db.session.commit()
                
                # Get audio features for the song
                features = SpotifyClient.get_audio_features(access_token, track['id'])
                if features:
                    song.set_features(features)
                    db.session.commit()
            
            # Create recommendation
            existing_rec = Recommendation.query.filter_by(
                user_id=user_id,
                song_id=song.id,
                is_shown=False
            ).first()
            
            if not existing_rec:
                recommendation = Recommendation(
                    user_id=user_id,
                    song_id=song.id,
                    recommendation_score=0.9,  # High score for Spotify recommendations
                    is_shown=False
                )
                db.session.add(recommendation)
        
        db.session.commit()
        logger.info(f"Stored Spotify recommendations for user {user_id}")
        return True

# Create a singleton instance
recommendation_engine = RecommendationEngine()
