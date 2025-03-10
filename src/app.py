from flask import Flask, jsonify

from src.settings import APP_REPOSITORIES, LOCALIZER
from src.sign_up.controllers.controllers import sign_up_blueprint

app = Flask(__name__)
app.config['APP_REPOSITORIES'] = APP_REPOSITORIES
app.config['LOCALIZER'] = LOCALIZER

app.register_blueprint(sign_up_blueprint)


@app.route('/ping', methods=['GET'])
def test():
    return jsonify({
        'status': 'Success',
        'message': 'If uou see this message, the server is running!'
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
