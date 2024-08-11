import sys
import socket
import threading
from http.client import responses
import datetime
import jwt

JWT_SECRET = '123'

class Server:
    routes = {}

    def __init__(self, host: str = 'localhost', port: int = 9090) -> None:
        self.host = host
        self.port = port

    def start_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((self.host, self.port))
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.listen()
            print(f"Server listening on {self.host}:{self.port}")
            while True:
                conn, addr = server_socket.accept()
                print(f"Connected by {addr}")
                threading.Thread(target=self.handleConnection, args=(conn, addr)).start()

    def handleConnection(self, conn: socket.socket, addr):
        with conn:
            while True:
                data = conn.recv(1024 * 2)
                if not data:
                    break

                reqstr = data.rstrip(b'\x00').decode()
                parsed = self.parseRequest(reqstr)
                pathkey = f'{parsed["verb"]} {parsed["path"]}'

                if pathkey in self.routes:
                    result = self.routes[pathkey](parsed)

                    if not isinstance(result, tuple):
                        return conn.sendall(self.writeReponse(result))

                    resultLen = len(result)
                    if resultLen == 3:
                        response, code, headers = result
                        return conn.sendall(self.writeReponse(response, code, headers))
                    if resultLen == 2:
                        response, code = result
                        return conn.sendall(self.writeReponse(response, code))

                    # 500 - invalid number of return values
                    conn.sendall(self.writeReponse('', 500))
                    raise ValueError("internal server error: handler returned bad number of values:", resultLen)

                # 404 - route not found
                else:
                    conn.sendall(
                        self.writeReponse('', 404)
                    )

    def writeReponse(self, resp, code = 200, headers = {}):
        resp = str(resp)
        codeMessage = responses.get(code, 'Eshta')
        httpResp = (
            f"HTTP/1.1 {code} {codeMessage}\r\n"
            "Content-Type: text/plain\r\n"
            f"Content-Length: {len(resp)}\r\n"
        )

        for header, value in headers.items():
            header, value = str(header), str(value)
            httpResp += f"{header}: {value}\r\n"

        httpResp += (
            "\r\n"
            f"{resp}"
        )

        return httpResp.encode()

    def parseRequest(self, reqstr: str):
        sep = "\r\n"
        head, body = reqstr.split(sep + sep)
        headlines = head.split(sep)
        head = headlines[0]
        headlines = headlines[1:]
        verb, path, _ = head.split(" ")
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

    def GET(self, path, handler):
        if path[0] != '/':
            path = '/' + path
        self.routes[f'GET {path}'] = handler

    def POST(self, path, handler):
        if path[0] != '/':
            path = '/' + path
        self.routes[f'POST {path}'] = handler

    def PUT(self, path, handler):
        if path[0] != '/':
            path = '/' + path
        self.routes[f'PUT {path}'] = handler

    def PATCH(self, path, handler):
        if path[0] != '/':
            path = '/' + path
        self.routes[f'PATCH {path}'] = handler

    def DELETE(self, path, handler):
        if path[0] != '/':
            path = '/' + path
        self.routes[f'DELETE {path}'] = handler

if __name__ == "__main__":
    s = Server(port=int(sys.argv[1]))

    def handlePing(request):
        return "pong", 403

    def handleAuth(request):
        token = request['headers'].get('Authentication', '')
        if not token: return "token not found", 401
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            return f"marhaban {payload['username']}"
        except: return "token can not be decoded", 401

    def handleLogin(request):
        username = request['headers'].get('username', '')
        if not username:
            return "username can not be found", 422
        payload = {
            'username': username,
            'iat': datetime.datetime.utcnow(),
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }
        token = jwt.encode(payload, JWT_SECRET, algorithm='HS256')
        return '', 200, { "Authentication": token }

    s.GET("/ping", handlePing)
    s.GET("/auth", handleAuth)
    s.POST("/login", handleLogin)
    s.start_server()
