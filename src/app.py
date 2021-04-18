from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash
from bson import json_util

app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb://localhost:27017/python-restapi-pymongo"
mongo = PyMongo(app)


@app.route('/users', methods=["POST"])
def users():
    """ this function is to create new users using POST method """
    if request.method == "POST":
        username = request.json.get("username")
        email = request.json.get("email")
        password = request.json.get("password")

        if username and email and password:
            hashed_password = generate_password_hash(password)

            id = mongo.db.users.insert({
                "username": username,
                "email": email,
                "password": hashed_password
            })

            response = {
                "id": str(id),
                "username": username,
                "email": email,
                "password": hashed_password
            }

        else:
            return error()

    return response


@app.route('/users', methods=['GET'])
def get_users():
    users = mongo.db.users.find()
    response = json_util.dumps(users)


    return response


@app.errorhandler(404)
def error(error=None):
    response = jsonify(
        {
            "message": "Error: " + request.url,
            "status": 404
        }
    )

    response.status_code = 404

    return response


if __name__ == '__main__':
    app.run(debug=True)
