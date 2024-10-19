# pylint: skip-file
from flask import Flask
from app.controllers.image_controller import bp as image_bp


app = Flask(__name__)
app.register_blueprint(image_bp)

if __name__ == '__main__':
    app.run(debug=True, port=5000)