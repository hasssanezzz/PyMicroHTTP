import sys, datetime
import jwt
from server import Server

JWT_SECRET = '123'
s = Server(port=int(sys.argv[1]))

@s.register('GET /ping')
def handlePing(request):
    return {"resp": "pong"}, 418

@s.register('GET /auth')
def handleAuth(request):
    token = request['headers'].get('Authentication', '')
    if not token: return "token not found", 401
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return f"marhaban {payload['username']}"
    except: return "token can not be decoded", 401

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
    return '', 200, { "Authentication": token }

if __name__ == "__main__":
    s.start_server()
