from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    description="A Job in AI Era — Single LangGraph Agent Career Intelligence Backend",
    version="1.0.0"
)

# Robust CORS Middleware Setup — supports both localhost & 127.0.0.1 with credentials
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Router
from backend.api.routes import router
app.include_router(router)


@app.get("/")
async def root():
    return {
        "status": "online",
        "app": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "models": {
            "chat": settings.MODEL_CHAT,
            "parsing": settings.MODEL_PARSING,
            "matching": settings.MODEL_MATCHING,
            "cover_letter": settings.MODEL_COVER_LETTER,
        }
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": settings.APP_NAME}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=settings.APP_PORT, reload=True)
