from .resources import * # nolint
from adrest.api import Api


api = Api(version='0.1')

api.register(AuthorResource)
api.register(BookResource)
