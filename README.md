# PyMicroHTTP

PyMicroHTTP is a lightweight, flexible HTTP framework built from scratch in Python. It provides a simple way to create HTTP services without heavy external dependencies, making it ideal for learning purposes or small projects.

## Features

- Built on raw TCP sockets
- Routing with HTTP verb and path matching
- Middleware support with easy chaining
- JSON response handling
- Zero external dependencies

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/pymicrohttp.git
   cd pymicrohttp
   ```

2. Install the required dependencies:
   ```
   pip install pyjwt
   ```

## Quick Start

Here's a simple example to get you started:

```python
from server import Server

s = Server(port=8080)

@s.register('GET /hello')
def hello(request):
    return {"message": "Hello, World!"}

if __name__ == "__main__":
    s.start_server()
```

Run this script, and you'll have a server running on `http://localhost:8080`. Access it with:

```
curl http://localhost:8080/hello
```

## Routing

Routes are defined using the `@s.register` decorator:

```python
@s.register('GET /users/{id}')
def get_user(request):
    user_id = request['path'].split('/')[-1]
    return {"user_id": user_id}
```

## Middleware

Middleware functions can be used to add functionality to your routes:

```python
def log_middleware(next):
    def handler(request):
        print(f"Request: {request['verb']} {request['path']}")
        return next(request)
    return handler

@s.register('GET /protected', log_middleware)
def protected_route(request):
    return {"message": "This is a protected route"}
```

## Response Handling

The framework supports different types of responses:

1. Dictionary (automatically converted to JSON):
   ```python
   return {"key": "value"}
   ```

2. String:
   ```python
   return "Hello, World!"
   ```

3. Tuple for custom status codes and headers:
   ```python
   return "Not Found", 404
   # or
   return "Created", 201, {"Location": "/resource/1"}
   ```

## Running the Server

To run the server:

```python
if __name__ == "__main__":
    s = Server(port=8080)
    # Register your routes here
    s.start_server()
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
