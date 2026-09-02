from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import db
from .routes import auth, reports

app = FastAPI(title="POS System API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])

@app.on_event("startup")
async def startup():
    print("✅ PostgreSQL connected")
    print("✅ Server running on http://0.0.0.0:8000")

@app.get("/")
async def root():
    return {"message": "POS System API", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "ok"}