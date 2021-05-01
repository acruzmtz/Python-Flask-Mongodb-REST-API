from flask import Flask, request, jsonify, Response
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash
from bson import json_util
from bson.objectid import ObjectId

app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb://localhost:27017/python-restapi-pymongo"
mongo = PyMongo(app)


@app.route('/users', methods=["POST"])
def users():
    """ this function is to create new users using POST method and returns the id, username, email and password of the user
    created """

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
    """ this function returns all users in the database or returns a message if there are no users """

    users = mongo.db.users.find()
    response = json_util.dumps(users)

    if response == '[]':
        return jsonify({"message": "Not users yet"})

    return Response(response, mimetype="application/json")


@app.route('/users/<oid>', methods=['GET'])
def get_users_by_oid(oid):
    """ this function search for a user by id, returns the user if it exists or returns an error message """

    user = mongo.db.users.find_one({"_id": ObjectId(oid)})

    if not user:
        return "User not found"

    response = json_util.dumps(user)

    return Response(response, mimetype='application/json')


@app.route('/users/<id>', methods=['DELETE'])
def delete_user(id):
    """ this function is to remove the user by id and return the id of the user or an error if the user does not exist """

    user_exists = get_users_by_oid(id)

    if user_exists == "User not found":
        return jsonify({"message": "User not exist"})
    else:
        mongo.db.users.delete_one({'_id': ObjectId(id)})

    return jsonify({
        "message": f"the user with id: {id} was deleted successfully"
    })


@app.route('/users/<id>', methods=['PUT'])
def update_user(id):
    """ this function is to update the user by id and return an error message if the user does not exist """

    user_exists = get_users_by_oid(id)

    if user_exists == "User not found":
        return jsonify({"message": "User not exist"})

    username = request.json.get("username")
    email = request.json.get("email")
    password = request.json.get("password")

    if username and email and password:
        hashed_password = generate_password_hash(password)

        mongo.db.users.update_one(
            {
                "_id": ObjectId(id)
            },
            { '$set': {
                "username": username,
                "email": email,
                "password": hashed_password
            }}
        )

        response = jsonify({
            "message": f"User with id: {id} was updated successfully"
        })

        return response

    return jsonify({"message": "An error was ocurred, please try again"})


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
