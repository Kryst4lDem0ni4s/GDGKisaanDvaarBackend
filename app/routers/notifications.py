from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Query
from firebase_admin import firestore, auth, storage, messaging, db
from google.cloud import vision, speech_v1p1beta1 as speech
from app.models.model_types import NotificationRequest, NotificationSubscriptionRequest
from app.controllers.auth import UserAuth

router = APIRouter()

# Google Cloud Services
speech_client = speech.SpeechClient()

@router.get("/api/notifications")
async def get_notifications(user=Depends(UserAuth.get_current_user)):
    """
    Retrieve all notifications for a user.
    """
    try:
        notifications_ref = db.reference(f"notifications/{user.uid}").get()
        notifications = notifications_ref if notifications_ref else []
        return {"notifications": notifications}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/api/notifications/{notificationId}/mark-read")
async def mark_notification_as_read(notificationId: str, user=Depends(UserAuth.get_current_user)):
    """
    Mark a notification as read.
    """
    try:
        notification_ref = db.reference(f"notifications/{user.uid}/{notificationId}")
        notification = notification_ref.get()
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
        notification_ref.update({"read": True})
        return {"message": "Notification marked as read"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/api/notifications/{notificationId}")
async def delete_notification(notificationId: str, user=Depends(UserAuth.get_current_user)):
    """
    Delete a notification.
    """
    try:
        notification_ref = db.reference(f"notifications/{user.uid}/{notificationId}")
        notification = notification_ref.get()
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
        notification_ref.delete()
        return {"message": "Notification deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/notifications/send")
async def send_notification(request: NotificationRequest, user=Depends(UserAuth.get_current_user)):
    """
    Send a notification to a user.
    """
    try:
        if not user.custom_claims.get("is_admin"):
            raise HTTPException(status_code=403, detail="Unauthorized action")
        
        notification_ref = db.reference(f"notifications/{request.user_id}").push()
        notification_data = request.dict()
        notification_data["notification_id"] = notification_ref.key
        notification_data["read"] = False
        notification_ref.set(notification_data)

        # Sending Firebase Cloud Messaging (FCM) notification
        message = messaging.Message(
            notification=messaging.Notification(
                title=request.title,
                body=request.body
            ),
            token=f"user_device_token_{request.user_id}"  # Assume a device token system
        )
        messaging.send(message)
        
        return {"message": "Notification sent successfully", "notification_id": notification_ref.key}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/notifications/unread-count")
async def get_unread_notification_count(user=Depends(UserAuth.get_current_user)):
    """
    Retrieve the count of unread notifications.
    """
    try:
        notifications_ref = db.reference(f"notifications/{user.uid}").get()
        unread_count = sum(1 for n in notifications_ref.values() if not n.get("read", False)) if notifications_ref else 0
        return {"unread_count": unread_count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/notifications")
async def get_notifications(user=Depends(UserAuth.get_current_user)):
    """
    Retrieve all notifications for a user.
    """
    try:
        notifications_ref = db.reference(f"notifications/{user.uid}").get()
        notifications = notifications_ref if notifications_ref else []
        return {"notifications": notifications}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/notifications/subscribe")
async def subscribe_to_notifications(request: NotificationSubscriptionRequest, user=Depends(UserAuth.get_current_user)):
    """
    Subscribe to notification topics.
    """
    try:
        topic = request.topic
        token = f"user_device_token_{user.uid}"  # Assume a device token system
        messaging.subscribe_to_topic([token], topic)
        return {"message": "Subscribed to topic successfully", "topic": topic}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/notifications/unsubscribe")
async def unsubscribe_from_notifications(request: NotificationSubscriptionRequest, user=Depends(UserAuth.get_current_user)):
    """
    Unsubscribe from notification topics.
    """
    try:
        topic = request.topic
        token = f"user_device_token_{user.uid}"  # Assume a device token system
        messaging.unsubscribe_from_topic([token], topic)
        return {"message": "Unsubscribed from topic successfully", "topic": topic}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
