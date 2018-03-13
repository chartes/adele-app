from app import app as flask_app

if __name__ == "__main__":
    flask_app.run(debug=True, port=5001, host='0.0.0.0')
