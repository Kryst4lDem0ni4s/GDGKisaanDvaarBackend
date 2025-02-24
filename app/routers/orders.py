from fastapi import APIRouter, FastAPI, Depends, HTTPException
from pydantic import BaseModel
from typing import List
from firebase_admin import auth, credentials, firestore, initialize_app, db
from uuid import uuid4
import datetime
import dotenv
import os
from app.routers.ai import get_current_user
from models.model_types import OrderCancellation, OrderFeedback, Order, OrderStatusUpdate

# Initialize Firebase
dotenv.load_dotenv()
CREDENTIALS_FILE = os.getenv("CREDENTIALS_FILE")
cred = credentials.Certificate(CREDENTIALS_FILE)

router = APIRouter()

# GET /api/orders - Fetch all orders (Authenticated)
@router.get("/api/orders", response_model=List[dict])
async def get_orders(user=Depends(get_current_user)):
    orders_ref = db.collection("orders").stream()
    orders = [doc.to_dict() for doc in orders_ref]
    return orders

# POST /api/orders - Create a new order
@router.post("/api/orders", response_model=dict)
async def create_order(order: Order, user=Depends(get_current_user)):
    if user["uid"] != order.farmerId:
        raise HTTPException(status_code=403, detail="Unauthorized to create order")

    order_id = str(uuid4())
    order_data = order.dict()
    order_data["orderId"] = order_id
    order_data["createdAt"] = datetime.datetime.utcnow().isoformat()
    
    db.collection("orders").document(order_id).set(order_data)
    return {"message": "Order created successfully", "orderId": order_id}

# GET /api/orders/{orderId} - Fetch a specific order
@router.get("/api/orders/{orderId}", response_model=dict)
async def get_order(orderId: str, user=Depends(get_current_user)):
    order_ref = db.collection("orders").document(orderId).get()
    if not order_ref.exists:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order_data = order_ref.to_dict()
    if user["uid"] not in [order_data["farmerId"], order_data["buyerId"]]:
        raise HTTPException(status_code=403, detail="Unauthorized access")
    
    return order_data

# PUT /api/orders/{orderId}/status - Update order status
@router.put("/api/orders/{orderId}/status", response_model=dict)
async def update_order_status(orderId: str, status_update: OrderStatusUpdate, user=Depends(get_current_user)):
    order_ref = db.collection("orders").document(orderId)
    order_doc = order_ref.get()

    if not order_doc.exists:
        raise HTTPException(status_code=404, detail="Order not found")

    order_data = order_doc.to_dict()
    if user["uid"] not in [order_data["farmerId"], order_data["buyerId"]]:
        raise HTTPException(status_code=403, detail="Unauthorized to update order")

    order_ref.update({"status": status_update.status})
    return {"message": "Order status updated", "newStatus": status_update.status}

# DELETE /api/orders/{orderId} - Delete an order
@router.delete("/api/orders/{orderId}", response_model=dict)
async def delete_order(orderId: str, user=Depends(get_current_user)):
    order_ref = db.collection("orders").document(orderId)
    order_doc = order_ref.get()

    if not order_doc.exists:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order_data = order_doc.to_dict()
    if user["uid"] != order_data["farmerId"]:
        raise HTTPException(status_code=403, detail="Unauthorized to delete order")

    order_ref.delete()
    return {"message": "Order deleted successfully"}

# GET /api/orders/{orderId}/tracking - Retrieve tracking details
@router.get("/api/orders/{orderId}/tracking", response_model=dict)
async def track_order(orderId: str, user=Depends(get_current_user)):
    order_ref = db.collection("orders").document(orderId).get()
    if not order_ref.exists:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order_data = order_ref.to_dict()
    if user["uid"] not in [order_data["farmerId"], order_data["buyerId"]]:
        raise HTTPException(status_code=403, detail="Unauthorized access")
    
    return {"trackingStatus": order_data.get("tracking", "No tracking available")}

# GET /api/orders/{orderId}/chat - Retrieve order chat (Mocked)
@router.get("/api/orders/{orderId}/chat", response_model=List[dict])
async def get_order_chat(orderId: str, user=Depends(get_current_user)):
    chat_ref = db.collection("orders").document(orderId).collection("chat").stream()
    chat_messages = [doc.to_dict() for doc in chat_ref]
    return chat_messages

# POST /api/orders/{orderId}/cancel - Cancel an order with reason
@router.post("/api/orders/{orderId}/cancel", response_model=dict)
async def cancel_order(orderId: str, cancellation: OrderCancellation, user=Depends(get_current_user)):
    order_ref = db.collection("orders").document(orderId)
    order_doc = order_ref.get()
    if not order_doc.exists:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order_data = order_doc.to_dict()
    if user["uid"] not in [order_data["farmerId"], order_data["buyerId"]]:
        raise HTTPException(status_code=403, detail="Unauthorized to cancel order")
    
    order_ref.update({"status": "Cancelled", "cancellationReason": cancellation.reason})
    return {"message": "Order cancelled", "reason": cancellation.reason}

# POST /api/orders/{orderId}/feedback - Submit feedback
@router.post("/api/orders/{orderId}/feedback", response_model=dict)
async def submit_feedback(orderId: str, feedback: OrderFeedback, user=Depends(get_current_user)):
    order_ref = db.collection("orders").document(orderId)
    order_doc = order_ref.get()
    if not order_doc.exists:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order_data = order_doc.to_dict()
    if user["uid"] != order_data["buyerId"]:
        raise HTTPException(status_code=403, detail="Only buyers can submit feedback")
    
    db.collection("orders").document(orderId).update({"feedback": feedback.dict()})
    return {"message": "Feedback submitted successfully"}
