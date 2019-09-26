from flask import Flask
from flask_restful import Api, Resource



app = Flask(__name__)
app.url_map.strict_slashes = False
api = Api(app)


class LoginResource(Resource):
    pass


class VerifyResource(Resource):
    pass


api.add_resource(LoginResource, "/login")
api.add_resource(VerifyResource, "/verify")

if __name__ == "__main__":
    app.run(debug=True)
