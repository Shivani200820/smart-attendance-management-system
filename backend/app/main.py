from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.health import router as health_router
from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.academic import router as academic_router
from app.api.timetable import router as timetable_router
from app.api.attendance_sessions import router as attendance_sessions_router
from app.api.attendance import router as attendance_router
from app.api.reports import router as reports_router

from app.core.config import settings

app = FastAPI(
    title="Attendance Management System API",
    description="Backend API foundation for Attendance Management System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS using settings.ALLOWED_ORIGINS
cors_origins = settings.allowed_origins_list

if "*" in cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_origin_regex=r"https?://.*",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Register API routes under /api
app.include_router(health_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(users_router, prefix="/api")
app.include_router(academic_router, prefix="/api")
app.include_router(timetable_router, prefix="/api")
app.include_router(attendance_sessions_router, prefix="/api")
app.include_router(attendance_router, prefix="/api")
app.include_router(reports_router, prefix="/api")






@app.get("/", include_in_schema=False)
def root():
    """
    Root endpoint redirecting to API status or Swagger docs.
    """
    return {
        "app": "Attendance Management System API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }
