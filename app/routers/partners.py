from fastapi import APIRouter, HTTPException
from google.cloud import firestore
from typing import List

router = APIRouter()

# Firestore client initialization
db = firestore.Client()

@router.get("/api/partners/retail")
async def get_retail_partners():
    """
    Retrieve a list of retail partners.
    """
    try:
        # Fetch retail partners from Firestore
        partners_ref = db.collection("partners").where("type", "==", "retail")
        partners = partners_ref.stream()

        # Collect partner data
        partner_list = []
        for partner in partners:
            partner_list.append(partner.to_dict())
        
        return {"partners": partner_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve retail partners: {str(e)}")

from pydantic import BaseModel

class RetailPartner(BaseModel):
    name: str
    location: str
    contact_info: str
    business_type: str
    rating: float
    user_id: str

@router.post("/api/partners/retail")
async def add_retail_partner(partner: RetailPartner):
    """
    Add a new retail partner.
    """
    try:
        # Store new partner in Firestore
        partner_ref = db.collection("partners").add({
            "name": partner.name,
            "location": partner.location,
            "contact_info": partner.contact_info,
            "business_type": partner.business_type,
            "rating": partner.rating,
            "type": "retail",
            "user_id": partner.user_id
        })

        return {"message": "Retail partner added successfully", "partner_id": partner_ref.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add retail partner: {str(e)}")

class UpdatePartnerDetails(BaseModel):
    partner_id: str
    name: str = None
    location: str = None
    contact_info: str = None
    business_type: str = None
    rating: float = None

@router.put("/api/partners/update")
async def update_partner_details(details: UpdatePartnerDetails):
    """
    Update partner details based on the provided partner_id.
    """
    try:
        partner_ref = db.collection("partners").document(details.partner_id)
        partner_doc = partner_ref.get()

        if not partner_doc.exists:
            raise HTTPException(status_code=404, detail="Partner not found.")
        
        # Prepare update data
        update_data = {}
        if details.name: update_data["name"] = details.name
        if details.location: update_data["location"] = details.location
        if details.contact_info: update_data["contact_info"] = details.contact_info
        if details.business_type: update_data["business_type"] = details.business_type
        if details.rating: update_data["rating"] = details.rating

        # Update partner details in Firestore
        partner_ref.update(update_data)

        return {"message": "Partner details updated successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update partner details: {str(e)}")

@router.get("/api/partners/{partnerId}/reviews")
async def get_partner_reviews(partnerId: str):
    """
    Retrieve reviews for a specific partner using partnerId.
    """
    try:
        # Fetch reviews from Firestore for the given partnerId
        reviews_ref = db.collection("partners").document(partnerId).collection("reviews")
        reviews = reviews_ref.stream()

        # Collect reviews data
        review_list = []
        for review in reviews:
            review_list.append(review.to_dict())

        return {"reviews": review_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve partner reviews: {str(e)}")

@router.get("/api/partners/cold-storage")
async def get_cold_storage_partners(user=Depends(get_current_user)):
    """
    Retrieve a list of cold storage partners.
    """
    try:
        # Fetch cold storage partners from Firestore
        cold_storage_ref = db.collection("partners").where("type", "==", "cold-storage")
        cold_storage_partners = cold_storage_ref.stream()

        partner_list = []
        for partner in cold_storage_partners:
            partner_list.append(partner.to_dict())
        
        return {"cold_storage_partners": partner_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve cold storage partners: {str(e)}")

class ColdStoragePartner(BaseModel):
    name: str
    location: str
    capacity: int  # In terms of volume or quantity
    contact_info: str
    user_id: str

@router.post("/api/partners/cold-storage")
async def add_cold_storage_partner(partner: ColdStoragePartner, user=Depends(get_current_user)):
    """
    Add a new cold storage partner.
    """
    try:
        # Add the cold storage partner to Firestore
        partner_ref = db.collection("partners").add({
            "name": partner.name,
            "location": partner.location,
            "capacity": partner.capacity,
            "contact_info": partner.contact_info,
            "user_id": user.uid,
            "type": "cold-storage"
        })
        return {"message": "Cold storage partner added successfully", "partner_id": partner_ref.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add cold storage partner: {str(e)}")

@router.get("/api/partners/transport")
async def get_transport_partners(user=Depends(get_current_user)):
    """
    Retrieve a list of transport partners.
    """
    try:
        # Fetch transport partners from Firestore
        transport_ref = db.collection("partners").where("type", "==", "transport")
        transport_partners = transport_ref.stream()

        partner_list = []
        for partner in transport_partners:
            partner_list.append(partner.to_dict())
        
        return {"transport_partners": partner_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve transport partners: {str(e)}")

class UpdatePartnerDetails(BaseModel):
    partner_id: str
    name: str = None
    location: str = None
    fleet_size: int = None  # For transport partners
    capacity: int = None  # For cold storage partners
    contact_info: str = None

@router.put("/api/partners/update")
async def update_partner_details(details: UpdatePartnerDetails, user=Depends(get_current_user)):
    """
    Update partner details for a specific partner.
    """
    try:
        partner_ref = db.collection("partners").document(details.partner_id)
        partner_doc = partner_ref.get()

        if not partner_doc.exists:
            raise HTTPException(status_code=404, detail="Partner not found.")
        
        # Prepare update data
        update_data = {}
        if details.name: update_data["name"] = details.name
        if details.location: update_data["location"] = details.location
        if details.fleet_size is not None: update_data["fleet_size"] = details.fleet_size
        if details.capacity is not None: update_data["capacity"] = details.capacity
        if details.contact_info: update_data["contact_info"] = details.contact_info

        # Update partner details in Firestore
        partner_ref.update(update_data)

        return {"message": "Partner details updated successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update partner details: {str(e)}")

@router.get("/api/partners/{partnerId}/reviews")
async def get_partner_reviews(partnerId: str):
    """
    Retrieve reviews for a specific partner using partnerId.
    """
    try:
        # Fetch reviews from Firestore for the given partnerId
        reviews_ref = db.collection("partners").document(partnerId).collection("reviews")
        reviews = reviews_ref.stream()

        # Collect reviews data
        review_list = []
        for review in reviews:
            review_list.append(review.to_dict())

        return {"reviews": review_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve partner reviews: {str(e)}")

from fastapi import APIRouter, HTTPException
from typing import List
from google.cloud import firestore

router = APIRouter()

# Firestore client initialization
db = firestore.Client()

@router.get("/api/partners/search")
async def search_partners(location: str = None, partner_type: str = None, min_rating: float = 0):
    """
    Search partners based on location, type, and rating.
    """
    try:
        # Initialize query reference
        partners_ref = db.collection("partners")

        # Apply filters dynamically based on query parameters
        if location:
            partners_ref = partners_ref.where("location", "==", location)
        if partner_type:
            partners_ref = partners_ref.where("type", "==", partner_type)
        if min_rating:
            partners_ref = partners_ref.where("rating", ">=", min_rating)

        partners = partners_ref.stream()

        partner_list = []
        for partner in partners:
            partner_list.append(partner.to_dict())

        return {"partners": partner_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search for partners: {str(e)}")

@router.get("/api/partners/{partnerId}/analytics")
async def get_partner_analytics(partnerId: str):
    """
    Provide performance metrics for a specific partner.
    - For transport: number of deliveries.
    - For cold storage: storage capacity utilization.
    """
    try:
        partner_ref = db.collection("partners").document(partnerId)
        partner_doc = partner_ref.get()

        if not partner_doc.exists:
            raise HTTPException(status_code=404, detail="Partner not found.")

        partner_data = partner_doc.to_dict()
        partner_type = partner_data.get("type")

        if partner_type == "transport":
            # Retrieve transport analytics (e.g., number of deliveries)
            deliveries_ref = db.collection("deliveries").where("partner_id", "==", partnerId)
            deliveries = deliveries_ref.stream()
            num_deliveries = sum(1 for _ in deliveries)
            return {"partner_id": partnerId, "num_deliveries": num_deliveries}
        
        elif partner_type == "cold-storage":
            # Retrieve cold storage analytics (e.g., capacity utilization)
            capacity_ref = db.collection("cold_storage_capacity").document(partnerId)
            capacity_doc = capacity_ref.get()
            
            if not capacity_doc.exists:
                raise HTTPException(status_code=404, detail="Cold storage capacity data not found.")
            
            capacity_data = capacity_doc.to_dict()
            total_capacity = capacity_data.get("total_capacity")
            current_utilization = capacity_data.get("current_utilization")
            utilization_rate = (current_utilization / total_capacity) * 100 if total_capacity else 0

            return {
                "partner_id": partnerId,
                "utilization_rate": utilization_rate
            }
        
        else:
            raise HTTPException(status_code=400, detail="Invalid partner type for analytics.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve analytics: {str(e)}")
