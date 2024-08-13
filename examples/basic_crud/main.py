import sys
import json
from inmemory_db import TodosDB
from pymicrohttp.server import Server


in_memory_db = TodosDB()
s = Server()


@s.register('GET /')
def show(request):
    todos = in_memory_db.find() or []
    checked = request['query'].get('checked', '')
    if not checked:
        return todos

    return [t for t in todos if t['checked'] == (checked not in ['0', 'false'])]


@s.register('GET /:id')
def find(request):
    id = request['params'].get('id')
    todo = in_memory_db.find(id)
    return todo if todo else ({'error': 'id not found'}, 404)


@s.register('POST /')
def create(request):
    try:
        btitle = json.loads(request['body']).get('title')
        if not btitle:
            return {'error': 'please provide a todo title'}, 400
        return in_memory_db.create(btitle)
    except json.JSONDecodeError:
        return {'error': 'can not parse json'}, 422


@s.register('PUT /:id')
def toggle(request):
    id = request['params'].get('id')
    todo = in_memory_db.toggle(id)
    return todo if todo else ({'error': 'id not found'}, 404)


@s.register('DELETE /:id')
def delete(request):
    id = request['params'].get('id')
    result = in_memory_db.delete(id)
    return ('', 204) if result else ({'error': 'id not found'}, 404)


if __name__ == '__main__':
    s.start_server(port=int(sys.argv[1]))
