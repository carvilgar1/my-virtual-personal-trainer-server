from flask import Flask
import users.interfaces.controllers as user_controllers

app = Flask(__name__)

app.add_url_rule("/sign_in", methods = ["POST"], view_func=user_controllers.sign_in_controller)
app.add_url_rule("/sign_up", methods = ["POST"], view_func=user_controllers.sign_up_controller)
