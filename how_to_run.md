# How to Run the Spotify Song Recommendation System

This step-by-step guide will walk you through setting up and running the Spotify Song Recommendation System on your local machine.

## Prerequisites

Before you begin, make sure you have the following installed:

1. **Python 3.8 or higher**
   - You can check your Python version by running `python --version` in your terminal
   - If needed, download Python from [python.org](https://www.python.org/downloads/)

2. **MySQL Database**
   - The application uses MySQL to store user data and preferences
   - You can use a local MySQL installation or a cloud-based service

3. **Git** (optional, for cloning the repository)
   - Download from [git-scm.com](https://git-scm.com/downloads)

## Step 1: Extract the Application Files

1. Locate the `spotify_recommender_updated.zip` file that was provided
2. Extract the contents to a directory of your choice
3. Open a terminal/command prompt and navigate to the extracted directory

```bash
# Example command to navigate to the directory
cd path/to/spotify_recommender
```

## Step 2: Set Up a Virtual Environment (Recommended)

Creating a virtual environment helps keep dependencies isolated:

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

## Step 3: Install Dependencies

Install all required packages using pip:

```bash
pip install -r requirements.txt
```

## Step 4: Configure the Database

1. Make sure your MySQL server is running
2. Open `src/main.py` in a text editor
3. Locate the database configuration section:

```python
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{os.getenv('DB_USERNAME', 'root')}:{os.getenv('DB_PASSWORD', 'password')}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '3306')}/{os.getenv('DB_NAME', 'mydb')}"
```

4. Modify the connection parameters if needed:
   - Default username: `root`
   - Default password: `password`
   - Default host: `localhost`
   - Default port: `3306`
   - Default database name: `mydb`

5. Create the database if it doesn't exist:

```bash
# Connect to MySQL
mysql -u root -p

# In MySQL prompt, create the database
CREATE DATABASE mydb;
EXIT;
```

## Step 5: Verify Spotify API Credentials

The Spotify API credentials have already been implemented in the code:

1. Open `src/routes/spotify.py`
2. Verify that the following lines contain your credentials:

```python
SPOTIFY_CLIENT_ID = "d7753592ca324b718d50aa4dbeacdb87"
SPOTIFY_CLIENT_SECRET = "03ae86e4fd494378a9fa01d83ed1d3e9"
REDIRECT_URI = "http://localhost:5000/api/auth/spotify/callback"
```

3. If you're deploying to a server (not localhost), update the `REDIRECT_URI` and add this URL to your Spotify Developer Dashboard's Redirect URIs.

## Step 6: Run the Application

Start the Flask application:

```bash
# Make sure you're in the project root directory
python src/main.py
```

You should see output indicating that the server is running, typically on http://localhost:5000.

## Step 7: Access the Application

1. Open a web browser and navigate to http://localhost:5000
2. You'll be directed to the login page
3. Register a new account by clicking "Register Instead"
4. Fill in the registration form and submit
5. Log in with your new credentials

## Step 8: Connect Your Spotify Account

1. After logging in, you'll see a prompt to connect your Spotify account
2. Click "Connect Spotify"
3. You'll be redirected to Spotify's authorization page
4. Log in to your Spotify account if needed
5. Authorize the application to access your Spotify data
6. You'll be redirected back to the application

## Step 9: Start Using the Application

1. The application will show initial recommendations based on popular songs
2. Listen to songs by clicking the "Play" button
3. Provide feedback using the "I like" (thumbs up) and "I don't like" (thumbs down) buttons
4. As you provide more feedback, the recommendations will become more personalized
5. You can refresh recommendations by clicking the "Refresh" button

## Troubleshooting

### Application Won't Start

- Check that all dependencies are installed: `pip install -r requirements.txt`
- Verify that the MySQL server is running
- Ensure the database exists and is accessible with the configured credentials

### Database Connection Issues

- Verify MySQL is running: `sudo service mysql status` (Linux) or check MySQL Workbench/Services (Windows)
- Check database credentials in `src/main.py`
- Ensure the database exists: `CREATE DATABASE mydb;`

### Spotify Connection Issues

- Verify your Spotify credentials in `src/routes/spotify.py`
- Check that the redirect URI matches what's registered in your Spotify Developer Dashboard
- Ensure your Spotify account is active and not in use by another application

### Playback Issues

- Some songs may not have preview URLs available from Spotify
- Check your browser's console for any JavaScript errors
- Ensure your browser allows autoplay of media

## Running in Production

For production deployment:

1. Set `debug=False` in `src/main.py`
2. Use a production WSGI server like Gunicorn or uWSGI
3. Set up a proper database with strong credentials
4. Configure the application to use environment variables for sensitive information
5. Use HTTPS for all communications

Example production startup with Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 'src.main:app'
```

## Additional Resources

- Flask Documentation: [flask.palletsprojects.com](https://flask.palletsprojects.com/)
- Spotify API Documentation: [developer.spotify.com/documentation/web-api](https://developer.spotify.com/documentation/web-api/)
- SQLAlchemy Documentation: [docs.sqlalchemy.org](https://docs.sqlalchemy.org/)

For more detailed information about the application architecture and features, refer to the included `architecture_design.md` and `user_guide.md` files.
