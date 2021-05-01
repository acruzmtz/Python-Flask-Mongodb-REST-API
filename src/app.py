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


    return Response(response, mimetype="application/json")


@app.route('/users/<oid>', methods=['GET'])
def get_users_by_oid(oid):
    user = mongo.db.users.find_one({"_id": ObjectId(oid)})

    if not user:
        return jsonify({'message': "User not found"})

    response = json_util.dumps(user)

    return Response(response, mimetype='application/json')


@app.route('/users/<id>', methods=['DELETE'])
def delete_user(id):
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
    user_exists = get_users_by_oid(id)
    print(user_exists)
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
