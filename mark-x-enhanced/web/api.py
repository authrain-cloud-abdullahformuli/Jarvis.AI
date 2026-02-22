"""FastAPI web interface for Mark-X Enhanced."""

import asyncio
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import json

from core.config import settings
from core.agent_orchestrator import orchestrator
from core.skills_loader import skills_loader
from memory.persistent_db import db

logger = logging.getLogger(__name__)

app = FastAPI(title="Mark-X Enhanced", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connections
active_connections: List[WebSocket] = []


class Message(BaseModel):
    """Chat message model."""
    text: str
    platform: str = "web"


class SettingsUpdate(BaseModel):
    """Settings update model."""
    key: str
    value: str


@app.get("/")
async def read_root():
    """Serve the main UI."""
    return FileResponse("web/static/index.html")


@app.get("/api/status")
async def get_status():
    """Get agent status."""
    return {
        "status": "online" if orchestrator.running else "offline",
        "skills_loaded": len(skills_loader.get_all_skills()),
        "platform": "macos",
        "version": "1.0.0"
    }


@app.get("/api/skills")
async def get_skills():
    """Get all available skills."""
    skills = skills_loader.get_all_skills()
    return {
        "skills": [
            {
                "name": skill.name,
                "description": skill.description,
                "category": skill.category.value,
                "examples": skill.examples
            }
            for skill in skills
        ]
    }


@app.get("/api/conversations")
async def get_conversations(limit: int = 50):
    """Get conversation history."""
    convs = db.get_recent_conversations(limit=limit)
    return {
        "conversations": [
            {
                "id": conv.id,
                "timestamp": conv.timestamp.isoformat(),
                "user_input": conv.user_input,
                "ai_response": conv.ai_response,
                "platform": conv.platform
            }
            for conv in convs
        ]
    }


@app.get("/api/memory")
async def get_memory():
    """Get user memory."""
    memory = db.get_user_memory_dict()
    return {"memory": memory}


@app.post("/api/message")
async def send_message(message: Message):
    """Send a message to the agent."""
    try:
        response = await orchestrator.process_message(
            text=message.text,
            user_id="web_user",
            context={
                "platform": message.platform,
                "username": "User"
            }
        )
        
        # Broadcast to all WebSocket connections
        for connection in active_connections:
            try:
                await connection.send_json({
                    "type": "message",
                    "user": message.text,
                    "assistant": response
                })
            except:
                pass
        
        return {"response": response}
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/settings")
async def update_settings(settings_update: SettingsUpdate):
    """Update settings."""
    # This would update settings in the config
    return {"status": "updated", "key": settings_update.key}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication."""
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            if message_data.get("type") == "message":
                response = await orchestrator.process_message(
                    text=message_data["text"],
                    user_id="web_user",
                    context={
                        "platform": "web",
                        "username": "User"
                    }
                )
                
                await websocket.send_json({
                    "type": "message",
                    "user": message_data["text"],
                    "assistant": response
                })
    
    except WebSocketDisconnect:
        active_connections.remove(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        if websocket in active_connections:
            active_connections.remove(websocket)


@app.on_event("startup")
async def startup_event():
    """Initialize agent on startup."""
    await orchestrator.initialize()
    # Don't start integrations in web mode
    logger.info("Web API started")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean shutdown."""
    await orchestrator.stop()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        log_level="info"
    )
