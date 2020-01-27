from app import create_app

app = flask_app = create_app()

if __name__ == "__main__":
    flask_app.run(debug=True, port=5000, host='0.0.0.0')
