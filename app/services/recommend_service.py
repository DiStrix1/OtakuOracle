# app/services/recommend_service.py

import json
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def load_manga_data():
    # Use pathlib for more robust path handling
    base_dir = Path(__file__).resolve().parent.parent.parent
    data_path = base_dir / "data" / "manga_data.json"
    
    try:
        with open(data_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Could not find manga data file at: {data_path}. Please run the data_fetch.py script first.")


def get_recommendations(title, top_n=5):
    manga_data = load_manga_data()
    
    # Convert title to lowercase for case-insensitive matching
    title = title.lower()
    titles = [m["title"].lower() for m in manga_data]
    
    # Check if the title exists (with partial matching)
    matching_indices = [i for i, t in enumerate(titles) if title in t]
    
    if not matching_indices:
        # No matches found
        return None
    
    # If we have multiple partial matches, use the closest one
    if len(matching_indices) > 1:
        # Find the closest match (shortest title that contains our search term)
        idx = min(matching_indices, key=lambda i: len(titles[i]))
    else:
        idx = matching_indices[0]
    
    # Create a list of combined text for TF-IDF
    combined_texts = []
    for manga in manga_data:
        # Combine title, description, genres and themes for better recommendations
        genres_text = " ".join([g + " " + g for g in manga.get("genres", [])])  # Double weight for genres
        themes_text = " ".join([t + " " + t for t in manga.get("themes", [])])  # Double weight for themes
        combined_text = f"{manga['title']} {manga.get('description', '')} {genres_text} {themes_text}"
        combined_texts.append(combined_text)
    
    # Create TF-IDF matrix with improved parameters
    tfidf = TfidfVectorizer(stop_words='english', min_df=2, max_df=0.85, ngram_range=(1,2))
    tfidf_matrix = tfidf.fit_transform(combined_texts)
    
    # Calculate cosine similarity
    cosine_sim = cosine_similarity(tfidf_matrix[idx:idx+1], tfidf_matrix).flatten()
    
    # Apply boosting based on genre and theme overlap
    target_manga = manga_data[idx]
    target_genres = set(target_manga.get("genres", []))
    target_themes = set(target_manga.get("themes", []))

    boosted_scores = []
    for i, score in enumerate(cosine_sim):
        if i == idx:
            boosted_scores.append(score)
            continue
        
        current_manga = manga_data[i]
        current_genres = set(current_manga.get("genres", []))
        current_themes = set(current_manga.get("themes", []))
        
        # Calculate genre and theme overlap using Jaccard similarity
        genre_overlap = len(target_genres.intersection(current_genres)) / max(1, len(target_genres.union(current_genres)))
        theme_overlap = len(target_themes.intersection(current_themes)) / max(1, len(target_themes.union(current_themes)))
        
        # Apply boosting - increase the multiplier for higher scores
        boosted_score = score * (1 + 2*genre_overlap + 2*theme_overlap)  # Increased weight for genre/theme overlap
        boosted_scores.append(boosted_score)
    
    # Get top similar manga indices using BOOSTED scores
    sim_scores = list(enumerate(boosted_scores))  # Use boosted_scores instead of cosine_sim
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:top_n+1]
    
    # Create detailed recommendations
    recommendations = []
    for i, score in sim_scores:
        manga = manga_data[i]
        recommendations.append({
            "title": manga["title"],
            "score": float(score),  # This will now be the boosted score
            "genres": manga.get("genres", []),
            "themes": manga.get("themes", []),
            "image_url": manga.get("image_url", "")
        })
    
    return recommendations
