from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from firebase_admin import firestore, auth
from config import db

router = APIRouter()

# Chat conversation models
class NewConversationRequest(BaseModel):
    participants: list[str]  # List of user IDs

class UpdateConversationRequest(BaseModel):
    archived: bool = False
    metadata: dict = {}

# Middleware for Firebase authentication
def get_current_user(user_id: str):
    try:
        user = auth.get_user(user_id)
        return user
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or unauthorized user")


@router.get("/api/chat/conversations")
async def get_conversations(user_id: str, user=Depends(get_current_user)):
    """
    Fetch all conversations for the authenticated user.
    """
    try:
        chat_ref = db.collection("chats").where("participants", "array_contains", user_id).stream()
        conversations = [doc.to_dict() for doc in chat_ref]
        
        if not conversations:
            raise HTTPException(status_code=404, detail="No conversations found")

        return {"conversations": conversations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/chat/conversations")
async def create_conversation(request: NewConversationRequest, user=Depends(get_current_user)):
    """
    Create a new chat conversation.
    """
    try:
        conversation_ref = db.collection("chats").document()
        conversation_data = {
            "conversation_id": conversation_ref.id,
            "participants": request.participants,
            "created_by": user.uid,
            "messages": [],
            "metadata": {},
            "archived": False
        }
        conversation_ref.set(conversation_data)

        return {"message": "Conversation created successfully", "conversation_id": conversation_ref.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/chat/conversations/{conversationId}")
async def get_conversation(conversationId: str, user=Depends(get_current_user)):
    """
    Fetch details of a specific conversation.
    """
    try:
        conversation_ref = db.collection("chats").document(conversationId).get()
        
        if not conversation_ref.exists:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        conversation = conversation_ref.to_dict()
        
        if user.uid not in conversation["participants"]:
            raise HTTPException(status_code=403, detail="Access denied")

        return conversation
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/api/chat/conversations/{conversationId}")
async def update_conversation(conversationId: str, request: UpdateConversationRequest, user=Depends(get_current_user)):
    """
    Update conversation metadata, archive status, etc.
    """
    try:
        conversation_ref = db.collection("chats").document(conversationId)
        conversation = conversation_ref.get()

        if not conversation.exists:
            raise HTTPException(status_code=404, detail="Conversation not found")

        conversation_data = conversation.to_dict()

        if user.uid not in conversation_data["participants"]:
            raise HTTPException(status_code=403, detail="Access denied")

        conversation_ref.update(request.dict())

        return {"message": "Conversation updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
