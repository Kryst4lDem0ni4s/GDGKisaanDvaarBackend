import os
from fastapi import FastAPI
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from firebase_admin import credentials
import firebase_admin
import uvicorn
from app.config import settings
from app.routers import auth, market, marketplace, chatbot, inventory, ai, analytics, cart, forum, geospatial, groups, notifications, onboarding, orders, partners, payments, sensors, services, sync, traceability, translate, utils

app = FastAPI()
load_dotenv()

# origins = [settings.CLIENT_ORIGIN]

origins = [
    "http://localhost:3001",  # Replace with your Flutter port
    "http://127.0.0.1:3001",  # Sometimes needed
]

CREDENTIALS_FILE = os.getenv("CREDENTIALS_FILE")
cred = credentials.Certificate(CREDENTIALS_FILE)

firebase_admin.initialize_app(cred)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, tags=["Authentication"], prefix="/api/auth")
app.include_router(market.router, tags=["Market"], prefix="/api/market")
app.include_router(chatbot.router, tags=["Chatbot"], prefix="/api/chatbot")
app.include_router(marketplace.router, tags=["Marketplace"], prefix="/api/marketplace")
app.include_router(inventory.router, tags=["Inventory"], prefix="/api/inventory")
app.include_router(ai.router, tags=["Authentication"], prefix="/api/auth")
app.include_router(analytics.router, tags=["Market"], prefix="/api/market")
app.include_router(cart.router, tags=["Chatbot"], prefix="/api/chatbot")
app.include_router(forum.router, tags=["Marketplace"], prefix="/api/marketplace")
app.include_router(geospatial.router, tags=["Inventory"], prefix="/api/inventory")
app.include_router(groups.router, tags=["Authentication"], prefix="/api/auth")
app.include_router(notifications.router, tags=["Market"], prefix="/api/market")
app.include_router(onboarding.router, tags=["Chatbot"], prefix="/api/chatbot")
app.include_router(orders.router, tags=["Marketplace"], prefix="/api/marketplace")
app.include_router(partners.router, tags=["Inventory"], prefix="/api/inventory")
app.include_router(payments.router, tags=["Authentication"], prefix="/api/auth")
app.include_router(sensors.router, tags=["Market"], prefix="/api/market")
app.include_router(services.router, tags=["Chatbot"], prefix="/api/chatbot")
app.include_router(sync.router, tags=["Marketplace"], prefix="/api/marketplace")
app.include_router(traceability.router, tags=["Inventory"], prefix="/api/inventory")
app.include_router(translate.router, tags=["Authentication"], prefix="/api/auth")
app.include_router(utils.router, tags=["Market"], prefix="/api/market")


@app.get("/health")
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
