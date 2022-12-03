from flask import Flask, request, jsonify
from db_connection_manager import connect_bd,disconnect_bd
from repositories.user_repository import insert_user, is_email_already_register, are_valid_credentials
from models.user import User, AuthCredentials
from models.status import status

app = Flask(__name__)

@app.route('/sign_up', methods = ['POST'])
def sign_up():
    form = request.form

    try:
        user = User(**form)
        user.auth_credentials.encrypt_user_credentials()
    except ValueError as e:
        return jsonify({"status": status.BAD_REQUEST, "description": "{0}".format(e)}), 400
    
    conn = connect_bd()
    if is_email_already_register(conn, user.auth_credentials.email): 
       _status, des, code = status.FORBIDDEN, "User already register", 403
    else:
        insert_user(conn, **user.to_json())
        _status, des, code = status.OK, "User has been registered satisfactorily", 201
    disconnect_bd(conn)
    return jsonify({"status": _status, "description": des}), code

@app.route('/sign_in', methods = ['POST'])
def sign_in():
    form = request.form

    try:
        auth_credentials = AuthCredentials(**form)
        auth_credentials.encrypt_user_credentials()
    except ValueError as e:
        return jsonify({"status": status.BAD_REQUEST, "description": "{0}".format(e)}), 400
    
    conn = connect_bd()
    if are_valid_credentials(conn, auth_credentials): 
        _status, des, code =  status.OK, "Successfully logged in user", 200
    else:
        _status, des, code =  status.UNAUTHORIZED, "Wrong credentials", 401
    disconnect_bd(conn)
    return jsonify({"status": _status, "description": des}), code