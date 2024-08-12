import sys, datetime
import jwt
from pymicrohttp.server import Server

JWT_SECRET = '123'
s = Server(port=int(sys.argv[1]))

@s.beforeAll()
def loggerMiddleware(next):
    def handler(request):
        verb, path = request['verb'], request['path']
        print(f'{datetime.datetime.now()} {verb} {path}')
        return next(request)
    return handler

def authMiddleware(next):
    def handler(request):
        token = request['headers'].get('Authorization', '')
        if not token: return "token not found", 401
        try:
            request['auth_payload'] = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            return next(request)
        except: return "token can not be decoded", 401
    return handler

@s.register('GET /ping')
def handlePing(request):
    return {"resp": "pong"}, 418

@s.register('GET /auth', authMiddleware)
def handleAuth(request):
    username = request['auth_payload']['username']
    return f"Hello {username}!!"

@s.register('POST /auth')
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
    return '', 200, { "Authorization": token }

if __name__ == "__main__":
    s.start_server()
