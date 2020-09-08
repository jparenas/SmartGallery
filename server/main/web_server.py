from flask import Flask, send_from_directory

import os


app = Flask(__name__, static_url_path='/',
            static_folder=os.environ.get('APP_STATIC_DIR'))


@app.route('/api')
def showMain():
    return "Hello world!"


@app.route('/', defaults={'path': ''})
@app.route("/<string:path>")
@app.route('/<path:path>')
def catch_all(path):
    return send_from_directory(app.static_folder, "index.html")


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
