from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    spotify_access_token = db.Column(db.String(256), nullable=True)
    spotify_refresh_token = db.Column(db.String(256), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    preferences = db.relationship('UserPreference', backref='user', lazy=True)
    recommendations = db.relationship('Recommendation', backref='user', lazy=True)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Song(db.Model):
    __tablename__ = 'songs'
    
    id = db.Column(db.Integer, primary_key=True)
    spotify_id = db.Column(db.String(64), unique=True, nullable=False)
    title = db.Column(db.String(256), nullable=False)
    artist = db.Column(db.String(256), nullable=False)
    album = db.Column(db.String(256), nullable=True)
    genre = db.Column(db.String(128), nullable=True)
    features = db.Column(db.Text, nullable=True)  # JSON string of audio features
    popularity = db.Column(db.Integer, nullable=True)
    preview_url = db.Column(db.String(512), nullable=True)
    
    preferences = db.relationship('UserPreference', backref='song', lazy=True)
    recommendations = db.relationship('Recommendation', backref='song', lazy=True)
    
    def __repr__(self):
        return f'<Song {self.title} by {self.artist}>'
    
    def get_features(self):
        if self.features:
            return json.loads(self.features)
        return {}
    
    def set_features(self, features_dict):
        self.features = json.dumps(features_dict)

class UserPreference(db.Model):
    __tablename__ = 'user_preferences'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    song_id = db.Column(db.Integer, db.ForeignKey('songs.id'), nullable=False)
    rating = db.Column(db.Boolean, nullable=False)  # True for like, False for dislike
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        rating_str = "like" if self.rating else "dislike"
        return f'<UserPreference {self.user_id} {rating_str} {self.song_id}>'

class Recommendation(db.Model):
    __tablename__ = 'recommendations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    song_id = db.Column(db.Integer, db.ForeignKey('songs.id'), nullable=False)
    recommendation_score = db.Column(db.Float, nullable=False)
    is_shown = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Recommendation {self.user_id} {self.song_id} score:{self.recommendation_score}>'
