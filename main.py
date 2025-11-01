"""Main FastAPI application for H. pylori CDSS."""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from contextlib import asynccontextmanager
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import settings
from app.db import create_tables
from app.routes_auth import router as auth_router
from app.routes_reco import router as reco_router
from app.routes_sms import router as sms_router
from app.routes_telemed import router as telemed_router
from app.routes_document import router as document_router


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle management for the application."""
    # Startup
    print("[*] Starting H. pylori CDSS...")
    
    # Validate settings
    try:
        settings.validate()
        print("[OK] Configuration validated")
    except Exception as e:
        print(f"[WARNING] Configuration warning: {e}")
    
    # Create database tables
    create_tables()
    print("[OK] Database initialized")
    
    # Create default admin user
    try:
        from app.db import SessionLocal
        from app.models import User
        from app.auth import get_password_hash
        
        db = SessionLocal()
        admin = db.query(User).filter(User.username == "admin").first()
        
        if admin:
            print("[*] Admin user exists - updating password...")
            admin.hashed_password = get_password_hash("Admin@2024")
            db.commit()
            print("[OK] Admin password updated: admin / Admin@2024")
        else:
            print("[*] Creating default admin user...")
            admin_user = User(
                username="admin",
                email="admin@hpylori.com",
                full_name="Administrator",
                hashed_password=get_password_hash("Admin@2024"),
                role="admin",
                specialty="Gastroenterology",
                institution="H. pylori CDSS",
                is_active=True
            )
            db.add(admin_user)
            db.commit()
            print("[OK] Admin user created: admin / Admin@2024")
        
        db.close()
    except Exception as e:
        print(f"[WARNING] Admin user setup failed: {e}")
    
    # Preload ML models (optional, for faster first request)
    try:
        from app.ml import ml_models
        ml_models.load_screening_model()
        ml_models.load_staging_model()
    except Exception as e:
        print(f"[WARNING] Model loading warning: {e}")
    
    print("[OK] Application ready!")
    
    yield
    
    # Shutdown
    print("[*] Shutting down H. pylori CDSS...")


# Create FastAPI app
app = FastAPI(
    title="H. pylori CDSS",
    description="Clinical Decision Support System for H. pylori Infection Screening and Staging",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

# Include API routers FIRST (order matters in FastAPI)
app.include_router(auth_router)
app.include_router(reco_router)
app.include_router(sms_router)
app.include_router(telemed_router)
app.include_router(document_router)

# Include workflow router (critical for multi-stage workflow)
from app.routes_workflow import router as workflow_router
app.include_router(workflow_router)

# Include prescription router (critical for prescription generation)
from app.routes_prescription import router as prescription_router
app.include_router(prescription_router)

# Include other enhanced routers
try:
    from app.routes_profile import router as profile_router
    from app.routes_admin import router as admin_router
    from app.routes_video import router as video_router
    from app.routes_scheduling import router as scheduling_router
    from app.routes_patient import router as patient_router
    
    app.include_router(profile_router)
    app.include_router(admin_router)
    app.include_router(video_router)
    app.include_router(scheduling_router)
    app.include_router(patient_router)
    print("[OK] All enhanced routes loaded successfully")
except ImportError as e:
    print(f"[WARNING] Some optional routes not available: {e}")

# Mount static files AFTER API routes (prevents route conflicts)
import os
from pathlib import Path

# Ensure directories exist
os.makedirs("uploads", exist_ok=True)

# Mount uploads directory
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Mount images directory
if os.path.exists("images"):
    app.mount("/images", StaticFiles(directory="images"), name="images")

# Mount UI files (MUST be last - acts as catch-all)
app.mount("/ui", StaticFiles(directory="ui", html=True), name="ui")


@app.get("/")
def root():
    """Redirect root to landing page."""
    return RedirectResponse(url="/ui/index.html", status_code=307)


@app.get("/health")
def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "service": "H. pylori CDSS",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)