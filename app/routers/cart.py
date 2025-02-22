from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Query
from pydantic import BaseModel
from firebase_admin import firestore, auth, storage, messaging
from google.cloud import vision, speech_v1p1beta1 as speech
from app.models.model_types import CartItemRequest
from config import db
import io
from typing import Optional, List
import uuid
import os
import dotenv
from app.routers.ai import get_current_user

"""
User Cart (in Database):
user_id (reference to the user document)
items (array of objects):
item_id (reference to the inventory item document)
quantity (number)
farm_id (reference to the seller's document) - Required to ensure items are bought from the same farm

API Endpoints:

Add to Cart:
POST /cart/add
Body: item_id (ID of the item to add), quantity (desired quantity)
View Cart:
GET /cart
Retrieve the user's cart items and total bill.
Update Cart Quantity:
PUT /cart/{item_id}
Body: quantity (updated desired quantity)
Remove from Cart:
DELETE /cart/{item_id}
Remove the specified item from the cart.
Empty Cart:
DELETE /cart/empty
Clear all items from the user's cart.

"""

dotenv.load_dotenv()
CREDENTIALS_FILE = os.getenv("CREDENTIALS_FILE")
FCM_SERVER_KEY = "YOUR_FCM_SERVER_KEY"
FCM_URL = "https://fcm.googleapis.com/fcm/send"

router = APIRouter()

# Google Cloud Services
speech_client = speech.SpeechClient()

@router.post("/cart/add")
async def add_to_cart(request: CartItemRequest, user=Depends(get_current_user)):
    """
    Adds an item to the user's cart.
    """
    try:
        inventory_ref = db.reference("inventory").child(request.item_id)
        inventory_data = inventory_ref.get()
        if not inventory_data:
            raise HTTPException(status_code=404, detail="Item not found")
        farm_id = inventory_data["farm"]

        cart_ref = db.reference("carts").child(user.uid)
        cart_data = cart_ref.get() or {"items": []}
        if cart_data["items"] and cart_data["items"][0]["farm_id"] != farm_id:
            raise HTTPException(status_code=400, detail="Cart can only have items from the same farm")

        cart_data["items"].append({"item_id": request.item_id, "quantity": request.quantity, "farm_id": farm_id})
        cart_ref.set(cart_data)

        return {"message": "Item added to cart successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cart")
async def view_cart(user=Depends(get_current_user)):
    """
    Retrieves the user's cart items and calculates the total bill.
    """
    try:
        cart_ref = db.reference("carts").child(user.uid)
        cart_data = cart_ref.get() or {"items": []}
        total_bill = 0
        for item in cart_data.get("items", []):
            inventory_ref = db.reference("inventory").child(item["item_id"])
            inventory_data = inventory_ref.get()
            if inventory_data:
                item_price = inventory_data["price"]["value"] * item["quantity"]
                total_bill += item_price
        return {"items": cart_data["items"], "total_bill": total_bill}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/cart/{item_id}")
async def update_cart_quantity(item_id: str, quantity: int, user=Depends(get_current_user)):
    """
    Updates the quantity of an item in the cart.
    """
    try:
        cart_ref = db.reference("carts").child(user.uid)
        cart_data = cart_ref.get() or {"items": []}
        for item in cart_data["items"]:
            if item["item_id"] == item_id:
                item["quantity"] = quantity
                cart_ref.set(cart_data)
                return {"message": "Cart updated successfully"}
        raise HTTPException(status_code=404, detail="Item not found in cart")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/cart/{item_id}")
async def remove_from_cart(item_id: str, user=Depends(get_current_user)):
    """
    Remove the specified item from the cart.
    """
    try:
        cart_ref = db.reference("carts").child(user.uid)
        cart_data = cart_ref.get() or {"items": []}
        cart_data["items"] = [item for item in cart_data["items"] if item["item_id"] != item_id]
        cart_ref.set(cart_data)
        return {"message": "Item removed from cart successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/cart/empty")
async def empty_cart(user=Depends(get_current_user)):
    """
    Clear all items from the user's cart.
    """
    try:
        cart_ref = db.reference("carts").child(user.uid)
        cart_ref.set({"items": []})
        return {"message": "Cart emptied successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
