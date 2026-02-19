from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import uuid
import json
import logging

from connection_manager import ConnectionManager
from database import init_db, get_connection, get_last_messages
from models import UserRegister, UserLogin
from security import hash_password, verify_password

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# -------------------- APP INIT --------------------
app = FastAPI(title="Chatterbox API", description="Real-time WebSocket Chat Application", version="1.0.0")

# ✅ CORS FIX (VERY IMPORTANT)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # frontend allowed
    allow_credentials=True,
    allow_methods=["*"],        # allows OPTIONS
    allow_headers=["*"],
)

manager = ConnectionManager()
sessions = {}  # token → username


# -------------------- STARTUP --------------------
@app.on_event("startup")
def startup():
    try:
        init_db()
        logger.info("✅ Server started successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")
        raise


@app.on_event("shutdown")
def shutdown():
    logger.info("🔴 Server shutting down")


# -------------------- AUTH --------------------
@app.post("/register", tags=["Authentication"])
def register(user: UserRegister):
    """Register a new user account"""
    try:
        conn = get_connection()
        cur = conn.cursor()

        # Validate username
        if len(user.username) < 3:
            raise HTTPException(status_code=400, detail="Username must be at least 3 characters")
        
        if len(user.password) < 6:
            raise HTTPException(status_code=400, detail="Password must be at least 6 characters")

        cur.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (user.username, hash_password(user.password))
        )
        conn.commit()
        logger.info(f"✅ New user registered: {user.username}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Registration failed for {user.username}: {e}")
        raise HTTPException(status_code=400, detail="User already exists")
    finally:
        conn.close()

    return {"message": "User registered successfully"}


@app.post("/login", tags=["Authentication"])
def login(user: UserLogin):
    """Authenticate user and receive access token"""
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "SELECT password_hash FROM users WHERE username = ?",
            (user.username,)
        )
        row = cur.fetchone()
        conn.close()

        if not row or not verify_password(user.password, row[0]):
            logger.warning(f"⚠️ Failed login attempt for: {user.username}")
            raise HTTPException(status_code=401, detail="Invalid credentials")

        token = str(uuid.uuid4())
        sessions[token] = user.username
        
        logger.info(f"✅ User logged in: {user.username}")
        return {"token": token}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Login error for {user.username}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# -------------------- HEALTH --------------------
@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint"""
    return {
        "status": "Server is running",
        "version": "1.0.0",
        "active_connections": len(manager.active_connections),
        "active_sessions": len(sessions)
    }


# -------------------- WEBSOCKET --------------------
@app.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...)
):
    """WebSocket endpoint for real-time chat"""
    
    # 🔒 AUTH CHECK
    if token not in sessions:
        logger.warning(f"⚠️ Unauthorized WebSocket connection attempt with token: {token[:8]}...")
        await websocket.close(code=1008, reason="Unauthorized")
        return

    username = sessions[token]
    
    try:
        await websocket.accept()
        manager.connect(websocket)
        logger.info(f"🔌 {username} connected. Total connections: {len(manager.active_connections)}")

        # 🔹 SEND CHAT HISTORY
        try:
            history = get_last_messages(limit=50)
            await websocket.send_json({
                "type": "history",
                "messages": history
            })
            logger.debug(f"📜 Sent {len(history)} messages to {username}")
        except Exception as e:
            logger.error(f"❌ Failed to send history to {username}: {e}")

        # 🔹 MAIN MESSAGE LOOP
        while True:
            try:
                raw = await websocket.receive_text()

                # 🔹 VALIDATE MESSAGE FORMAT
                try:
                    data = json.loads(raw)
                    content = data.get("content", "").strip()
                    
                    if not content:
                        await websocket.send_json({
                            "type": "error",
                            "detail": "Message cannot be empty"
                        })
                        continue
                    
                    if len(content) > 5000:
                        await websocket.send_json({
                            "type": "error",
                            "detail": "Message too long (max 5000 characters)"
                        })
                        continue
                        
                except json.JSONDecodeError:
                    logger.warning(f"⚠️ Invalid JSON from {username}")
                    await websocket.send_json({
                        "type": "error",
                        "detail": "Invalid message format"
                    })
                    continue
                except Exception as e:
                    logger.error(f"❌ Message validation error: {e}")
                    await websocket.send_json({
                        "type": "error",
                        "detail": "Invalid message format"
                    })
                    continue

                timestamp = datetime.utcnow().isoformat()

                # 🔹 SAVE MESSAGE
                try:
                    conn = get_connection()
                    cur = conn.cursor()
                    cur.execute(
                        "INSERT INTO messages (username, content, timestamp) VALUES (?, ?, ?)",
                        (username, content, timestamp)
                    )
                    conn.commit()
                    conn.close()
                except Exception as e:
                    logger.error(f"❌ Database error saving message from {username}: {e}")
                    await websocket.send_json({
                        "type": "error",
                        "detail": "Failed to save message"
                    })
                    continue

                # 🔹 BROADCAST MESSAGE
                message_data = {
                    "type": "message",
                    "username": username,
                    "content": content,
                    "timestamp": timestamp
                }
                
                try:
                    await manager.broadcast(json.dumps(message_data))
                    logger.debug(f"📤 {username}: {content[:50]}...")
                except Exception as e:
                    logger.error(f"❌ Broadcast error: {e}")

            except WebSocketDisconnect:
                logger.info(f"👋 {username} disconnected (normal)")
                break
            except Exception as e:
                logger.error(f"❌ Unexpected error in message loop for {username}: {e}")
                break

    except WebSocketDisconnect:
        logger.info(f"👋 {username} disconnected during handshake")
    except Exception as e:
        logger.error(f"❌ WebSocket error for {username}: {e}")
    finally:
        manager.disconnect(websocket)
        logger.info(f"🔌 {username} disconnected. Remaining connections: {len(manager.active_connections)}")


# -------------------- ADMIN ENDPOINTS --------------------
@app.get("/stats", tags=["Admin"])
async def get_stats():
    """Get server statistics"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT COUNT(*) FROM users")
        total_users = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM messages")
        total_messages = cur.fetchone()[0]
        
        conn.close()
        
        return {
            "total_users": total_users,
            "total_messages": total_messages,
            "active_connections": len(manager.active_connections),
            "active_sessions": len(sessions)
        }
    except Exception as e:
        logger.error(f"❌ Stats error: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve statistics")
