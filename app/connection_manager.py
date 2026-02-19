from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active_connections = []

    def connect(self, websocket: WebSocket):
        self.active_connections.append(websocket)
        print(f"CONNECTED: {len(self.active_connections)} clients")

    def disconnect(self, websocket: WebSocket):
        # Only remove if it exists in the list
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            print(f"DISCONNECTED: {len(self.active_connections)} clients")

    async def broadcast(self, message: str):
        dead = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                dead.append(connection)

        # Remove dead connections
        for d in dead:
            if d in self.active_connections:
                self.active_connections.remove(d)