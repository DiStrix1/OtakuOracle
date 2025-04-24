# app/routes/recommend.py

from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Path
from pydantic import BaseModel
from app.services.recommend_service import get_recommendations


# Define response models
class MangaRecommendation(BaseModel):
    title: str
    score: float
    genres: List[str] = []
    themes: List[str] = []
    image_url: str = ""


class RecommendationResponse(BaseModel):
    recommendations: List[MangaRecommendation]


# Create router with tags for API documentation
router = APIRouter(
    prefix="/recommend",
    tags=["recommendations"],
    responses={404: {"description": "Manga not found"}},
)


@router.get("/", response_model=RecommendationResponse)
async def recommend(
    title: str = Query(
        ...,
        min_length=1,
        max_length=100,
        description="Title of the manga to get recommendations for",
        example="Naruto"
    ),
    count: int = Query(
        5,
        ge=1,
        le=20,
        description="Number of recommendations to return",
    )
):
    """
    Get manga recommendations based on a given title.
    
    This endpoint returns a list of manga titles that are similar to the provided title
    based on content similarity analysis.
    
    - **title**: The title of the manga to get recommendations for (can be partial)
    - **count**: Number of recommendations to return (default: 5)
    
    Returns a list of recommended manga titles or a 404 error if the manga is not found.
    """
    # Get recommendations from service
    result = get_recommendations(title, top_n=count)
    
    # Handle not found case
    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"No manga found matching '{title}'"
        )
        
    return {"recommendations": result}


@router.get("/fetch", response_model=Dict[str, str])
async def fetch_data(
    pages: int = Query(
        10,
        ge=1,
        le=50,
        description="Number of pages to fetch from the API"
    )
):
    """
    Fetch manga data from the API.
    
    This endpoint triggers the data fetching process to update the manga database.
    
    - **pages**: Number of pages to fetch from the API (default: 10)
    
    Returns a success message with the path to the saved data file.
    """
    from app.utils.data_fetch import fetch_manga_data
    
    try:
        data_path = fetch_manga_data(pages=pages)
        return {
            "status": "success",
            "message": f"Fetched manga data and saved to {data_path}"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching manga data: {str(e)}"
        )
