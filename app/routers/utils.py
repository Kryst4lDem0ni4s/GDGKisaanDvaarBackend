from fastapi import APIRouter, Depends, HTTPException, Query
from google.cloud import firestore
from typing import Dict
from firebase_admin import auth
from app.helpers.ai_helpers import get_admin_user
from app.models.model_types import LogData

router = APIRouter()

# Firestore client initialization
db = firestore.Client()

@router.get("/api/config")
async def get_config():
    """
    Retrieve configuration data (feature toggles, API keys, etc.)
    """
    try:
        # Fetch configuration data from Firestore
        config_ref = db.collection("config").document("global")
        config_doc = config_ref.get()

        if not config_doc.exists:
            raise HTTPException(status_code=404, detail="Configuration not found.")

        config_data = config_doc.to_dict()
        return {"config": config_data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch configuration: {str(e)}")

from pydantic import BaseModel

@router.post("/api/logs")
async def submit_logs(log: LogData):
    """
    Submit client-side error logs or events for analysis.
    """
    try:
        # Store log data in Firestore
        log_ref = db.collection("logs").add({
            "user_id": log.user_id,
            "log_type": log.log_type,
            "message": log.message,
            "timestamp": log.timestamp,
            "metadata": log.metadata
        })

        return {"message": "Log submitted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit log: {str(e)}")

@router.get("/api/search")
async def global_search(query: str):
    """
    Perform a global search across inventory, forums, groups, etc.
    """
    try:
        results = []

        # Search in inventory
        inventory_ref = db.collection("inventory").where("name", "==", query)
        inventory_items = inventory_ref.stream()
        for item in inventory_items:
            results.append({"collection": "inventory", "data": item.to_dict()})

        # Search in forums
        forums_ref = db.collection("forums").where("title", "==", query)
        forum_posts = forums_ref.stream()
        for post in forum_posts:
            results.append({"collection": "forums", "data": post.to_dict()})

        # Search in groups
        groups_ref = db.collection("groups").where("name", "==", query)
        groups = groups_ref.stream()
        for group in groups:
            results.append({"collection": "groups", "data": group.to_dict()})

        if not results:
            raise HTTPException(status_code=404, detail="No results found.")

        return {"results": results}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to perform search: {str(e)}")

@router.get("/api/health")
async def health_check():
    """
    Health check endpoint to verify if the API is running.
    """
    return {"status": "ok", "message": "API is running smoothly."}

@router.get("/api/version")
async def get_api_version():
    """
    Retrieve the current API version.
    """
    # Define the current API version
    api_version = "1.0.0"
    return {"version": api_version}

@router.get("/api/admin/users")
async def list_users(admin_token: dict = Depends(get_admin_user)):
    """
    List all users (Admin only).
    """
    try:
        # Fetch all users from Firestore
        users_ref = db.collection("users")
        users = users_ref.stream()

        user_list = []
        for user in users:
            user_data = user.to_dict()
            user_list.append(user_data)

        return {"users": user_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve users: {str(e)}")

@router.put("/api/admin/users/{userId}/ban")
async def ban_user(userId: str, admin_token: dict = Depends(get_admin_user)):
    """
    Admin functionality to ban a user.
    """
    try:
        # Retrieve the user by userId
        user = auth.get_user(userId)
        
        # Update the user's custom claim to reflect that they are banned
        auth.set_custom_user_claims(userId, {"banned": True})

        # Alternatively, you could set a field in Firestore to flag the user as banned
        # db.collection("users").document(userId).update({"banned": True})

        return {"message": f"User {userId} has been banned successfully."}
    except auth.UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to ban user: {str(e)}")

@router.get("/api/admin/logs")
async def get_system_logs(page: int = Query(1, le=100), limit: int = Query(10, le=100)):
    """
    Admin functionality to retrieve system logs with pagination.
    """
    try:
        # Get logs from Firestore (you can adjust the collection path based on how logs are stored)
        logs_ref = db.collection("logs").order_by("timestamp", direction=firestore.Query.DESCENDING)

        # Implementing pagination
        logs = logs_ref.offset((page - 1) * limit).limit(limit).stream()

        log_list = []
        for log in logs:
            log_list.append(log.to_dict())

        if not log_list:
            raise HTTPException(status_code=404, detail="No logs found.")

        return {"logs": log_list, "page": page, "limit": limit}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve logs: {str(e)}")

@router.get("/api/feature-flags")
async def get_feature_flags(admin_token: dict = Depends(get_admin_user)):
    """
    Retrieve active feature flags for the application.
    """
    try:
        # Assuming feature flags are stored in Firestore
        flags_ref = db.collection("feature_flags").document("active_flags")
        flags_doc = flags_ref.get()

        if not flags_doc.exists:
            raise HTTPException(status_code=404, detail="Feature flags not found.")
        
        flags_data = flags_doc.to_dict()
        return {"feature_flags": flags_data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch feature flags: {str(e)}")

# Initialize rate-limiting (using a backend like Redis)
# @router.on_event("startup")
# async def startup():
#     redis = await aioredis.create_redis_pool("redis://localhost")
#     FastAPILimiter.init(redis)

# # Apply rate limiting to specific routes
# @router.get("/api/admin/users")
# @limiter.limit("5/minute")  # 5 requests per minute
# async def list_users(admin_token: dict = Depends(get_admin_user)):
#     # Endpoint logic...
#     pass

# @router.get("/api/admin/logs")
# @limiter.limit("10/minute")  # 10 requests per minute
# async def get_logs():
#     # Endpoint logic...
#     pass
