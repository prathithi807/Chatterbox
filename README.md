# Chatterbox: Real-time WebSocket Chat Application

# Project Overview

Chatterbox is a high-performance, real-time chat application built using FastAPI and WebSockets. It demonstrates event-driven architecture, asynchronous programming, and modern web technologies to create a scalable chat platform.

# Table of Contents
1. [Features]
2. [Architecture]
3. [Installation]
4. [API Documentation]
5. [Database Schema]
6. [Running the Application]
7. [Project Structure]
8. [Technical Details]


# Features

Real-time Communication: WebSocket-based bidirectional messaging
User Authentication: Token-based session management
Message Persistence: SQLite database for chat history
Multi-user Support: Concurrent connections with broadcast messaging
Multiple Clients: Terminal-based CLI and web-based GUI
Chat History: Last 50 messages loaded on connection
Asynchronous Design: High-performance async/await architecture

# Architecture

# System Components


┌─────────────┐
│   Clients   │ (Terminal/Web)
└──────┬──────┘
       │ WebSocket + HTTP
       ▼
┌─────────────────────────────┐
│    FastAPI Server           │
│  ┌─────────────────────┐   │
│  │ WebSocket Manager   │   │ ← Connection handling
│  └─────────────────────┘   │
│  ┌─────────────────────┐   │
│  │   Authentication    │   │ ← Token-based auth
│  └─────────────────────┘   │
└──────────┬──────────────────┘
           │
           ▼
    ┌──────────────┐
    │   Database   │ (SQLite)
    │ - Users      │
    │ - Messages   │
    └──────────────┘
```

# Data Flow

1. Client Connection:
   - Client registers/logs in via HTTP POST
   - Server returns authentication token
   - Client connects to WebSocket with token

2. Message Broadcasting:
   - Client sends message via WebSocket
   - Server validates and saves to database
   - Server broadcasts to all connected clients

3. Chat History:
   - On connection, server sends last 50 messages
   - Messages displayed in chronological order

---

## Installation

# Prerequisites
- Python 3.8 or higher
- pip package manager

# Setup

1. Clone the repository(or download the project files)

2. Install dependencies:
   bash
   cd app
   pip install -r requirements.txt
   

3. Database initialization:
   The database is automatically created on first server start.

# API Documentation

# Base URL
```
http://127.0.0.1:8000
```

#Endpoints

# 1. Health Check
**GET** `/`

Returns server status.

**Response**:
json
{
  "status": "Server is running"
}


# 2. User Registration
**POST** `/register`

Register a new user account.

**Request Body**:
```json
{
  "username": "alice",
  "password": "password123"
}
```

Response (Success - 200):
```json
{
  "message": "User registered successfully"
}
```

Response (Error - 400):
```json
{
  "detail": "User already exists"
}
```

---

# 3. User Login
POST `/login`

Authenticate and receive an access token.

**Request Body**:
```json
{
  "username": "alice",
  "password": "password123"
}
```

**Response** (Success - 200):
```json
{
  "token": "a1b2c3d4-e5f6-7890-1234-567890abcdef"
}
```

**Response** (Error - 401):
```json
{
  "detail": "Invalid credentials"
}
```

---

#### 4. WebSocket Connection
**WebSocket** `/ws?token={token}`

Establish a persistent WebSocket connection for real-time chat.

**Query Parameters**:
- `token` (required): Authentication token from login

**Messages Sent by Server**:

1. **Chat History** (on connection):
```json
{
  "type": "history",
  "messages": [
    {
      "username": "alice",
      "content": "Hello!",
      "timestamp": "2024-02-07T10:30:00.000000"
    }
  ]
}
```

2. **New Message** (broadcast):
```json
{
  "type": "message",
  "username": "bob",
  "content": "Hi everyone!",
  "timestamp": "2024-02-07T10:31:00.000000"
}
```

3. **Error Message**:
```json
{
  "type": "error",
  "detail": "Invalid message format"
}
```

**Messages Sent by Client**:
```json
{
  "content": "Hello, world!"
}
```

---

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
);
```

### Messages Table
```sql
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    content TEXT NOT NULL,
    timestamp TEXT NOT NULL
);
```

---

## Running the Application

### 1. Start the Server

Navigate to the `app` directory and run:

```bash
uvicorn main:app --reload
```

The server will start on `http://127.0.0.1:8000`

**Server Output**:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Started server process
Database initialized at: /path/to/chat.db
INFO:     Application startup complete.
```

---

### 2. Using the Terminal Client

**Open a new terminal window** and navigate to the `clients` directory:

```bash
cd clients
```

**Step 1: Register/Login**
```bash
python test_auth.py
```

Follow the prompts to create an account and get your authentication token.

**Step 2: Update client.py**

Open `client.py` and update the TOKEN:
```python
TOKEN = "your-token-from-test-auth"
```

**Step 3: Run the client**
```bash
python client.py
```

**Step 4: Start chatting!**
Type messages and press Enter. Messages appear in real-time for all connected users.

---

### 3. Using the Web Client

**Step 1: Open the HTML file**

Double-click `chat.html` or open it in your browser.

**Step 2: Register/Login**

Use the web interface to register and login.

**Step 3: Start chatting!**

Type in the message box and click Send or press Enter.

---

### 4. Multiple Users

To test with multiple users:

1. **Terminal**: Open multiple terminal windows, each running `client.py` with different tokens
2. **Web**: Open multiple browser windows/tabs with different accounts
3. **Mixed**: Use both terminal and web clients simultaneously

---

## Project Structure

```
app (1)/
│
├── app/                          # Server application
│   ├── main.py                   # FastAPI server & WebSocket endpoint
│   ├── connection_manager.py     # WebSocket connection management
│   ├── database.py               # Database operations
│   ├── models.py                 # Pydantic models
│   ├── security.py               # Password hashing
│   ├── check_db.py               # Database inspection utility
│   ├── requirements.txt          # Python dependencies
│   └── __init__.py
│
├── clients/                      # Client applications
│   ├── client.py                 # Terminal-based client
│   ├── client2.py                # Second client instance
│   └── test_auth.py              # Authentication helper
│
├── chat.html                     # Web-based client
└── chat.db                       # SQLite database (auto-created)
```

---

## Technical Details

### Technologies Used

**Backend**:
- FastAPI - Modern async web framework
- Uvicorn - ASGI server
- WebSockets - Real-time bidirectional communication
- SQLite - Lightweight relational database
- Pydantic - Data validation

**Frontend**:
- HTML5 + CSS3 + JavaScript
- WebSocket API
- Fetch API for HTTP requests

### Key Features

**1. Asynchronous Design**
```python
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    # Non-blocking message handling
    while True:
        data = await websocket.receive_text()
        await manager.broadcast(data)
```

**2. Connection Management**
```python
class ConnectionManager:
    def __init__(self):
        self.active_connections = []
    
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)
```

**3. Token-based Authentication**
- UUID tokens generated on login
- Stored in memory (sessions dict)
- Validated before WebSocket connection

**4. Message Persistence**
- All messages saved to SQLite
- Timestamps in ISO format
- Last 50 messages retrieved on connection

---

## Performance Characteristics

- **Concurrent Connections**: Supports thousands (limited by system resources)
- **Message Latency**: Sub-millisecond for local connections
- **Database**: SQLite with row_factory for dict-style access
- **Memory**: Tokens and connections stored in-memory

---

## Security Considerations

**Current Implementation** (Educational/Development):
- SHA256 password hashing (basic)
- UUID tokens (session-based, in-memory)
- No HTTPS/WSS
- No rate limiting

**Production Recommendations**:
- Use bcrypt or Argon2 for password hashing
- Implement JWT tokens with expiration
- Enable HTTPS/WSS
- Add rate limiting
- Input validation and sanitization
- CORS configuration
- Environment variables for configuration

---

## Troubleshooting

### Server won't start
- Check if port 8000 is already in use
- Ensure all dependencies are installed
- Verify Python version (3.8+)

### Client can't connect
- Ensure server is running
- Check token is valid and not expired
- Verify WebSocket URL is correct

### Messages not appearing
- Check server logs for errors
- Verify both clients are authenticated
- Ensure server hasn't restarted (tokens are in-memory)

### Database errors
- Delete `chat.db` and restart server
- Check file permissions

---

## Future Enhancements

Potential improvements:
- Private messaging
- Chat rooms/channels
- User presence indicators
- Message reactions/emojis
- File sharing
- Message editing/deletion
- User profiles and avatars
- Push notifications
- Message search
- Redis for scaling

---

## License

This is an educational project for learning WebSocket communication and real-time applications.

---

## Contact & Support

For issues or questions, refer to the project documentation or consult the FastAPI and WebSocket documentation.

---

**Built with FastAPI, WebSockets, and SQLite**
