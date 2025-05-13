from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS # Import CORS
import os

app = Flask(__name__)
# Allow all origins for /todos and /todos/* for now.
# For production, you might want to restrict this to your frontend's domain.
CORS(app, resources={
    r"/todos/*": {"origins": ["http://zaynpythonapi.mooo.com", "http://localhost:5173", "http://app.zaynpythonapi.mooo.com"]},
    r"/todos": {"origins": ["http://zaynpythonapi.mooo.com", "http://localhost:5173", "http://app.zaynpythonapi.mooo.com"]}
})

# Database Configuration - Replace with your actual connection string
# For local development, you might use something like:
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@host:port/database'
# For Kubernetes, we'll use environment variables passed from the deployment
db_user = os.environ.get('DB_USER', 'todouser') # Default to 'todouser' if not set
db_password = os.environ.get('DB_PASSWORD', 'supersecretVGpassword123') # Default to 'supersecretVGpassword123' if not set
db_host = os.environ.get('DB_HOST', 'postgres-service.yatest.svc.cluster.local') # Default to Kubernetes service
db_name = os.environ.get('DB_NAME', 'tododb') # Default to 'tododb' if not set
db_port = os.environ.get('DB_PORT', '5432') # Default to '5432' if not set

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define the To-Do model
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_description = db.Column(db.String(200), nullable=False)
    is_completed = db.Column(db.Boolean, default=False)

    def to_dict(self): # Helper to convert model to dictionary
        return {
            'id': self.id,
            'task_description': self.task_description,
            'is_completed': self.is_completed
        }

    def __repr__(self):
        return f'<Todo {self.id} {self.task_description} {self.is_completed}>'

@app.route('/')
def hello():
    return "Hello from Flask To-Do API!"

# Create a new to-do item
@app.route('/todos', methods=['POST'])
def create_todo():
    data = request.get_json()
    if not data or 'task_description' not in data:
        return jsonify({'error': 'Missing task_description'}), 400
    new_todo = Todo(task_description=data['task_description'], is_completed=data.get('is_completed', False))
    db.session.add(new_todo)
    db.session.commit()
    return jsonify(new_todo.to_dict()), 201

# Get all to-do items
@app.route('/todos', methods=['GET'])
def get_todos():
    todos = Todo.query.all()
    return jsonify([todo.to_dict() for todo in todos])

# Get a specific to-do item
@app.route('/todos/<int:todo_id>', methods=['GET'])
def get_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    return jsonify(todo.to_dict())

# Update a to-do item
@app.route('/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    if 'task_description' in data:
        todo.task_description = data['task_description']
    if 'is_completed' in data:
        todo.is_completed = data['is_completed']
        
    db.session.commit()
    return jsonify(todo.to_dict())

# Delete a to-do item
@app.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    db.session.delete(todo)
    db.session.commit()
    return jsonify({'message': 'To-do item deleted'}), 200

def create_tables():
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    # Create database tables if they don't exist
    # In a production app, you'd likely use migrations (e.g., Flask-Migrate)
    create_tables()
    app.run(debug=True, host='0.0.0.0', port=5000)
else:
    # This will be called when the app is run by a WSGI server like Gunicorn (used by 'flask run')
    # This is not ideal for production but might get it working for now.
    create_tables()