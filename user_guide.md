# Spotify Song Recommendation System - User Guide

## Overview
This application is a web-based song recommendation system that uses the Spotify API to retrieve and play songs, and an AI-based recommendation engine that learns from your feedback over time. You can provide feedback through "I like" and "I don't like" buttons, which helps the system improve its recommendations.

## Features
- User registration and login
- Spotify API integration for song playback
- AI-powered song recommendations that learn from your feedback
- "I like" and "I don't like" buttons for providing feedback
- Persistent storage of preferences between sessions
- Responsive design that works on both desktop and mobile devices

## Getting Started

### Prerequisites
- Python 3.8 or higher
- MySQL database
- Spotify Developer account (for API credentials)

### Installation
1. Clone the repository or extract the provided files
2. Navigate to the project directory
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Configure Spotify API credentials:
   - Open `src/routes/spotify.py`
   - Replace `YOUR_SPOTIFY_CLIENT_ID` and `YOUR_SPOTIFY_CLIENT_SECRET` with your actual Spotify API credentials
   - Update `REDIRECT_URI` if needed

5. Configure the database:
   - The application is set up to use MySQL by default
   - Database connection settings can be modified in `src/main.py`

6. Run the application:
   ```
   python src/main.py
   ```
7. Access the application at `http://localhost:5000`

## Using the Application

### Registration and Login
1. When you first access the application, you'll be directed to the login page
2. If you don't have an account, click "Register Instead"
3. Fill in the registration form and submit
4. Log in with your new credentials

### Connecting Spotify
1. After logging in, you'll see a prompt to connect your Spotify account
2. Click "Connect Spotify" and follow the authorization process
3. Once connected, you'll be able to play songs and get personalized recommendations

### Getting Recommendations
1. The application will initially show recommendations based on popular songs
2. As you provide feedback, recommendations will become more personalized
3. You can refresh recommendations by clicking the "Refresh" button

### Providing Feedback
1. For each recommended song, you can:
   - Click the "I like" (thumbs up) button if you enjoy the song
   - Click the "I don't like" (thumbs down) button if you don't enjoy the song
2. The AI will learn from your feedback and improve future recommendations
3. After providing feedback on several songs, the system will automatically update recommendations

### Playing Songs
1. Click the "Play" button on any song to start playback
2. Use the player controls to:
   - Play/pause the current song
   - Skip to the next or previous song
   - See playback progress

### Viewing History
1. Click "History" in the navigation bar to see your feedback history
2. This page shows all songs you've rated, organized by date

### Profile
1. Click "Profile" in the navigation bar to view your account information
2. Here you can see:
   - Account details
   - Spotify connection status
   - Statistics about your activity

## How It Works

### AI Recommendation System
The recommendation system works in three phases:

1. **Initial Recommendations**: For new users, recommendations are based on song popularity
2. **Learning Phase**: As you provide feedback, the system learns your preferences by analyzing:
   - Audio features of songs you like/dislike (tempo, energy, danceability, etc.)
   - Patterns in your feedback
3. **Personalized Recommendations**: After sufficient feedback, recommendations become tailored to your taste

### Feedback Loop
1. You provide feedback on recommended songs
2. The AI analyzes the audio features of liked/disliked songs
3. The recommendation model is updated based on your preferences
4. New recommendations are generated using the updated model
5. The process repeats, continuously improving recommendations

## Troubleshooting

### Common Issues
- **Spotify Connection Issues**: If you encounter problems connecting to Spotify, try logging out and logging back in
- **Playback Issues**: Some songs may not have preview URLs available from Spotify
- **Recommendation Quality**: The system needs at least 5-10 feedback submissions to start providing personalized recommendations

### Support
If you encounter any issues or have questions, please contact support at support@example.com

## Privacy and Data Usage
- Your Spotify account information is only used to access the Spotify API
- Your listening preferences are stored securely and only used to improve recommendations
- No personal data is shared with third parties

## Technical Details
- Backend: Flask (Python)
- Database: MySQL
- Frontend: HTML, CSS, JavaScript
- AI: Scikit-learn (Nearest Neighbors algorithm)
- API: Spotify Web API

## License
This application is provided for personal use only and is not for redistribution.

---

Thank you for using the Spotify Song Recommendation System! We hope you enjoy discovering new music tailored to your taste.
