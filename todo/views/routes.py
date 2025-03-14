from flask import Blueprint, jsonify, request
from todo.models import db
from todo.models.todo import Todo
from datetime import datetime, timedelta
 
api = Blueprint('api', __name__, url_prefix='/api/v1') 

TEST_ITEM = {
    "id": 1,
    "title": "Watch CSSE6400 Lecture",
    "description": "Watch the CSSE6400 lecture on ECHO360 for week 1",
    "completed": True,
    "deadline_at": "2023-02-27T00:00:00",
    "created_at": "2023-02-20T00:00:00",
    "updated_at": "2023-02-20T00:00:00"
}
 
@api.route('/health') 
def health():
    """Return a status of 'ok' if the server is running and listening to request"""
    return jsonify({"status": "ok"})


@api.route('/todos', methods=['GET'])
def get_todos():
    args = request.args
    completed = args.get('completed')
    window = args.get('window')

    if window is not None and completed is not None:
        max_date = datetime.now() + timedelta(days=int(window))
        todos = Todo.query.filter(Todo.deadline_at <= max_date, Todo.completed.startswith(completed)).all()
    elif completed is not None:
        completed_bool = bool(completed.upper())
        todos = Todo.query.filter(Todo.completed == completed_bool).all()
    elif window is not None:
        max_date = datetime.now() + timedelta(days=int(window))
        todos = Todo.query.filter(Todo.deadline_at <= max_date).all()
    else:
        todos = Todo.query.all()
    result = []
    for todo in todos:
        result.append(todo.to_dict())
    return jsonify(result)

@api.route('/todos/<int:todo_id>', methods=['GET'])
def get_todo(todo_id):
    todo = Todo.query.get(todo_id)
    if todo is None:
        return jsonify({'error': 'Todo not found'}), 404
    return jsonify(todo.to_dict())

@api.route('/todos', methods=['POST'])
def create_todo():

    REQUIRED_KEYS = {'title'}    
    VALID_KEYS = {'title', 'description', 'completed', 'deadline_at', 'created_at', 'updated_at'}
    data = request.get_json()
    extra_fields = set(data.keys()) - VALID_KEYS
    missing_fields = REQUIRED_KEYS - set(data.keys())

    if len(missing_fields) > 0:
        return jsonify({'error': 'Missing JSON'}), 400
    
    if len(extra_fields) > 0:
        return jsonify({'error': f'Unexpected fields: {extra_fields}'}), 400
    todo = Todo(
    title=request.json.get('title'),
    description=request.json.get('description'),
    completed=request.json.get('completed', False),
    )
    if 'deadline_at' in request.json:
        todo.deadline_at = datetime.fromisoformat(request.json.get('deadline_at'))

    # Adds a new record to the database or will update an existing record.
    db.session.add(todo)
    # Commits the changes to the database.
    # This must be called for the changes to be saved.
    db.session.commit()
    return jsonify(todo.to_dict()), 201

@api.route('/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    todo = Todo.query.get(todo_id)
    if todo is None:
        return jsonify({'error': 'Todo not found'}), 404
    valid_keys = {'title', 'description', 'completed', 'deadline_at'}
    extra_fields = set(request.json.keys()) - valid_keys
    if len(extra_fields) > 0:
        return jsonify({'error': f'Unexpected fields: {extra_fields}'}), 400
    todo.title = request.json.get('title', todo.title)
    todo.description = request.json.get('description', todo.description)
    todo.completed = request.json.get('completed', todo.completed)
    todo.deadline_at = request.json.get('deadline_at', todo.deadline_at)
    db.session.commit()
    return jsonify(todo.to_dict())

@api.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    todo = Todo.query.get(todo_id)
    if todo is None:
        return jsonify({}), 200
    db.session.delete(todo)
    db.session.commit()
    return jsonify(todo.to_dict()), 200
 
