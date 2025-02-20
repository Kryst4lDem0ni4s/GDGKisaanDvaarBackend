from fastapi import APIRouter, HTTPException
from google.cloud import firestore

router = APIRouter()

# Firestore client initialization
db = firestore.Client()

@router.get("/api/analytics/users")
async def get_user_engagement():
    """
    Retrieve user engagement metrics, such as active users, login frequency, etc.
    """
    try:
        # Get the user collection
        users_ref = db.collection("users")
        users = users_ref.stream()

        total_users = 0
        active_users = 0
        inactive_users = 0

        for user in users:
            user_data = user.to_dict()
            total_users += 1
            # Assuming there's an "active" field to track user engagement
            if user_data.get("active"):
                active_users += 1
            else:
                inactive_users += 1

        return {
            "total_users": total_users,
            "active_users": active_users,
            "inactive_users": inactive_users
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch user engagement data: {str(e)}")

@router.get("/api/analytics/sales")
async def get_sales_report():
    """
    Retrieve sales and transaction metrics, such as total sales and transaction volume.
    """
    try:
        # Get the sales transactions collection
        transactions_ref = db.collection("transactions")
        transactions = transactions_ref.stream()

        total_sales = 0
        total_transactions = 0
        avg_order_value = 0

        for transaction in transactions:
            transaction_data = transaction.to_dict()
            total_sales += transaction_data.get("total_amount", 0)
            total_transactions += 1

        if total_transactions > 0:
            avg_order_value = total_sales / total_transactions

        return {
            "total_sales": total_sales,
            "total_transactions": total_transactions,
            "avg_order_value": avg_order_value
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch sales data: {str(e)}")

@router.get("/api/analytics/system")
async def get_system_usage():
    """
    Retrieve system usage statistics, such as active sessions, system errors, etc.
    """
    try:
        # Get session data (example: assume sessions are stored in a Firestore collection)
        sessions_ref = db.collection("sessions")
        sessions = sessions_ref.stream()

        active_sessions = 0
        total_sessions = 0
        total_errors = 0

        for session in sessions:
            session_data = session.to_dict()
            total_sessions += 1
            if session_data.get("active"):
                active_sessions += 1
            if session_data.get("error"):
                total_errors += 1

        return {
            "total_sessions": total_sessions,
            "active_sessions": active_sessions,
            "total_errors": total_errors
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch system usage data: {str(e)}")

@router.get("/api/analytics/sales")
async def get_sales_report(page: int = 1, limit: int = 10):
    """
    Retrieve sales and transaction metrics, with pagination.
    """
    try:
        # Get the sales transactions collection
        transactions_ref = db.collection("transactions").order_by("timestamp")
        
        # Implement pagination using offset and limit
        transactions = transactions_ref.offset((page - 1) * limit).limit(limit).stream()

        total_sales = 0
        total_transactions = 0
        avg_order_value = 0

        for transaction in transactions:
            transaction_data = transaction.to_dict()
            total_sales += transaction_data.get("total_amount", 0)
            total_transactions += 1

        if total_transactions > 0:
            avg_order_value = total_sales / total_transactions

        return {
            "total_sales": total_sales,
            "total_transactions": total_transactions,
            "avg_order_value": avg_order_value,
            "page": page,
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch sales data: {str(e)}")

from fastapi_limiter import FastAPILimiter
from fastapi import FastAPI
import aioredis

app = FastAPI()

@app.on_event("startup")
async def startup():
    redis = await aioredis.create_redis_pool("redis://localhost")
    FastAPILimiter.init(redis)

@router.get("/api/analytics/users")
@limiter.limit("5/minute")  # 5 requests per minute
async def get_user_engagement():
    # Endpoint logic...
    pass
