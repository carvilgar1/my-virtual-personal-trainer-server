from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/test', methods=['GET'])
def test():
    return jsonify({
        'status': 'Success', 
        'message': 'If uou see this message, the test was successful!'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)