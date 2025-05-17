import unittest
from flask import Flask, session
from src.models.user import db, User, Song, UserPreference, Recommendation
from src.models.recommendation import recommendation_engine
import os
import sys
import json

# Set up test app
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from src.main import app as flask_app

class SpotifyRecommenderTests(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment before each test"""
        flask_app.config['TESTING'] = True
        flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        flask_app.config['WTF_CSRF_ENABLED'] = False
        
        self.app = flask_app.test_client()
        self.app_context = flask_app.app_context()
        self.app_context.push()
        
        db.create_all()
        
        # Create test user
        test_user = User(
            username='testuser',
            email='test@example.com',
            password_hash='pbkdf2:sha256:150000$abc123$abcdef123456789'
        )
        db.session.add(test_user)
        
        # Create test songs
        for i in range(1, 11):
            song = Song(
                spotify_id=f'spotify_id_{i}',
                title=f'Test Song {i}',
                artist=f'Test Artist {i}',
                album=f'Test Album {i}',
                popularity=90-i,
                preview_url=f'https://example.com/preview_{i}.mp3'
            )
            db.session.add(song)
        
        db.session.commit()
    
    def tearDown(self):
        """Clean up after each test"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_user_registration(self):
        """Test user registration functionality"""
        response = self.app.post('/api/auth/register', 
            json={
                'username': 'newuser',
                'email': 'new@example.com',
                'password': 'password123'
            }
        )
        self.assertEqual(response.status_code, 201)
        self.assertIn(b'User registered successfully', response.data)
        
        # Check user was added to database
        user = User.query.filter_by(username='newuser').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'new@example.com')
    
    def test_user_login(self):
        """Test user login functionality"""
        # This is a mock test since we can't easily test password hashing in this setup
        with flask_app.test_request_context():
            # Simulate login by setting session
            session['user_id'] = 1
            session.modified = True
            
            # Test profile access
            response = self.app.get('/api/user/profile')
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertEqual(data['username'], 'testuser')
    
    def test_recommendation_generation(self):
        """Test recommendation generation"""
        # Create test preferences
        user = User.query.filter_by(username='testuser').first()
        songs = Song.query.all()
        
        # Add some likes
        for i in range(3):
            pref = UserPreference(
                user_id=user.id,
                song_id=songs[i].id,
                rating=True  # Like
            )
            db.session.add(pref)
        
        # Add some dislikes
        for i in range(3, 6):
            pref = UserPreference(
                user_id=user.id,
                song_id=songs[i].id,
                rating=False  # Dislike
            )
            db.session.add(pref)
        
        db.session.commit()
        
        # Test recommendation generation
        with flask_app.test_request_context():
            session['user_id'] = user.id
            session.modified = True
            
            # Generate recommendations
            recommendation_engine.generate_recommendations(user.id)
            
            # Check recommendations were created
            recommendations = Recommendation.query.filter_by(user_id=user.id).all()
            self.assertTrue(len(recommendations) > 0)
    
    def test_feedback_processing(self):
        """Test feedback processing"""
        user = User.query.filter_by(username='testuser').first()
        song = Song.query.first()
        
        with flask_app.test_request_context():
            session['user_id'] = user.id
            session.modified = True
            
            # Submit feedback
            response = self.app.post('/api/feedback', 
                json={
                    'song_id': song.spotify_id,
                    'rating': 'like'
                }
            )
            self.assertEqual(response.status_code, 200)
            
            # Check preference was stored
            preference = UserPreference.query.filter_by(
                user_id=user.id,
                song_id=song.id
            ).first()
            self.assertIsNotNone(preference)
            self.assertTrue(preference.rating)  # Should be True for 'like'

if __name__ == '__main__':
    unittest.main()
