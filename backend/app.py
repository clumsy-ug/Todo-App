"""A module that provides an entry point for Flask applications."""

import os
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity,
)
from werkzeug.security import generate_password_hash, check_password_hash

# 環境に応じて.envファイルを読み込む
if os.environ.get("ENVIRONMENT") == "production":
    load_dotenv(".env.production")
else:
    load_dotenv(".env.development")

app = Flask(__name__)

# 環境変数から設定を読み込む
app.config["DEBUG"] = os.environ.get("FLASK_DEBUG", "1") == "1"

# 環境変数から CORS の設定を読み込む
ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
CORS(app, resources={r"/*": {"origins": ALLOWED_ORIGINS}})

# 環境変数からデータベースURIを読み込む
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "sqlite:///my_database.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# JWT設定
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "your-secret-key")
jwt = JWTManager(app)

db = SQLAlchemy(app)


class User(db.Model):
    """A class that represents a user model."""

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        """A function that sets the password hash."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """A function that checks the password hash."""
        return check_password_hash(self.password_hash, password)


class Todo(db.Model):
    """A class that represents a todo model."""

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(80), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def __init__(self, content, user_id):
        self.content = content
        self.user_id = user_id

    def __repr__(self):
        return self.content


# アプリケーションコンテキスト内でデータベースを作成
with app.app_context():
    db.create_all()


@app.route("/todos", methods=["GET"])
@jwt_required()
def get_todos():
    """A function that returns all todos."""
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    todos = Todo.query.filter_by(user_id=user.id).all()
    return jsonify([{"id": todo.id, "content": todo.content} for todo in todos])


@app.route("/todos", methods=["POST"])
@jwt_required()
def add_todo():
    """A function that adds a new todo."""
    if not request.json or "content" not in request.json:
        return jsonify({"error": "Bad Request", "message": "Content is required"}), 400
    content = request.json["content"]
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    todo = Todo(content=content, user_id=user.id)
    db.session.add(todo)
    db.session.commit()
    return jsonify({"id": todo.id, "content": todo.content}), 201


@app.route("/todos/<int:todo_id>", methods=["DELETE"])
@jwt_required()
def delete_todo(todo_id):
    """A function that deletes a todo."""
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    todo = Todo.query.filter_by(id=todo_id, user_id=user.id).first_or_404()
    db.session.delete(todo)
    db.session.commit()
    return jsonify({"id": todo.id, "content": todo.content}), 200


@app.route("/todos/<int:todo_id>", methods=["PUT"])
@jwt_required()
def update_todo(todo_id):
    """A function that updates a todo."""
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    todo = Todo.query.filter_by(id=todo_id, user_id=user.id).first_or_404()
    if not request.json or "content" not in request.json:
        return jsonify({"error": "Bad Request", "message": "Content is required"}), 400
    todo.content = request.json["content"]
    db.session.commit()
    return jsonify({"id": todo.id, "content": todo.content}), 200


@app.route("/register", methods=["POST"])
def register():
    """A function that registers a new user."""
    username = request.json.get("username", None)
    password = request.json.get("password", None)

    # username, password共にiuput欄をそもそもrequiredにしてある(App.jsx側で)ので、
    # どちらかもしくはどちらも空のまま送られることはないはずだが、
    # 予想外のバグ(例えば送ってる途中でデータが消し飛ぶとか)が発生した時のために念の為エラーハンドリングしておく
    if not username and not password:
        return jsonify({"msg": "Missing username and password"}), 400
    if not username:
        return jsonify({"msg": "Missing username"}), 400
    if not password:
        return jsonify({"msg": "Missing password"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"msg": "Username already exists"}), 400

    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({"msg": "Registration successful"}), 201


@app.route("/login", methods=["POST"])
def login():
    """A function that logs in a user."""
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200
    return jsonify({"msg": "Bad username or password"}), 401


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
