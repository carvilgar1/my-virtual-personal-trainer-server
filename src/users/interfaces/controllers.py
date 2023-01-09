from flask import request, jsonify
import json
from appcore.domain.status import Status
from appcore.interfaces.mongodb_connection_manager import MongoDBConnectionManagerImpl
from users.domain.service import UserService
from users.interfaces.mongo_repository_impl import MongoDBUserRepositoryImpl

user_service = UserService(MongoDBUserRepositoryImpl(MongoDBConnectionManagerImpl()))

def sign_up_controller():
    user_service.user_repository.base_repository.create_connection()
    form = request.form
    if user_service.is_email_already_register(form['email']):
        _status, des, code = Status.FORBIDDEN, "User already register", 403
    else:
        user_service.insert_user(form)
        _status, des, code = Status.OK, "User has been registered satisfactorily", 201
    user_service.user_repository.base_repository.close_connection()
    return jsonify({"status": _status, "description": des}), code


def sign_in_controller():
    user_service.user_repository.base_repository.create_connection()
    if user_service.are_valid_credentials(request.form['email'], request.form['password']):
        _status, des, code = Status.OK, "Successfully logged in user", 200
    else:
        _status, des, code = Status.UNAUTHORIZED, "Wrong credentials", 401
    user_service.user_repository.base_repository.close_connection()
    return jsonify({"status": _status, "description": des}), code


def find_user_controller():
    user_service = UserService(
        MongoDBUserRepositoryImpl(MongoDBConnectionManagerImpl()))
    return jsonify({"status": Status.OK, "description": json.dumps(user_service.get_all_users(),
                                                                   default=serialize_user)}), 200


def serialize_user(user):
    res = user.__dict__['_id'] = str(user.__dict__['_id'])
    return res
