# PyMicroHTTP

PyMicroHTTP is a lightweight, flexible HTTP framework built from scratch in Python. It provides a simple way to create HTTP services without heavy external dependencies, making it ideal for learning purposes or small projects.

## Features

- Built on raw TCP sockets
- Routing with HTTP verb and path matching
- Middleware support with easy chaining
- JSON response handling
- Zero external dependencies

## Installation

You can install the package via pip:
```
$ pip install pymicrohttp
```

## Quick Start

Here's a simple example to get you started:

```python
from pymicrohttp.server import Server

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
@s.register('GET /ping')
def ping_handler(request):
    return "pong"
```

Example:

```python
@s.register('POST /login')
def login_handler(request):
    try:
        body = json.loads(request['body'])
        if 'username' not in body or 'password' not in body:
            # do somthing
    except:
        return { 'error': 'invalid data' }
```

## Request Object

The request object is a dict containing these key and value:
```py
{
    'verb': ...
    'path': ...
    'headers': ...
    'body': ...
}
```

You can access it via the handler:
```py
@s.register('GET /ping')
def ping_handler(request):
    # accessing request headers
    if 'double' in request['headers']:
        return "pong-pong"
    return "pong"
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


## Middleware
Middleware functions can be used to add functionality to your routes:

```python
def log_middleware(next):
    def handler(request):
        print(f"Request: {request['verb']} {request['path']}")
        return next(request)
    return handler

@s.register('GET /logged', log_middleware)
def logged_route(request):
    return {"message": "This is a logged route"}
```

### Before all

If you want to run a middleware before every single request you can use the `s.beforeAll()` decorator:
```py
@s.beforeAll()
def logger(next):
    def handler(request):
        verb, path = request['verb'], request['path']
        print(f'{datetime.datetime.now()} {verb} {path}')
        return next(request)
    return handler
```

### Middleware chaining
You can chain multiple middlwares together
```py
def log_middleware(next):
    def handler(request):
        # do your loggin logic here
        return next(request)
    return handler

def auth_middleware(next):
    def handler(request):
        # do your auth logic here
        return next(request)
    return handler

@s.register('GET /protected', [log_middleware, auth_middleware])
def protected_route(request):
    return {"message": "This is a protected route"}
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
