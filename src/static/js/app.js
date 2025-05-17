// Main application JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // App state
    const state = {
        user: null,
        currentPage: null,
        recommendations: [],
        history: [],
        currentSong: null,
        player: null,
        isPlaying: false
    };

    // Navigation
    function showPage(pageId) {
        // Hide all pages
        document.querySelectorAll('.container > div[id$="-page"]').forEach(page => {
            page.classList.add('d-none');
        });
        
        // Show selected page
        const page = document.getElementById(pageId + '-page');
        if (page) {
            page.classList.remove('d-none');
            state.currentPage = pageId;
        }
        
        // Update navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        const navLink = document.querySelector(`#nav-${pageId} .nav-link`);
        if (navLink) {
            navLink.classList.add('active');
        }
        
        // Load page-specific data
        if (pageId === 'recommendations') {
            loadRecommendations();
        } else if (pageId === 'history') {
            loadHistory();
        } else if (pageId === 'profile') {
            loadProfile();
        }
    }

    // Authentication
    function checkAuth() {
        fetch('/api/user/profile')
            .then(response => {
                if (response.ok) {
                    return response.json();
                }
                throw new Error('Not logged in');
            })
            .then(data => {
                state.user = data;
                updateAuthUI(true);
                showPage('recommendations');
            })
            .catch(error => {
                state.user = null;
                updateAuthUI(false);
                showPage('login');
            });
    }

    function updateAuthUI(isLoggedIn) {
        if (isLoggedIn) {
            document.getElementById('nav-login').classList.add('d-none');
            document.getElementById('nav-register').classList.add('d-none');
            document.getElementById('nav-recommendations').classList.remove('d-none');
            document.getElementById('nav-history').classList.remove('d-none');
            document.getElementById('nav-profile').classList.remove('d-none');
            document.getElementById('nav-logout').classList.remove('d-none');
            
            // Check Spotify connection
            if (state.user.has_spotify) {
                document.getElementById('spotify-connect-container').classList.add('d-none');
                document.getElementById('spotify-status-connected').classList.remove('d-none');
                document.getElementById('spotify-status-disconnected').classList.add('d-none');
            } else {
                document.getElementById('spotify-connect-container').classList.remove('d-none');
                document.getElementById('spotify-status-connected').classList.add('d-none');
                document.getElementById('spotify-status-disconnected').classList.remove('d-none');
            }
        } else {
            document.getElementById('nav-login').classList.remove('d-none');
            document.getElementById('nav-register').classList.remove('d-none');
            document.getElementById('nav-recommendations').classList.add('d-none');
            document.getElementById('nav-history').classList.add('d-none');
            document.getElementById('nav-profile').classList.add('d-none');
            document.getElementById('nav-logout').classList.add('d-none');
        }
    }

    // Login
    document.getElementById('login-form').addEventListener('submit', function(e) {
        e.preventDefault();
        
        const username = document.getElementById('login-username').value;
        const password = document.getElementById('login-password').value;
        
        fetch('/api/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        })
        .then(response => {
            if (response.ok) {
                return response.json();
            }
            throw new Error('Login failed');
        })
        .then(data => {
            state.user = data.user;
            showToast('Success', 'Logged in successfully');
            updateAuthUI(true);
            showPage('recommendations');
        })
        .catch(error => {
            showToast('Error', 'Login failed. Please check your credentials.');
        });
    });

    // Register
    document.getElementById('register-form').addEventListener('submit', function(e) {
        e.preventDefault();
        
        const username = document.getElementById('register-username').value;
        const email = document.getElementById('register-email').value;
        const password = document.getElementById('register-password').value;
        
        fetch('/api/auth/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, email, password })
        })
        .then(response => {
            if (response.ok) {
                return response.json();
            }
            throw new Error('Registration failed');
        })
        .then(data => {
            showToast('Success', 'Registered successfully. Please log in.');
            document.getElementById('register-form').reset();
            showPage('login');
        })
        .catch(error => {
            showToast('Error', 'Registration failed. Please try again.');
        });
    });

    // Logout
    document.querySelector('#nav-logout').addEventListener('click', function(e) {
        e.preventDefault();
        
        fetch('/api/auth/logout')
            .then(response => {
                state.user = null;
                updateAuthUI(false);
                showPage('login');
                showToast('Success', 'Logged out successfully');
            })
            .catch(error => {
                showToast('Error', 'Logout failed');
            });
    });

    // Recommendations
    function loadRecommendations() {
        if (!state.user) return;
        
        document.getElementById('recommendations-loading').classList.remove('d-none');
        document.getElementById('recommendations-list').innerHTML = '';
        document.getElementById('no-recommendations').classList.add('d-none');
        
        fetch('/api/recommendations')
            .then(response => {
                if (response.ok) {
                    return response.json();
                }
                throw new Error('Failed to load recommendations');
            })
            .then(data => {
                state.recommendations = data;
                document.getElementById('recommendations-loading').classList.add('d-none');
                
                if (data.length === 0) {
                    document.getElementById('no-recommendations').classList.remove('d-none');
                    return;
                }
                
                renderSongs(data, 'recommendations-list');
            })
            .catch(error => {
                document.getElementById('recommendations-loading').classList.add('d-none');
                document.getElementById('no-recommendations').classList.remove('d-none');
                showToast('Error', 'Failed to load recommendations');
            });
    }

    // History
    function loadHistory() {
        if (!state.user) return;
        
        document.getElementById('history-loading').classList.remove('d-none');
        document.getElementById('history-list').innerHTML = '';
        document.getElementById('no-history').classList.add('d-none');
        
        fetch('/api/user/preferences')
            .then(response => {
                if (response.ok) {
                    return response.json();
                }
                throw new Error('Failed to load history');
            })
            .then(data => {
                state.history = data;
                document.getElementById('history-loading').classList.add('d-none');
                
                if (data.length === 0) {
                    document.getElementById('no-history').classList.remove('d-none');
                    return;
                }
                
                // Count likes and dislikes for profile stats
                const likes = data.filter(item => item.rating === 'like').length;
                const dislikes = data.filter(item => item.rating === 'dislike').length;
                document.getElementById('stats-liked').textContent = likes;
                document.getElementById('stats-disliked').textContent = dislikes;
                
                // Render songs
                renderSongs(data.map(item => item.song), 'history-list');
            })
            .catch(error => {
                document.getElementById('history-loading').classList.add('d-none');
                document.getElementById('no-history').classList.remove('d-none');
                showToast('Error', 'Failed to load history');
            });
    }

    // Profile
    function loadProfile() {
        if (!state.user) return;
        
        document.getElementById('profile-username').textContent = state.user.username;
        document.getElementById('profile-email').textContent = state.user.email;
        document.getElementById('profile-created').textContent = new Date(state.user.created_at).toLocaleDateString();
        document.getElementById('profile-last-login').textContent = state.user.last_login ? new Date(state.user.last_login).toLocaleDateString() : 'Never';
        
        // Update Spotify connection status
        if (state.user.has_spotify) {
            document.getElementById('spotify-status-connected').classList.remove('d-none');
            document.getElementById('spotify-status-disconnected').classList.add('d-none');
        } else {
            document.getElementById('spotify-status-connected').classList.add('d-none');
            document.getElementById('spotify-status-disconnected').classList.remove('d-none');
        }
        
        // Update stats
        fetch('/api/recommendations')
            .then(response => response.json())
            .then(data => {
                document.getElementById('stats-recommendations').textContent = data.length;
            })
            .catch(error => {
                document.getElementById('stats-recommendations').textContent = '0';
            });
    }

    // Render songs
    function renderSongs(songs, containerId) {
        const container = document.getElementById(containerId);
        container.innerHTML = '';
        
        const template = document.getElementById('song-template');
        
        songs.forEach(song => {
            const clone = template.content.cloneNode(true);
            
            // Set song data
            clone.querySelector('.song-title').textContent = song.title;
            clone.querySelector('.song-artist').textContent = song.artist;
            
            // Set album art if available
            if (song.image_url) {
                clone.querySelector('.song-image').src = song.image_url;
            } else {
                clone.querySelector('.song-image').src = 'https://via.placeholder.com/300?text=No+Image';
            }
            
            // Set song ID for play button
            const playButton = clone.querySelector('.play-song-btn');
            playButton.dataset.songId = song.spotify_id;
            playButton.addEventListener('click', function() {
                playSong(song);
            });
            
            // Set feedback buttons
            const likeBtn = clone.querySelector('.like-btn');
            const dislikeBtn = clone.querySelector('.dislike-btn');
            
            likeBtn.dataset.songId = song.spotify_id;
            dislikeBtn.dataset.songId = song.spotify_id;
            
            likeBtn.addEventListener('click', function() {
                submitFeedback(song, 'like');
                likeBtn.classList.add('text-success');
                dislikeBtn.classList.remove('text-danger');
            });
            
            dislikeBtn.addEventListener('click', function() {
                submitFeedback(song, 'dislike');
                dislikeBtn.classList.add('text-danger');
                likeBtn.classList.remove('text-success');
            });
            
            container.appendChild(clone);
        });
    }

    // Play song
    function playSong(song) {
        state.currentSong = song;
        
        // Update player UI
        document.getElementById('current-song-title').textContent = song.title;
        document.getElementById('current-song-artist').textContent = song.artist;
        
        if (song.image_url) {
            document.getElementById('current-album-art').src = song.image_url;
        } else {
            document.getElementById('current-album-art').src = 'https://via.placeholder.com/300?text=No+Image';
        }
        
        // If preview URL is available, play it
        if (song.preview_url) {
            if (state.player) {
                state.player.pause();
                state.player = null;
            }
            
            state.player = new Audio(song.preview_url);
            state.player.play();
            state.isPlaying = true;
            
            document.getElementById('play-btn').classList.add('d-none');
            document.getElementById('pause-btn').classList.remove('d-none');
            
            // Update progress bar
            state.player.addEventListener('timeupdate', updateProgress);
            state.player.addEventListener('ended', function() {
                state.isPlaying = false;
                document.getElementById('play-btn').classList.remove('d-none');
                document.getElementById('pause-btn').classList.add('d-none');
            });
        } else {
            showToast('Info', 'No preview available for this song');
        }
    }

    // Update progress bar
    function updateProgress() {
        if (!state.player) return;
        
        const currentTime = state.player.currentTime;
        const duration = state.player.duration;
        const progressPercent = (currentTime / duration) * 100;
        
        document.querySelector('.progress-bar').style.width = `${progressPercent}%`;
        
        // Update time displays
        document.getElementById('current-time').textContent = formatTime(currentTime);
        document.getElementById('duration').textContent = formatTime(duration);
    }

    // Format time (seconds to MM:SS)
    function formatTime(seconds) {
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = Math.floor(seconds % 60);
        return `${minutes}:${remainingSeconds < 10 ? '0' : ''}${remainingSeconds}`;
    }

    // Player controls
    document.getElementById('play-btn').addEventListener('click', function() {
        if (state.player) {
            state.player.play();
            state.isPlaying = true;
            document.getElementById('play-btn').classList.add('d-none');
            document.getElementById('pause-btn').classList.remove('d-none');
        }
    });

    document.getElementById('pause-btn').addEventListener('click', function() {
        if (state.player) {
            state.player.pause();
            state.isPlaying = false;
            document.getElementById('play-btn').classList.remove('d-none');
            document.getElementById('pause-btn').classList.add('d-none');
        }
    });

    document.getElementById('next-btn').addEventListener('click', function() {
        if (state.recommendations.length > 0) {
            const currentIndex = state.recommendations.findIndex(song => song.spotify_id === state.currentSong?.spotify_id);
            const nextIndex = (currentIndex + 1) % state.recommendations.length;
            playSong(state.recommendations[nextIndex]);
        }
    });

    document.getElementById('prev-btn').addEventListener('click', function() {
        if (state.recommendations.length > 0) {
            const currentIndex = state.recommendations.findIndex(song => song.spotify_id === state.currentSong?.spotify_id);
            const prevIndex = (currentIndex - 1 + state.recommendations.length) % state.recommendations.length;
            playSong(state.recommendations[prevIndex]);
        }
    });

    // Submit feedback
    function submitFeedback(song, rating) {
        fetch('/api/feedback', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                song_id: song.spotify_id,
                title: song.title,
                artist: song.artist,
                album: song.album,
                preview_url: song.preview_url,
                rating: rating
            })
        })
        .then(response => {
            if (response.ok) {
                return response.json();
            }
            throw new Error('Failed to submit feedback');
        })
        .then(data => {
            showToast('Success', `Song ${rating === 'like' ? 'liked' : 'disliked'}`);
            
            // Process feedback to update recommendations
            fetch('/api/feedback/process', {
                method: 'POST'
            })
            .then(response => {
                if (response.ok) {
                    // Optionally reload recommendations
                    if (state.currentPage === 'recommendations') {
                        loadRecommendations();
                    }
                }
            });
        })
        .catch(error => {
            showToast('Error', 'Failed to submit feedback');
        });
    }

    // Connect Spotify
    document.getElementById('connect-spotify').addEventListener('click', connectSpotify);
    document.getElementById('profile-connect-spotify').addEventListener('click', connectSpotify);

    function connectSpotify() {
        fetch('/api/auth/spotify')
            .then(response => response.json())
            .then(data => {
                window.location.href = data.auth_url;
            })
            .catch(error => {
                showToast('Error', 'Failed to connect to Spotify');
            });
    }

    // Disconnect Spotify
    document.getElementById('disconnect-spotify').addEventListener('click', function() {
        // This would typically call an API endpoint to remove Spotify tokens
        showToast('Info', 'Spotify disconnection not implemented in this demo');
    });

    // Navigation event listeners
    document.querySelector('#nav-recommendations').addEventListener('click', function(e) {
        e.preventDefault();
        showPage('recommendations');
    });

    document.querySelector('#nav-history').addEventListener('click', function(e) {
        e.preventDefault();
        showPage('history');
    });

    document.querySelector('#nav-profile').addEventListener('click', function(e) {
        e.preventDefault();
        showPage('profile');
    });

    document.querySelector('#nav-login').addEventListener('click', function(e) {
        e.preventDefault();
        showPage('login');
    });

    document.querySelector('#nav-register').addEventListener('click', function(e) {
        e.preventDefault();
        showPage('register');
    });

    // Auth page navigation
    document.getElementById('go-to-register').addEventListener('click', function() {
        showPage('register');
    });

    document.getElementById('go-to-login').addEventListener('click', function() {
        showPage('login');
    });

    // Toast notifications
    function showToast(title, message) {
        const toastId = 'toast-' + Date.now();
        const toastHtml = `
            <div id="${toastId}" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="toast-header">
                    <strong class="me-auto">${title}</strong>
                    <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
                <div class="toast-body">
                    ${message}
                </div>
            </div>
        `;
        
        document.getElementById('toast-container').insertAdjacentHTML('beforeend', toastHtml);
        const toastElement = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastElement, { autohide: true, delay: 3000 });
        toast.show();
        
        // Remove toast from DOM after it's hidden
        toastElement.addEventListener('hidden.bs.toast', function() {
            toastElement.remove();
        });
    }

    // Initialize app
    checkAuth();
});
