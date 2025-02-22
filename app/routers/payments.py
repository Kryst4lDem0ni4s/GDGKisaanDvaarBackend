from fastapi import APIRouter, HTTPException, Depends
import razorpay
from pydantic import BaseModel
from firebase_admin import auth
from config import RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET, db

router = APIRouter()

# Razorpay client
razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))


# Middleware for Firebase authentication
def get_current_user(user_id: str):
    try:
        user = auth.get_user(user_id)
        return user
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or unauthorized user")


@router.post("/api/payments/initiate")
async def initiate_payment(request: PaymentRequest, user=Depends(get_current_user)):
    """
    Creates a Razorpay order and returns the order ID.
    """
    try:
        order_data = {
            "amount": request.amount,
            "currency": request.currency,
            "receipt": request.receipt_id,
            "payment_capture": 1  # Auto-capture payment
        }
        order = razorpay_client.order.create(order_data)

        # Store payment details in Firebase
        db.reference(f"payments/{order['id']}").set({
            "user_id": request.user_id,
            "amount": request.amount,
            "status": "created"
        })

        return {"order_id": order["id"], "status": "created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/payments/status")
async def get_payment_status(order_id: str, user=Depends(get_current_user)):
    """
    Fetches payment status from Razorpay.
    """
    try:
        payment_info = razorpay_client.order.fetch(order_id)
        return {"status": payment_info["status"], "order_id": order_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/api/payments/confirmation")
async def confirm_payment(data: PaymentConfirmation, user=Depends(get_current_user)):
    """
    Verifies the payment signature and marks the order as paid.
    """
    try:
        params_dict = {
            "razorpay_order_id": data.order_id,
            "razorpay_payment_id": data.payment_id,
            "razorpay_signature": data.signature
        }

        # Validate signature
        if razorpay_client.utility.verify_payment_signature(params_dict):
            db.reference(f"payments/{data.order_id}").update({"status": "paid"})
            return {"message": "Payment confirmed", "status": "paid"}
        else:
            raise HTTPException(status_code=400, detail="Invalid payment signature")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/payments/refund")
async def process_refund(request: RefundRequest, user=Depends(get_current_user)):
    """
    Initiates a refund for a given payment.
    """
    try:
        refund_data = {"payment_id": request.payment_id}
        if request.amount:
            refund_data["amount"] = request.amount  # Partial refund

        refund = razorpay_client.payment.refund(refund_data)

        db.reference(f"refunds/{refund['id']}").set({
            "payment_id": request.payment_id,
            "amount": refund["amount"],
            "status": "processed"
        })

        return {"refund_id": refund["id"], "status": "processed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from fastapi import APIRouter, HTTPException, Depends
import razorpay
from pydantic import BaseModel
from firebase_admin import auth
from config import RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET, db

router = APIRouter()

# Razorpay client
razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

# Middleware for Firebase authentication
def get_current_user(user_id: str):
    try:
        user = auth.get_user(user_id)
        return user
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or unauthorized user")


@router.get("/api/payments/history")
async def get_payment_history(user_id: str, user=Depends(get_current_user)):
    """
    Fetches payment history for a specific user from Firebase.
    """
    try:
        payment_ref = db.reference(f"payments").order_by_child("user_id").equal_to(user_id).get()
        if not payment_ref:
            raise HTTPException(status_code=404, detail="No payment history found")
        
        return {"history": list(payment_ref.values())}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/payments/methods")
async def get_payment_methods():
    """
    Fetches available payment methods supported by Razorpay.
    """
    try:
        methods = razorpay_client.payment.fetch_payment_methods()
        return {"methods": methods}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/payments/razorpay")
async def razorpay_custom_integration(data: dict):
    """
    Custom Razorpay API integration. This endpoint can be used to trigger
    custom requests such as fetching transaction details, creating virtual accounts, etc.
    """
    try:
        if "action" not in data or "params" not in data:
            raise HTTPException(status_code=400, detail="Missing action or parameters")

        action = data["action"]
        params = data["params"]

        # Example actions:
        if action == "fetch_payment":
            payment_id = params.get("payment_id")
            if not payment_id:
                raise HTTPException(status_code=400, detail="Payment ID required")
            return razorpay_client.payment.fetch(payment_id)

        if action == "create_virtual_account":
            return razorpay_client.virtual_account.create(params)

        return {"message": "Invalid action"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/integrations/tokens")
async def manage_integration_tokens(request: IntegrationTokenRequest, user=Depends(get_current_user)):
    """
    Store or update integration tokens for external payment providers securely in Firebase.
    """
    try:
        token_ref = db.reference(f"integrations/tokens/{request.provider}")
        token_ref.set({"token": request.token, "updated_by": user.uid})

        return {"message": f"{request.provider} token updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
