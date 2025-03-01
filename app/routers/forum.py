from firebase_admin import firestore, auth
from app.models.model_types import BotQueryRequest, ForumCommentRequest, ForumThreadRequest, ModerateThreadRequest, ReportRequest, UpdateThreadRequest, VoteRequest
from firebase_admin import db
import speech_recognition as sr
import io
from app.controllers.auth import UserAuth
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Query
from pydantic import BaseModel
from firebase_admin import firestore, auth
from typing import Optional
from google.cloud import firestore

db = firestore.Client()


router = APIRouter()

@router.post("/api/chat/bot")
async def chatbot_query(request: BotQueryRequest, user=Depends(UserAuth.get_current_user)):
    """
    Handle chatbot queries and return responses.
    """
    try:
        response = {"response": f"Bot response to query: {request.query}"}  # Replace with actual chatbot logic
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/chat/audio/upload")
async def upload_audio(file: UploadFile = File(...), user=Depends(UserAuth.get_current_user)):
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
async def get_conversation_metadata(conversationId: str, user=Depends(UserAuth.get_current_user)):
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

@router.get("/api/forum/categories")
async def get_forum_categories():
    """
    Fetch all forum categories.
    """
    try:
        categories_ref = db.collection("forum_categories").stream()
        categories = [doc.to_dict() for doc in categories_ref]
        return {"categories": categories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/forum/threads")
async def get_forum_threads():
    """
    Fetch all forum threads.
    """
    try:
        threads_ref = db.collection("forum_threads").stream()
        threads = [doc.to_dict() for doc in threads_ref]
        return {"threads": threads}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/forum/threads")
async def create_forum_thread(request: ForumThreadRequest, user=Depends(UserAuth.get_current_user)):
    """
    Create a new forum thread.
    """
    try:
        thread_ref = db.collection("forum_threads").document()
        thread_data = request.dict()
        thread_data["thread_id"] = thread_ref.id
        thread_ref.set(thread_data)
        return {"message": "Thread created successfully", "thread_id": thread_ref.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/forum/threads/{threadId}")
async def get_forum_thread(threadId: str):
    """
    Retrieve details of a specific forum thread.
    """
    try:
        thread_ref = db.collection("forum_threads").document(threadId).get()
        if not thread_ref.exists:
            raise HTTPException(status_code=404, detail="Thread not found")
        return thread_ref.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/api/forum/threads/{threadId}")
async def update_forum_thread(threadId: str, request: UpdateThreadRequest, user=Depends(UserAuth.get_current_user)):
    """
    Update an existing forum thread.
    """
    try:
        thread_ref = db.collection("forum_threads").document(threadId)
        thread = thread_ref.get()
        if not thread.exists:
            raise HTTPException(status_code=404, detail="Thread not found")
        thread_data = {k: v for k, v in request.dict().items() if v is not None}
        thread_ref.update(thread_data)
        return {"message": "Thread updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/api/forum/threads/{threadId}")
async def delete_forum_thread(threadId: str, user=Depends(UserAuth.get_current_user)):
    """
    Delete a specific forum thread.
    """
    try:
        thread_ref = db.collection("forum_threads").document(threadId)
        thread = thread_ref.get()
        if not thread.exists:
            raise HTTPException(status_code=404, detail="Thread not found")
        thread_ref.delete()
        return {"message": "Thread deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/forum/threads/{threadId}/comments")
async def get_forum_comments(threadId: str):
    """
    Retrieve all comments for a specific forum thread.
    """
    try:
        comments_ref = db.collection("forum_threads").document(threadId).collection("comments").stream()
        comments = [doc.to_dict() for doc in comments_ref]
        return {"comments": comments}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/forum/threads/{threadId}/comments")
async def create_forum_comment(threadId: str, request: ForumCommentRequest, user=Depends(UserAuth.get_current_user)):
    """
    Add a new comment to a forum thread.
    """
    try:
        comment_ref = db.collection("forum_threads").document(threadId).collection("comments").document()
        comment_data = request.dict()
        comment_data["comment_id"] = comment_ref.id
        comment_ref.set(comment_data)
        return {"message": "Comment added successfully", "comment_id": comment_ref.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/forum/search")
async def search_forum_threads(
    query: Optional[str] = Query(None, min_length=3),
    category: Optional[str] = None,
    user_id: Optional[str] = None
):
    """
    Search forum threads based on keywords, category, or user.
    """
    try:
        query_ref = db.collection("forum_threads")
        filters = []
        if category:
            filters.append(query_ref.where("category", "==", category))
        if user_id:
            filters.append(query_ref.where("created_by", "==", user_id))
        
        threads = []
        for thread in query_ref.stream():
            thread_data = thread.to_dict()
            if query and query.lower() not in thread_data.get("title", "").lower():
                continue
            threads.append(thread_data)
        
        return {"threads": threads}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/forum/threads/{threadId}/vote")
async def vote_thread(threadId: str, request: VoteRequest, user=Depends(UserAuth.get_current_user)):
    """
    Upvote or downvote a thread.
    """
    try:
        thread_ref = db.collection("forum_threads").document(threadId)
        thread = thread_ref.get()
        if not thread.exists:
            raise HTTPException(status_code=404, detail="Thread not found")
        thread_data = thread.to_dict()
        votes = thread_data.get("votes", {"up": 0, "down": 0})
        
        if request.vote == "up":
            votes["up"] += 1
        elif request.vote == "down":
            votes["down"] += 1
        else:
            raise HTTPException(status_code=400, detail="Invalid vote type")
        
        thread_ref.update({"votes": votes})
        return {"message": "Vote registered", "votes": votes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/forum/threads/{threadId}/report")
async def report_thread(threadId: str, request: ReportRequest, user=Depends(UserAuth.get_current_user)):
    """
    Report a thread for inappropriate content.
    """
    try:
        report_ref = db.collection("forum_threads").document(threadId).collection("reports").document()
        report_data = request.dict()
        report_data["report_id"] = report_ref.id
        report_data["status"] = "pending"
        report_ref.set(report_data)
        return {"message": "Report submitted successfully", "report_id": report_ref.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/api/forum/threads/{threadId}/moderate")
async def moderate_thread(threadId: str, request: ModerateThreadRequest, user=Depends(UserAuth.get_current_user)):
    """
    Perform moderator actions on a thread (lock, unlock, delete, warn).
    """
    try:
        thread_ref = db.collection("forum_threads").document(threadId)
        thread = thread_ref.get()
        if not thread.exists:
            raise HTTPException(status_code=404, detail="Thread not found")
        
        if request.action not in ["lock", "unlock", "delete", "warn"]:
            raise HTTPException(status_code=400, detail="Invalid moderation action")
        
        update_data = {}
        if request.action == "lock":
            update_data["locked"] = True
        elif request.action == "unlock":
            update_data["locked"] = False
        elif request.action == "delete":
            thread_ref.delete()
            return {"message": "Thread deleted successfully"}
        elif request.action == "warn":
            update_data["warning"] = {"moderator_id": request.moderator_id, "reason": request.reason}
        
        thread_ref.update(update_data)
        return {"message": "Thread moderation applied", "action": request.action}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
