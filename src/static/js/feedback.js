// Enhanced feedback functionality for app.js
// This code should be added to the existing app.js file

// Feedback handling functions
function submitFeedback(song, rating) {
    // Show visual feedback immediately
    const songElements = document.querySelectorAll(`[data-song-id="${song.spotify_id}"]`);
    songElements.forEach(element => {
        const likeBtn = element.closest('.card').querySelector('.like-btn');
        const dislikeBtn = element.closest('.card').querySelector('.dislike-btn');
        
        if (rating === 'like') {
            likeBtn.classList.add('text-success');
            dislikeBtn.classList.remove('text-danger');
        } else {
            dislikeBtn.classList.add('text-danger');
            likeBtn.classList.remove('text-success');
        }
    });
    
    // Send feedback to server
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
        
        // Process feedback to update AI model
        return fetch('/api/feedback/process', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                song_id: song.spotify_id,
                rating: rating
            })
        });
    })
    .then(response => {
        if (response.ok) {
            // After 5 feedback submissions, refresh recommendations
            const feedbackCount = parseInt(localStorage.getItem('feedbackCount') || '0') + 1;
            localStorage.setItem('feedbackCount', feedbackCount.toString());
            
            if (feedbackCount % 5 === 0) {
                showToast('Info', 'Updating recommendations based on your feedback...');
                setTimeout(() => {
                    if (state.currentPage === 'recommendations') {
                        loadRecommendations();
                    }
                }, 1500);
            }
        }
    })
    .catch(error => {
        showToast('Error', 'Failed to submit feedback');
        console.error('Feedback error:', error);
    });
}

// Function to mark existing preferences on song load
function markExistingPreferences() {
    // Get user preferences
    fetch('/api/user/preferences')
        .then(response => {
            if (response.ok) {
                return response.json();
            }
            throw new Error('Failed to load preferences');
        })
        .then(preferences => {
            // For each preference, mark the appropriate button
            preferences.forEach(pref => {
                const songElements = document.querySelectorAll(`[data-song-id="${pref.song.spotify_id}"]`);
                songElements.forEach(element => {
                    const likeBtn = element.closest('.card').querySelector('.like-btn');
                    const dislikeBtn = element.closest('.card').querySelector('.dislike-btn');
                    
                    if (pref.rating === 'like') {
                        likeBtn.classList.add('text-success');
                        dislikeBtn.classList.remove('text-danger');
                    } else {
                        dislikeBtn.classList.add('text-danger');
                        likeBtn.classList.remove('text-success');
                    }
                });
            });
        })
        .catch(error => {
            console.error('Error loading preferences:', error);
        });
}

// Enhanced song rendering with feedback button functionality
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
        
        // Set song ID for play button and feedback buttons
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
        
        // Add event listeners with enhanced feedback
        likeBtn.addEventListener('click', function() {
            submitFeedback(song, 'like');
        });
        
        dislikeBtn.addEventListener('click', function() {
            submitFeedback(song, 'dislike');
        });
        
        container.appendChild(clone);
    });
    
    // Mark existing preferences after rendering
    markExistingPreferences();
}

// Add a function to request fresh recommendations
function refreshRecommendations() {
    showToast('Info', 'Generating new recommendations...');
    
    fetch('/api/recommendations/generate', {
        method: 'POST'
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        }
        throw new Error('Failed to generate recommendations');
    })
    .then(data => {
        showToast('Success', 'New recommendations generated');
        loadRecommendations();
    })
    .catch(error => {
        showToast('Error', 'Failed to generate recommendations');
        console.error('Recommendation error:', error);
    });
}

// Add a refresh button to the recommendations page
document.addEventListener('DOMContentLoaded', function() {
    const recommendationsHeader = document.querySelector('#recommendations-page h2');
    if (recommendationsHeader) {
        const refreshButton = document.createElement('button');
        refreshButton.className = 'btn btn-sm btn-outline-spotify ms-3';
        refreshButton.innerHTML = '<i class="bi bi-arrow-clockwise"></i> Refresh';
        refreshButton.addEventListener('click', refreshRecommendations);
        recommendationsHeader.appendChild(refreshButton);
    }
    
    // Initialize feedback count in localStorage if not exists
    if (!localStorage.getItem('feedbackCount')) {
        localStorage.setItem('feedbackCount', '0');
    }
});
