from firebase_admin import credentials, initialize_app, auth, db
from fastapi import UploadFile, File
import app.models.model_types as modelType
from app.helpers import ai_helpers
from app.utils import utils
import json
from typing import *
import os
import firebase_admin
from fastapi import APIRouter, HTTPException

# Initialize the Firebase Admin SDK with the downloaded service account key
# cred = credentials.Certificate("D:/DdriveCodes/SIH/app/helpers/kisaandvaar-firebase-adminsdk-t83e9-f6d6bf9844.json")
# initialize_app(cred)

#auth = auth()

router = APIRouter()

@router.post("/api/inventory/items")
def create_inventory_item(name, category, quantity, storage, description, price, item_id=None, rating=0.0, item_status="in stock"):
    try:
        storage_collection = db.collection(storage)  # Use storage as collection name

        # Generate a unique ID if item_id is not provided
        if not item_id:
            item_id = storage_collection.document().id

        doc_ref = storage_collection.document(item_id)
        doc_ref.set({
            "name": name,
            "category": category,
            "quantity": {
                "value": quantity,
                "unit": "kg"  # kg, gm, pound, etc options
            },
            "storage": storage,  # self_stored or externally_stored
            "description": description,
            "price": {
                "value": price,
                "unit": "kg"  # kg, gm, pound, etc options
            },
            "ratings": [],  # an empty list for ratings
            "average_rating": 0.0,  # Initialize average rating to zero
            "item_status": item_status,  # item status field (in stock, sold, etc)
        })
        print("Inventory item created:", doc_ref)

        return {"status": "success", "message": "Inventory item created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Function to retrieve all items from the inventory based on storage type.
@router.get("/api/inventory/{storage}")
def get_items1(storage):
    try:
        storage_collection = db.collection(storage)  # Use storage type as collection name
        docs = storage_collection.get()
        items = []
        for doc in docs:
            items.append(doc.to_dict())
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Function to retrieve all items from the inventory.
@router.get("/api/inventory")
def get_items():
    try:
        self_stored_collection = db.collection("self_stored")
        self_stored_docs = self_stored_collection.get()

        externally_stored_collection = db.collection("externally_stored")
        externally_stored_docs = externally_stored_collection.get()

        all_items = []
        all_items.extend(doc.to_dict() for doc in self_stored_docs)
        all_items.extend(doc.to_dict() for doc in externally_stored_docs)

        return all_items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/api/inventory/{storage}/{itemId}")
def get_item(storage: str, item_id: str):
    try:
        storage_collection = db.collection(storage)
        doc_ref = storage_collection.document(item_id)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        else:
            raise HTTPException(status_code=404, detail="Item not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Example usage:
# create_inventory_item("Apples", "fruits", 10, "self", "Fresh, red apples", 20)
@router.delete("/api/inventory/{storage}/{item_id}")
def delete_item(storage: str, item_id: str):
    try:
        storage_collection = db.collection(storage)
        doc_ref = storage_collection.document(item_id)
        doc_ref.delete()
        return {"status": "success", "message": "Item deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.put("/api/inventory/{storage}/{item_id}")
def update_item(storage, item_id, name: Optional[str] = None, category: Optional[str] = None, quantity: Optional[int] = None, description: Optional[str] = None, price: Optional[float] = None):
    try:
        storage_collection = db.collection(storage)
        doc_ref = storage_collection.document(item_id)

        data = {}
        if name is not None:
            data["name"] = name
        if category is not None:
            data["category"] = category
        if quantity is not None:
            data["quantity"] = quantity
            if quantity == 0:
                data["item_status"] = "out of stock"
        if description is not None:
            data["description"] = description
        if price is not None:
            data["price"] = price

        doc_ref.update(data)
        return {"status": "success", "message": "Item updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
# GET /api/inventory/categories
@router.get("/api/inventory/{storage}/{category}")
def get_categories(storage, category, **kwargs):
    try:
        categories = set()
        for cat in category.split(','):  # Split the comma-separated values to handle multiple categories
            docs = db.collection(storage).where('category', '==', cat).get()
            for doc in docs:
                categories.add(doc.to_dict().get("category"))
        return list(categories)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# GET /api/inventory/search
@router.get("/api/inventory/search")
def search_inventory(
    category: Optional[str] = None,
    keyword: Optional[str] = None,
    location: Optional[str] = None,
    storage_type: Optional[str] = None
):
    try:
        collections = ["self_stored", "externally_stored"] if not storage_type else [storage_type]
        results = []
        
        for collection in collections:
            docs = db.collection(collection).get()
            for doc in docs:
                item = doc.to_dict()
                if (not category or item.get("category") == category) and \
                   (not keyword or keyword.lower() in item.get("name", "").lower()) and \
                   (not location or item.get("location") == location):
                    results.append(item)
        
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# GET /api/inventory/history
@router.get("/api/inventory/history")
def get_inventory_history(storage_type: Optional[str] = None):
    try:
        collections = ["self_stored", "externally_stored"] if not storage_type else [storage_type]
        history = []
        
        for collection in collections:
            docs = db.collection(f"{collection}_history").get()
            history.extend(doc.to_dict() for doc in docs)
        
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# POST /api/inventory/items/{itemId}/upload-image
@router.post("/api/inventory/{storage}/{itemId}/upload-image")
def upload_item_image(storage: str, itemId: str, file: UploadFile = File(...)):
    try:
        file_location = f"uploaded_images/{itemId}_{file.filename}"
        os.makedirs(os.path.dirname(file_location), exist_ok=True)
        
        with open(file_location, "wb") as buffer:
            buffer.write(file.file.read())
        
        db.collection("storage").document(itemId).update({"image_url": file_location})
        
        return {"status": "success", "message": "Image uploaded successfully", "file_path": file_location}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# GET /api/inventory/analytics
@router.get("/api/inventory/analytics")
def get_inventory_analytics():
    try:
        analytics = {}
        for storage_type in ["self_stored", "externally_stored"]:
            docs = db.collection(storage_type).get()
            analytics[storage_type] = len(docs)
            # implement logic for analytics aka charts to represent storage distribution
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
