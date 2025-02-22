from fastapi import APIRouter, HTTPException, Depends
from google.cloud import firestore
from pydantic import BaseModel
from typing import List
from app.models.model_types import SyncAsset, SyncChatRequest, SyncConflictResolution, SyncInventoryRequest, SyncOrderRequest, UserSettingsSync
from app.routers.ai import get_current_user
import time
import random

router = APIRouter()

# Firestore client initialization
db = firestore.Client()

@router.post("/api/sync/inventory")
async def sync_inventory(sync_request: SyncInventoryRequest, user=Depends(get_current_user)):
    """
    Sync offline inventory changes when the user is online.
    """
    try:
        for item in sync_request.items:
            item_ref = db.collection("inventory").document(item.item_id)

            if item.action == 'add':
                item_ref.set({
                    "name": item.name,
                    "category": item.category,
                    "quantity": item.quantity,
                    "price": item.price,
                    "image_url": item.image_url,
                    "user_id": user.uid
                })
            elif item.action == 'edit':
                item_ref.update({
                    "name": item.name,
                    "category": item.category,
                    "quantity": item.quantity,
                    "price": item.price,
                    "image_url": item.image_url
                })
            elif item.action == 'remove':
                item_ref.delete()

        return {"message": "Inventory sync successful."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to sync inventory: {str(e)}")

@router.post("/api/sync/chat")
async def sync_chat(sync_request: SyncChatRequest, user=Depends(get_current_user)):
    """
    Sync offline chat messages when the user is online.
    """
    try:
        for message in sync_request.messages:
            # Save each message to the Firestore chat collection
            chat_ref = db.collection("chats").document(message.conversation_id)
            message_ref = chat_ref.collection("messages").document(message.message_id)

            message_ref.set({
                "sender_id": message.sender_id,
                "message": message.message,
                "timestamp": message.timestamp,
                "user_id": user.uid
            })

        return {"message": "Chat messages synced successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to sync chat messages: {str(e)}")

@router.post("/api/sync/orders")
async def sync_orders(sync_request: SyncOrderRequest, user=Depends(get_current_user)):
    """
    Sync offline order updates when the user is online.
    """
    try:
        for order in sync_request.orders:
            order_ref = db.collection("orders").document(order.order_id)

            if order.action == 'add':
                order_ref.set({
                    "order_status": order.order_status,
                    "items": order.items,
                    "delivery_address": order.delivery_address,
                    "payment_status": order.payment_status,
                    "user_id": user.uid
                })
            elif order.action == 'update':
                order_ref.update({
                    "order_status": order.order_status,
                    "items": order.items,
                    "delivery_address": order.delivery_address,
                    "payment_status": order.payment_status
                })
            elif order.action == 'cancel':
                order_ref.update({
                    "order_status": "cancelled"
                })

        return {"message": "Order sync successful."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to sync orders: {str(e)}")

@router.post("/api/sync/settings")
async def sync_user_settings(settings: UserSettingsSync, user=Depends(get_current_user)):
    """
    Sync offline user settings when the user is online.
    """
    try:
        # Update user settings in Firestore
        settings_ref = db.collection("user_settings").document(settings.user_id)
        settings_ref.set({
            "language": settings.language,
            "notifications_enabled": settings.notifications_enabled,
            "theme": settings.theme,
            "user_id": user.uid
        })
        
        return {"message": "User settings synced successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to sync user settings: {str(e)}")

@router.post("/api/sync/conflict")
async def resolve_sync_conflict(conflict: SyncConflictResolution, user=Depends(get_current_user)):
    """
    Resolve data conflicts during sync by choosing the action: 'overwrite' or 'merge'.
    """
    try:
        doc_ref = db.collection("user_data").document(conflict.document_id)
        doc = doc_ref.get()

        if not doc.exists:
            raise HTTPException(status_code=404, detail="Document not found for conflict resolution.")

        # Resolve conflict based on resolution_action
        if conflict.resolution_action == "overwrite":
            # Overwrite with local value
            doc_ref.update({conflict.field_name: conflict.local_value})
        elif conflict.resolution_action == "merge":
            # Merge logic can be implemented (e.g., merging strings, appending data, etc.)
            existing_value = doc.to_dict().get(conflict.field_name, "")
            merged_value = existing_value + " " + conflict.local_value  # Example of merging strings
            doc_ref.update({conflict.field_name: merged_value})
        else:
            raise HTTPException(status_code=400, detail="Invalid resolution action.")

        return {"message": "Conflict resolved successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to resolve conflict: {str(e)}")

@router.post("/api/sync/assets")
async def sync_assets(sync_request: List[SyncAsset], user=Depends(get_current_user)):
    """
    Sync static assets or configuration when the user is back online.
    """
    try:
        for asset in sync_request:
            # Assuming assets are stored in Google Cloud Storage or Firestore URLs
            asset_ref = db.collection("user_assets").document(asset.asset_name)
            asset_ref.set({
                "asset_url": asset.asset_url,
                "user_id": user.uid
            })

        return {"message": "Assets synced successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to sync assets: {str(e)}")

@router.get("/api/sync/status")
async def get_sync_status(user=Depends(get_current_user)):
    """
    Check the sync status to see if the user's data is fully synchronized.
    """
    try:
        # Fetch sync status from Firestore (assuming you store sync status)
        sync_status_ref = db.collection("user_sync_status").document(user.uid)
        sync_status = sync_status_ref.get()

        if not sync_status.exists:
            return {"message": "Sync status not found."}
        
        status_data = sync_status.to_dict()
        return {"status": status_data.get("status", "Syncing"), "last_synced": status_data.get("last_synced")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch sync status: {str(e)}")

def retry_sync(sync_function, max_retries=5, delay=2):
    """
    Retry the sync operation using exponential backoff.
    """
    retries = 0
    while retries < max_retries:
        try:
            # Attempt to perform the sync function
            sync_function()
            return {"message": "Sync successful."}
        except Exception as e:
            retries += 1
            if retries == max_retries:
                raise HTTPException(status_code=500, detail="Max retries reached, sync failed.")
            else:
                backoff_delay = delay * (2 ** retries) + random.uniform(0, 1)
                time.sleep(backoff_delay)

# 6. Real-Time Sync Using Firestore:
# For real-time synchronization, Firestore offers a simple way to listen for updates and synchronize data across devices. Firestore automatically handles synchronization across clients in real time.

# Example of subscribing to real-time updates in a client-side application:

# python
# Copy
# Edit
# # Client-side JavaScript example for Firestore real-time sync

# const db = firebase.firestore();
# const userRef = db.collection('user_data').doc(userId);

# userRef.onSnapshot((doc) => {
#     console.log("Real-time update: ", doc.data());
# });
# This will allow any changes to the user data to be reflected in real-time across devices, as Firestore will automatically sync updates.

