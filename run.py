#!/usr/bin/env python
"""
run.py -- Simple startup script for Antigravity AI backend.
Usage: python run.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import uvicorn
from backend.config import settings

if __name__ == "__main__":
    print("=" * 54)
    print("   ANTIGRAVITY AI BACKEND")
    print("   Single LangGraph Agent + OpenRouter + Playwright")
    print("=" * 54)
    print(f"   Chat Model    : {settings.MODEL_CHAT}")
    print(f"   Parsing Model : {settings.MODEL_PARSING}")
    print(f"   Matching Model: {settings.MODEL_MATCHING}")
    print(f"   Cover Letter  : {settings.MODEL_COVER_LETTER}")
    print(f"   Embeddings    : BAAI/bge-small-en-v1.5 (fastembed/ONNX)")
    print(f"   API Server    : http://localhost:{settings.APP_PORT}")
    print(f"   Swagger Docs  : http://localhost:{settings.APP_PORT}/docs")
    print("=" * 54)
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=settings.APP_PORT,
        reload=True,
        log_level="info"
    )
