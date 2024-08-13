class TodosDB:
    def __init__(self):
        self.todos = []

    def find(self, id = None):
        if not id:
            return self.todos

        for i in range(len(self.todos)):
            if self.todos[i]['id'] == id:
                return self.todos[i]

    def create(self, title):
        index = len(self.todos)
        todo = {
            'id': str(index),
            'title': title,
            'checked': False
        }
        self.todos.append(todo)
        return todo

    def update(self, id, todo):
        for i in range(len(self.todos)):
            if self.todos[i]['id'] == id:
                self.todos[i] = todo
                return self.todos[i]

    def toggle(self, id):
        for i in range(len(self.todos)):
            if self.todos[i]['id'] == id:
                self.todos[i]['checked'] = not self.todos[i]['checked']
                return self.todos[i]

    def delete(self, id):
        for i in range(len(self.todos)):
            if self.todos[i]['id'] == id:
                self.todos.pop(i)
                return 1
