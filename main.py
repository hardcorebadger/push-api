import os
from flask import Flask, jsonify
from app.database import get_db, engine
from sqlalchemy import text

app = Flask(__name__)

@app.route("/")
def hello_world():
    return {"message": "Hello, World!"}

@app.route("/db-test")
def db_test():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            return jsonify({"message": "Database connection successful!", "result": result.scalar()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)