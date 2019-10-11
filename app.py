from flask import Flask
from flask_restful import Api, Resource

from config import config
from auth import AuthenticationHandler

app = Flask(__name__)
app.url_map.strict_slashes = False
api = Api(app)


class LoginResource(Resource):
    def post(self):
        auth_handler = AuthenticationHandler("anon") # TODO get mnemonic and credentials from request
        return auth_handler.get_jwt(), 200


class VerifyResource(Resource):
    pass


api.add_resource(LoginResource, "/login")
api.add_resource(VerifyResource, "/verify")

if __name__ == "__main__":
    app.run(host=config.get_host(), port=config.get_port(), debug=config.is_debug_mode())

