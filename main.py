import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Appointment

app = FastAPI(title="Barbershop API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Barbershop backend is running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "Unknown"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response

# Helper to convert Mongo _id to string
class AppointmentOut(BaseModel):
    id: str
    name: str
    email: Optional[str]
    phone: str
    date: str
    time: str
    service: str
    notes: Optional[str]
    status: str
    preferred_barber: Optional[str]

# Create appointment
@app.post("/api/appointments", response_model=dict)
async def create_appointment(appointment: Appointment):
    try:
        inserted_id = create_document("appointment", appointment)
        return {"id": inserted_id, "status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# List appointments (basic, latest first)
@app.get("/api/appointments", response_model=List[AppointmentOut])
async def list_appointments(limit: int = 50):
    try:
        docs = get_documents("appointment", {}, limit)
        # Sort by created_at desc if field exists
        docs_sorted = sorted(docs, key=lambda d: d.get("created_at"), reverse=True)
        result = []
        for d in docs_sorted:
            result.append(AppointmentOut(
                id=str(d.get("_id")),
                name=d.get("name"),
                email=d.get("email"),
                phone=d.get("phone"),
                date=d.get("date"),
                time=d.get("time"),
                service=d.get("service"),
                notes=d.get("notes"),
                status=d.get("status", "pending"),
                preferred_barber=d.get("preferred_barber"),
            ))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Basic barber info endpoint
class BarberInfo(BaseModel):
    name: str
    tagline: str
    about: str
    address: str
    phone: str
    email: Optional[str]
    hours: dict
    latitude: float
    longitude: float

BARBER_INFO = BarberInfo(
    name="Your Barbershop",
    tagline="Fresh fades. Clean shaves. Good vibes.",
    about="We are a neighborhood barbershop focused on classic cuts and modern styles. Enjoy a chill atmosphere, premium products, and barbers who care about the details.",
    address="123 Main St, Your City",
    phone="(555) 123-4567",
    email="book@yourbarbershop.com",
    hours={
        "Mon-Fri": "9:00 AM - 7:00 PM",
        "Sat": "9:00 AM - 5:00 PM",
        "Sun": "Closed"
    },
    latitude=40.7128,
    longitude=-74.0060,
)

@app.get("/api/info", response_model=BarberInfo)
async def get_info():
    return BARBER_INFO

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
