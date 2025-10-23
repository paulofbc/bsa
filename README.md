# WebSocket Server - Backend Technical Challenge
Asynchronous WebSocket system in Python with datetime broadcasting, Fibonacci processing, and connected client management features.

## How to run

### Option 1: Using UV (Recommended - Faster)

1. Install UV:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Create virtual environment and install dependencies:
```bash
uv venv
uv run pip install -r requirements.txt
```

3. Run the server:
```bash
uv run python server.py
```

4. In another terminal, run the client:
```bash
uv run python client.py
```

### Option 2: Using pip (Traditional)

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the server:
```bash
python server.py
```

4. In another terminal, run the client:
```bash
python client.py
```


## How to use the client
After connecting to the server, you can use the following commands:
```bash
fib <n>  - Calculate the Fibonacci number of n
quit     - Disconnect and exit
```
