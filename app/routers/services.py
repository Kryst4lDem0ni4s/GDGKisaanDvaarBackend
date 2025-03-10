import os
from firebase_admin import credentials, initialize_app, auth
from typing import *
from fastapi import APIRouter, HTTPException
from app.controllers.auth import UserAuth
from firebase_admin import db

router = APIRouter()

@router.post("/cold_storage_services")
async def create_cold_storage_service(name, address, phone_number, email=None, website=None, description="", minimum_quantity=0, areas_served=[], payment_methods=[], rating=0, favorites=[], status="active"):
    """Creates a new cold storage service document in the Firebase database."""
    
    # Validate user's occupation (ensure they are a customer) TO-DO
    user = await UserAuth.get_current_user()
    if user.occupation != "customer":
        raise HTTPException(status_code=403, detail="Only customers can create service listings.")
    
    data = {
        "name": name,
        "address": address,
        "phone_number": phone_number,
        "email": email,
        "website": website,
        "description": description,
        "minimum_quantity": minimum_quantity,
        "areas_served": areas_served,
        "payment_methods": payment_methods,
        "rating": rating,
        "status": status
    }

    # Assuming you have already initialized Firebase and obtained a database reference
    db_ref = db.reference("cold_storage_services")
    new_ref = db_ref.push()
    new_ref.set(data)
    return new_ref.key  # Returns the generated ID for the new document

@router.get("/cold_storage_services")
async def get_cold_storage_services():
    db_ref = db.reference("cold_storage_services")
    data = db_ref.get()
    return data

@router.get("/cold_storage_services/{service_id}")
async def get_cold_storage_service(service_id):
    db_ref = db.reference(f"cold_storage_services/{service_id}")
    data = db_ref.get()
    return data

# async def update_cold_storage_service(service_id, data: dict):
@router.put("/cold_storage_services/{service_id}")
async def update_cold_storage_service(service_id, name, address, phone_number, email=None, website=None, description="", minimum_quantity=0, areas_served=[], payment_methods=[], rating=0, favorites=[], status="active"):
    """User authentication per session is possible from flutter side, TODO"""
    # Validate user's occupation (ensure they are the customer that uploaded.)
    user = await UserAuth.get_current_user()
    if user.occupation not in ["customer"]:
        raise HTTPException(status_code=403, detail="Only owners or admins can update service listings.")
    # https://firebase.google.com/docs/auth/android/manage-users

    data = {
        "name": name,
        "address": address,
        "phone_number": phone_number,
        "email": email,
        "website": website,
        "description": description,
        "minimum_quantity": minimum_quantity,
        "areas_served": areas_served,
        "payment_methods": payment_methods,
        "rating": rating,
        "status": status
    }

    db_ref = db.reference(f"cold_storage_services/{service_id}")
    db_ref.update(data)
    return data

@router.delete("/cold_storage_services/{service_id}")
async def delete_cold_storage_service(service_id):

    db_ref = db.reference(f"cold_storage_services/{service_id}")
    db_ref.delete()
    return {"message": "Service listing deleted successfully"}

@router.patch("/cold_storage_services/{service_id}/favorite")
async def mark_as_favorite(service_id):
    
    # Validate user's occupation (ensure they are a farmer)
    user = await UserAuth.get_current_user()
    if user.occupation != "farmer":
        raise HTTPException(status_code=403, detail="Only farmers can mark services as favorites.")

    # Add the service to the user's favorites array
    user_ref = db.reference(f"users/{user.uid}")
    favorites = user_ref.child("favorites").get() or []
    favorites.append(service_id)
    user_ref.child("favorites").set(favorites)

    return {"message": "Service marked as favorite"}

@router.patch("/cold_storage_services/{service_id}/unfavorite")
async def unmark_as_favorite(service_id):
    # Validate user's occupation (ensure they are a farmer)
    user = await UserAuth.get_current_user()
    if user.occupation != "farmer":
        raise HTTPException(status_code=403, detail="Only farmers can unmark services as favorites.")

    # Remove the service from the user's favorites array
    user_ref = db.reference(f"users/{user.uid}")
    favorites = user_ref.child("favorites").get() or []
    favorites = [favorite for favorite in favorites if favorite != service_id]
    user_ref.child("favorites").set(favorites)

    return {"message": "Service unmarked as favorite"}