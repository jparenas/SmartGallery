from main import create_web_server_app

if __name__ == '__main__':
    app = create_web_server_app()
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
