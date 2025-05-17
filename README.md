# Spotify Song Recommendation System

A web application that provides personalized song recommendations using the Spotify API and AI-based feedback learning.

## Features

- User authentication (registration and login)
- Spotify API integration for song playback and data
- AI-powered recommendation engine that learns from user feedback
- "I like" and "I don't like" buttons for providing feedback
- Persistent storage of user preferences between sessions
- Responsive design for both desktop and mobile

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLite (configurable for MySQL)
- **Frontend**: HTML, CSS, JavaScript
- **AI**: Scikit-learn for recommendation algorithms
- **API**: Spotify Web API

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/spotify-recommender.git
   cd spotify-recommender
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Configure Spotify API credentials:
   - Create a Spotify Developer account at [developer.spotify.com](https://developer.spotify.com)
   - Create a new application to get your Client ID and Client Secret
   - Update the credentials in `src/routes/spotify.py`

4. Run the application:
   ```
   python src/main.py
   ```

5. Access the application at http://localhost:5000

## Usage

1. Register a new account
2. Log in with your credentials
3. Connect your Spotify account when prompted
4. Browse and listen to recommended songs
5. Provide feedback using the "I like" and "I don't like" buttons
6. Watch as recommendations improve based on your feedback

## Project Structure

- `src/` - Main application code
  - `models/` - Database models and AI recommendation engine
  - `routes/` - API endpoints and route handlers
  - `static/` - Frontend assets (HTML, CSS, JS)
- `tests.py` - Unit tests
- `requirements.txt` - Python dependencies

## Configuration

The application can be configured to use either SQLite (default) or MySQL:

- SQLite (default): No additional configuration needed
- MySQL: Update the database URI in `src/main.py`

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Spotify Web API for providing music data
- Flask for the web framework
- Scikit-learn for machine learning capabilities
