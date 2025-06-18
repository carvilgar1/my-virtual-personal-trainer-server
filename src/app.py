import os
import secrets

from flask import Flask, jsonify
from flask_wtf import CSRFProtect

from src.sign_up.controllers.controllers import sign_up_blueprint
from src.token_auth.controllers.controllers import token_blueprint
from src.user_profile.controllers.controllers import user_blueprint
from src.workouts.controllers.controllers import workouts_blueprint

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY") or secrets.token_hex(32)
csrf = CSRFProtect()
csrf.init_app(app)

# Register blueprints
csrf.exempt(sign_up_blueprint) 
app.register_blueprint(sign_up_blueprint)

csrf.exempt(token_blueprint)
app.register_blueprint(token_blueprint)

csrf.exempt(user_blueprint) 
app.register_blueprint(user_blueprint)

csrf.exempt(workouts_blueprint) 
app.register_blueprint(workouts_blueprint)


@app.route('/ping', methods=['GET'])
def test():
    return jsonify({
        'status': 'Success',
        'message': 'If you see this message, the server is running!'
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0')
