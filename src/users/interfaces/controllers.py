from flask import request, jsonify
from users.application.sign_in import sign_in
from users.application.sign_up import sign_up

def sign_up_controller():
    form = request.form
    response = sign_up(form)
    return jsonify(response.__dict__), response.code

def sign_in_controller():
    form = request.form
    response = sign_in(form)
    return jsonify(response.__dict__), response.code
