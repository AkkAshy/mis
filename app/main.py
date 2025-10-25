from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth, patients, appointments, stats

app = FastAPI(
    title="Medical Information System",
    description="Электронная медицинская информационная система",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(patients.router, prefix="/patients", tags=["patients"])
app.include_router(appointments.router, prefix="/appointments", tags=["appointments"])
app.include_router(stats.router, prefix="/stats", tags=["statistics"])

@app.get("/")
def read_root():
    return {"message": "Medical Information System API"}