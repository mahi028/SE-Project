from flask_restful import Api

api = Api(prefix='/api') # change it to api

# add Api resouces here. Example:

from .example import Index
api.add_resource(Index, '')