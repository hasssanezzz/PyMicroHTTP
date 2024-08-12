import re, socket, threading, json
from http.client import responses

class Server:
    routes = {}
    beforeAllMiddlewares = []

    def __init__(self, host: str = 'localhost', port: int = 9090) -> None:
        self.host = host
        self.port = port

    def start_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((self.host, self.port))
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.listen()
            print(f'Server listening on {self.host}:{self.port}')
            while True:
                conn, addr = server_socket.accept()
                print(f'Connected by {addr}')
                threading.Thread(target=self.__handleConnection, args=(conn, addr)).start()

    def registerHandler(self, path: str, handler):
        if not self.__isPathValid(path):
            raise ValueError('invalid provided path:', path)
        self.routes[path] = handler

    def register(self, path, middleware = None):
        if not self.__isPathValid(path):
            raise ValueError('invalid provided path:', path)  
                  
        def decorator(func):
            if middleware:
                if isinstance(middleware, list):
                    self.routes[path] = self.__chainMiddlewares(middleware, func)
                else:
                    self.routes[path] = middleware(func)
            else:
                self.routes[path] = func
                
        return decorator
    
    def beforeAll(self):
        def decorator(func):
            self.beforeAllMiddlewares.append(func)
        return decorator
            

    def __handleConnection(self, conn: socket.socket, addr):
        with conn:
            while True:
                data = conn.recv(1024 * 2)
                if not data:
                    break

                reqstr = data.rstrip(b'\x00').decode()
                parsed = self.__parseRequest(reqstr)
                pathkey = f'{parsed["verb"]} {parsed["path"]}'

                if pathkey in self.routes:
                    handler = self.routes[pathkey]
                    
                    if self.beforeAllMiddlewares:
                        chainedHandler = self.__chainMiddlewares(self.beforeAllMiddlewares, handler)
                        result = chainedHandler(parsed)
                    else:
                        result = handler(parsed)
                    
                    if not isinstance(result, tuple):
                        return conn.sendall(self.__writeReponse(self.__checkIfResultIsDict(result)))
                    resultLen = len(result)
                    if resultLen == 3:
                        response, code, headers = result
                        return conn.sendall(self.__writeReponse(self.__checkIfResultIsDict(response), code, headers))
                    if resultLen == 2:
                        response, code = result
                        return conn.sendall(self.__writeReponse(self.__checkIfResultIsDict(response), code))
                    # 500 - invalid number of return values
                    conn.sendall(self.__writeReponse('', 500))
                    raise ValueError('internal server error: handler returned bad number of values:', resultLen)
                # 404 - route not found
                return conn.sendall(self.__writeReponse('', 404))

    def __checkIfResultIsDict(self, result):
        if isinstance(result, dict):
            return json.dumps(result)
        return result

    def __writeReponse(self, resp, code = 200, headers = {}, contentType = 'application/json'):
        resp = str(resp)
        codeMessage = responses.get(code, 'Eshta')
        httpResp = (
            f'HTTP/1.1 {code} {codeMessage}\r\n'
            f'Content-Type: {contentType}\r\n'
            f'Content-Length: {len(resp)}\r\n'
        )

        for header, value in headers.items():
            header, value = str(header), str(value)
            httpResp += f'{header}: {value}\r\n'

        return (httpResp + (
            '\r\n'
            f'{resp}'
        )).encode()

    def __parseRequest(self, reqstr: str):
        sep = '\r\n'
        head, body = reqstr.split(sep + sep)
        headlines = head.split(sep)
        head = headlines[0]
        headlines = headlines[1:]
        verb, path, _ = head.split(' ')
        headers = {}
        for line in headlines:
            idx = line.index(':')
            header, value = line[:idx], line[idx+2:]
            headers[header] = value

        return {
            'verb': verb,
            'path': path,
            'headers': headers,
            'body': body
        }

    def __isPathValid(self, path: str) -> bool:
        pattern = r'^(GET|POST|PUT|DELETE|HEAD|OPTIONS|PATCH) /[^\s]*$'
        return bool(re.match(pattern, path))

    def __chainMiddlewares(self, middlewares, func):
        for middleware in reversed(middlewares):
            func = middleware(func)
        return func