# app/main.py

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routes.recommend import router as recommend_router
from pathlib import Path
from contextlib import asynccontextmanager

# Define lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app_: FastAPI):
    # Startup: Create data directory if it doesn't exist
    base_dir = Path(__file__).resolve().parent.parent
    data_dir = base_dir / "data"
    data_dir.mkdir(exist_ok=True)
    
    # Check if manga_data.json exists
    data_file = data_dir / "manga_data.json"
    if not data_file.exists():
        print("Warning: manga_data.json not found. Use the /api/v1/recommend/fetch endpoint to fetch data.")
    
    yield  # This is where the app runs
    
    # Shutdown: Clean up resources if needed
    pass

# Create FastAPI application
app = FastAPI(
    title="Manga Recommendation API",
    description="API for recommending manga based on similarity",
    version="1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Mount static files directory
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")

# Include routers
app.include_router(recommend_router, prefix="/api/v1")

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(_: Request, exc: Exception):
    # Using underscore to indicate unused parameter
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal Server Error: {str(exc)}"},
    )

# Root endpoint - serve the frontend
@app.get("/", response_class=FileResponse)
async def root():
    return Path(__file__).parent / "static" / "index.html"
