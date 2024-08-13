# PyMicroHTTP

PyMicroHTTP is a lightweight, flexible HTTP framework built from scratch in Python. It provides a simple way to create HTTP services without heavy external dependencies, making it ideal for learning purposes or small projects.

__NOTE: this is a toy project and not production ready.__

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

s = Server()

@s.register('GET /hello')
def hello(request):
    return {"message": "Hello, World!"}

@s.register('GET /hello/:name')
def hello_name(request):
    name = request['params'].get('name')
    return {"message": f"Hello, {name}!"}


if __name__ == "__main__":
    s.start_server(port=8080)
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

Following this syntax:
```
VERB /<PATH>
```
With a signle space separating between the verb and the request path.

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

### Path parameters

You can declare dynamic path params using a colon, for example:
```
GET /users/:group/:channel
```
To read these params you can access them via the request object:
```py
@s.register('GET /users/:group/:channel')
def handler(request):
    ...
    group = request['params']['group']
    channel = request['params']['channel']
    ...
```

### Query parameters
You can read query parameters via the request obejct:
```py
@s.register('GET /products')
def handler(request):
    ...
    name = request['query'].get('name', '')
    category = request['query'].get('category', 'shoes')
    ...
```
Note that it is better to use `.get(key, default_value)` because query params are optional and may not exist, and accessing them without the `.get()` method may result in key errors.

## Request Object

The request object is a dict containing these key and value:
```
{
    'verb':    ...
    'path':    ...
    'body':    ...
    'headers': ... # { 'key': 'value' }
    'params':  ... # { 'key': 'value' }
    'query':   ... # { 'key': 'value' }
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

Examples:

1. Accessing headers:
    ```py
    # say hello
    s.register('GET /hello/:name')
    def hello(request):
        name = request['params']['name']
        return "Hello " + name
    ```

1. Accessing dynamic path params:
    ```py
    # say hello `n` times
    s.register('GET /hello/:name/:n')
    def hello(request):
        name, n = request['params']['name'], request['params']['n']
        return "Hello " * int(n) + name
    ```

1. Accessing query params:
    ```py
    # say hello `n` times
    # read n from query params
    # with default value of 3
    s.register('GET /hello/:name')
    def hello(request):
        name = request['params']['name']
        n = request['query'].get('n', 3)
        return "Hello " * n + name
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
        # do your logging logic here
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
    s = Server()
    # Register your routes here
    s.start_server(port=8080)
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
