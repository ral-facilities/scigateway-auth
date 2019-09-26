from flask import Flask
from flask_restful import Api, Resource



app = Flask(__name__)
app.url_map.strict_slashes = False
api = Api(app)



if __name__ == "__main__":
    app.run(debug=True)
