from fastapi import APIRouter
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

load_dotenv()
from app.config import settings
from app.routers import auth, market, marketplace, chatbot, inventory, ai, analytics, cart, forum, geospatial, groups, notifications, onboarding, orders, partners, payments, sensors, services, sync, traceability, translate, utils

router = APIRouter()

origins = [settings.CLIENT_ORIGIN]

origins = [
    "http://localhost:YOUR_FLUTTER_PORT",  # Replace with your Flutter port
    "http://127.0.0.1:YOUR_FLUTTER_PORT",  # Sometimes needed
]


router.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router.include_router(auth.router, tags=["Authentication"], prefix="/api/auth")
router.include_router(market.router, tags=["Market"], prefix="/api/market")
router.include_router(chatbot.router, tags=["Chatbot"], prefix="/api/chatbot")
router.include_router(marketplace.router, tags=["Marketplace"], prefix="/api/marketplace")
router.include_router(inventory.router, tags=["Inventory"], prefix="/api/inventory")
router.include_router(ai.router, tags=["Authentication"], prefix="/api/auth")
router.include_router(analytics.router, tags=["Market"], prefix="/api/market")
router.include_router(cart.router, tags=["Chatbot"], prefix="/api/chatbot")
router.include_router(forum.router, tags=["Marketplace"], prefix="/api/marketplace")
router.include_router(geospatial.router, tags=["Inventory"], prefix="/api/inventory")
router.include_router(groups.router, tags=["Authentication"], prefix="/api/auth")
router.include_router(notifications.router, tags=["Market"], prefix="/api/market")
router.include_router(onboarding.router, tags=["Chatbot"], prefix="/api/chatbot")
router.include_router(orders.router, tags=["Marketplace"], prefix="/api/marketplace")
router.include_router(partners.router, tags=["Inventory"], prefix="/api/inventory")
router.include_router(payments.router, tags=["Authentication"], prefix="/api/auth")
router.include_router(sensors.router, tags=["Market"], prefix="/api/market")
router.include_router(services.router, tags=["Chatbot"], prefix="/api/chatbot")
router.include_router(sync.router, tags=["Marketplace"], prefix="/api/marketplace")
router.include_router(traceability.router, tags=["Inventory"], prefix="/api/inventory")
router.include_router(translate.router, tags=["Authentication"], prefix="/api/auth")
router.include_router(utils.router, tags=["Market"], prefix="/api/market")


@router.get("/health")
async def root():
    return {"message": "API is working fine."}


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app", host="127.0.0.1", port=8000, log_level="info", reload=True
    )

# App run command
# uvicorn app.main:app --reload

# Swagger URL for this API's
# http://127.0.0.1:8000/docs#/
