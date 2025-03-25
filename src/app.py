from flask import Flask, jsonify

from src.sign_up.controllers.controllers import sign_up_blueprint
from src.token.controllers.controllers import token_blueprint

app = Flask(__name__)

app.register_blueprint(sign_up_blueprint)
app.register_blueprint(token_blueprint)


@app.route('/ping', methods=['GET'])
def test():
    return jsonify({
        'status': 'Success',
        'message': 'If uou see this message, the server is running!'
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
