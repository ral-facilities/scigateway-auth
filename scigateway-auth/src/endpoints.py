from flask_restful import Resource, reqparse


class Endpoint(Resource):

    def get_credentials_from_post_body(self):
        parser =  reqparse.RequestParser()