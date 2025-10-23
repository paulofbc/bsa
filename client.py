import asyncio
import websockets
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WebSocketClient:
    def __init__(self, uri: str = "ws://localhost:8765"):
        self.uri = uri
        self.websocket = None
    
    async def connect(self):
        """Connect to the WebSocket server"""
        try:
            self.websocket = await websockets.connect(self.uri)
            logger.info(f"Connected to {self.uri}")
            return True
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False
    
    async def send_fibonacci_request(self, n: int):
        """Send a Fibonacci calculation request"""
        if not self.websocket:
            logger.error("Not connected to server")
            return
        
        message = json.dumps({
            "type": "fibonacci",
            "n": n
        })
        await self.websocket.send(message)
        logger.info(f"Sent Fibonacci request for n={n}")
    
    async def receive_messages(self):
        """Receive and process messages from the server"""
        try:
            async for message in self.websocket:
                data = json.loads(message)
                message_type = data.get("type")
                
                match message_type:
                    case "welcome":
                        logger.info(f"Welcome message: {data.get('message')}")
                        logger.info(f"Client ID: {data.get('client_id')}")
                    
                    case "datetime":
                        logger.info(f"Server time: {data.get('data')}")
                    
                    case "fibonacci_result":
                        logger.info(f"Fibonacci({data.get('n')}) = {data.get('result')}")
                    
                    case "error":
                        logger.error(f"Server error: {data.get('message')}")
                    
                    case _:
                        logger.warning(f"Unknown message type: {message_type}")
        
        except websockets.exceptions.ConnectionClosed:
            logger.info("Connection closed by server")
        except Exception as e:
            logger.error(f"Error receiving messages: {e}")
    
    async def interactive_mode(self):
        """Run client in interactive mode"""
        if not await self.connect():
            return
        
        # Start receiving messages in background
        receive_task = asyncio.create_task(self.receive_messages())
        
        print("\n=== WebSocket Client Interactive Mode ===")
        print("Commands:")
        print("  fib <n>  - Calculate Fibonacci(n)")
        print("  quit     - Disconnect and exit")
        print("=========================================\n")
        
        try:
            while True:
                try:
                    user_input = await asyncio.get_event_loop().run_in_executor(
                        None, input, "Enter command: "
                    )
                    
                    if user_input.lower() == "quit":
                        break
                    
                    parts = user_input.split()
                    if len(parts) == 2 and parts[0].lower() == "fib":
                        try:
                            n = int(parts[1])
                            await self.send_fibonacci_request(n)
                        except ValueError:
                            print("Invalid number. Usage: fib <number>")
                    else:
                        print("Invalid command. Use 'fib <n>' or 'quit'")
                
                except EOFError:
                    break
        
        finally:
            if self.websocket:
                await self.websocket.close()
                logger.info("Disconnected from server")
            receive_task.cancel()

async def main():
    """Main entry point for the client"""
    client = WebSocketClient()
    await client.interactive_mode()

if __name__ == "__main__":
    asyncio.run(main())