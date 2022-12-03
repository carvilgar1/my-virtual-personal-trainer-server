from flask import Flask, request, jsonify
from models.status import status
from db_connection_manager import connect_bd,disconnect_bd
from repositories.user_repository import find_user, insert_user
from models.user import User

app = Flask(__name__)

@app.route('/sign_up', methods = ['POST'])
def sign_up():
    try:
        form = request.form
        #Form data validation
        User(_id = None, **form)
    except ValueError as e:
        return jsonify({"status": status.BAD_REQUEST, "description": "{0}".format(e)}), 400
    
    conn = connect_bd()
    if find_user(conn, email=form['email']): 
       _status, des, code = status.FORBIDDEN, "User already register", 403
    else:
        insert_user(conn, **form)
        _status, des, code = status.OK, "User has been registered satisfactorily", 201
    disconnect_bd(conn)
    return jsonify({"status": _status, "description": des}), code

@app.route('/sign_in', methods = ['POST'])
def sign_in():
    form = request.form
    if 'email' not in form:
        return jsonify({"status": status.BAD_REQUEST, "description": "Email can't be empty or blank"}), 400
    if 'password' not in form:
        return jsonify({"status": status.BAD_REQUEST, "description": "Password can't be empty or blank"}), 400
    
    conn = connect_bd()
    if find_user(conn, **form): 
        _status, des, code =  status.OK, "Successfully logged in user", 200
    else:
        _status, des, code =  status.UNAUTHORIZED, "Wrong credentials", 401
    disconnect_bd(conn)
    return jsonify({"status": _status, "description": des}), code