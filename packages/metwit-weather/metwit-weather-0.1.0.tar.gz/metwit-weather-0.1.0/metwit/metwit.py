from .rest import Resource, RestApi


class Metwit(RestApi):
    base_url = "https://api.metwit.com/"
    token_url = 'https://api.metwit.com/token/'
    dialog_url = "https://metwit.com/oauth/authorize/"

    weather = Resource('/v2/weather/')
    metags = Resource('/v2/metags/')
    users = Resource('/v2/users/')
