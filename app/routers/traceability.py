from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Query
from pydantic import BaseModel
from firebase_admin import firestore, auth, storage
from google.cloud import vision, speech_v1p1beta1 as speech
from config import db
import io
from typing import Optional, List
import uuid

router = APIRouter()

# Google Cloud Services
speech_client = speech.SpeechClient()

class TraceabilityScanRequest(BaseModel):
    code_type: str  # e.g., QR, Barcode
    code_value: str

class TraceabilityDocumentRequest(BaseModel):
    product_id: str
    document_type: str  # e.g., Invoice, Certificate
    document_url: str

class ReviewRequest(BaseModel):
    product_id: str
    rating: int  # 1 to 5
    comment: Optional[str] = None
    user_id: str

# Middleware for Firebase authentication
def get_current_user(user_id: str):
    try:
        user = auth.get_user(user_id)
        return user
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or unauthorized user")

@router.get("/api/traceability")
async def get_traceability(product_id: str, user=Depends(get_current_user)):
    """
    Retrieve traceability data for a specific product.
    """
    try:
        trace_ref = db.reference(f"traceability/{product_id}").get()
        if not trace_ref:
            raise HTTPException(status_code=404, detail="Traceability data not found")
        return {"traceability_data": trace_ref}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/traceability/scan")
async def scan_traceability_code(request: TraceabilityScanRequest, user=Depends(get_current_user)):
    """
    Scan a QR code or Barcode for product tracking.
    """
    try:
        scan_ref = db.reference("traceability/scans").push()
        scan_data = request.dict()
        scan_data["user_id"] = user.uid
        scan_ref.set(scan_data)
        return {"message": "Code scanned successfully", "scan_id": scan_ref.key}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/traceability/upload")
async def upload_traceability_document(file: UploadFile = File(...), product_id: str = Query(...), document_type: str = Query(...), user=Depends(get_current_user)):
    """
    Upload supporting traceability documents for a product.
    """
    try:
        document_id = str(uuid.uuid4())
        blob = storage.bucket().blob(f"traceability/documents/{product_id}/{document_id}-{file.filename}")
        blob.upload_from_file(file.file)
        document_url = blob.public_url

        db.reference(f"traceability/{product_id}/documents").push().set({
            "document_type": document_type,
            "document_url": document_url,
            "uploaded_by": user.uid
        })

        return {"message": "Document uploaded successfully", "document_url": document_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/reviews")
async def get_reviews(product_id: str, user=Depends(get_current_user)):
    """
    Retrieve reviews for a specific product.
    """
    try:
        reviews_ref = db.reference(f"reviews/{product_id}").get()
        reviews = reviews_ref if reviews_ref else []
        return {"reviews": reviews}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/reviews")
async def submit_review(request: ReviewRequest, user=Depends(get_current_user)):
    """
    Submit a review for a product.
    """
    try:
        if request.user_id != user.uid:
            raise HTTPException(status_code=403, detail="Unauthorized user ID")

        review_ref = db.reference(f"reviews/{request.product_id}").push()
        review_data = request.dict()
        review_data["review_id"] = review_ref.key
        review_ref.set(review_data)

        return {"message": "Review submitted successfully", "review_id": review_ref.key}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/reviews/summary")
async def get_review_summary(product_id: str, user=Depends(get_current_user)):
    """
    Retrieve summary of reviews (e.g., average rating) for a product.
    """
    try:
        reviews_ref = db.reference(f"reviews/{product_id}").get()
        if not reviews_ref:
            return {"average_rating": 0, "total_reviews": 0}

        ratings = [review["rating"] for review in reviews_ref.values()]
        average_rating = sum(ratings) / len(ratings) if ratings else 0
        return {"average_rating": average_rating, "total_reviews": len(ratings)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Query
from pydantic import BaseModel
from firebase_admin import firestore, auth, storage
from google.cloud import vision, speech_v1p1beta1 as speech
from config import db
import io
from typing import Optional, List
import uuid

router = APIRouter()

# Google Cloud Services
speech_client = speech.SpeechClient()

class TraceabilityScanRequest(BaseModel):
    code_type: str  # e.g., QR, Barcode
    code_value: str

class TraceabilityDocumentRequest(BaseModel):
    product_id: str
    document_type: str  # e.g., Invoice, Certificate
    document_url: str

class ReviewRequest(BaseModel):
    product_id: str
    rating: int  # 1 to 5
    comment: Optional[str] = None
    user_id: str

class ModerateReviewRequest(BaseModel):
    review_id: str
    action: str  # "approve", "reject", "flag"
    reason: Optional[str] = None
    moderator_id: str

# Middleware for Firebase authentication
def get_current_user(user_id: str):
    try:
        user = auth.get_user(user_id)
        return user
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or unauthorized user")

@router.put("/api/reviews/{reviewId}")
async def edit_review(reviewId: str, request: ReviewRequest, user=Depends(get_current_user)):
    """
    Edit an existing review (if editing is allowed).
    """
    try:
        review_ref = db.reference(f"reviews/{request.product_id}/{reviewId}")
        review = review_ref.get()
        if not review:
            raise HTTPException(status_code=404, detail="Review not found")
        if review["user_id"] != user.uid:
            raise HTTPException(status_code=403, detail="Unauthorized to edit this review")
        review_ref.update(request.dict())
        return {"message": "Review edited successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/api/reviews/{reviewId}")
async def delete_review(reviewId: str, product_id: str, user=Depends(get_current_user)):
    """
    Delete a review.
    """
    try:
        review_ref = db.reference(f"reviews/{product_id}/{reviewId}")
        review = review_ref.get()
        if not review:
            raise HTTPException(status_code=404, detail="Review not found")
        if review["user_id"] != user.uid:
            raise HTTPException(status_code=403, detail="Unauthorized to delete this review")
        review_ref.delete()
        return {"message": "Review deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/users/{userId}/reviews")
async def get_user_reviews(userId: str, user=Depends(get_current_user)):
    """
    Retrieve a user's review history.
    """
    try:
        if userId != user.uid:
            raise HTTPException(status_code=403, detail="Unauthorized access to this user's reviews")
        reviews_ref = db.reference("reviews").get()
        user_reviews = [review for product_reviews in reviews_ref.values() for review in product_reviews.values() if review["user_id"] == userId]
        return {"user_reviews": user_reviews}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/api/reviews/moderate")
async def moderate_review(request: ModerateReviewRequest, user=Depends(get_current_user)):
    """
    Admin/moderator action to moderate reviews.
    """
    try:
        # Authorization check (assuming admin/moderator roles are managed via custom claims)
        if not user.custom_claims.get("is_admin") and not user.custom_claims.get("is_moderator"):
            raise HTTPException(status_code=403, detail="Unauthorized action")

        review_ref = db.reference(f"reviews/{request.review_id}")
        review = review_ref.get()
        if not review:
            raise HTTPException(status_code=404, detail="Review not found")

        if request.action == "approve":
            review_ref.update({"status": "approved"})
        elif request.action == "reject":
            review_ref.update({"status": "rejected", "moderator_reason": request.reason})
        elif request.action == "flag":
            review_ref.update({"status": "flagged", "moderator_reason": request.reason})
        else:
            raise HTTPException(status_code=400, detail="Invalid moderation action")

        return {"message": "Moderation action applied successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

