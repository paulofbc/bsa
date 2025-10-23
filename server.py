import asyncio
import websockets
import json
from datetime import datetime
from typing import Set
import logging
from database import Database

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WebSocketServer:
    def __init__(self, host: str = "0.0.0.0", port: int = 8765):
        self.host = host
        self.port = port
        self.clients: Set[websockets.WebSocketServerProtocol] = set()
        self.db = Database()
        
    def fibonacci(self, n: int) -> int:
        """Calculate Fibonacci number recursively with memoization"""
        if n <= 0:
            return 0
        elif n == 1:
            return 1
        
        # For larger numbers, use iterative approach for efficiency
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return b
    
    async def broadcast_datetime(self):
        """Send current datetime to all connected clients every second"""
        while True:
            await asyncio.sleep(1)
            if self.clients:
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                message = json.dumps({
                    "type": "datetime",
                    "data": current_time
                })
                
                # Send to all connected clients
                disconnected_clients = set()
                for client in self.clients:
                    try:
                        await client.send(message)
                    except websockets.exceptions.ConnectionClosed:
                        disconnected_clients.add(client)
                
                # Remove disconnected clients
                for client in disconnected_clients:
                    await self.unregister_client(client)
    
    async def register_client(self, websocket: websockets.WebSocketServerProtocol):
        """Register new client connection"""
        self.clients.add(websocket)
        client_id = id(websocket)
        client_address = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        
        # Save to database
        self.db.add_client(client_id, client_address)
        logger.info(f"Client connected: {client_address} (ID: {client_id})")
        logger.info(f"Total connected clients: {len(self.clients)}")
        
        # Send welcome message
        welcome_message = json.dumps({
            "type": "welcome",
            "message": "Connected to WebSocket server",
            "client_id": client_id
        })
        await websocket.send(welcome_message)
    
    async def unregister_client(self, websocket: websockets.WebSocketServerProtocol):
        """Unregister client connection"""
        if websocket in self.clients:
            self.clients.remove(websocket)
            client_id = id(websocket)
            client_address = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
            
            # Remove from database
            self.db.remove_client(client_id)
            logger.info(f"Client disconnected: {client_address} (ID: {client_id})")
            logger.info(f"Total connected clients: {len(self.clients)}")
    
    async def handle_message(self, websocket: websockets.WebSocketServerProtocol, message: str):
        """Process incoming messages from clients"""
        try:
            data = json.loads(message)
            command_type = data.get("type")
            
            if command_type == "fibonacci":
                n = data.get("n")
                
                if not isinstance(n, int) or n < 0:
                    error_response = json.dumps({
                        "type": "error",
                        "message": "Invalid input. 'n' must be a non-negative integer"
                    })
                    await websocket.send(error_response)
                    return
                
                # Calculate Fibonacci
                logger.info(f"Calculating Fibonacci({n}) for client {id(websocket)}")
                result = self.fibonacci(n)
                
                # Send result only to requesting client
                response = json.dumps({
                    "type": "fibonacci_result",
                    "n": n,
                    "result": result
                })
                await websocket.send(response)
                logger.info(f"Fibonacci({n}) = {result} sent to client {id(websocket)}")
            
            else:
                error_response = json.dumps({
                    "type": "error",
                    "message": f"Unknown command type: {command_type}"
                })
                await websocket.send(error_response)
                
        except json.JSONDecodeError:
            error_response = json.dumps({
                "type": "error",
                "message": "Invalid JSON format"
            })
            await websocket.send(error_response)
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            error_response = json.dumps({
                "type": "error",
                "message": str(e)
            })
            await websocket.send(error_response)
    
    async def handler(self, websocket: websockets.WebSocketServerProtocol, path: str):
        """Main handler for WebSocket connections"""
        await self.register_client(websocket)
        
        try:
            async for message in websocket:
                await self.handle_message(websocket, message)
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Connection closed for client {id(websocket)}")
        finally:
            await self.unregister_client(websocket)
    
    async def start(self):
        """Start the WebSocket server"""
        # Create datetime broadcast task
        asyncio.create_task(self.broadcast_datetime())
        
        # Start WebSocket server
        async with websockets.serve(self.handler, self.host, self.port):
            logger.info(f"WebSocket server started on ws://{self.host}:{self.port}")
            await asyncio.Future()  # Run forever

if __name__ == "__main__":
    server = WebSocketServer()
    asyncio.run(server.start())
