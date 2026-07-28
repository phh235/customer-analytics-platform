from fastapi import APIRouter

from app.schemas.msg import Message

router = APIRouter()


@router.get("/hello", response_model=Message)
async def hello():
    return Message(message="Hello from the Customer Analytics Backend!")
