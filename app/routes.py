from fastapi import APIRouter

router = APIRouter()

@router.get("/api/status")
async def status():
    return {"message": "API is working"}
