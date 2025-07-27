from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import upload
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Jigyasa Backend API",
    description="Audio-to-Quiz Generation API",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React development server
        "https://*.netlify.app",   # Netlify domains
        "https://netlify.app",     # Netlify domains
        "https://*.vercel.app",    # Vercel domains (alternative to Netlify)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload.router, prefix="/api", tags=["upload"])

@app.get("/")
async def root():
    return {
        "message": "🤔 Jigyasa Backend API is running!",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "jigyasa-backend"}