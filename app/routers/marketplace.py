from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Query
from pydantic import BaseModel
from firebase_admin import firestore, auth, storage, messaging
from google.cloud import vision, speech_v1p1beta1 as speech
from config import db
import io
from typing import Optional, List
import uuid
import os
import dotenv
from geopy.distance import distance as geopy_distance
from geopy.geocoders import Nominatim

dotenv.load_dotenv()
CREDENTIALS_FILE = os.getenv("CREDENTIALS_FILE")
FCM_SERVER_KEY = "YOUR_FCM_SERVER_KEY"
FCM_URL = "https://fcm.googleapis.com/fcm/send"

router = APIRouter()

# Google Cloud Services
speech_client = speech.SpeechClient()

# Middleware for Firebase authentication
def get_current_user(user_id: str):
    try:
        user = auth.get_user(user_id)
        return user
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or unauthorized user")


router = APIRouter()

"""
The marketplace should list items based on the category of the items, and also based on other filters 
like quanity, farmer/farm, location, price, ratings, etc in ascending order. It should not display out of stock items. 
It should retrive all the listings made by farmer accounts based on these conditions.
The endpoints to be used are:

/marketplace
/marketplace/query={query}
/marketplace/{item_category}
/marketplace/{item_category}/query={query}
/marketplace/{farm}/query={query}
/marketplace/{pincode}/query={query}
/marketplace/query={query}/sorted_by_ratings
/marketplace/query={query}/sorted_by_price
/marketplace/query={query}/sorted_by_quantity

args:
- item_category: str OR Other filters 
- query: str
return:
- list of items

TODO:
Implement being able to specify a location's radius:
eg. 100 km range from 201305 pincode
TODO:
Multiple filters applied at the same time is also to be implemented.

"""

def find_common_items(query_results1, query_results2):
    """
    Finds common items in two query results.
    """
    items1_set = set(query_results1)
    items2_set = set(query_results2)
    common_items_set = items1_set.intersection(items2_set)
    return common_items_set

@router.get("/marketplace")
async def get_all_marketplace_items():
  """
  Retrieves all in-stock listings from the database.
  """
  inventory_ref = db.reference("inventory")
  # Query documents where item_status is "in stock"
  query = inventory_ref.where("item_status", "==", "in stock")
  documents = query.get()

  items = []
  for doc in documents:
    # item_data = doc.to_dict()
    item_data = dict(doc)
    items.append(item_data)

  return items

@router.get("/marketplace/query={query}")
async def get_marketplace_items_by_query(query):
    """
    Retrieves marketplace items based on a search query.
    """
    inventory_ref = db.reference("inventory")
    # Query documents where the name or description contains the query
    query_results = inventory_ref.order_by_child("name").start_at(query).end_at(query + "\uf8ff").get()

    items = []
    for doc in query_results:
        #item_data = dict(doc)
        # item_data = doc.to_dict()
        if item_data["item_status"] == "in stock":  # Filter in-stock items
            items.append(item_data)

    return items

# @router.get("/marketplace/{item_category}/query={query}")
# async def get_marketplace_items_by_category_and_query(item_category: str, query: str):
#     """
#     Retrieves marketplace items based on a category and search query.
#     """
#     inventory_ref = db.reference("inventory")
    
#     # Query documents where the category matches and the name or description contains the query
#     query_results = inventory_ref.order_by_child("category").start_at(item_category).end_at(item_category + "\uf8ff")
#     query_results2 = inventory_ref.order_by_child("name").start_at(query).end_at(query + "\uf8ff")
    
#     items = []
#     for doc in query_results:
#         # item_data = doc.to_dict()
#         item_data = dict(doc)
#         if item_data["item_status"] == "in stock":  # Filter in-stock items
#             items.append(item_data)

#     return items

@router.get("/marketplace/{item_category}/query={query}")
async def get_marketplace_items_by_category_and_query(item_category, query):
    """
    Retrieves items based on category and a search query.
    """
    inventory_ref = db.reference("inventory")
    # Query documents by category and search query
    query_results = inventory_ref.order_by_child("category").start_at(item_category).end_at(item_category + "\uf8ff")
    query_results2 = inventory_ref.order_by_child("name").start_at(query).end_at(query + "\uf8ff")

    # Find common items
    common_items_Set = find_common_items(query_results, query_results2)
    
    items = []
    for doc in common_items_Set:
        # item_data = doc.to_dict()
        item_data = dict(doc)
        if item_data["item_status"] == "in stock":  # Filter in-stock items
            items.append(item_data)

    return items

@router.get("/marketplace/{farm}/query={query}")
async def get_marketplace_items_by_farm_and_query(farm, query):
    """
    Retrieves items based on farm and a search query.
    """
    inventory_ref = db.reference("inventory")
    # Query documents by farm and search query
    query_results = inventory_ref.order_by_child("farm").start_at(farm).end_at(farm + "\uf8ff")
    query_results2 = inventory_ref.order_by_child("name").start_at(query).end_at(query + "\uf8ff")

    # Find common items
    common_items_set = find_common_items(query_results, query_results2)

    items = []
    for doc in common_items_set:
        item_data = dict(doc)
        if item_data["item_status"] == "in stock":  # Filter in-stock items
            items.append(item_data)

    return items

@router.get("/marketplace/{item_category}")
async def get_marketplace_items_by_category(item_category):
    """
    Retrieves items based on category.
    """
    inventory_ref = db.reference("inventory")
    # Query documents by category
    query_results = inventory_ref.order_by_child("category").start_at(item_category).end_at(item_category + "\uf8ff")

    items = []
    for doc in query_results:
        item_data = dict(doc)
        if item_data["item_status"] == "in stock":  # Filter in-stock items
            items.append(item_data)

    return items

@router.get("/marketplace/query={query}/sort_by_price")
async def get_marketplace_items_by_query_and_sort_by_price(query):
    """
    Retrieves items based on a search query and sorts them by price.
    """
    inventory_ref = db.reference("inventory")

    # Query documents where name or description contains the query
    query_results = inventory_ref.order_by_child("name").start_at(query).end_at(query + "\uf8ff")
    query_results2 = inventory_ref.order_by_child("description").start_at(query).end_at(query + "\uf8ff")

    # Find common items
    common_items_set = find_common_items(query_results, query_results2)

    # Sort common items by price
    sorted_items = sorted(common_items_set, key=lambda item: item["price"]["value"])

    return sorted_items

@router.get("/marketplace/query={query}/sort_by_quantity")
async def get_marketplace_items_by_query_and_sort_by_quantity(query):
    """
    Retrieves items based on a search query and sorts them by quantity.
    """
    inventory_ref = db.reference("inventory")

    # Query documents where name or description contains the query
    query_results = inventory_ref.order_by_child("name").start_at(query).end_at(query + "\uf8ff")
    query_results2 = inventory_ref.order_by_child("description").start_at(query).end_at(query + "\uf8ff")

    # Find common items
    common_items_set = find_common_items(query_results, query_results2)

    # Sort common items by quantity
    sorted_items = sorted(common_items_set, key=lambda item: item["quantity"]["value"])

    return sorted_items

@router.get("/marketplace/query={query}/sorted_by_ratings")
async def get_marketplace_items_by_query_and_sort_by_ratings(query):
    """
    Retrieves items based on a search query and sorts them by average rating.
    """
    inventory_ref = db.reference("inventory")

    # Query documents where name or description contains the query
    query_results = inventory_ref.order_by_child("name").start_at(query).end_at(query + "\uf8ff")
    query_results2 = inventory_ref.order_by_child("description").start_at(query).end_at(query + "\uf8ff")

    # Find common items
    common_items_set = find_common_items(query_results, query_results2)

    # Sort common items by average rating
    sorted_items = sorted(common_items_set, key=lambda item: item["average_rating"], reverse=True)

    return sorted_items

@router.get("/marketplace/{pincode}/query={query}")
async def get_marketplace_items_by_pincode_and_query(pincode, query):
    """
    Retrieves items based on a pincode and a search query.
    """
    inventory_ref = db.reference("inventory")

    # Query documents by pincode and search query
    query_results = inventory_ref.order_by_child("pincode").start_at(pincode).end_at(pincode + "\uf8ff")
    query_results2 = inventory_ref.order_by_child("name").start_at(query).end_at(query + "\uf8ff")

    # Find common items
    common_items_set = find_common_items(query_results, query_results2)

    items = []
    for doc in common_items_set:
        item_data = dict(doc)
        if item_data["item_status"] == "in stock":  # Filter in-stock items
            items.append(item_data)

    return items

@router.post("/marketplace/query")
async def query_marketplace(request: MarketplaceQueryRequest):
    """
    Retrieves marketplace items based on a complex query with multiple filters, sorting options, and location radius filtering.
    """
    try:
        inventory_ref = db.reference("inventory")
        query_results = inventory_ref.get() or []
        items = list(query_results.values())

        # Step 1: Apply Location Radius Filter First
        if request.radius and request.pincode:

            geolocator = Nominatim(user_agent="marketplace_locator")
            location_ref = db.reference("locations").child(request.pincode).get()
            if location_ref:
                user_lat, user_lon = location_ref["lat"], location_ref["lon"]
                filtered_items = []
                for item in items:
                    item_location = db.reference("locations").child(item["pincode"]).get()
                    if item_location:
                        item_lat, item_lon = item_location["lat"], item_location["lon"]
                        user_coords = (user_lat, user_lon)
                        item_coords = (item_lat, item_lon)
                        distance = geopy_distance(user_coords, item_coords).km
                        if distance <= request.radius:
                            filtered_items.append(item)
                items = filtered_items

        # Step 2: Apply Category, Farm, and Pincode Filters
        if request.category or request.farm or request.pincode:
            items = [item for item in items if
                     (not request.category or item.get("category") == request.category) and
                     (not request.farm or item.get("farm") == request.farm) and
                     (not request.pincode or item.get("pincode") == request.pincode)]

        # Step 3: Apply Custom and Additional Filters
        if request.filters:
            for filter_key, filter_value in request.filters.items():
                if filter_key == "min_price":
                    items = [item for item in items if item["price"]["value"] >= filter_value]
                elif filter_key == "max_price":
                    items = [item for item in items if item["price"]["value"] <= filter_value]
                elif filter_key == "min_quantity":
                    items = [item for item in items if item["quantity"]["value"] >= filter_value]
                elif filter_key == "max_quantity":
                    items = [item for item in items if item["quantity"]["value"] <= filter_value]
                elif filter_key == "rating_threshold":
                    items = [item for item in items if item.get("average_rating", 0) >= filter_value]

        # Step 4: Filter by Item Status
        items = [item for item in items if item.get("item_status") == "in stock"]

        # Step 5: Sorting
        if request.sorted_by:
            sort_key = {
                "ratings": lambda x: x.get("average_rating", 0),
                "price": lambda x: x.get("price", {}).get("value", 0),
                "quantity": lambda x: x.get("quantity", {}).get("value", 0),
            }.get(request.sorted_by)

            if sort_key:
                reverse = request.sorted_by == "ratings"
                items.sort(key=sort_key, reverse=reverse)

        return {"items": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))