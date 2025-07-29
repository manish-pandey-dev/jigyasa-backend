from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
import os

router = APIRouter()


# Pydantic models for request/response
class MessageResponse(BaseModel):
    message: str
    timestamp: str
    service: str
    environment: str


class InfoResponse(BaseModel):
    name: str
    version: str
    environment: str
    python_version: str
    port: int


@router.get("/hello", response_model=MessageResponse)
async def hello():
    """Simple hello endpoint"""
    return MessageResponse(
        message="Hello from Jigyasa Backend!",
        timestamp=datetime.now().isoformat(),
        service="Cloud Run",
        environment=os.environ.get("ENVIRONMENT", "development")
    )


@router.get("/info", response_model=InfoResponse)
async def get_info():
    """Get API information"""
    import sys
    return InfoResponse(
        name="Jigyasa Backend API",
        version="1.0.0",
        environment=os.environ.get("ENVIRONMENT", "development"),
        python_version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        port=int(os.environ.get("PORT", 8080))
    )


@router.get("/test/{item_id}")
async def test_endpoint(item_id: int, q: str = None):
    """Test endpoint with path and query parameters"""
    if item_id < 1:
        raise HTTPException(status_code=400, detail="Item ID must be positive")

    return {
        "item_id": item_id,
        "query": q,
        "message": f"You requested item {item_id}",
        "timestamp": datetime.now().isoformat()
    }