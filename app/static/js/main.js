// Main JavaScript for Manga Recommender

// DOM Elements
const searchForm = document.getElementById('search-form');
const searchInput = document.getElementById('manga-title');
const recommendationsDiv = document.getElementById('recommendations');
const loadingDiv = document.getElementById('loading');
const errorDiv = document.getElementById('error-message');
const noResultsDiv = document.getElementById('no-results');
const themeToggle = document.getElementById('theme-toggle');
const resultsTitle = document.getElementById('results-title');
const modal = document.getElementById('manga-modal');

// Theme Management
function initTheme() {
    // Check for saved theme preference or use preferred color scheme
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-theme');
        themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
    } else if (savedTheme === 'light') {
        document.body.classList.remove('dark-theme');
        themeToggle.innerHTML = '<i class="fas fa-moon"></i>';
    } else {
        // Check user preference
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            document.body.classList.add('dark-theme');
            themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
        }
    }
}

function toggleTheme() {
    if (document.body.classList.contains('dark-theme')) {
        document.body.classList.remove('dark-theme');
        localStorage.setItem('theme', 'light');
        themeToggle.innerHTML = '<i class="fas fa-moon"></i>';
    } else {
        document.body.classList.add('dark-theme');
        localStorage.setItem('theme', 'dark');
        themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
    }
}

// API Interactions
async function getRecommendations(title, count = 10) {
    if (!title) {
        showError('Please enter a manga title');
        return;
    }
    
    resetUI();
    showLoading(true);
    
    try {
        const response = await fetch(`/api/v1/recommend/?title=${encodeURIComponent(title)}&count=${count}`);
        
        if (!response.ok) {
            if (response.status === 404) {
                showNoResults();
            } else {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return;
        }
        
        const data = await response.json();
        
        if (data.recommendations && data.recommendations.length > 0) {
            displayRecommendations(data.recommendations, title);
        } else {
            showNoResults();
        }
    } catch (error) {
        console.error('Error:', error);
        showError(`Error: ${error.message}`);
    } finally {
        showLoading(false);
    }
}

async function fetchData(pages = 10) {
    showLoading(true);
    
    try {
        const response = await fetch(`/api/v1/recommend/fetch?pages=${pages}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        showSuccess(`Database updated successfully! ${data.message}`);
        
    } catch (error) {
        console.error('Error:', error);
        showError(`Error updating database: ${error.message}`);
    } finally {
        showLoading(false);
    }
}

// UI Functions
function resetUI() {
    recommendationsDiv.innerHTML = '';
    errorDiv.style.display = 'none';
    noResultsDiv.style.display = 'none';
    resultsTitle.style.display = 'none';
}

function showLoading(isLoading) {
    loadingDiv.style.display = isLoading ? 'block' : 'none';
}

function showError(message) {
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
    
    // Scroll to error message
    errorDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

function showSuccess(message) {
    // Create a success notification
    const notification = document.createElement('div');
    notification.className = 'success-notification';
    notification.innerHTML = `
        <i class="fas fa-check-circle"></i>
        <p>${message}</p>
    `;
    
    document.body.appendChild(notification);
    
    // Remove after 5 seconds
    setTimeout(() => {
        notification.classList.add('fade-out');
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 500);
    }, 5000);
}

function showNoResults() {
    noResultsDiv.style.display = 'block';
}

function displayRecommendations(recommendations, searchTitle) {
    resultsTitle.textContent = `Recommendations for "${searchTitle}"`;
    resultsTitle.style.display = 'block';
    
    // Clear previous results
    recommendationsDiv.innerHTML = '';
    
    // Add each manga card with staggered animation
    recommendations.forEach((manga, index) => {
        const card = createMangaCard(manga, index);
        recommendationsDiv.appendChild(card);
    });
    
    // Scroll to results
    resultsTitle.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function createMangaCard(manga, index) {
    const card = document.createElement('div');
    card.className = 'manga-card';
    card.style.animationDelay = `${index * 0.1}s`;
    
    // Calculate percentage score for display
    const scorePercentage = (manga.score * 100).toFixed(1);
    
    // Create genre and theme tags
    const genreTags = manga.genres.map(genre => 
        `<span class="genre-tag"><i class="fas fa-bookmark"></i> ${genre}</span>`
    ).join('');
    
    const themeTags = manga.themes.map(theme => 
        `<span class="theme-tag"><i class="fas fa-tag"></i> ${theme}</span>`
    ).join('');
    
    card.innerHTML = `
        <div class="manga-card-image">
            <img src="${manga.image_url || '/static/images/no-image.jpg'}" alt="${manga.title}" 
                onerror="this.src='/static/images/no-image.jpg'">
            <div class="manga-score-badge">${scorePercentage}%</div>
        </div>
        <div class="manga-info">
            <h3 class="manga-title">${manga.title}</h3>
            <div class="manga-genres">
                ${genreTags || '<span class="genre-tag">No genres</span>'}
            </div>
            <div class="manga-themes">
                ${themeTags || '<span class="theme-tag">No themes</span>'}
            </div>
        </div>
    `;
    
    // Add click event to show modal with details
    card.addEventListener('click', () => showMangaDetails(manga));
    
    return card;
}

function showMangaDetails(manga) {
    const scorePercentage = (manga.score * 100).toFixed(1);
    
    // Create genre and theme tags
    const genreTags = manga.genres.map(genre => 
        `<span class="genre-tag"><i class="fas fa-bookmark"></i> ${genre}</span>`
    ).join('');
    
    const themeTags = manga.themes.map(theme => 
        `<span class="theme-tag"><i class="fas fa-tag"></i> ${theme}</span>`
    ).join('');
    
    // Update modal content
    document.getElementById('modal-title').textContent = manga.title;
    document.getElementById('modal-score').textContent = `${scorePercentage}% Match`;
    document.getElementById('modal-image').src = manga.image_url || '/static/images/no-image.jpg';
    document.getElementById('modal-genres').innerHTML = genreTags || 'No genres available';
    document.getElementById('modal-themes').innerHTML = themeTags || 'No themes available';
    
    // Show modal
    modal.style.display = 'block';
    
    // Prevent body scrolling
    document.body.style.overflow = 'hidden';
}

function closeModal() {
    modal.style.display = 'none';
    document.body.style.overflow = 'auto';
}

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    
    // Search form submission
    if (searchForm) {
        searchForm.addEventListener('submit', (e) => {
            e.preventDefault();
            getRecommendations(searchInput.value);
        });
    }
    
    // Theme toggle
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }
    
    // Close modal when clicking outside
    window.addEventListener('click', (e) => {
        if (e.target === modal) {
            closeModal();
        }
    });
    
    // Close modal with escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && modal.style.display === 'block') {
            closeModal();
        }
    });
    
    // Add animation to elements when they come into view
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate');
            }
        });
    }, { threshold: 0.1 });
    
    document.querySelectorAll('.animate-on-scroll').forEach(el => {
        observer.observe(el);
    });
});

// Helper Functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Random recommendations for empty search
function getRandomRecommendations() {
    const popularManga = [
        'One Piece', 'Naruto', 'Bleach', 'Attack on Titan', 'Death Note',
        'Fullmetal Alchemist', 'Dragon Ball', 'Hunter x Hunter', 'Berserk', 'JoJo'
    ];
    
    const randomIndex = Math.floor(Math.random() * popularManga.length);
    getRecommendations(popularManga[randomIndex]);
}

// Export functions for global access
window.getRecommendations = getRecommendations;
window.fetchData = fetchData;
window.closeModal = closeModal;
window.getRandomRecommendations = getRandomRecommendations;
