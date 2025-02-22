from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from firebase_admin import firestore, auth
from config import db

router = APIRouter()

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


from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from firebase_admin import firestore, auth
from config import db

router = APIRouter()


# Middleware for Firebase authentication
def get_current_user(user_id: str):
    try:
        user = auth.get_user(user_id)
        return user
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or unauthorized user")

@router.get("/api/chat/conversations")
async def get_conversations(user_id: str, user=Depends(get_current_user)):
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

@router.delete("/api/chat/conversations/{conversationId}")
async def delete_conversation(conversationId: str, user=Depends(get_current_user)):
    try:
        conversation_ref = db.collection("chats").document(conversationId)
        conversation = conversation_ref.get()
        
        if not conversation.exists:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        conversation_data = conversation.to_dict()
        if user.uid != conversation_data["created_by"]:
            raise HTTPException(status_code=403, detail="Unauthorized to delete conversation")
        
        conversation_ref.delete()
        return {"message": "Conversation deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/chat/conversations/{conversationId}/messages")
async def get_messages(conversationId: str, user=Depends(get_current_user)):
    try:
        messages_ref = db.collection("chats").document(conversationId).collection("messages").stream()
        messages = [doc.to_dict() for doc in messages_ref]
        return {"messages": messages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/chat/conversations/{conversationId}/messages")
async def send_message(conversationId: str, request: NewMessageRequest, user=Depends(get_current_user)):
    try:
        message_ref = db.collection("chats").document(conversationId).collection("messages").document()
        message_data = {
            "message_id": message_ref.id,
            "sender_id": request.sender_id,
            "content": request.content,
            "timestamp": firestore.SERVER_TIMESTAMP,
            "read": False
        }
        message_ref.set(message_data)
        return {"message": "Message sent successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/api/chat/conversations/{conversationId}/messages/read")
async def mark_messages_as_read(conversationId: str, user=Depends(get_current_user)):
    try:
        messages_ref = db.collection("chats").document(conversationId).collection("messages").stream()
        for message in messages_ref:
            message.reference.update({"read": True})
        return {"message": "Messages marked as read"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from pydantic import BaseModel
from firebase_admin import firestore, auth
from config import db
import speech_recognition as sr
import io

router = APIRouter()


# Middleware for Firebase authentication
def get_current_user(user_id: str):
    try:
        user = auth.get_user(user_id)
        return user
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or unauthorized user")

@router.post("/api/chat/bot")
async def chatbot_query(request: BotQueryRequest, user=Depends(get_current_user)):
    """
    Handle chatbot queries and return responses.
    """
    try:
        response = {"response": f"Bot response to query: {request.query}"}  # Replace with actual chatbot logic
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/chat/audio/upload")
async def upload_audio(file: UploadFile = File(...), user=Depends(get_current_user)):
    """
    Process and transcribe uploaded audio files.
    """
    try:
        recognizer = sr.Recognizer()
        audio_data = sr.AudioFile(io.BytesIO(await file.read()))
        with audio_data as source:
            audio = recognizer.record(source)
        transcript = recognizer.recognize_google(audio)
        return {"transcript": transcript}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/chat/conversations/{conversationId}/metadata")
async def get_conversation_metadata(conversationId: str, user=Depends(get_current_user)):
    """
    Retrieve metadata of a specific conversation.
    """
    try:
        conversation_ref = db.collection("chats").document(conversationId).get()
        if not conversation_ref.exists:
            raise HTTPException(status_code=404, detail="Conversation not found")
        conversation_data = conversation_ref.to_dict()
        return {"metadata": conversation_data.get("metadata", {})}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
